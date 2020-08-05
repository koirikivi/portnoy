import logging
import os
import time
from uuid import uuid4

import alpaca_trade_api
from alpaca_trade_api.common import URL
from dotenv import load_dotenv

load_dotenv(verbose=True)
logger = logging.getLogger(__name__)

ALPACA_ENDPOINT = os.environ['ALPACA_ENDPOINT']
ALPACA_API_KEY = os.environ['ALPACA_API_KEY']
ALPACA_API_SECRET = os.environ['ALPACA_API_SECRET']
TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
TWITTER_API_SECRET = os.environ['TWITTER_API_SECRET']
TWITTER_BEARER_TOKEN = os.environ['TWITTER_BEARER_TOKEN']


def main():
    # the main algorithm works like this:
    # (0. print current positions in alpaca)
    # 1. read all *new* tweets from david portnoy
    # 2. scan everything which contains a ticker symbol
    # 3. for each of those, make a buy or sell on alpaca.exchange using the API

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    alpaca_client = alpaca_trade_api.REST(
        key_id=ALPACA_API_KEY,
        secret_key=ALPACA_API_SECRET,
        base_url=URL(ALPACA_ENDPOINT),
    )
    alpaca_account = alpaca_client.get_account()

    print('account:')
    print(alpaca_account)
    print('positions:')
    print(alpaca_client.list_positions())

    wait_for_market_open(alpaca_client)

    #alpaca_client.submit_order(
    #    symbol='TSLA',
    #    qty=1,
    #    side='buy',
    #    time_in_force='gtc',
    #    type='limit',
    #    limit_price='400.00',
    #    client_order_id=str(uuid4()),
    #)
    return alpaca_client, alpaca_account


def wait_for_market_open(alpaca_client: alpaca_trade_api.REST):
    clock = alpaca_client.get_clock()
    if clock.is_open:
        num_seconds = (clock.next_open - clock.timestamp).seconds
        print(f'The market is closed. Sleeping for {num_seconds} seconds until it opens...')
        time.sleep(num_seconds)


if __name__ == '__main__':
    main()
