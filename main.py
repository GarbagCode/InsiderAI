from fetch_data.quiverquant import fetch_from_api
from helpers.unique_tickers import get_unique_tickers
from fetch_data.yfinanace import download_and_cache_prices
from db.queries.stock_prices import get_stock_price



price = get_stock_price('BCEI', '2020-07-27')

print(price)