import sqlite3
import pandas as pd

def validate_ingestion(db_path="data.db"):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    # Check total number of rows in daily_data table
    df_count = pd.read_sql_query("SELECT COUNT(*) as total_rows FROM daily_data", conn)
    total_rows = df_count['total_rows'].iloc[0]
    print(f"Total rows in daily_data: {total_rows}")
    
    # Check distinct tickers ingested
    df_tickers = pd.read_sql_query("SELECT COUNT(DISTINCT ticker) as ticker_count FROM daily_data", conn)
    ticker_count = df_tickers['ticker_count'].iloc[0]
    print(f"Distinct tickers ingested: {ticker_count}")
    
    # Optionally, show a sample of the data to verify correctness
    df_sample = pd.read_sql_query("SELECT * FROM daily_data ORDER BY date LIMIT 10", conn)
    print("Sample rows from daily_data:")
    print(df_sample)
    conn.close()

    #if you need to empty the database after validation, uncomment the next line
    conn = sqlite3.connect("data.db")

# Execute a DELETE command to remove all rows from your table, e.g., "daily_data"
    '''conn.execute("DELETE FROM daily_data")
    conn.commit()  # Commit the changes
    conn.close()
    '''

    conn = sqlite3.connect("data.db")
    date_to_test = "2025-04-03"  # Replace with an actual trading date in your data
    query = """
    SELECT ticker, closing_price, market_cap
    FROM daily_data
    WHERE date = ?
    ORDER BY market_cap DESC
    LIMIT 100
    """
    df = pd.read_sql_query(query, conn, params=(date_to_test,))
    print(f"Data for {date_to_test}:\n", df)
    conn.close()

    conn = sqlite3.connect("data.db")
    test_date = "2025-04-03"
    query = """
    SELECT ticker, closing_price, market_cap, date
    FROM daily_data
    WHERE DATE(date) BETWEEN ? AND ?
    ORDER BY DATE(date), market_cap DESC
    """
    df = pd.read_sql_query(query, conn, params=(test_date,test_date))
    print(df)
    conn.close()

if __name__ == "__main__":
    validate_ingestion()