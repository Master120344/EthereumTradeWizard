# order_manager.py

import asyncio
import logging
import requests
import websockets
import json
from typing import Dict, Any, Optional
from config import EXCHANGE_API_KEYS, EXCHANGE_URLS, TIMING_SETTINGS

# Setup logging
logging.basicConfig(
    filename='order_manager.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class OrderManager:
    """Manages orders across multiple exchanges."""

    def __init__(self):
        self.orders = {}
        self.exchanges = {name: ExchangeAPI(name) for name in EXCHANGE_URLS.keys()}

    async def place_order(self, exchange_name: str, pair: str, amount: float, price: float, order_type: str) -> Dict[str, Any]:
        """Place an order on a specified exchange."""
        exchange = self.exchanges[exchange_name]
        logging.info(f"Placing {order_type} order on {exchange_name} for {pair} at {price} with amount {amount}")
        
        retry_count = 0
        max_retries = 5
        while retry_count < max_retries:
            try:
                order_response = await exchange.place_order(pair, amount, price, order_type)
                order_id = order_response.get('orderId')
                if order_id:
                    self.orders[order_id] = {
                        'exchange': exchange_name,
                        'pair': pair,
                        'amount': amount,
                        'price': price,
                        'order_type': order_type,
                        'status': 'pending'
                    }
                return order_response
            except Exception as e:
                logging.error(f"Error placing {order_type} order on {exchange_name} for pair {pair}: {e}")
                retry_count += 1
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
        return {}

    async def cancel_order(self, exchange_name: str, order_id: str) -> bool:
        """Cancel a specific order on an exchange."""
        exchange = self.exchanges[exchange_name]
        logging.info(f"Cancelling order {order_id} on {exchange_name}")
        
        retry_count = 0
        max_retries = 5
        while retry_count < max_retries:
            try:
                cancel_response = await exchange.cancel_order(order_id)
                if cancel_response.get('status') == 'CANCELED':
                    if order_id in self.orders:
                        self.orders[order_id]['status'] = 'canceled'
                    return True
                return False
            except Exception as e:
                logging.error(f"Error cancelling order {order_id} on {exchange_name}: {e}")
                retry_count += 1
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
        return False

    async def monitor_orders(self) -> None:
        """Monitor the status of all active orders."""
        while True:
            tasks = []
            for order_id, order_info in self.orders.items():
                tasks.append(self._check_order_status(order_id, order_info))
            await asyncio.gather(*tasks)
            await asyncio.sleep(10)  # Monitor every 10 seconds

    async def _check_order_status(self, order_id: str, order_info: Dict[str, Any]) -> None:
        """Check the status of a single order."""
        exchange_name = order_info['exchange']
        exchange = self.exchanges[exchange_name]
        try:
            order_status = await exchange.get_order_status(order_id)
            if order_status:
                status = order_status.get('status')
                if status == 'FILLED':
                    self.orders[order_id]['status'] = 'filled'
                elif status == 'CANCELED':
                    self.orders[order_id]['status'] = 'canceled'
        except Exception as e:
            logging.error(f"Error checking status of order {order_id} on {exchange_name}: {e}")

    async def handle_real_time_updates(self) -> None:
        """Listen to WebSocket updates from exchanges."""
        ws_tasks = [self._listen_to_websocket(exchange_name) for exchange_name in self.exchanges]
        await asyncio.gather(*ws_tasks)

    async def _listen_to_websocket(self, exchange_name: str) -> None:
        """Listen to WebSocket updates for a specific exchange."""
        exchange = self.exchanges[exchange_name]
        websocket_url = exchange.get_websocket_url()
        
        async with websockets.connect(websocket_url) as websocket:
            while True:
                try:
                    message = await websocket.recv()
                    self._process_websocket_message(exchange_name, message)
                except Exception as e:
                    logging.error(f"WebSocket error for {exchange_name}: {e}")
                    await asyncio.sleep(5)  # Wait before reconnecting

    def _process_websocket_message(self, exchange_name: str, message: str) -> None:
        """Process a WebSocket message from an exchange."""
        try:
            data = json.loads(message)
            # Example: Update order status or handle other real-time updates
            logging.info(f"Received WebSocket message from {exchange_name}: {data}")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding WebSocket message from {exchange_name}: {e}")

class ExchangeAPI:
    """Handles interactions with a single exchange."""
    
    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name
        self.api_key = EXCHANGE_API_KEYS[exchange_name]['api_key']
        self.api_secret = EXCHANGE_API_KEYS[exchange_name]['api_secret']
        self.base_url = EXCHANGE_URLS[exchange_name]
        self.session = requests.Session()

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

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an existing order."""
        url = f"{self.base_url}/api/v3/order"
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        params = {
            'orderId': order_id
        }
        
        try:
            response = self.session.delete(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error cancelling order {order_id} on {self.exchange_name}: {e}")
            return {}

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get the status of an existing order."""
        url = f"{self.base_url}/api/v3/order"
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        params = {
            'orderId': order_id
        }
        
        try:
            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error getting status of order {order_id} on {self.exchange_name}: {e}")
            return {}

    def get_websocket_url(self) -> str:
        """Return the WebSocket URL for the exchange."""
        return f"wss://{self.exchange_name}.websocket.url"  # Replace with actual WebSocket URL

if __name__ == "__main__":
    order_manager = OrderManager()
    asyncio.run(asyncio.gather(
        order_manager.monitor_orders(),
        order_manager.handle_real_time_updates()
    ))
