# Hedgineer: Custom Equal-Weighted Index Dashboard and Data Ingestion System

## Overview
Hedgineer is a Python-based project designed to fetch, process, and analyze stock market data. It provides tools for creating a custom equal-weighted index, visualizing stock performance, and exporting data for further analysis. The project includes a Streamlit-based dashboard for interactive exploration and a command-line utility for data ingestion.

---

## Features
- **Data Ingestion**: Fetch historical and incremental stock data using `yfinance`.
- **Custom Index Calculation**: Compute an equal-weighted index based on the top 100 stocks by market cap.
- **Streamlit Dashboard**: Visualize index composition and performance over a selected date range.
- **Data Export**: Export index history to Excel and PDF formats.
- **Validation Utility**: Validate the ingested data for correctness and completeness.

---

## Repository Structure
```
hedgineer/
├── constants.py               # Contains constants like top 200 US stock tickers
├── custom_index_calculator.py # Logic for calculating custom equal-weighted index
├── dashboard.py               # Streamlit-based dashboard for visualization
├── data_fetcher.py            # Fetches stock data using yfinance
├── data_ingestion.py          # Command-line utility for data ingestion
├── data_validation_utility.py # Utility for validating ingested data
├── database_manager.py        # Manages SQLite database operations
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
```

---

## Installation

### Prerequisites
- Python 3.8 or higher
- `pip` (Python package manager)

### Required Libraries
Install the required libraries using the following command:
```bash
pip install -r requirements.txt
```

---

## Usage

### 1. **Data Ingestion**
Run the `data_ingestion.py` script to fetch and store stock data in the SQLite database.

#### Command-Line Arguments:
- `--historical_load`: Perform a historical load (`yes` or `no`). Default is `no`.
- `--backfill_days`: Number of days to backfill for historical load. Default is `730`.
- `--export_files`: Export index history to Excel and PDF (`yes` or `no`). Default is `no`.

#### Example Commands:
- Incremental Load:
  ```bash
  python data_ingestion.py
  ```
- Historical Load with 365 Days Backfill:
  ```bash
  python data_ingestion.py --historical_load yes --backfill_days 365
  ```
- Export Files:
  ```bash
  python data_ingestion.py --export_files yes
  ```

---

### 2. **Streamlit Dashboard**
Launch the dashboard to visualize the custom index and stock data.

#### Command:
```bash
streamlit run dashboard.py
```

#### Features:
- Select a date range to view index composition.
- Visualize the top 10 stocks by average market cap.
- Display index performance over the past 30 days.

---

### 3. **Data Validation**
Use the `data_validation_utility.py` script to validate the ingested data.

#### Command:
```bash
python data_validation_utility.py
```

#### Features:
- Check the total number of rows in the `daily_data` table.
- Validate distinct tickers ingested.
- Display sample rows for verification.

---

## Key Components

### 1. **`data_ingestion.py`**
Handles data ingestion from `yfinance` and stores it in an SQLite database. Supports both historical and incremental data loading.

### 2. **`dashboard.py`**
A Streamlit-based dashboard for visualizing stock data and custom index performance.

### 3. **`custom_index_calculator.py`**
Calculates an equal-weighted custom index based on the top 100 stocks by market cap.

### 4. **`database_manager.py`**
Manages SQLite database operations, including creating tables, inserting data, and querying top stocks.

### 5. **`data_validation_utility.py`**
Validates the ingested data for correctness and completeness.

---

## Example Workflow

1. **Ingest Data**:
   Run the `data_ingestion.py` script to fetch and store stock data.
   ```bash
   python data_ingestion.py --historical_load yes --backfill_days 365
   ```

2. **Validate Data**:
   Use the `data_validation_utility.py` script to ensure data integrity.
   ```bash
   python data_validation_utility.py
   ```

3. **Launch Dashboard**:
   Start the Streamlit dashboard to explore and visualize the data.
   ```bash
   streamlit run dashboard.py
   ```

---

## Contributing
Contributions are welcome! Feel free to submit issues or pull requests to improve the project.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---