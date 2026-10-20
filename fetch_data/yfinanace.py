import requests
import sqlite3
import pandas as pd
import logging
import time
import re
from datetime import datetime, timezone
from requests.exceptions import Timeout, HTTPError, RequestException, ConnectionError as RequestsConnectionError
from config.environments import ALPACA_APP_KEY, ALPACA_SECRET_KEY

logger = logging.getLogger(__name__)

def is_valid_stock_symbol(symbol):
    """Filter out invalid symbols (bonds, treasuries, junk tickers)"""
    if not symbol or len(symbol) > 5:
        return False
    
    if re.search(r'[^A-Z0-9\-]', symbol):
        return False
    
    if symbol[0].isdigit():
        return False
    
    junk = ['MATURE', 'WEEK', 'MONTH', 'CASH', 'DUE', 'FUND', 'SYMBOL', 'TICKER']
    if any(junk_word in symbol for junk_word in junk):
        return False
    
    return True

def download_and_cache_prices(tickers, start_date='2016-01-01', end_date='2024-12-31', 
                          db_path='db/stock_prices.db', feed='iex', adjustment='all'):
    """
    Download daily bars from Alpaca and cache to SQLite.
    
    Args:
        tickers: List of stock symbols
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        db_path: SQLite database path
        feed: 'iex' (free) or 'sip' (paid)
        adjustment: 'raw', 'split', 'dividend', 'all', etc.
    """
    
    # Filter valid tickers
    valid_tickers = [t for t in tickers if is_valid_stock_symbol(t)]
    skipped = len(tickers) - len(valid_tickers)
    logger.info(f"Filtered {len(tickers)} tickers -> {len(valid_tickers)} valid ({skipped} skipped)")
    
    url = "https://data.alpaca.markets/v2/stocks/bars"
    headers = {
        "APCA-API-KEY-ID": ALPACA_APP_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
        "accept": "application/json",
    }
    
    # Rate limit: 200 requests/min = 0.35 seconds per request
    REQUEST_DELAY = 0.35
    
    conn = sqlite3.connect(db_path)
    
    for i, ticker in enumerate(valid_tickers):
        logger.info(f"Fetching {ticker} ({i+1}/{len(valid_tickers)}) - {start_date} to {end_date}")
        
        base_params = {
            "symbols": ticker,
            "timeframe": "1Day",
            "feed": feed,
            "adjustment": adjustment,
            "limit": 10000,
            "sort": "asc",
            "start": start_date,
            "end": end_date,
        }
        
        max_retries = 3
        backoff = 2
        
        for attempt in range(max_retries):
            # Pagination
            all_bars = []
            page_token = None
            page_num = 0
            
            try:
                while True:
                    page_num += 1
                    params = dict(base_params)
                    if page_token:
                        params["page_token"] = page_token
                    
                    try:
                        resp = requests.get(url, headers=headers, params=params, timeout=30)
                        resp.raise_for_status()
                    
                    except Timeout:
                        logger.error(f"Request timeout for {ticker}")
                        raise ConnectionError(f"API request timed out for {ticker}")
                    
                    except HTTPError as e:
                        status = resp.status_code
                        if status == 401:
                            logger.critical(f"Auth failed - invalid API key/secret")
                        elif status == 403:
                            logger.error(f"Access forbidden for {ticker} - feed '{feed}' not allowed on plan")
                        elif status == 422:
                            logger.error(f"Invalid params for {ticker}: {resp.text}")
                        elif status == 429:
                            logger.warning(f"Rate limited for {ticker} (attempt {attempt+1}/{max_retries})")
                            raise HTTPError("Rate limited")
                        else:
                            logger.error(f"HTTP {status} for {ticker}: {resp.text}")
                        raise
                    
                    except RequestsConnectionError:
                        logger.error(f"Network connection error for {ticker}")
                        raise
                    
                    try:
                        data = resp.json()
                    except ValueError:
                        logger.error(f"Invalid JSON response for {ticker}")
                        raise ValueError(f"Failed to parse JSON for {ticker}")
                    
                    # Validate structure
                    if "bars" not in data:
                        logger.error(f"No 'bars' key in response for {ticker}")
                        raise ValueError(f"Unexpected response for {ticker}")
                    
                    bars = data["bars"]
                    if isinstance(bars, dict):
                        symbol_bars = bars.get(ticker, []) or []
                    else:
                        symbol_bars = bars or []
                    
                    all_bars.extend(symbol_bars)
                    logger.debug(f"Page {page_num}: {len(symbol_bars)} bars (cumulative {len(all_bars)})")
                    
                    page_token = data.get("next_page_token")
                    if not page_token:
                        break
                
                if not all_bars:
                    logger.warning(f"No data for {ticker}")
                    break
                
                # Convert to DataFrame
                df = pd.DataFrame(all_bars)
                
                # Rename columns: t->date, o->open, h->high, l->low, c->close, v->volume
                df = df.rename(columns={
                    "t": "date",
                    "o": "open",
                    "h": "high",
                    "l": "low",
                    "c": "close",
                    "v": "volume",
                })
                
                df["ticker"] = ticker
                df["date"] = pd.to_datetime(df["date"]).dt.date
                
                # Keep only needed columns
                df = df[["date", "ticker", "open", "high", "low", "close", "volume"]]
                
                # Ensure numeric types
                for col in ["open", "high", "low", "close", "volume"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                
                # Save to SQLite
                df.to_sql('stock_prices', conn, if_exists='append', index=False)
                logger.info(f"  Cached {len(df)} bars for {ticker}")
                
                # Respect rate limit
                time.sleep(REQUEST_DELAY)
                break
            
            except HTTPError as e:
                if "Rate limited" in str(e) and attempt < max_retries - 1:
                    logger.warning(f"  Waiting {backoff}s before retry...")
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    logger.error(f"Error processing {ticker}: {e}")
                    break
            
            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
                break
    
    # Create index
    try:
        conn.execute('CREATE INDEX IF NOT EXISTS idx_ticker_date ON stock_prices(ticker, date)')
        conn.commit()
    except:
        pass
    
    conn.close()
    logger.info("Download complete!")

# Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Get tickers from your congressional trades
    from fetch_data.quiverquant import fetch_from_api, get_unique_tickers
    
    trades = fetch_from_api()
    tickers = get_unique_tickers(trades)
    
    download_and_cache_prices(tickers)