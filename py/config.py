# config.py

import os
import json
import logging
from typing import Dict, Any
from jsonschema import validate, ValidationError

# Base directory for configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration schema for validation
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "EXCHANGE_API_KEYS": {
            "type": "object",
            "patternProperties": {
                ".*": {
                    "type": "object",
                    "properties": {
                        "api_key": {"type": "string"},
                        "api_secret": {"type": "string"},
                        "api_passphrase": {"type": "string"}
                    },
                    "required": ["api_key", "api_secret"]
                }
            }
        },
        "EXCHANGE_URLS": {
            "type": "object",
            "patternProperties": {
                ".*": {"type": "string", "format": "uri"}
            }
        },
        "TRADING_PAIRS": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "pair": {"type": "string"},
                    "min_trade_amount": {"type": "number", "minimum": 0}
                },
                "required": ["pair", "min_trade_amount"]
            }
        },
        "ARBITRAGE_PARAMS": {
            "type": "object",
            "properties": {
                "slippage_tolerance": {"type": "number", "minimum": 0},
                "price_difference_threshold": {"type": "number", "minimum": 0},
                "trade_volume_limit": {"type": "number", "minimum": 0}
            },
            "required": ["slippage_tolerance", "price_difference_threshold", "trade_volume_limit"]
        },
        "GAS_PRICE": {
            "type": "object",
            "properties": {
                "gas_price_threshold": {"type": "integer", "minimum": 0},
                "gas_price_limit": {"type": "integer", "minimum": 0}
            },
            "required": ["gas_price_threshold", "gas_price_limit"]
        },
        "LOGGING_SETTINGS": {
            "type": "object",
            "properties": {
                "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                "log_file": {"type": "string"}
            },
            "required": ["log_level", "log_file"]
        },
        "TIMING_SETTINGS": {
            "type": "object",
            "properties": {
                "update_interval": {"type": "integer", "minimum": 1},
                "order_retry_limit": {"type": "integer", "minimum": 1}
            },
            "required": ["update_interval", "order_retry_limit"]
        },
        "NOTIFICATION_SETTINGS": {
            "type": "object",
            "properties": {
                "enable_email_notifications": {"type": "boolean"},
                "email_recipient": {"type": "string", "format": "email"},
                "smtp_server": {"type": "string"},
                "smtp_port": {"type": "integer", "minimum": 1, "maximum": 65535},
                "smtp_user": {"type": "string"},
                "smtp_password": {"type": "string"}
            },
            "required": ["enable_email_notifications", "email_recipient", "smtp_server", "smtp_port", "smtp_user", "smtp_password"]
        }
    },
    "required": [
        "EXCHANGE_API_KEYS",
        "EXCHANGE_URLS",
        "TRADING_PAIRS",
        "ARBITRAGE_PARAMS",
        "GAS_PRICE",
        "LOGGING_SETTINGS",
        "TIMING_SETTINGS",
        "NOTIFICATION_SETTINGS"
    ]
}

def load_config_from_file(config_file: str) -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    if not os.path.isfile(config_file):
        raise FileNotFoundError(f"Configuration file {config_file} not found.")
    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
        validate_config(config)
        return config
    except json.JSONDecodeError as e:
        logging.error("Error decoding JSON configuration file %s: %s", config_file, e)
        raise
    except ValidationError as e:
        logging.error("Configuration validation error: %s", e)
        raise
    except Exception as e:
        logging.error("Error loading configuration file %s: %s", config_file, e)
        raise

def load_config_from_env() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    config = {
        "EXCHANGE_API_KEYS": json.loads(os.getenv('EXCHANGE_API_KEYS', '{}')),
        "EXCHANGE_URLS": json.loads(os.getenv('EXCHANGE_URLS', '{}')),
        "TRADING_PAIRS": json.loads(os.getenv('TRADING_PAIRS', '[]')),
        "ARBITRAGE_PARAMS": {
            "slippage_tolerance": float(os.getenv('SLIPPAGE_TOLERANCE', 0.01)),
            "price_difference_threshold": float(os.getenv('PRICE_DIFF_THRESHOLD', 0.02)),
            "trade_volume_limit": float(os.getenv('TRADE_VOLUME_LIMIT', 10000)),
        },
        "GAS_PRICE": {
            "gas_price_threshold": int(os.getenv('GAS_PRICE_THRESHOLD', 50)),
            "gas_price_limit": int(os.getenv('GAS_PRICE_LIMIT', 100)),
        },
        "LOGGING_SETTINGS": {
            "log_level": os.getenv('LOG_LEVEL', 'INFO').upper(),
            "log_file": os.getenv('LOG_FILE', os.path.join(BASE_DIR, 'logs', 'arbitrage_bot.log'))
        },
        "TIMING_SETTINGS": {
            "update_interval": int(os.getenv('UPDATE_INTERVAL', 60)),
            "order_retry_limit": int(os.getenv('ORDER_RETRY_LIMIT', 3)),
        },
        "NOTIFICATION_SETTINGS": {
            "enable_email_notifications": os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true',
            "email_recipient": os.getenv('EMAIL_RECIPIENT', ''),
            "smtp_server": os.getenv('SMTP_SERVER', ''),
            "smtp_port": int(os.getenv('SMTP_PORT', 587)),
            "smtp_user": os.getenv('SMTP_USER', ''),
            "smtp_password": os.getenv('SMTP_PASSWORD', ''),
        }
    }
    validate_config(config)
    return config

def validate_config(config: Dict[str, Any]) -> None:
    """Validate the configuration data against the schema."""
    try:
        validate(instance=config, schema=CONFIG_SCHEMA)
    except ValidationError as e:
        logging.error("Configuration validation error: %s", e)
        raise

# Choose configuration source
if os.getenv('USE_ENV_CONFIG', 'false').lower() == 'true':
    CONFIG = load_config_from_env()
else:
    CONFIG = load_config_from_file(os.path.join(BASE_DIR, 'config.json'))

# Configuration constants
EXCHANGE_API_KEYS = CONFIG['EXCHANGE_API_KEYS']
EXCHANGE_URLS = CONFIG['EXCHANGE_URLS']
TRADING_PAIRS = CONFIG['TRADING_PAIRS']
ARBITRAGE_PARAMS = CONFIG['ARBITRAGE_PARAMS']
GAS_PRICE = CONFIG['GAS_PRICE']
LOGGING_SETTINGS = CONFIG['LOGGING_SETTINGS']
TIMING_SETTINGS = CONFIG['TIMING_SETTINGS']
NOTIFICATION_SETTINGS = CONFIG['NOTIFICATION_SETTINGS']

# Setup logging configuration
logging.basicConfig(
    filename=LOGGING_SETTINGS['log_file'],
    level=getattr(logging, LOGGING_SETTINGS['log_level']),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Example usage of configuration settings
if __name__ == "__main__":
    print("Exchange API Keys:", EXCHANGE_API_KEYS)
    print("Exchange URLs:", EXCHANGE_URLS)
    print("Trading Pairs:", TRADING_PAIRS)
    print("Arbitrage Parameters:", ARBITRAGE_PARAMS)
    print("Gas Price Settings:", GAS_PRICE)
    print("Logging Settings:", LOGGING_SETTINGS)
    print("Timing Settings:", TIMING_SETTINGS)
    print("Notification Settings:", NOTIFICATION_SETTINGS)
