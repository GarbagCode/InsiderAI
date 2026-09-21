from dotenv import load_dotenv
import os

load_dotenv()
QUIVERQUANT_AUTH = os.getenv("QUIVERQUANT_AUTH")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")