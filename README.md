# Portnoy trading bot
 
Trade assets on Alpaca.markets based on Dave Portnoy's (@stoolpresidente) Tweets.

It's currently very bare bones and only makes market buys for each mentioned symbol.
The algorithm is roughly like this:

1. Get all new tweets from @stoolpresidente
2. Parse each cashtag (e.g. `$amzn`) from the Tweets
3. For each tweet and cashtag, make a Market Buy order on Alpaca.markets

## TODO
- Sentiment analysis for tweets (positive/negative -> buy/sell).
  Currently it buys every symbol, even those that have been dissed.
- Implement selling / shorting
- Make limit orders instead of market orders?
- Parse videos (ambitious)
