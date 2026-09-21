from fetch_data.quiverquant import fetch_from_api
from helpers.unique_tickers import get_unique_tickers
from fetch_data.yfinanace import download_and_cache_prices
from db.queries.stock_prices import get_stock_price


trades = fetch_from_api()
tickers = get_unique_tickers(trades)
price_data = download_and_cache_prices(tickers)

price = get_stock_price('AAPL', '2024-01-15')

print(price)