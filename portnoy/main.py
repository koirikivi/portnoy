import os
from dotenv import load_dotenv


load_dotenv(verbose=True)

ALPACA_ENDPOINT = os.environ['ALPACA_ENDPOINT']
ALPACA_API_KEY = os.environ['ALPACA_API_KEY']
ALPACA_SECRET_KEY = os.environ['ALPACA_SECRET_KEY']


