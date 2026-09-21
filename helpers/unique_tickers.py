# Step 1: Get all unique tickers from congressional trades
def get_unique_tickers(trades_data):
    tickers = set()
    for trade in trades_data:
        if trade['Ticker']:
            tickers.add(trade['Ticker'])
    return list(tickers)