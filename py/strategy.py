# strategy.py

import asyncio
import logging
from typing import List, Dict, Any, Tuple, Optional
from exchange_connector import ExchangeConnector
from order_manager import OrderManager
from config import TRADING_PAIRS, ARBITRAGE_PARAMS

# Setup logging
logging.basicConfig(
    filename='strategy.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TradingStrategy:
    """Defines and executes arbitrage trading strategies with advanced features."""

    def __init__(self, exchanges: List[str]):
        self.exchanges = exchanges
        self.connectors = {exchange: ExchangeConnector(exchange) for exchange in exchanges}
        self.order_managers = {exchange: OrderManager(exchange) for exchange in exchanges}
    
    async def detect_arbitrage_opportunity(self) -> Optional[Tuple[str, str, float, float]]:
        """Detect arbitrage opportunities between exchanges."""
        prices = await self._fetch_all_prices()
        opportunity = self._find_arbitrage_opportunities(prices)
        if opportunity:
            logging.info(f"Arbitrage opportunity detected: {opportunity}")
        else:
            logging.info("No arbitrage opportunities found.")
        return opportunity

    async def execute_arbitrage(self, opportunity: Tuple[str, str, float, float]) -> None:
        """Execute trades based on detected arbitrage opportunities."""
        buy_exchange, sell_exchange, buy_price, sell_price = opportunity
        amount = self._calculate_trade_amount(buy_price, sell_price)

        logging.info(f"Executing arbitrage: Buy on {buy_exchange} at {buy_price}, Sell on {sell_exchange} at {sell_price}")
        
        # Place buy order on the buy exchange
        buy_order = await self.order_managers[buy_exchange].place_order('ETH/USD', amount, buy_price, 'BUY')
        if not buy_order:
            logging.error(f"Failed to place buy order on {buy_exchange}")
            return

        # Place sell order on the sell exchange
        sell_order = await self.order_managers[sell_exchange].place_order('ETH/USD', amount, sell_price, 'SELL')
        if not sell_order:
            logging.error(f"Failed to place sell order on {sell_exchange}. Attempting to cancel buy order.")
            # Attempt to cancel the buy order if the sell order fails
            await self.order_managers[buy_exchange].cancel_order(buy_order.get('orderId'))
            return

        # Monitor orders to ensure they are filled
        await asyncio.gather(
            self.order_managers[buy_exchange].monitor_orders([buy_order.get('orderId')], 'ETH/USD'),
            self.order_managers[sell_exchange].monitor_orders([sell_order.get('orderId')], 'ETH/USD')
        )
        logging.info(f"Arbitrage execution complete: Buy order {buy_order['orderId']}, Sell order {sell_order['orderId']}")

    async def _fetch_all_prices(self) -> Dict[str, Dict[str, float]]:
        """Fetch prices from all connected exchanges with error handling."""
        tasks = []
        for exchange in self.connectors:
            for pair in TRADING_PAIRS:
                tasks.append(self._safe_fetch_price(exchange, pair['pair']))

        results = await asyncio.gather(*tasks)
        prices = {}
        for exchange, price_data in results:
            if price_data:  # Only include if data is successfully fetched
                prices[exchange] = price_data
        return prices

    async def _safe_fetch_price(self, exchange: str, pair: str) -> Tuple[str, Optional[Dict[str, float]]]:
        """Fetch price with error handling for individual exchange connectors."""
        try:
            price = await self.connectors[exchange].fetch_price(pair)
            return exchange, price
        except Exception as e:
            logging.error(f"Error fetching price from {exchange} for {pair}: {e}")
            return exchange, None

    def _find_arbitrage_opportunities(self, prices: Dict[str, Dict[str, float]]) -> Optional[Tuple[str, str, float, float]]:
        """Find the best arbitrage opportunity from the fetched prices."""
        best_opportunity = None
        highest_profit = 0

        for buy_exchange, buy_prices in prices.items():
            for sell_exchange, sell_prices in prices.items():
                if buy_exchange == sell_exchange:
                    continue
                
                buy_price = buy_prices.get('ETH/USD')
                sell_price = sell_prices.get('ETH/USD')

                if not buy_price or not sell_price:
                    continue

                profit = sell_price - buy_price
                if profit > highest_profit and profit > ARBITRAGE_PARAMS['min_profit_threshold']:
                    highest_profit = profit
                    best_opportunity = (buy_exchange, sell_exchange, buy_price, sell_price)

        return best_opportunity

    def _calculate_trade_amount(self, buy_price: float, sell_price: float) -> float:
        """Calculate the trade amount based on risk management and the price."""
        volume_limit = ARBITRAGE_PARAMS['trade_volume_limit']
        profit_margin = sell_price - buy_price
        # Example: trade smaller amounts if profit margin is low
        trade_amount = volume_limit * (profit_margin / sell_price)  
        return max(trade_amount, ARBITRAGE_PARAMS['min_trade_volume'])

    async def run(self) -> None:
        """Continuously run the trading strategy with configurable update intervals."""
        while True:
            opportunity = await self.detect_arbitrage_opportunity()
            if opportunity:
                await self.execute_arbitrage(opportunity)
            await asyncio.sleep(ARBITRAGE_PARAMS['update_interval'])

async def main():
    """Example usage of TradingStrategy."""
    exchanges = ['binance', 'coinbase']  # Add more exchanges as needed
    strategy = TradingStrategy(exchanges)
    await strategy.run()

if __name__ == "__main__":
    asyncio.run(main())