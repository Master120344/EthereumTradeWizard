import requests
import time
import hmac
import hashlib
from config import EXCHANGE_API_KEYS, EXCHANGE_URLS, TIMING_SETTINGS

# Utility function to handle rate limits
def handle_rate_limit(response):
    retry_after = response.headers.get('Retry-After')
    if retry_after:
        retry_seconds = int(retry_after)
        print(f"Rate limit exceeded. Retrying after {retry_seconds} seconds.")
        time.sleep(retry_seconds)
    elif response.status_code == 429:
        print("Too many requests. Applying default wait time.")
        time.sleep(1)  # Default wait time, can be adjusted as per exchange's documentation

# Helper function to generate signatures
def generate_signature(api_secret, query_string):
    return hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

# Custom AuthBase class for exchanges requiring API keys and secrets
class ExchangeAuth(requests.auth.AuthBase):
    def __init__(self, api_key, api_secret, api_passphrase=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase

    def __call__(self, r):
        r.headers.update({
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json',
            # Add other required headers specific to the exchange here
        })
        return r

# Generalized function for making requests to the exchange
def make_request(method, exchange, endpoint, params=None, data=None, auth=None):
    url = f"{EXCHANGE_URLS[exchange]}{endpoint}"
    headers = {
        'X-Api-Key': EXCHANGE_API_KEYS[exchange]['api_key'],
        'Content-Type': 'application/json',
    }
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, auth=auth)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, auth=auth)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, params=params, auth=auth)

        handle_rate_limit(response)  # Handle rate limits

        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error during {method} request to {url}: {e}")
        return None

def get_price(exchange, pair):
    endpoint = f"/api/v3/ticker/price"
    params = {'symbol': pair.replace('/', '')}
    return make_request("GET", exchange, endpoint, params)

def place_order(exchange, pair, side, quantity, price):
    endpoint = "/api/v3/order"
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
    return make_request("POST", exchange, endpoint, data=data, auth=auth)

def get_order_status(exchange, order_id):
    endpoint = "/api/v3/order"
    params = {'orderId': order_id}
    return make_request("GET", exchange, endpoint, params)

def cancel_order(exchange, order_id):
    endpoint = "/api/v3/order"
    params = {'orderId': order_id}
    return make_request("DELETE", exchange, endpoint, params)

def fetch_market_data(exchange, endpoint, params=None):
    return make_request("GET", exchange, f"/api/v3/{endpoint}", params)

# Example usage for additional exchange methods
def get_exchange_info(exchange):
    return fetch_market_data(exchange, 'exchangeInfo')

def get_depth(exchange, pair):
    return fetch_market_data(exchange, 'depth', {'symbol': pair.replace('/', '')})

def get_recent_trades(exchange, pair):
    return fetch_market_data(exchange, 'trades', {'symbol': pair.replace('/', '')})