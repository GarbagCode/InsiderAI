import yfinance as yf
import sqlite3
import pandas as pd

def download_and_cache_prices(tickers, start_date='2016-01-01', db_path='stock_prices.db'):
    """Download using yfinance (simple, no auth needed)"""
    conn = sqlite3.connect(db_path)
    
    # Download all at once (much faster than 1-by-1)
    data = yf.download(tickers, start=start_date, end='2024-12-31', progress=True)
    
    # Transform to long format
    prices = []
    for ticker in tickers:
        ticker_data = data[ticker] if len(tickers) > 1 else data
        for date, row in ticker_data.iterrows():
            prices.append({
                'Date': date.date(),
                'Ticker': ticker,
                'Open': row['Open'],
                'High': row['High'],
                'Low': row['Low'],
                'Close': row['Close'],
                'Volume': row['Volume']
            })
    
    df = pd.DataFrame(prices)
    df.to_sql('stock_prices', conn, if_exists='append', index=False)
    
    conn.execute('CREATE INDEX IF NOT EXISTS idx_ticker_date ON stock_prices(Ticker, Date)')
    conn.commit()
    conn.close()
    print(f"Finished caching {len(df)} price points to SQLite")