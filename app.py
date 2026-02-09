# app.py
import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt

plt.style.use("ggplot")

st.set_page_config(page_title="Stock Dashboard", layout="wide")

st.title("📈 Stock Analytics Dashboard")

# -----------------------------
# 1️⃣ MySQL connection
# -----------------------------
mysql_config = {
    "host": "localhost",
    "user": "root",
    "password": "",       # your MySQL password
    "database": "stocks_db"
}

conn = mysql.connector.connect(**mysql_config)

# -----------------------------
# 2️⃣ Load tickers dynamically
# -----------------------------
tickers_query = "SELECT DISTINCT ticker FROM stock_prices"
tickers = pd.read_sql(tickers_query, conn)['ticker'].tolist()

st.sidebar.header("Select Tickers")
selected_tickers = st.sidebar.multiselect("Tickers", tickers, default=tickers[:4])

# -----------------------------
# 3️⃣ Load data for selected tickers
# -----------------------------
if selected_tickers:
    placeholders = ','.join(['%s'] * len(selected_tickers))
    query = f"""
    SELECT Date, ticker, adj_close
    FROM stock_prices
    WHERE ticker IN ({placeholders})
    ORDER BY Date
    """
    df = pd.read_sql(query, conn, params=selected_tickers)
else:
    st.warning("Please select at least one ticker.")
    st.stop()

conn.close()

# -----------------------------
# 4️⃣ Prepare data
# -----------------------------
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.drop_duplicates(subset=['Date', 'ticker'])
df_pivot = df.pivot(index='Date', columns='ticker', values='adj_close')
df_returns = df_pivot.pct_change()
df_cum = (1 + df_returns).cumprod() - 1
ma_windows = [20, 50]

# -----------------------------
# 5️⃣ Adjusted Close Prices
# -----------------------------
st.subheader("Adjusted Close Prices")
fig, ax = plt.subplots(figsize=(12, 6))
for ticker in df_pivot.columns:
    ax.plot(df_pivot.index, df_pivot[ticker], label=ticker)
ax.set_xlabel("Date")
ax.set_ylabel("Price ($)")
ax.legend()
st.pyplot(fig)

# -----------------------------
# 6️⃣ Daily Returns
# -----------------------------
st.subheader("Daily Returns")
fig, ax = plt.subplots(figsize=(12, 4))
for ticker in df_returns.columns:
    ax.plot(df_returns.index, df_returns[ticker], label=ticker)
ax.axhline(0, color='red', linestyle='--', alpha=0.5)
ax.set_xlabel("Date")
ax.set_ylabel("Return")
ax.legend()
st.pyplot(fig)

# -----------------------------
# 7️⃣ Moving Averages
# -----------------------------
st.subheader("Moving Averages (20-day & 50-day)")
for ticker in df_pivot.columns:
    st.write(f"**{ticker}**")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df_pivot.index, df_pivot[ticker], label=f'{ticker} Price')
    for w in ma_windows:
        ax.plot(df_pivot.index, df_pivot[ticker].rolling(window=w).mean(), label=f'MA-{w}')
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($)")
    ax.legend()
    st.pyplot(fig)

# -----------------------------
# 8️⃣ Cumulative Returns
# -----------------------------
st.subheader("Cumulative Returns")
fig, ax = plt.subplots(figsize=(12, 5))
for ticker in df_cum.columns:
    ax.plot(df_cum.index, df_cum[ticker], label=ticker)
ax.set_xlabel("Date")
ax.set_ylabel("Cumulative Return")
ax.legend()
st.pyplot(fig)

# -----------------------------
# 9️⃣ Summary Statistics
# -----------------------------
st.subheader("Daily Returns Summary")
st.dataframe(df_returns.describe())
