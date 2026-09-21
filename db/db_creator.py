import sqlite3

def create_stock_prices_schema(db_path='db/stock_prices.db'):
    """Create the SQLite schema for stock prices"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
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
        )
    ''')
    
    # Create indexes for fast queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_ticker_date 
        ON stock_prices(Ticker, Date)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_ticker 
        ON stock_prices(Ticker)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_date 
        ON stock_prices(Date)
    ''')
    
    conn.commit()
    conn.close()
    print("Schema created successfully")

# Run once to initialize
create_stock_prices_schema()