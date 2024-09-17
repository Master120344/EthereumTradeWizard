# notifications.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from config import NOTIFICATION_SETTINGS

# Setup logging
logging.basicConfig(
    filename='notifications.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EmailNotification:
    """Handles email notifications for the bot."""

    def __init__(self):
        self.smtp_server = NOTIFICATION_SETTINGS['smtp_server']
        self.smtp_port = NOTIFICATION_SETTINGS['smtp_port']
        self.smtp_user = NOTIFICATION_SETTINGS['smtp_user']
        self.smtp_password = NOTIFICATION_SETTINGS['smtp_password']
        self.recipient = NOTIFICATION_SETTINGS['email_recipient']

    def send_email(self, subject: str, body: str) -> None:
        """Send an email notification."""
        msg = MIMEMultipart()
        msg['From'] = self.smtp_user
        msg['To'] = self.recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                logging.info(f"Email sent to {self.recipient} with subject: {subject}")
        except Exception as e:
            logging.error(f"Error sending email: {e}")

    def notify_order_placed(self, order_id: str, exchange: str, pair: str) -> None:
        """Notify about a new order placement."""
        subject = f"New Order Placed: {order_id}"
        body = f"Order ID: {order_id}\nExchange: {exchange}\nPair: {pair}\nStatus: Placed"
        self.send_email(subject, body)

    def notify_order_filled(self, order_id: str, exchange: str, pair: str) -> None:
        """Notify about an order being filled."""
        subject = f"Order Filled: {order_id}"
        body = f"Order ID: {order_id}\nExchange: {exchange}\nPair: {pair}\nStatus: Filled"
        self.send_email(subject, body)

    def notify_order_failed(self, order_id: str, exchange: str, pair: str) -> None:
        """Notify about a failed order."""
        subject = f"Order Failed: {order_id}"
        body = f"Order ID: {order_id}\nExchange: {exchange}\nPair: {pair}\nStatus: Failed"
        self.send_email(subject, body)

    def notify_arbitrage_opportunity(self, buy_exchange: str, sell_exchange: str, buy_price: float, sell_price: float) -> None:
        """Notify about an arbitrage opportunity."""
        subject = "Arbitrage Opportunity Detected"
        body = (f"Buy Exchange: {buy_exchange}\n"
                f"Sell Exchange: {sell_exchange}\n"
                f"Buy Price: {buy_price}\n"
                f"Sell Price: {sell_price}\n"
                f"Profit Potential: {sell_price - buy_price}")
        self.send_email(subject, body)

def main():
    """Example usage of EmailNotification."""
    notifier = EmailNotification()
    notifier.notify_arbitrage_opportunity('binance', 'coinbase', 2000, 2050)
    notifier.notify_order_placed('12345', 'binance', 'ETH/USD')
    notifier.notify_order_filled('12345', 'binance', 'ETH/USD')
    notifier.notify_order_failed('12345', 'binance', 'ETH/USD')

if __name__ == "__main__":
    main()
