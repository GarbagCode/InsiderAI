import sqlite3

conn = sqlite3.connect('db/stock_prices.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM stock_prices")
total_rows = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT Ticker) FROM stock_prices")
unique_tickers = cursor.fetchone()[0]

cursor.execute("SELECT Ticker, COUNT(*) as days FROM stock_prices GROUP BY Ticker ORDER BY days DESC LIMIT 10")
print("Top 10 tickers by data points:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} days")

conn.close()

print(f"\nTotal price records: {total_rows:,}")
print(f"Unique tickers with data: {unique_tickers}")