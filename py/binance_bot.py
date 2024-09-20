import requests
import time
import logging
from threading import Thread, Event

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BinanceBot:
    def __init__(self, symbol, reporting_bot_url, check_interval=5):
        self.api_url = "https://api.binance.com/api/v3/ticker/price"
        self.best_price = None
        self.symbol = symbol
        self.reporting_bot_url = reporting_bot_url
        self.check_interval = check_interval
        self.stop_event = Event()

    def fetch_price(self):
        try:
            response = requests.get(f"{self.api_url}?symbol={self.symbol}")
            response.raise_for_status()
            data = response.json()
            return float(data['price'])
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching price: {e}")
            return None

    def check_best_price(self):
        while not self.stop_event.is_set():
            current_price = self.fetch_price()
            if current_price is not None:
                logging.info(f"Current price for {self.symbol}: {current_price}")
                if self.best_price is None or current_price < self.best_price:
                    self.best_price = current_price
                    self.report_best_price()
            time.sleep(self.check_interval)

    def report_best_price(self):
        payload = {
            'exchange': 'Binance',
            'symbol': self.symbol,
            'best_price': self.best_price
        }
        try:
            response = requests.post(self.reporting_bot_url, json=payload)
            response.raise_for_status()
            logging.info(f"Reported best price: {self.best_price} for {self.symbol}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error reporting price: {e}")

    def start(self):
        logging.info(f"Starting BinanceBot for {self.symbol}")
        self.thread = Thread(target=self.check_best_price)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()
        logging.info("BinanceBot stopped.")

if __name__ == "__main__":
    reporting_bot_url = "http://reporting_bot_url"  # Update with actual reporting bot URL
    symbol = "BTCUSDT"  # Example trading pair; adjust as needed

    binance_bot = BinanceBot(symbol, reporting_bot_url)
    try:
        binance_bot.start()
        while True:  # Keep the main thread alive
            time.sleep(1)
    except KeyboardInterrupt:
        binance_bot.stop()