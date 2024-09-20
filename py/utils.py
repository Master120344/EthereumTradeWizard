# utils.py

import json
import os
import logging
import time
from typing import Any, Dict, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
logging.basicConfig(filename='utils.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class ConfigManager:
    """Class for managing application configuration."""

    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from a JSON file."""
        if not os.path.isfile(self.config_file):
            raise FileNotFoundError(f"Configuration file {self.config_file} not found.")
        try:
            with open(self.config_file, 'r') as file:
                config = json.load(file)
            self.validate_config(config)
            return config
        except json.JSONDecodeError as e:
            logging.error("Error decoding JSON configuration file %s: %s", self.config_file, e)
            raise
        except Exception as e:
            logging.error("Error loading configuration file %s: %s", self.config_file, e)
            raise

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to a JSON file."""
        try:
            with open(self.config_file, 'w') as file:
                json.dump(config, file, indent=4)
        except IOError as e:
            logging.error("Error saving configuration file %s: %s", self.config_file, e)
            raise

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate the configuration data."""
        # Add validation logic if needed
        pass

def parse_price(price_str: str) -> float:
    """Parse price from a string and handle potential formatting issues."""
    try:
        return float(price_str.replace(',', '').strip())
    except ValueError as e:
        logging.error("Error parsing price '%s': %s", price_str, e)
        return float('nan')  # Return NaN to indicate parsing failure

def handle_api_error(response: Any) -> None:
    """Handle API errors based on response status code and content."""
    status_code = response.status_code
    if status_code == 401:
        logging.error("Unauthorized access. Check API keys.")
    elif status_code == 403:
        logging.error("Forbidden request. Check permissions.")
    elif status_code == 429:
        logging.warning("Rate limit exceeded. Consider retrying.")
    elif status_code >= 500:
        logging.error("Server error: %d. Try again later.", status_code)
    else:
        logging.error("API error: %d - %s", status_code, response.text)

def create_directory(directory: str) -> None:
    """Create a directory if it does not exist."""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except Exception as e:
            logging.error("Error creating directory %s: %s", directory, e)
            raise

def retry_request(func: Callable, *args, retries: int = 3, delay: int = 5, **kwargs) -> Any:
    """Retry a function call with specified retries and delay."""
    last_exception = None
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            logging.error("Error during request: %s. Attempt %d/%d", e, attempt + 1, retries)
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                logging.error("Max retries reached. Raising last exception.")
                raise last_exception

def parallel_process(func: Callable, items: list, max_workers: int = 5) -> list:
    """Process a list of items in parallel using ThreadPoolExecutor."""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(func, item): item for item in items}
        for future in as_completed(futures):
            item = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logging.error("Error processing item %s: %s", item, e)
    return results

class DataValidator:
    """Class for validating data."""

    @staticmethod
    def validate_price(price: float) -> bool:
        """Validate price to be a positive number."""
        if price > 0:
            return True
        logging.error("Invalid price: %f", price)
        return False

    @staticmethod
    def validate_order(order: Dict[str, Any]) -> bool:
        """Validate order structure and data."""
        required_keys = {'symbol', 'side', 'type', 'price', 'quantity'}
        if not required_keys.issubset(order.keys()):
            logging.error("Order missing required keys: %s", order)
            return False
        if not DataValidator.validate_price(order.get('price', 0)):
            logging.error("Invalid order price: %f", order.get('price', 0))
            return False
        return True

# Example usage of utility functions
if __name__ == "__main__":
    # Load and save configuration example
    config_manager = ConfigManager('config.json')
    config = config_manager.config
    config_manager.save_config(config)

    # Create a directory example
    create_directory('logs')

    # Example of parsing price
    price = parse_price('1,234.56')
    print(f"Parsed price: {price}")

    # Example of parallel processing
    def dummy_func(item):
        return item * 2

    items = [1, 2, 3, 4, 5]
    results = parallel_process(dummy_func, items)
    print(f"Parallel processing results: {results}")

    # Example of data validation
    valid_price = DataValidator.validate_price(123.45)
    print(f"Is price valid? {valid_price}")

    valid_order = DataValidator.validate_order({
        'symbol': 'ETH/USD',
        'side': 'BUY',
        'type': 'LIMIT',
        'price': 1234.56,
        'quantity': 1
    })
    print(f"Is order valid? {valid_order}")