import pandas as pd
from datetime import datetime, timedelta
from quiverquant import fetch_from_api
from db.queries.stock_prices import get_stock_price


# Fetch congressional trades
trades_data = fetch_from_api()  # Your QuiverQuant API call

# For each trade, get the stock's performance after filing date
def prepare_training_data(trades_data, lookback_days=5):
    training_data = []
    
    for trade in trades_data:
        filed_date = datetime.fromisoformat(trade['Filed'])
        ticker = trade['Ticker']
        
        # Get historical price data for this stock
        price_at_filed = get_stock_price(ticker, filed_date)
        price_after_days = get_stock_price(ticker, filed_date + timedelta(days=lookback_days))
        
        # Calculate return %
        return_pct = ((price_after_days - price_at_filed) / price_at_filed) * 100
        
        # Create feature row
        feature_row = {
            'ticker': ticker,
            'company': trade['Company'],
            'transaction_type': trade['Transaction'],  # Buy or Sale
            'trade_size_usd': float(trade['Trade_Size_USD']) if trade['Trade_Size_USD'] else 0,
            'party': trade['Party'],
            'chamber': trade['Chamber'],
            'politician_name': trade['Name'],
            'days_to_file': (filed_date - datetime.fromisoformat(trade['Traded'])).days,
            'target_return': return_pct  # Your Y variable
        }
        training_data.append(feature_row)
    
    return pd.DataFrame(training_data)