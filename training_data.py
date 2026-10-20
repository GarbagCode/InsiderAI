import pandas as pd
from datetime import datetime, timedelta
from fetch_data.quiverquant import fetch_from_api
from db.queries.stock_prices import get_stock_price

def parse_trade_size(trade_size_str):
    """Parse trade size from range format like '$1,001 - $15,000'"""
    if not trade_size_str:
        return 0
    
    try:
        # Remove $ and spaces, split by '-'
        parts = trade_size_str.replace('$', '').replace(',', '').split('-')
        
        if len(parts) == 2:
            lower = float(parts[0].strip())
            upper = float(parts[1].strip())
            # Use midpoint of range
            return (lower + upper) / 2
        else:
            # Single value
            return float(parts[0].strip())
    except:
        return 0

def prepare_training_data(trades_data, lookback_days=5, output_path='data/training_data_sell_in_5_days_with_time.csv'):
    training_data = []
    skipped = 0
    
    for trade in trades_data:
        try:
            filed_date = datetime.fromisoformat(trade['Filed']).date() if isinstance(trade['Filed'], str) else trade['Filed'].date()
            ticker = trade['Ticker']
            
            # Get historical price data for this stock
            price_at_filed = get_stock_price(ticker, filed_date)
            
            # Skip if no price at filing date
            if price_at_filed is None:
                skipped += 1
                continue
            
            price_after_days = get_stock_price(ticker, filed_date + timedelta(days=lookback_days))
            
            # Skip if no price after lookback period
            if price_after_days is None:
                skipped += 1
                continue
            
            # Calculate return %
            return_pct = ((price_after_days - price_at_filed) / price_at_filed) * 100
            
            # Create feature row
            feature_row = {
                'ticker': ticker,
                'company': trade.get('Company', ''),
                'transaction_type': trade['Transaction'],
                'trade_size_usd': parse_trade_size(trade.get('Trade_Size_USD')),
                'party': trade['Party'],
                'chamber': trade['Chamber'],
                'politician_name': trade['Name'],
                'filed_date': filed_date,
                'days_to_file': (filed_date - datetime.fromisoformat(trade['Traded']).date()).days,
                'target_return': return_pct
            }
            training_data.append(feature_row)
        
        except Exception as e:
            print(f"Error processing trade for {ticker}: {e}")
            skipped += 1
            continue
    
    df = pd.DataFrame(training_data)
    print(f"Prepared {len(training_data)} training samples, skipped {skipped}")
    
    # Save to file
    df.to_csv(output_path, index=False)
    print(f"Saved training data to {output_path}")
    
    return df

if __name__ == "__main__":
    # Fetch congressional trades
    trades_data = fetch_from_api()
    prepare_training_data(trades_data)