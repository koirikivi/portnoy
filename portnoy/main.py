"""
Portnoy trading bot
===================

Trade assets on Alpaca.markets based on Dave Portnoy's (@stoolpresidente) Tweets.

It's currently very bare bones and only makes market buys for each mentioned symbol.
The algorithm is roughly like this:

1. Get all new tweets from @stoolpresidente
2. Parse each cashtag (e.g. `$amzn`) from the Tweets
3. For each tweet and cashtag, make a Market Buy order on Alpaca.markets

Read README.md for details on how to run.
"""
import functools
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
VAR_DIR = BASE_DIR / 'var'
LAST_PROCESSED_TWEET_FILE = VAR_DIR / 'last_processed_tweet'

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


TradeAction = Literal['buy', 'sell']


@dataclass
class TradeAdvice:
    type: TradeAction
    symbol: str
    tweet: twitter.models.Status


# HACK: flush prints automatically to make piping to `tee` work
print = functools.partial(print, flush=True)


def main():
    # the main algorithm works like this:
    # 1. read all *new* tweets from david portnoy
    # 2. scan everything which contains a ticker symbol
    # 3. for each of those, make a buy or sell on alpaca.exchange using the API

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    os.makedirs(VAR_DIR, exist_ok=True)

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
    ret = []
    for tweet in tweets:
        if '$' not in tweet.full_text:
            continue

        action = decide_buy_or_sell(tweet.full_text)
        cashtags = cashtag_re.findall(tweet.full_text)
        for cashtag in set(cashtags):
            symbol = cashtag.upper().lstrip('$')
            if symbol not in tradable_symbols:
                logger.info('%s is not in tradable symbols', symbol)
                continue
            ret.append(TradeAdvice(
                type=action,
                symbol=symbol,
                tweet=tweet,
            ))
    return ret


def decide_buy_or_sell(tweet_text: str) -> TradeAction:
    # TODO: implement this. now it only buys and never sells.
    # This is not good, since we have tweets like this: "Whoever gave me $jakk should die"
    # So we should deduce if a tweet is positive or negative
    return 'buy'


def wait_for_market_open():
    clock = alpaca_client.get_clock()
    if clock.is_open:
        num_seconds = (clock.next_open - clock.timestamp).seconds
        print(f'The market is closed. Sleeping for {num_seconds} seconds until it opens...')
        time.sleep(num_seconds)


if __name__ == '__main__':
    main()
