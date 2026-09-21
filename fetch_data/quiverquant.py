import requests
import time
import json
from config.environments import QUIVERQUANT_AUTH

CHECKPOINT_FILE = 'trades_checkpoint.json'

def load_checkpoint():
    """Load saved progress"""
    try:
        with open(CHECKPOINT_FILE, 'r') as f:
            data = json.load(f)
            return data['trades'], data['last_page']
    except FileNotFoundError:
        return [], 1

def save_checkpoint(trades, page):
    """Save progress to resume later"""
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({'trades': trades, 'last_page': page}, f)
    print(f"Checkpoint saved: page {page}, {len(trades)} trades")

def fetch_from_api():
    site = "https://api.quiverquant.com/beta/bulk/congresstrading"

    headers = {
        "Authorization": f"Bearer {QUIVERQUANT_AUTH}"
    }

    all_trades, start_page = load_checkpoint()
    page = start_page
    max_retries = 3
    
    while True:
        params = {
            "version": "V2",
            "page": page,
            "page_size": 100
        }

        retry_count = 0
        while retry_count < max_retries:
            try:
                response = requests.get(site, headers=headers, params=params, timeout=30)  # Increased to 30s
                
                if response.status_code == 429:
                    wait_time = 90
                    print(f"Rate limited on page {page}! Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    retry_count += 1
                    continue
                
                response.raise_for_status()
                
                data = response.json()
                
                if not data:
                    print(f"Completed! Total trades: {len(all_trades)}")
                    save_checkpoint(all_trades, page)
                    return all_trades
                
                all_trades.extend(data)
                page += 1
                print(f"Fetched page {page - 1}, total trades: {len(all_trades)}")
                
                # Save checkpoint every 10 pages
                if page % 10 == 0:
                    save_checkpoint(all_trades, page)
                
                time.sleep(1)  # Increased delay
                break
                
            except requests.exceptions.Timeout:
                retry_count += 1
                wait_time = 60 * retry_count
                print(f"Timeout on page {page}, retry {retry_count}/{max_retries}. Waiting {wait_time}s...")
                time.sleep(wait_time)
            
            except requests.exceptions.RequestException as e:
                print(f"Error on page {page}: {e}")
                save_checkpoint(all_trades, page)
                raise
        
        if retry_count >= max_retries:
            print(f"Max retries exceeded on page {page}. Saving progress...")
            save_checkpoint(all_trades, page)
            raise Exception(f"Failed after {max_retries} retries on page {page}")
    
    return all_trades