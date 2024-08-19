# Orignal idea

Social Sentiment Trading dApp:

- We select 10-12 twitter personalities who are influencers in crypto
- We use sentiment analysis via LLMs to identify
- 1. When that person is talking about a coin that is tradeable (consensus is needed here)
- 2. Determine if the sentiment in that tweet is positive (Buy signal) (consensus is needed here)
- 3. We calculate the performance of that coin based on prices of the coin, i.e. did the asset go up, down, etc.
- 4. We have a leaderboard of which personalities are performing the best
- 5. Users of the dapp can then choose which personalities they want to follow > we can even have an agentic piece where users can copy trade those personalities (This will allow the dapp to make fees/commission). Fees can also be given to personalities who perform well which would incentivize them to talk about coins ...creates a flywheel
- The goal with this is to transparently assess the performance of people promoting coins to show who is actually good

# Current Behavior

- Users can follow a twitter personality
- We manually feed tweets to the dapp
  - Old tweets impact the leaderboard by comparing the sentiment of the tweet with the daily price change of the coin
  - New tweets are used to automatically make investments on behalf of the user
- The leaderboard shows the performance of the twitter personalities

# Limitations we've faced

## Real-time data

We'd like our dApp to automatically fetch tweets from the twitter personalities we're following periodically. This would be similar to the concept of a cron job, which are not in the scope of the GenVM.
This will probably require a separate service to be running, hosted by the dApp owner.

- This makes sense in ecomonic terms, given that feeding tweets is costly. Maybe we can add some behavior to pay the dApp owner for feeding tweets.

## Private APIs and Web Scraping

We wanted to use the Twitter API to fetch tweets from the personalities we're following. However, the Twitter API requires authentication, which would require a private key. Is there a secure way to store secrets in the GenVM?

Also, web scraping is really hard given that most websites are dynamic and require JavaScript to be execute.

- We wanted to use the CoinGecko API to fetch the price of the coins, but we had to resort to using coinmarketcap.
- Web scraping features in the simulator currently only allow GET requests, which is not enough for most websites.

## Integration with other Contracts

# TODOs

- [ ] Tweets are compared to the daily price change of the coin today, but we should compare it to the price change of the coin on the day the tweet was made
- [ ] Tweets are manually fed to the dApp, but we should automatically fetch tweets from the twitter personalities we're following
  - [ ] We should use the CoinGecko API to fetch the price of the coins
  - [ ] We should handle duplicate tweets
