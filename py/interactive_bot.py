# interactive_bot.py

import asyncio
import logging
from typing import List
from strategy import TradingStrategy
from data_storage import DataStorage
from notifications import EmailNotification
from config import EXCHANGE_API_KEYS, EXCHANGE_URLS, TRADING_PAIRS, ARBITRAGE_PARAMS, GAS_PRICE, TIMING_SETTINGS, NOTIFICATION_SETTINGS

# Setup logging
logging.basicConfig(
    filename='interactive_bot.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class InteractiveBot:
    """Interactive command-line bot for trading and arbitrage."""

    def __init__(self):
        self.data_storage = DataStorage('trading_data.db')
        self.email_notifier = EmailNotification()
        self.exchanges = list(EXCHANGE_API_KEYS.keys())

    def start(self):
        """Start the interactive bot."""
        print("Welcome to the Legendary Crypto Arbitrage Bot!")
        while True:
            self._display_main_menu()
            choice = input("Enter your choice: ").strip().lower()
            if choice == '1':
                self._configure_trade()
            elif choice == '2':
                self._stop()
                break
            elif choice == '3':
                self._view_data()
            elif choice == '4':
                self._view_settings()
            elif choice == 'q':
                print("Exiting the bot.")
                self._stop()
                break
            else:
                print("Invalid choice, please try again.")

    def _display_main_menu(self):
        """Display the main menu."""
        print("\nMain Menu:")
        print("1. Configure and Start Trading")
        print("2. Stop the Bot")
        print("3. View Trade Data")
        print("4. View Bot Settings")
        print("Q. Quit")

    def _configure_trade(self):
        """Guide the user through the trading configuration process."""
        print("\nConfigure Trade:")
        print("Available cryptocurrencies: ", ', '.join([pair['pair'] for pair in TRADING_PAIRS]))
        crypto_pair = input("Enter the cryptocurrency pair (e.g., ETH/USD): ").strip().upper()
        if not self._validate_pair(crypto_pair):
            print("Invalid cryptocurrency pair. Please try again.")
            return
        
        print("Available exchanges: ", ', '.join(self.exchanges))
        exchange = input("Enter the exchange you want to trade on: ").strip().lower()
        if exchange not in self.exchanges:
            print("Invalid exchange. Please try again.")
            return
        
        wallet_address = input("Enter your wallet address: ").strip()
        print(f"Using {crypto_pair} on {exchange} with wallet address {wallet_address}")
        
        self._start_trading(crypto_pair, exchange, wallet_address)

    def _validate_pair(self, pair: str) -> bool:
        """Validate if the pair is available in the config."""
        return any(p['pair'] == pair for p in TRADING_PAIRS)

    def _start_trading(self, pair: str, exchange: str, wallet_address: str) -> None:
        """Start the trading strategy and provide real-time feedback."""
        print("Starting trading...")
        print("Looking for the best trades...")
        print("Checking markets...")
        print("Updating gas prices...")
        print("Evaluating slippage...")
        
        strategy = TradingStrategy(self.exchanges)
        asyncio.run(self._run_strategy(strategy))

    async def _run_strategy(self, strategy: TradingStrategy) -> None:
        """Run the trading strategy asynchronously."""
        try:
            await strategy.run()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            self.email_notifier.send_email("Bot Error", f"An error occurred: {e}")

    def _view_data(self):
        """View stored trade and price data."""
        print("\nTrade Data:")
        trades = self.data_storage.fetch_trades()
        print(trades)
        print("\nPrice Data:")
        prices = self.data_storage.fetch_prices()
        print(prices)

    def _view_settings(self):
        """View current bot settings."""
        print("\nCurrent Bot Settings:")
        print("Exchanges:", EXCHANGE_API_KEYS.keys())
        print("Trading Pairs:", TRADING_PAIRS)
        print("Arbitrage Parameters:", ARBITRAGE_PARAMS)
        print("Gas Prices:", GAS_PRICE)
        print("Timing Settings:", TIMING_SETTINGS)
        print("Notification Settings:", NOTIFICATION_SETTINGS)

    def _stop(self):
        """Stop the bot and clean up resources."""
        self.data_storage.close()
        print("Bot stopped and resources cleaned up.")

def main():
    """Entry point for the interactive bot."""
    bot = InteractiveBot()
    bot.start()

if __name__ == "__main__":
    main()
