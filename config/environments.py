from dotenv import load_dotenv
import os

load_dotenv()
QUIVERQUANT_AUTH = os.getenv("QUIVERQUANT_AUTH")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
ALPACA_APP_KEY = os.getenv("ALPACA_APP_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
