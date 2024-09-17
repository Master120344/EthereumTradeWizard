# config.py

# Exchange API keys and secrets
EXCHANGE_API_KEYS = {
    'binance': {
        'api_key': 'YOUR_BINANCE_API_KEY',
        'api_secret': 'YOUR_BINANCE_API_SECRET',
    },
    'coinbase': {
        'api_key': 'YOUR_COINBASE_API_KEY',
        'api_secret': 'YOUR_COINBASE_API_SECRET',
        'api_passphrase': 'YOUR_COINBASE_API_PASSPHRASE',
    },
    # Add more exchanges and their credentials as needed
}

# Exchange URLs (for API requests)
EXCHANGE_URLS = {
    'binance': 'https://api.binance.com',
    'coinbase': 'https://api.coinbase.com',
    # Add more exchange URLs as needed
}

# Trading pairs to monitor (format: 'base_currency/quote_currency')
TRADING_PAIRS = [
    {'pair': 'ETH/USD', 'min_trade_amount': 0.01},
    {'pair': 'BTC/USD', 'min_trade_amount': 0.001},
    # Add more trading pairs with minimum trade amounts
]

# Arbitrage parameters
ARBITRAGE_PARAMS = {
    'slippage_tolerance': 0.01,  # Slippage tolerance in percentage (e.g., 1% slippage)
    'price_difference_threshold': 0.02,  # Minimum price difference to consider arbitrage (2%)
    'trade_volume_limit': 10000,  # Maximum trade volume per arbitrage opportunity
}

# Gas price settings (in Gwei)
GAS_PRICE = {
    'gas_price_threshold': 50,  # Example gas price threshold
    'gas_price_limit': 100,     # Maximum gas price to consider (for Ethereum)
}

# Logging settings
LOGGING_SETTINGS = {
    'log_level': 'INFO',  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    'log_file': 'arbitrage_bot.log',  # File to write logs
}

# Timing settings
TIMING_SETTINGS = {
    'update_interval': 60,  # How often to update prices and check arbitrage opportunities (in seconds)
    'order_retry_limit': 3,  # Number of retries for failed orders
}

# Notification settings
NOTIFICATION_SETTINGS = {
    'enable_email_notifications': True,
    'email_recipient': 'your_email@example.com',
    'smtp_server': 'smtp.example.com',
    'smtp_port': 587,
    'smtp_user': 'your_email@example.com',
    'smtp_password': 'your_email_password',
}

# Define any additional settings or parameters as needed
