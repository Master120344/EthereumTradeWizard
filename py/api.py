# api.py

import requests
import time
import hmac
import hashlib
from config import EXCHANGE_API_KEYS, EXCHANGE_URLS, TIMING_SETTINGS

# Utility function to handle rate limits
def handle_rate_limit(response):
    if 'Retry-After' in response.headers:
        retry_after = int(response.headers['Retry-After'])
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
        time.sleep(retry_after)

# Helper function to generate signature for exchanges requiring it
def generate_signature(api_secret, query_string):
    return hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

# Custom AuthBase class for exchanges requiring API keys and secrets
class ExchangeAuth(AuthBase):
    def __init__(self, api_key, api_secret, api_passphrase=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase

    def __call__(self, r):
        r.headers.update({
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json',
            # Add other required headers here
        })
        return r

def get_price(exchange, pair):
    try:
        url = f"{EXCHANGE_URLS[exchange]}/api/v3/ticker/price"
        params = {'symbol': pair.replace('/', '')}
        response = requests.get(url, params=params)
        
        handle_rate_limit(response)  # Handle rate limits if applicable
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching price: {e}")
        return None

def place_order(exchange, pair, side, quantity, price):
    try:
        url = f"{EXCHANGE_URLS[exchange]}/api/v3/order"
        headers = {
            'X-Api-Key': EXCHANGE_API_KEYS[exchange]['api_key'],
            'Content-Type': 'application/json',
        }
        data = {
            'symbol': pair.replace('/', ''),
            'side': side,
            'type': 'LIMIT',
            'price': price,
            'quantity': quantity,
            'timeInForce': 'GTC',
        }
        
        auth = ExchangeAuth(
            EXCHANGE_API_KEYS[exchange]['api_key'],
            EXCHANGE_API_KEYS[exchange]['api_secret']
        )
        
        response = requests.post(url, headers=headers, json=data, auth=auth)
        
        handle_rate_limit(response)  # Handle rate limits if applicable
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error placing order: {e}")
        return None

def get_order_status(exchange, order_id):
    try:
        url = f"{EXCHANGE_URLS[exchange]}/api/v3/order"
        params = {'orderId': order_id}
        headers = {
            'X-Api-Key': EXCHANGE_API_KEYS[exchange]['api_key'],
            'Content-Type': 'application/json',
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        handle_rate_limit(response)  # Handle rate limits if applicable
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error getting order status: {e}")
        return None

def cancel_order(exchange, order_id):
    try:
        url = f"{EXCHANGE_URLS[exchange]}/api/v3/order"
        headers = {
            'X-Api-Key': EXCHANGE_API_KEYS[exchange]['api_key'],
            'Content-Type': 'application/json',
        }
        params = {'orderId': order_id}
        
        response = requests.delete(url, headers=headers, params=params)
        
        handle_rate_limit(response)  # Handle rate limits if applicable
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error cancelling order: {e}")
        return None

def fetch_market_data(exchange, endpoint, params=None):
    try:
        url = f"{EXCHANGE_URLS[exchange]}/{endpoint}"
        response = requests.get(url, params=params)
        
        handle_rate_limit(response)  # Handle rate limits if applicable
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching market data: {e}")
        return None

# Example usage for additional exchange methods
def get_exchange_info(exchange):
    return fetch_market_data(exchange, 'api/v3/exchangeInfo')

def get_depth(exchange, pair):
    return fetch_market_data(exchange, 'api/v3/depth', {'symbol': pair.replace('/', '')})

def get_recent_trades(exchange, pair):
    return fetch_market_data(exchange, 'api/v3/trades', {'symbol': pair.replace('/', '')})

# Add more functions as needed
