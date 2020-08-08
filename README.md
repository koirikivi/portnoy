# Portnoy trading bot
 
Trade assets on Alpaca.markets based on Dave Portnoy's (@stoolpresidente) Tweets.

![Bot in use](https://raw.githubusercontent.com/koirikivi/portnoy/master/assets/bot-in-use.png)

It's currently very bare bones and only makes market buys for each mentioned symbol.
The algorithm is roughly like this:

1. Get all new tweets from @stoolpresidente
2. Parse each cashtag (e.g. `$amzn`) from the Tweets
3. For each tweet and cashtag, make a Market Buy order on Alpaca.markets

## Installation

```shell script
$ python3.8 -m venv venv
$ venv/bin/pip install -r requirements.txt
$ venv/bin/pip install -e .
```

## Installation

```shell script
$ venv/bin/python -m portnoy
```

## TODO
- Store id of last processed tweet and use it in `since_id`
- Sentiment analysis for tweets (positive/negative -> buy/sell).
  Currently it buys every symbol, even those that have been dissed.
- Implement selling / shorting
- Make limit orders instead of market orders?
- Parse videos (ambitious)
