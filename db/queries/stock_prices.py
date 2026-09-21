
import sqlite3

def get_stock_price(ticker, date, db_path='db/stock_prices.db'):
    """Query SQLite cache"""
    conn = sqlite3.connect(db_path)
    query = """
        SELECT Close FROM stock_prices 
        WHERE Ticker = ? AND Date = ?
    """
    result = conn.execute(query, (ticker, str(date))).fetchone()
    conn.close()
    
    return result[0] if result else None
