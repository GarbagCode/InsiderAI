CREATE TABLE IF NOT EXISTS stock_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Date TEXT NOT NULL,
    Ticker TEXT NOT NULL,
    Open REAL,
    High REAL,
    Low REAL,
    Close REAL NOT NULL,
    Volume INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(Ticker, Date)
);

CREATE INDEX IF NOT EXISTS idx_ticker_date 
ON stock_prices(Ticker, Date);

CREATE INDEX IF NOT EXISTS idx_ticker 
ON stock_prices(Ticker);

CREATE INDEX IF NOT EXISTS idx_date 
ON stock_prices(Date);