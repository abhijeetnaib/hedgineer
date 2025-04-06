import streamlit as st
import datetime
import pandas as pd
from database_manager import DatabaseManager
from custom_index_calculator import calculate_index_for_date_range
import sqlite3
import os

# Set up database directory and path
db_dir = r"C:\Users\abhij\OneDrive\Desktop\hedgineer"
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

db_path = os.path.join(db_dir, "data.db")
print(f"Database path: {db_path}")

st.write("Connecting to database...")
db_manager = DatabaseManager(db_path=db_path)
st.write("Connected to database.")

st.title("Custom Equal-Weighted Index Dashboard")

# Sidebar: Let the user select a date range for composition data
st.sidebar.header("Date Range Selection")
default_start_date = datetime.date.today() - datetime.timedelta(days=30)
default_end_date = datetime.date.today()

selected_date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(default_start_date, default_end_date),
    key="date_range_input"
)

# Validate the selected date range
if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date = selected_date_range[0].strftime('%Y-%m-%d')
    end_date = selected_date_range[1].strftime('%Y-%m-%d')
else:
    st.error("Invalid date range selected. Please select a valid start and end date.")
    st.stop()

# Ensure start_date is before end_date
if start_date > end_date:
    st.error("Start date must be before end date.")
    st.stop()

# Query the database for composition data
composition_query = """
    SELECT ticker, closing_price, market_cap, date
    FROM daily_data
    WHERE DATE(date) BETWEEN ? AND ?
    ORDER BY DATE(date), market_cap DESC
"""
composition_df = pd.read_sql_query(composition_query, db_manager.conn, params=(start_date, end_date))

if composition_df.empty:
    st.write(f"No index composition data available for the selected date range: {start_date} to {end_date}.")
else:
    st.subheader(f"Index Composition from {start_date} to {end_date}")
    st.dataframe(composition_df)
    
    # For visualization, compute the average market cap per ticker over the period
    avg_mcap_df = composition_df.groupby("ticker")["market_cap"].mean().reset_index()
    avg_mcap_df = avg_mcap_df.sort_values(by="market_cap", ascending=False).head(10)
    st.subheader("Top 10 Stocks by Average Market Cap (Composition over period)")
    st.bar_chart(avg_mcap_df.set_index("ticker")["market_cap"])

# Display index performance over the past 30 days
today = datetime.date.today()
perf_start_date = (today - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
perf_end_date = today.strftime('%Y-%m-%d')
index_history_df = calculate_index_for_date_range(db_manager, perf_start_date, perf_end_date)

if index_history_df.empty:
    st.write("No index performance data available for the past 30 days.")
else:
    st.subheader("Index Performance Over the Past 30 Days")
    index_history_df['daily_change'] = index_history_df['index_value'].pct_change() * 100
    index_history_df['cumulative_return'] = (1 + index_history_df['daily_change'] / 100).cumprod() - 1
    st.line_chart(index_history_df.set_index('date')['index_value'])

    # Display summary metrics
    st.subheader("Summary Metrics")
    st.write(f"Cumulative Return: {index_history_df['cumulative_return'].iloc[-1]:.2%}")
    st.write(f"Average Daily Change: {index_history_df['daily_change'].mean():.2f}%")

# Highlight composition changes
composition_changes_query = """
    SELECT DISTINCT date
    FROM daily_data
    WHERE ticker NOT IN (
        SELECT ticker
        FROM daily_data
        WHERE DATE(date) = ?
    )
"""
composition_changes_df = pd.read_sql_query(composition_changes_query, db_manager.conn, params=(start_date,))
if not composition_changes_df.empty:
    st.subheader("Composition Changes")
    st.write("Days with changes in index composition:")
    st.dataframe(composition_changes_df)