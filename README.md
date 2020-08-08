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

The bot is configured with environment variables and it reads `.env` automatically.
So create a file called `.env` in this directory with the following contents:

```
# note: #ALPACA_ENDPOINT=https://api.alpaca.markets for production trading
ALPACA_ENDPOINT=https://paper-api.alpaca.markets
ALPACA_API_KEY=<Your alpaca api key goes here>
ALPACA_API_SECRET=<Your alpaca api secret goes here>
TWITTER_API_KEY=<Your twitter api key goes here>
TWITTER_API_SECRET=<Your twitter api secret goes here>
TWITTER_ACCESS_TOKEN_KEY=<Your twitter access token key goes here>
TWITTER_ACCESS_TOKEN_SECRET=<Your twitter access token secret goes here>
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
