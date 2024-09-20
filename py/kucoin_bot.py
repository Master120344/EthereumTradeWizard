import requests
import time
import logging
from threading import Thread, Event
import smtplib
from email.mime.text import MIMEText

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KuCoinBot:
    def __init__(self, symbol, reporting_bot_url, email_config, check_interval=5):
        self.api_url = f"https://api.kucoin.com/api/v1/market/orderbook/level_1?symbol={symbol}"
        self.symbol = symbol
        self.reporting_bot_url = reporting_bot_url
        self.check_interval = check_interval
        self.best_price = None
        self.stop_event = Event()
        self.price_history = []
        self.price_alert_threshold = 0.05  # 5% price drop for alerting

    def fetch_price(self):
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            return float(response.json()['data']['price'])  # Last price from the response
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching price for {self.symbol}: {e}")
            return None

    def analyze_price_trend(self, current_price):
        if len(self.price_history) >= 5:
            self.price_history.pop(0)
        self.price_history.append(current_price)

        if len(self.price_history) == 5:
            avg_price = sum(self.price_history) / len(self.price_history)
            if current_price < avg_price * (1 - self.price_alert_threshold):
                self.send_price_alert(current_price, avg_price)

    def send_price_alert(self, current_price, avg_price):
        subject = f"Price Alert: {self.symbol}"
        body = (f"Current Price: {current_price}\n"
                f"Average Price: {avg_price}\n"
                "Significant drop detected.")
        self.send_email(subject, body)

    def send_email(self, subject, body):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = email_config['sender_email']
        msg['To'] = email_config['recipient_email']
        
        with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
            server.starttls()
            server.login(email_config['sender_email'], email_config['password'])
            server.sendmail(email_config['sender_email'], email_config['recipient_email'], msg.as_string())
            logging.info("Price alert email sent.")

    def monitor_prices(self):
        while not self.stop_event.is_set():
            current_price = self.fetch_price()
            if current_price is not None:
                logging.info(f"Current price for {self.symbol}: {current_price}")
                self.analyze_price_trend(current_price)
                if self.best_price is None or current_price < self.best_price:
                    self.best_price = current_price
                    self.report_best_price()
            time.sleep(self.check_interval)

    def report_best_price(self):
        payload = {
            'exchange': 'KuCoin',
            'symbol': self.symbol,
            'best_price': self.best_price
        }
        try:
            response = requests.post(self.reporting_bot_url, json=payload)
            response.raise_for_status()
            logging.info(f"Reported best price: {self.best_price} for {self.symbol}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error reporting price for {self.symbol}: {e}")

    def start(self):
        logging.info(f"Starting KuCoinBot for {self.symbol}")
        self.thread = Thread(target=self.monitor_prices)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()
        logging.info("KuCoinBot stopped.")

if __name__ == "__main__":
    email_config = {
        'sender_email': 'your_email@example.com',  # Update with your email
        'recipient_email': 'recipient_email@example.com',  # Update with recipient email
        'password': 'your_email_password',  # Update with your email password
        'smtp_server': 'smtp.example.com',  # Update with your SMTP server
        'smtp_port': 587,  # Common SMTP port for TLS
    }
    
    reporting_bot_url = "http://reporting_bot_url"  # Update with actual reporting bot URL
    symbol = "BTC-USDT"  # Example trading pair; adjust as needed

    kucoin_bot = KuCoinBot(symbol, reporting_bot_url, email_config)
    try:
        kucoin_bot.start()
        while True:  # Keep the main thread alive
            time.sleep(1)
    except KeyboardInterrupt:
        kucoin_bot.stop()