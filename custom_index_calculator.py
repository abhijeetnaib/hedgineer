import logging
import pandas as pd

logger = logging.getLogger(__name__)

class CustomIndexCalculator:
    """
    Class to calculate an equal-weighted custom index.
    It retrieves the top 100 stocks by market cap from the database for a given date
    and computes the average of their closing prices.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def calculate_index_value(self, date):
        """
        Calculate the equal-weighted index value for a given date.
        This is computed as the average closing price of the top 100 stocks by market cap.
        :param date: Date string in 'YYYY-MM-DD' format.
        :return: Average closing price (float) or None if no data is available.
        """
        query = """
            SELECT ticker, closing_price, market_cap 
            FROM daily_data
            WHERE DATE(date) = ?
            ORDER BY market_cap DESC
            LIMIT 100
        """
        logger.warning(f"Calculating index value for date: {date}")
        df = pd.read_sql_query(query, self.db_manager.conn, params=(date,))
        if df.empty:
            logger.warning(f"No data available for {date}")
            return None
        # Return the mean of the closing prices
        return df['closing_price'].mean()

def calculate_index_for_date_range(db_manager, start_date, end_date):
    """
    Calculate the equal-weighted custom index for each business day in the specified date range.
    Uses pandas.bdate_range to iterate only over trading days.
    Returns a DataFrame with columns 'date' and 'index_value'.
    :param db_manager: Instance of DatabaseManager.
    :param start_date: Start date in 'YYYY-MM-DD' format.
    :param end_date: End date in 'YYYY-MM-DD' format.
    :return: pandas DataFrame with index values for each trading day.
    """
    # Generate business days (trading days) between start_date and end_date
    dates = pd.bdate_range(start=start_date, end=end_date)
    index_values = []
    calc = CustomIndexCalculator(db_manager)
    for d in dates:
        date_str = d.strftime('%Y-%m-%d')
        index_value = calc.calculate_index_value(date_str)
        index_values.append({'date': date_str, 'index_value': index_value})
    return pd.DataFrame(index_values)