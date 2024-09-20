# trading_strategy.py

import asyncio
import logging
import json
import numpy as np
from typing import List, Dict, Any, Optional
import websockets
from config import TRADING_PAIRS, ARBITRAGE_PARAMS
from order_manager import OrderManager

# Setup logging
logging.basicConfig(
    filename='trading_strategy.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TradingStrategy:
    """Implements advanced trading strategies including real-time arbitrage detection."""

    def __init__(self):
        self.order_manager = OrderManager()
        self.prices = {pair['pair']: {} for pair in TRADING_PAIRS}
        self.active_trades = {}

    async def run(self) -> None:
        """Main loop to run the trading strategy."""
        tasks = [
            self.detect_arbitrage_opportunities(),
            self.handle_real_time_updates()
        ]
        await asyncio.gather(*tasks)

    async def detect_arbitrage_opportunities(self) -> None:
        """Detect arbitrage opportunities across trading pairs."""
        while True:
            try:
                for pair in TRADING_PAIRS:
                    await self._check_arbitrage_for_pair(pair['pair'], pair['min_trade_amount'])
            except Exception as e:
                logging.error(f"Error in arbitrage detection: {e}")
            await asyncio.sleep(ARBITRAGE_PARAMS['update_interval'])

    async def _check_arbitrage_for_pair(self, pair: str, min_trade_amount: float) -> None:
        """Check for arbitrage opportunities for a single trading pair."""
        if pair not in self.prices:
            return
        
        prices = self.prices[pair]
        if len(prices) < 2:
            # Not enough price data to detect arbitrage
            return

        sorted_prices = sorted(prices.values())
        best_buy_price = sorted_prices[0]
        best_sell_price = sorted_prices[-1]

        price_diff = best_sell_price - best_buy_price
        if price_diff / best_buy_price >= ARBITRAGE_PARAMS['price_difference_threshold']:
            logging.info(f"Arbitrage opportunity detected for {pair}: Buy at {best_buy_price}, Sell at {best_sell_price}")
            await self._execute_trades(pair, best_buy_price, best_sell_price, min_trade_amount)

    async def _execute_trades(self, pair: str, buy_price: float, sell_price: float, amount: float) -> None:
        """Execute buy and sell trades for a detected arbitrage opportunity."""
        if pair in self.active_trades:
            logging.info(f"Skipping trade execution for {pair} as an active trade is ongoing.")
            return

        self.active_trades[pair] = True
        try:
            # Fetch updated prices before placing orders
            latest_prices = await self._fetch_prices_for_pair(pair)
            buy_orders = [
                self.order_manager.place_order(exchange, pair, amount, buy_price, 'BUY')
                for exchange in self.order_manager.exchanges
                if buy_price in latest_prices.get(exchange, [])
            ]
            sell_orders = [
                self.order_manager.place_order(exchange, pair, amount, sell_price, 'SELL')
                for exchange in self.order_manager.exchanges
                if sell_price in latest_prices.get(exchange, [])
            ]

            # Execute all buy orders
            buy_results = await asyncio.gather(*buy_orders)
            for result in buy_results:
                if result.get('orderId'):
                    logging.info(f"Buy order placed successfully: {result}")

            # Execute all sell orders
            sell_results = await asyncio.gather(*sell_orders)
            for result in sell_results:
                if result.get('orderId'):
                    logging.info(f"Sell order placed successfully: {result}")
        except Exception as e:
            logging.error(f"Error executing trades for {pair}: {e}")
        finally:
            del self.active_trades[pair]

    async def handle_real_time_updates(self) -> None:
        """Handle real-time updates from exchanges via WebSockets."""
        ws_tasks = [self._listen_to_websocket(exchange_name) for exchange_name in self.order_manager.exchanges]
        await asyncio.gather(*ws_tasks)

    async def _listen_to_websocket(self, exchange_name: str) -> None:
        """Listen to WebSocket updates for a specific exchange."""
        exchange = self.order_manager.exchanges[exchange_name]
        websocket_url = exchange.get_websocket_url()

        async with websockets.connect(websocket_url) as websocket:
            while True:
                try:
                    message = await websocket.recv()
                    await self._process_websocket_message(exchange_name, message)
                except Exception as e:
                    logging.error(f"WebSocket error for {exchange_name}: {e}")
                    await asyncio.sleep(5)  # Wait before reconnecting

    async def _process_websocket_message(self, exchange_name: str, message: str) -> None:
        """Process a WebSocket message from an exchange."""
        try:
            data = json.loads(message)
            pair = data.get('pair')
            price = data.get('price')

            if pair and price:
                if pair in self.prices:
                    self.prices[pair][exchange_name] = price
                    logging.info(f"Updated price for {pair} from {exchange_name}: {price}")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding WebSocket message from {exchange_name}: {e}")

    def calculate_slippage(self, executed_price: float, expected_price: float) -> float:
        """Calculate slippage percentage."""
        return ((executed_price - expected_price) / expected_price) * 100

    def handle_risk_management(self, price_diff: float) -> None:
        """Advanced risk management strategy."""
        avg_price = np.mean([price for prices in self.prices.values() for price in prices.values()])
        price_diff_ratio = price_diff / avg_price
        if price_diff_ratio > ARBITRAGE_PARAMS['price_difference_threshold']:
            logging.warning(f"High risk detected: Price difference ratio is {price_diff_ratio:.2%}")

if __name__ == "__main__":
    strategy = TradingStrategy()
    asyncio.run(strategy.run())