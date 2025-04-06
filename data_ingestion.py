import argparse
import datetime
import pandas as pd
import logging
from database_manager import DatabaseManager
from custom_index_calculator import CustomIndexCalculator, calculate_index_for_date_range
from exports import export_to_excel, export_to_pdf
from data_fetcher import DataFetcher
from constants import top_200_us_stock_tickers
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_latest_date_from_db(db_manager):
    """
    Returns the latest date available in the daily_data table as a pandas Timestamp.
    If no data exists, returns None.
    """
    query = "SELECT MIN(date) as latest_date FROM daily_data"
    df = pd.read_sql_query(query, db_manager.conn)
    if pd.isna(df['latest_date'].iloc[0]):
        return None
    print(f"Latest date in database: {df['latest_date'].iloc[0]}")
    return pd.to_datetime(df['latest_date'].iloc[0])

def run_data_ingestion(historical_load=False, backfill_days=730, export_files=False):
    # Initialize DataFetcher without specifying tickers or CSV file so that it loads all US tickers.
    fetcher = DataFetcher(tickers=top_200_us_stock_tickers)
    # Initialize the in-memory database
    db_manager = DatabaseManager(db_path="data.db")
    
    # Determine the date range for data fetching:
    # If the database is empty, perform an initial load for the last `backfill_days`.
    # Otherwise, fetch incrementally from the day after the latest stored date.
    latest_date = get_latest_date_from_db(db_manager)
    today = datetime.date.today()
    
    if historical_load or latest_date is None:
        # Historical load: backfill for the specified number of days
        start_date = (today - datetime.timedelta(days=backfill_days)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        logger.info(f"Performing historical load. Loading data from {start_date} to {end_date}.")
    else:
        # Incremental load: day after the latest stored date until today.
        start_date = (latest_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        logger.info(f"Performing incremental load. Loading data from {start_date} to {end_date}.")

    # Fetch the data using yfinance for the specified date range
    data = fetcher.fetch_data(start_date, end_date)

    # Insert fetched data into the database
    for ticker, df in data.items():
        db_manager.insert_stock(ticker)
        logger.info(f"Inserted data for {ticker} into the database.")
        for row in df.itertuples(index=False):
            # Ensure that the Date column is available and correctly formatted.
            # If the column name is 'Date' (after flattening MultiIndex), use row.Date.
            date_str = pd.to_datetime(row.Date).strftime('%Y-%m-%d')
            db_manager.insert_daily_data(date_str, ticker, row.closing_price, row.market_cap)
            logger.info(f"Inserted daily data for {ticker} on {date_str}.")
    
    # Now you can calculate the custom index for a given day (e.g., latest date) or over a range.
    calc = CustomIndexCalculator(db_manager)
    test_date = today.strftime('%Y-%m-%d')
    index_value = calc.calculate_index_value(test_date)
    if index_value is not None:
        logger.info(f"Index value on {test_date}: {index_value}")
    else:
        logger.info(f"No index value calculated for {test_date}")
    
    # Calculate the index for a full date range (e.g., the past month)
    index_history_df = calculate_index_for_date_range(db_manager, (today - datetime.timedelta(days=30)).strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
    
    # Optionally export the historical index
    if export_files:
        export_to_excel(index_history_df, "index_history.xlsx")
        export_to_pdf(index_history_df, "index_history.pdf")
        logger.info("Exported index history to Excel and PDF.")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run data ingestion for stock data.")
    parser.add_argument("--historical_load", type=str, choices=["yes", "no"], default="no",
                        help="Perform a historical load (yes or no). Default is no.")
    parser.add_argument("--backfill_days", type=int, default=730,
                        help="Number of days to backfill for historical load. Default is 730 days.")
    parser.add_argument("--export_files", type=str, choices=["yes", "no"], default="no",
                        help="Export index history to Excel and PDF (yes or no). Default is no.")
    
    # Parse arguments
    args = parser.parse_args()
    historical_load = args.historical_load.lower() == "yes"
    backfill_days = args.backfill_days
    export_files = args.export_files.lower() == "yes"

    # Run data ingestion with parsed arguments
    run_data_ingestion(historical_load=historical_load, backfill_days=backfill_days, export_files=export_files)