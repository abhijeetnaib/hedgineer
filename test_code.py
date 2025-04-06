import unittest
from database_manager import DatabaseManager
from custom_index_calculator import CustomIndexCalculator
from exports import export_to_excel, export_to_pdf
from data_ingestion import run_data_ingestion
import os
import datetime
import pandas as pd


class TestCustomIndex(unittest.TestCase):
    def setUp(self):
        # Set up an in-memory database and insert dummy data for testing
        self.db_manager = DatabaseManager()
        tickers = ["TEST1", "TEST2", "TEST3"]
        for ticker in tickers:
            self.db_manager.insert_stock(ticker)
        # Insert dummy daily data for a specific date "2023-01-01"
        test_date = "2023-01-01"
        data = [
            (test_date, "TEST1", 100.0, 5_000_000),
            (test_date, "TEST2", 200.0, 3_000_000),
            (test_date, "TEST3", 300.0, 7_000_000)
        ]
        cursor = self.db_manager.conn.cursor()
        for row in data:
            cursor.execute("""
                INSERT OR REPLACE INTO daily_data (date, ticker, closing_price, market_cap)
                VALUES (?, ?, ?, ?)
            """, row)
        self.db_manager.conn.commit()

    def tearDown(self):
        # Clean up the database after each test
        self.db_manager.conn.close()

    def test_query_top_stocks(self):
        # Test that the query returns the top stock by market cap correctly.
        df = self.db_manager.query_top_stocks("2023-01-01", limit=1)
        self.assertFalse(df.empty)
        top_stock = df.iloc[0]
        # TEST3 has the highest dummy market cap (7,000,000)
        self.assertEqual(top_stock['ticker'], "TEST3")
        self.assertEqual(top_stock['market_cap'], 7_000_000)

    def test_index_calculation(self):
        # Test that the index calculation returns the correct average of closing prices.
        calc = CustomIndexCalculator(self.db_manager)
        index_value = calc.calculate_index_value("2023-01-01")
        # Expected average = (100 + 200 + 300) / 3 = 200
        self.assertAlmostEqual(index_value, 200.0)

    def test_export_excel(self):
        # Test exporting to Excel creates a file.
        df = self.db_manager.query_top_stocks("2023-01-01")
        filename = "test_export.xlsx"
        export_to_excel(df, filename)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)

    def test_export_pdf(self):
        # Test exporting to PDF creates a file.
        df = self.db_manager.query_top_stocks("2023-01-01")
        filename = "test_export.pdf"
        export_to_pdf(df, filename)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)

    def test_run_data_ingestion(self):
        # Test that run_data_ingestion inserts data into the database
        run_data_ingestion()
        # Check if data was inserted into the database
        cursor = self.db_manager.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM daily_data")
        count = cursor.fetchone()[0]
        self.assertGreater(count, 0, "No data was ingested into the database.")

    def test_empty_data_handling(self):
        # Test that the system handles empty data gracefully
        calc = CustomIndexCalculator(self.db_manager)
        index_value = calc.calculate_index_value("2025-01-01")  # Future date with no data
        self.assertIsNone(index_value, "Index value should be None for a date with no data.")

    def test_invalid_date_handling(self):
        # Test that the system handles invalid dates gracefully
        with self.assertRaises(ValueError):
            self.db_manager.query_top_stocks("invalid-date")

    def test_missing_ticker_handling(self):
        # Test that the system handles missing tickers gracefully
        df = self.db_manager.query_top_stocks("2023-01-01", limit=10)
        self.assertTrue("TEST4" not in df['ticker'].values, "Unexpected ticker found in results.")


if __name__ == "__main__":
    # Run the test suite
    unittest.main(argv=['first-arg-is-ignored'], exit=False)