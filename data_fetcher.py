import pandas as pd
import logging
import yfinance as yf


logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Class to fetch historical stock data using yfinance.
    If no tickers or ticker source file is provided, it ingests all US tickers
    from an online source (e.g., NASDAQ Trader file).
    """
    def __init__(self, tickers=None, ticker_source_file=None):
        if tickers is not None:
            self.tickers = tickers
        elif ticker_source_file is not None:
            try:
                tickers_df = pd.read_csv(ticker_source_file)
                self.tickers = tickers_df['ticker'].tolist()
                logger.info(f"Loaded {len(self.tickers)} tickers from file.")
            except Exception as e:
                logger.error(f"Error loading tickers from file: {e}")
                self.tickers = []
        else:
            self.tickers = self.load_all_us_tickers()
            logger.info(f"Loaded {len(self.tickers)} tickers from the default online source.")

    def load_all_us_tickers(self):
        url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqtraded.txt"
        try:
            df = pd.read_csv(url, sep="|")
            df = df[df['Test Issue'] != 'Y']
            tickers = df['Symbol'].tolist()
            return tickers[2]
        except Exception as e:
            logger.error(f"Error loading tickers from default source: {e}")
            return []

    def fetch_data(self, start_date, end_date):
        """
        Fetch historical data for each ticker between start_date and end_date.
        Returns a dictionary mapping ticker -> DataFrame.
        The DataFrame will have a 'Date' column, 'closing_price' (from 'Close'),
        and a dummy 'market_cap' computed for demonstration.
        """
        data = {}
        logger.info(f"Fetching data from {start_date} to {end_date} for {len(self.tickers)} tickers.")
        for ticker in self.tickers:
            try:
                logger.info(f"Fetching data for {ticker}")
                # Explicitly set interval='1d' to avoid invalid period errors.
                df = yf.download(ticker, start=start_date, end=end_date, interval='1d',threads=True)
                logger.info(f"Data fetched for {ticker}: {df.shape[0]} rows")
                if not df.empty:
                    df = df.reset_index()
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    df['ticker'] = ticker
                    df.rename(columns={'Close': 'closing_price'}, inplace=True)
                    # For demonstration: simulate market cap as closing_price * 1,000,000.
                    df['market_cap'] = df['closing_price'] * 1_000_000
                    data[ticker] = df
                else:
                    logger.warning(f"No data returned for {ticker}")
            except Exception as e:
                # Log the error and skip the ticker.
                logger.error(f"Error fetching data for {ticker}: {e}")
                continue
        return data