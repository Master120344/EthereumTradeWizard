import sqlite3
import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from config import LOGGING_SETTINGS

# Setup logging
logging.basicConfig(
    filename=LOGGING_SETTINGS['log_file'],
    level=getattr(logging, LOGGING_SETTINGS['log_level']),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DataStorage:
    """Manages data storage for trade and price data."""
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connection = None
        self.connect()

    def connect(self) -> None:
        """Establish a connection to the SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.create_tables()
            logging.info(f"Connected to database {self.db_name}")
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to database {self.db_name}: {e}")
            raise

    def create_tables(self) -> None:
        """Create tables for storing trade and price data."""
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exchange TEXT,
                    pair TEXT,
                    amount REAL,
                    price REAL,
                    side TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exchange TEXT,
                    pair TEXT,
                    price REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def store_trade(self, exchange: str, pair: str, amount: float, price: float, side: str) -> None:
        """Store trade information in the database."""
        with self.connection:
            self.connection.execute('''
                INSERT INTO trades (exchange, pair, amount, price, side)
                VALUES (?, ?, ?, ?, ?)
            ''', (exchange, pair, amount, price, side))
            logging.info(f"Trade stored: {exchange} {pair} {amount} {price} {side}")

    def store_price(self, exchange: str, pair: str, price: float) -> None:
        """Store price information in the database."""
        with self.connection:
            self.connection.execute('''
                INSERT INTO prices (exchange, pair, price)
                VALUES (?, ?, ?)
            ''', (exchange, pair, price))
            logging.info(f"Price stored: {exchange} {pair} {price}")

    def fetch_trades(self, pair: Optional[str] = None) -> pd.DataFrame:
        """Fetch trade data from the database."""
        query = 'SELECT * FROM trades'
        params = ()
        if pair:
            query += ' WHERE pair = ?'
            params = (pair,)
        df = pd.read_sql_query(query, self.connection, params=params)
        return df

    def fetch_prices(self, pair: Optional[str] = None) -> pd.DataFrame:
        """Fetch price data from the database."""
        query = 'SELECT * FROM prices'
        params = ()
        if pair:
            query += ' WHERE pair = ?'
            params = (pair,)
        df = pd.read_sql_query(query, self.connection, params=params)
        return df

    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logging.info(f"Database connection to {self.db_name} closed.")

def main():
    """Example usage of DataStorage."""
    try:
        storage = DataStorage('trading_data.db')
        storage.store_trade('binance', 'ETH/USD', 0.01, 2000, 'BUY')
        storage.store_price('binance', 'ETH/USD', 2000)
        
        trades = storage.fetch_trades()
        prices = storage.fetch_prices()
        
        print("Trades:")
        print(trades)
        print("Prices:")
        print(prices)
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    
    finally:
        storage.close()

if __name__ == "__main__":
    main()