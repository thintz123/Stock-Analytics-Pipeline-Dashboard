import yfinance as yf
import pandas as pd
import mysql.connector
import os

# -----------------------------
# 1️⃣ Configuration
# -----------------------------
tickers = ["XOM", "AAPL", "MSFT", "GOOG"]  # Add more tickers here
start_date = "2018-01-01"
end_date = "2023-12-31"

output_dir = "data"
os.makedirs(output_dir, exist_ok=True)
csv_file = os.path.join(output_dir, "raw_prices.csv")

# MySQL configuration
mysql_config = {
    "host": "localhost",
    "user": "root",        # your MySQL username
    "password": "",        # your MySQL password
    "database": "stocks_db"
}

# -----------------------------
# 2️⃣ Download data from Yahoo Finance
# -----------------------------
all_data = pd.DataFrame()
for ticker in tickers:
    print(f"Downloading {ticker}...")
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        print(f"⚠️ No data for {ticker}")
        continue
    all_data[ticker] = data['Close']

all_data.index.name = "Date"
all_data.reset_index(inplace=True)

# -----------------------------
# 3️⃣ Convert to long format for MySQL
# -----------------------------
df_long = all_data.melt(id_vars='Date', var_name='ticker', value_name='adj_close')

# Ensure dates are strings in YYYY-MM-DD format for MySQL DATE column
df_long['Date'] = pd.to_datetime(df_long['Date']).dt.strftime('%Y-%m-%d')

# Save CSV for notebook use
df_long.to_csv(csv_file, index=False)
print(f"CSV saved: {csv_file}")

# -----------------------------
# 4️⃣ Insert into MySQL (skip duplicates)
# -----------------------------
try:
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()

    # Make sure columns have correct types:
    # Date: DATE, ticker: VARCHAR(10), adj_close: FLOAT
    # (Run once manually if needed)
    # cursor.execute("ALTER TABLE stock_prices MODIFY COLUMN Date DATE NOT NULL;")
    # cursor.execute("ALTER TABLE stock_prices MODIFY COLUMN ticker VARCHAR(10) NOT NULL;")
    # cursor.execute("ALTER TABLE stock_prices MODIFY COLUMN adj_close FLOAT;")
    # cursor.execute("ALTER TABLE stock_prices ADD UNIQUE KEY unique_date_ticker (Date, ticker);")

    # Insert data using INSERT IGNORE to skip duplicates
    insert_query = """
    INSERT IGNORE INTO stock_prices (Date, ticker, adj_close)
    VALUES (%s, %s, %s)
    """
    data_to_insert = df_long.values.tolist()
    cursor.executemany(insert_query, data_to_insert)
    conn.commit()

    print(f"{cursor.rowcount} rows inserted into MySQL (duplicates skipped)")

except mysql.connector.Error as err:
    print(f"MySQL Error: {err}")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()

