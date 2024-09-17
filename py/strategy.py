# strategy.py

import asyncio
import logging
from typing import List, Dict, Any, Tuple
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
    """Defines and executes trading strategies with advanced features."""

    def __init__(self, exchanges: List[str]):
        self.exchanges = exchanges
        self.connectors = {exchange: ExchangeConnector(exchange) for exchange in exchanges}
        self.order_managers = {exchange: OrderManager(exchange) for exchange in exchanges}
    
    async def detect_arbitrage_opportunity(self) -> Tuple[str, str, float, float]:
        """Detect arbitrage opportunities between exchanges."""
        prices = await self._fetch_all_prices()
        opportunities = self._find_arbitrage_opportunities(prices)
        return opportunities

    async def execute_arbitrage(self, opportunity: Tuple[str, str, float, float]) -> None:
        """Execute trades based on detected arbitrage opportunities."""
        buy_exchange, sell_exchange, buy_price, sell_price = opportunity
        amount = self._calculate_trade_amount(buy_price, sell_price)

        # Place buy order on the buy exchange
        buy_order = await self.order_managers[buy_exchange].place_order('ETH/USD', amount, buy_price, 'BUY')
        if not buy_order:
            logging.error(f"Failed to place buy order on {buy_exchange}")
            return

        # Place sell order on the sell exchange
        sell_order = await self.order_managers[sell_exchange].place_order('ETH/USD', amount, sell_price, 'SELL')
        if not sell_order:
            logging.error(f"Failed to place sell order on {sell_exchange}")
            # Attempt to cancel the buy order if the sell order fails
            await self.order_managers[buy_exchange].cancel_order(buy_order.get('orderId'), 'ETH/USD')
            return

        # Monitor orders to ensure they are filled
        await asyncio.gather(
            self.order_managers[buy_exchange].monitor_orders([buy_order.get('orderId')], 'ETH/USD'),
            self.order_managers[sell_exchange].monitor_orders([sell_order.get('orderId')], 'ETH/USD')
        )
    
    async def _fetch_all_prices(self) -> Dict[str, Dict[str, float]]:
        """Fetch prices from all connected exchanges."""
        tasks = []
        for exchange in self.connectors:
            for pair in TRADING_PAIRS:
                tasks.append(self.connectors[exchange].fetch_price(pair['pair']))
        prices = {}
        results = await asyncio.gather(*tasks)
        for exchange, price in zip(self.connectors.keys(), results):
            prices[exchange] = price
        return prices

    def _find_arbitrage_opportunities(self, prices: Dict[str, Dict[str, float]]) -> Tuple[str, str, float, float]:
        """Find the best arbitrage opportunity from the fetched prices."""
        best_opportunity = None
        highest_profit = 0
        for buy_exchange in prices:
            for sell_exchange in prices:
                if buy_exchange == sell_exchange:
                    continue
                buy_price = prices[buy_exchange].get('ETH/USD')
                sell_price = prices[sell_exchange].get('ETH/USD')
                if not buy_price or not sell_price:
                    continue
                profit = sell_price - buy_price
                if profit > highest_profit:
                    highest_profit = profit
                    best_opportunity = (buy_exchange, sell_exchange, buy_price, sell_price)
        return best_opportunity

    def _calculate_trade_amount(self, buy_price: float, sell_price: float) -> float:
        """Calculate the trade amount based on the price and other parameters."""
        # Implement risk management and trading volume calculations
        volume_limit = ARBITRAGE_PARAMS['trade_volume_limit']
        return min(volume_limit, 1.0)  # Example: Adjust as needed
    
    async def run(self) -> None:
        """Continuously run the trading strategy."""
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
