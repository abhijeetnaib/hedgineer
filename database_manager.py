import logging
import sqlite3
import pandas as pd



logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Class to manage SQLite database operations.
    """
    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.create_tables()

    def create_tables(self):
        """
        Create the required tables: stocks and daily_data.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                ticker TEXT PRIMARY KEY,
                name TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_data (
                date DATE,
                ticker TEXT,
                closing_price REAL,
                market_cap REAL,
                PRIMARY KEY (date, ticker),
                FOREIGN KEY (ticker) REFERENCES stocks(ticker)
            )
        """)
        self.conn.commit()

    def insert_stock(self, ticker, name=None):
        """
        Insert a stock into the stocks table if it doesn't already exist.
        """
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO stocks (ticker, name) VALUES (?, ?)", (ticker, name))
        self.conn.commit()

    def insert_daily_data(self, date, ticker, closing_price, market_cap):
        """
        Insert daily stock data into the daily_data table.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO daily_data (date, ticker, closing_price, market_cap)
            VALUES (?, ?, ?, ?)
        """, (date, ticker, closing_price, market_cap))
        self.conn.commit()

    def query_top_stocks(self, date, limit=100):
        """
        Query the top stocks by market cap for a given date.
        Returns a pandas DataFrame.
        """
        query = """
            SELECT ticker, closing_price, market_cap FROM daily_data
            WHERE date = ?
            ORDER BY market_cap DESC
            LIMIT ?
        """
        df = pd.read_sql_query(query, self.conn, params=(date, limit))
        return df