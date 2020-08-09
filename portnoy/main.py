"""
Portnoy trading bot
===================

Trade assets on Alpaca.markets based on Dave Portnoy's (@stoolpresidente) Tweets.

It's currently very bare bones and only makes market buys for each mentioned symbol.
The algorithm is roughly like this:

1. Get all new tweets from @stoolpresidente
2. Parse each cashtag (e.g. `$amzn`) from the Tweets
3. For each tweet and cashtag, make a Market Buy order on Alpaca.markets

Usage
-----

1. Install python3.8 (3.7 and 3.6 might also work)
2. $ pip3 install python-dotenv alpaca-trade-api python-twitter
3. Create a file named .env in the same directory as this file, with the following contents:

    # note: #ALPACA_ENDPOINT=https://paper-api.alpaca.markets for paper trading
    ALPACA_ENDPOINT=https://api.alpaca.markets
    ALPACA_API_KEY=<Your alpaca api key goes here>
    ALPACA_API_SECRET=<Your alpaca api secret goes here>
    TWITTER_API_KEY=<Your twitter api key goes here>
    TWITTER_API_SECRET=<Your twitter api secret goes here>
    TWITTER_ACCESS_TOKEN_KEY=<Your twitter access token key goes here>
    TWITTER_ACCESS_TOKEN_SECRET=<Your twitter access token secret goes here>

4. $ python3 portnoy.py

Next steps
----------
- Sentiment analysis for tweets (positive/negative -> buy/sell).
  Currently it buys every symbol, even those that have been dissed.
- Implement selling / shorting
- Make limit orders instead of market orders?
- Parse videos (ambitious)
"""
import logging
import os
import re
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys
from typing import List, Union, Literal

import alpaca_trade_api
import twitter
from alpaca_trade_api.common import URL
from dotenv import load_dotenv

load_dotenv(verbose=True)
logger = logging.getLogger(__name__)

SLEEP_TIME = 30
BUY_QTY = 1
PORTNOY_TWITTER_USERNAME = 'stoolpresidente'
BASE_DIR = Path(__file__).parent.parent.resolve()
LAST_PROCESSED_TWEET_FILE = BASE_DIR / '.last_processed_tweet'

ALPACA_ENDPOINT = os.environ['ALPACA_ENDPOINT']
ALPACA_API_KEY = os.environ['ALPACA_API_KEY']
ALPACA_API_SECRET = os.environ['ALPACA_API_SECRET']
TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
TWITTER_API_SECRET = os.environ['TWITTER_API_SECRET']
TWITTER_ACCESS_TOKEN_KEY = os.environ['TWITTER_ACCESS_TOKEN_KEY']
TWITTER_ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

alpaca_client = alpaca_trade_api.REST(
    key_id=ALPACA_API_KEY,
    secret_key=ALPACA_API_SECRET,
    base_url=URL(ALPACA_ENDPOINT),
)
twitter_client = twitter.Api(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token_key=TWITTER_ACCESS_TOKEN_KEY,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
    tweet_mode='extended',  # don't truncate it, use full_text instead of text
)


@dataclass
class TradeAdvice:
    type: Union[Literal['buy'], Literal['sell']]
    symbol: str
    tweet: twitter.models.Status


def main():
    # the main algorithm works like this:
    # 1. read all *new* tweets from david portnoy
    # 2. scan everything which contains a ticker symbol
    # 3. for each of those, make a buy or sell on alpaca.exchange using the API

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print('Launching portnoy bot')
    # alpaca_account = alpaca_client.get_account()
    alpaca_assets = alpaca_client.list_assets()
    tradable_symbols = set(a.symbol for a in alpaca_assets if a.tradable)
    print(f'Got {len(tradable_symbols)} assets to trade with')

    print("Current positions:")
    for p in alpaca_client.list_positions():
        print(f"{p.symbol:8}{'':8}{p.side:8}{p.qty} @ {p.avg_entry_price:10}")
    print("Open orders:")
    for o in alpaca_client.list_orders():
        print(f"{o.symbol:8}{o.type:8}{o.side:8}{o.qty} @ {o.limit_price}")

    while True:
        try:
            print('')
            print(datetime.now().isoformat())
            # Uncomment the following to not do anything before market opens
            # wait_for_market_open()

            tweets = fetch_new_tweets()

            print(f"Got {len(tweets)} tweet(s)")

            trade_advices = get_trade_advice(tweets=tweets, tradable_symbols=tradable_symbols)
            print(f"Got {len(trade_advices)} trade advice(s)")

            for advice in trade_advices:
                if advice.type == 'buy':
                    print(f'Buying {advice.symbol} based on "{advice.tweet.full_text}"')
                    # TODO: make limit orders, not market orders
                    alpaca_client.submit_order(
                        symbol=advice.symbol,
                        qty=BUY_QTY,
                        side='buy',
                        type='market',
                        time_in_force='day',
                    )
                elif advice.type == 'sell':
                    print(f'Would sell {advice.symbol} based on "{advice.tweet.full_text}" but selling not implemented')

            print(f"Sleeping for {SLEEP_TIME} seconds")
        except KeyboardInterrupt:
            print("Bye bye!")
            sys.exit()
        except Exception:  # noqa
            traceback.print_exc()
            print('Error caught, sleeping and trying again')

        time.sleep(SLEEP_TIME)


def fetch_new_tweets():
    since_id = None
    if LAST_PROCESSED_TWEET_FILE.exists():
        with open(LAST_PROCESSED_TWEET_FILE) as f:
            since_id = int(f.read().strip())

    print(f'Waiting for new tweets... (since {since_id})')
    while True:
        tweets = twitter_client.GetUserTimeline(
            screen_name=PORTNOY_TWITTER_USERNAME,
            count=50,
            since_id=since_id,
        )
        if tweets:
            since_id = tweets[0].id
            with open(LAST_PROCESSED_TWEET_FILE, 'w') as f:
                f.write(str(since_id))
            return tweets
        else:
            time.sleep(SLEEP_TIME)


cashtag_re = re.compile(r'\$[a-zA-Z]+')
def get_trade_advice(*, tweets, tradable_symbols) -> List[TradeAdvice]:
    # TODO: now this only buys and never sells.
    # This is not good, since we have tweets like this: "Whoever gave me $jakk should die"
    # So we should deduce if a tweet is positive or negative
    ret = []
    for tweet in tweets:
        if '$' not in tweet.full_text:
            continue
        cashtags = cashtag_re.findall(tweet.full_text)
        for cashtag in set(cashtags):
            symbol = cashtag.upper().lstrip('$')
            if symbol not in tradable_symbols:
                logger.info('%s is not in tradable symbols', symbol)
                continue
            ret.append(TradeAdvice(
                type='buy',  # always buy!
                symbol=symbol,
                tweet=tweet,
            ))
    return ret


def wait_for_market_open():
    clock = alpaca_client.get_clock()
    if clock.is_open:
        num_seconds = (clock.next_open - clock.timestamp).seconds
        print(f'The market is closed. Sleeping for {num_seconds} seconds until it opens...')
        time.sleep(num_seconds)


if __name__ == '__main__':
    main()
