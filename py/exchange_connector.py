import aiohttp
import asyncio
import json
import logging
import hmac
import hashlib
import time
from typing import Dict, Any, Optional
from config import EXCHANGE_API_KEYS, EXCHANGE_URLS

# Setup logging
logging.basicConfig(
    filename='exchange_connector.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ExchangeConnector:
    """Handles advanced connection and operations with cryptocurrency exchanges."""

    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name
        self.api_key = EXCHANGE_API_KEYS[exchange_name]['api_key']
        self.api_secret = EXCHANGE_API_KEYS[exchange_name]['api_secret']
        self.base_url = EXCHANGE_URLS[exchange_name]
        self.rate_limit = 1  # Rate limit per second (can be configured per exchange)
        self._last_request_time = 0
        self._rate_limit_interval = 1  # Interval in seconds for rate limiting
        self.session = None

    async def start(self) -> None:
        """Initialize the aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def fetch_price(self, pair: str) -> Optional[float]:
        """Fetch the current price of a trading pair with advanced retry mechanism."""
        await self.start()
        url = f"{self.base_url}/api/v3/ticker/price?symbol={self._pair_to_symbol(pair)}"
        retries = 5
        for attempt in range(retries):
            try:
                await self._ensure_rate_limit()
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data['price'])
                    else:
                        logging.warning(f"Failed to fetch price. Status: {response.status}")
                        await asyncio.sleep(self._get_backoff_delay(attempt))
            except Exception as e:
                logging.error(f"Error fetching price for {pair} from {self.exchange_name}: {e}")
                await asyncio.sleep(self._get_backoff_delay(attempt))
        return None

    async def place_order(self, pair: str, amount: float, price: float, side: str) -> Dict[str, Any]:
        """Place a buy or sell order with authentication and advanced retry mechanism."""
        await self.start()
        url = f"{self.base_url}/api/v3/order"
        payload = {
            'symbol': self._pair_to_symbol(pair),
            'side': side,
            'type': 'LIMIT',
            'price': price,
            'quantity': amount,
            'timeInForce': 'GTC',
            'timestamp': int(time.time() * 1000)
        }
        signature = self._generate_signature(payload)
        payload['signature'] = signature
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        retries = 5
        for attempt in range(retries):
            try:
                await self._ensure_rate_limit()
                async with self.session.post(url, data=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        logging.warning(f"Failed to place order. Status: {response.status}")
                        await asyncio.sleep(self._get_backoff_delay(attempt))
            except Exception as e:
                logging.error(f"Error placing {side} order for {pair} on {self.exchange_name}: {e}")
                await asyncio.sleep(self._get_backoff_delay(attempt))
        return {}

    async def listen_to_websocket(self) -> None:
        """Listen to WebSocket updates with advanced management."""
        websocket_url = await self.get_websocket_url()
        retries = 5  # Add limit to number of retries for WebSocket reconnections
        attempt = 0
        async with aiohttp.ClientSession() as session:
            while attempt < retries:
                try:
                    async with session.ws_connect(websocket_url) as ws:
                        attempt = 0  # Reset retries after a successful connection
                        while True:
                            msg = await ws.receive()
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self._process_websocket_message(msg.data)
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                logging.error(f"WebSocket error: {ws.exception()}")
                                break
                except Exception as e:
                    attempt += 1
                    logging.error(f"WebSocket communication error: {e}")
                    await asyncio.sleep(5 * attempt)  # Exponential backoff before reconnecting

    async def get_websocket_url(self) -> str:
        """Get the WebSocket URL for real-time data."""
        return f"wss://{self.exchange_name}.com/ws/{self._pair_to_symbol('BTC/USD')}@trade"

    async def _process_websocket_message(self, message: str) -> None:
        """Process and parse a WebSocket message with enhanced parsing."""
        try:
            data = json.loads(message)
            pair = data.get('s')
            price = data.get('p')

            if pair and price:
                pair = self._symbol_to_pair(pair)
                if pair:
                    logging.info(f"Updated price for {pair}: {price}")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding WebSocket message: {e}")

    async def _ensure_rate_limit(self) -> None:
        """Ensure rate limit compliance with adaptive sleep."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._rate_limit_interval:
            await asyncio.sleep(self._rate_limit_interval - elapsed)
        self._last_request_time = time.time()

    def _get_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        base_delay = 2 ** attempt
        jitter = base_delay * 0.1
        return base_delay + jitter

    def _pair_to_symbol(self, pair: str) -> str:
        """Convert trading pair to symbol used by the exchange."""
        return pair.replace('/', '').upper()

    def _symbol_to_pair(self, symbol: str) -> Optional[str]:
        """Convert exchange symbol to trading pair."""
        return symbol[:3] + '/' + symbol[3:]

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """Generate HMAC SHA256 signature with dynamic API secret."""
        query_string = '&'.join([f"{key}={value}" for key, value in sorted(params.items())])
        return hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            logging.info("Session closed successfully")

async def main():
    """Example usage of ExchangeConnector."""
    exchange_name = 'binance'
    connector = ExchangeConnector(exchange_name)
    
    price = await connector.fetch_price('ETH/USD')
    print(f"Current price of ETH/USD on {exchange_name}: {price}")
    
    order_response = await connector.place_order('ETH/USD', 0.01, price, 'BUY')
    print(f"Order response: {order_response}")

    # Example: start listening to WebSocket
    asyncio.create_task(connector.listen_to_websocket())

    await connector.close()

if __name__ == "__main__":
    asyncio.run(main())