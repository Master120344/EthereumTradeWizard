# trading_bot.py

import asyncio
import logging
import requests
from typing import List, Dict, Any
from config import (
    EXCHANGE_API_KEYS, EXCHANGE_URLS, TRADING_PAIRS, ARBITRAGE_PARAMS, 
    LOGGING_SETTINGS, TIMING_SETTINGS
)

# Setup logging
logging.basicConfig(
    filename=LOGGING_SETTINGS['log_file'],
    level=getattr(logging, LOGGING_SETTINGS['log_level']),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ExchangeAPI:
    """Handles interactions with a single exchange."""
    
    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name
        self.api_key = EXCHANGE_API_KEYS[exchange_name]['api_key']
        self.api_secret = EXCHANGE_API_KEYS[exchange_name]['api_secret']
        self.base_url = EXCHANGE_URLS[exchange_name]
        self.session = requests.Session()

    async def fetch_price(self, pair: str) -> float:
        """Fetch current price of a trading pair."""
        url = f"{self.base_url}/api/v3/ticker/price"
        params = {'symbol': pair.replace('/', '')}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return float(data['price'])
        except requests.RequestException as e:
            logging.error(f"Error fetching price from {self.exchange_name} for pair {pair}: {e}")
            return None

    async def place_order(self, pair: str, amount: float, price: float, order_type: str) -> Dict[str, Any]:
        """Place an order on the exchange."""
        url = f"{self.base_url}/api/v3/order"
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        params = {
            'symbol': pair.replace('/', ''),
            'side': order_type,
            'type': 'LIMIT',
            'price': price,
            'quantity': amount,
            'timeInForce': 'GTC'
        }
        
        try:
            response = self.session.post(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error placing {order_type} order on {self.exchange_name} for pair {pair}: {e}")
            return {}

class TradingBot:
    def __init__(self):
        self.exchanges = {name: ExchangeAPI(name) for name in EXCHANGE_URLS.keys()}
        self.pair_prices = {}

    async def fetch_prices(self) -> Dict[str, Dict[str, float]]:
        """Fetch prices for all trading pairs from all exchanges."""
        prices = {pair['pair']: {} for pair in TRADING_PAIRS}
        
        async def fetch_from_exchange(exchange: ExchangeAPI):
            for pair in prices.keys():
                price = await exchange.fetch_price(pair)
                if price is not None:
                    prices[pair][exchange.exchange_name] = price
        
        tasks = [fetch_from_exchange(exchange) for exchange in self.exchanges.values()]
        await asyncio.gather(*tasks)
        return prices

    def detect_arbitrage_opportunity(self, prices: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """Detect arbitrage opportunities based on price discrepancies."""
        opportunities = []

        for pair, exchange_prices in prices.items():
            if len(exchange_prices) < 2:
                continue

            sorted_prices = sorted(exchange_prices.items(), key=lambda x: x[1])
            low_exchange, low_price = sorted_prices[0]
            high_exchange, high_price = sorted_prices[-1]

            price_diff = (high_price - low_price) / low_price
            if price_diff >= ARBITRAGE_PARAMS['price_difference_threshold']:
                opportunities.append({
                    'pair': pair,
                    'buy_exchange': low_exchange,
                    'sell_exchange': high_exchange,
                    'buy_price': low_price,
                    'sell_price': high_price,
                    'price_diff': price_diff,
                    'trade_amount': min([pair_info['min_trade_amount'] for pair_info in TRADING_PAIRS if pair_info['pair'] == pair], default=0)
                })
        
        return opportunities

    async def execute_trade(self, opportunity: Dict[str, Any]) -> None:
        """Execute the trade based on the detected arbitrage opportunity."""
        buy_exchange = self.exchanges[opportunity['buy_exchange']]
        sell_exchange = self.exchanges[opportunity['sell_exchange']]
        pair = opportunity['pair']
        trade_amount = opportunity['trade_amount']

        logging.info(f"Executing trade: Buy {pair} on {opportunity['buy_exchange']} at {opportunity['buy_price']} and sell on {opportunity['sell_exchange']} at {opportunity['sell_price']}")

        try:
            buy_order = await buy_exchange.place_order(pair, trade_amount, opportunity['buy_price'], 'BUY')
            sell_order = await sell_exchange.place_order(pair, trade_amount, opportunity['sell_price'], 'SELL')
            logging.info(f"Buy order response: {buy_order}")
            logging.info(f"Sell order response: {sell_order}")
        except Exception as e:
            logging.error(f"Error executing trade for {pair}: {e}")

    async def run(self) -> None:
        """Main loop to continuously monitor and trade."""
        while True:
            logging.info("Checking for arbitrage opportunities...")
            prices = await self.fetch_prices()
            opportunities = self.detect_arbitrage_opportunity(prices)

            if opportunities:
                for opportunity in opportunities:
                    await self.execute_trade(opportunity)
            else:
                logging.info("No arbitrage opportunities detected.")
            
            await asyncio.sleep(TIMING_SETTINGS['update_interval'])

if __name__ == "__main__":
    bot = TradingBot()
    asyncio.run(bot.run())