# Grok Agent Prompts: Alpha from X/Twitter

**Objective**: Deploy Grok agents to scrape X/Twitter for real-time alpha, whale activity, and market sentiment related to Polymarket 5-min crypto markets and BTC price action.

---

## Agent 1: Polymarket Whale Tracker

**Task**: Identify and track large traders on Polymarket.

**Prompt to Grok**:
```
You are an alpha researcher scanning X/Twitter (via your real-time feed) for information about Polymarket traders.

Your mission:
1. Find tweets mentioning "Polymarket" AND large bet sizes (e.g., "bet $10,000", "large position", "whale", "heavy", "sized")
2. Identify wallet addresses if they are shared.
3. Extract: Who is the trader? (username, bio). What market did they bet on? Bet side (YES/NO)? Size? Time?
4. Build a leaderboard of most frequently mentioned "smart money" traders.
5. Note any patterns: Do certain traders consistently win? Do they bet in specific hours? Do they focus on 5-min or 15-min markets?

Output format: JSON list of {
  "trader_handle": "@...",
  "display_name": "...",
  "tweet_url": "...",
  "timestamp": "...",
  "market_description": "...",
  "bet_side": "yes" or "no",
  "bet_size_usd_estimate": number or null,
  "confidence_indicators": ["high", "low", "medium"],
  "follow_up_outcome": "win"/"loss"/"pending"/null
}

Run continuously. Provide daily summary.
```

---

## Agent 2: BTC 5-Minute Market Sentiment

**Task**: Gauge retail sentiment specifically for BTC 5-min prediction markets.

**Prompt to Grok**:
```
Monitor X/Twitter for mentions of:
- "BTC 5 min"
- "Bitcoin 5-minute"
- "Polymarket BTC"
- "5-minute crypto"
- "up or down" within context of BTC and 5 minutes

For each relevant tweet:
- Sentiment: bullish, bearish, neutral (on BTC direction)
- Timeframe: confirm it's about a 5-minute market, not longer
- Urgency: Is the tweet time-sensitive? (e.g., "expires in 2 min")
- Influencer check: Is the user a known crypto trader (high followers, blue check)?
- Volume: How many likes/retweets? (as proxy for reach)

Aggregate sentiment score: (bullish - bearish) / total, weighted by follower count.

Output hourly dashboard: sentiment trend over time. Correlate with actual Polymarket price moves?

Also track hashtags: #Polymarket, #BTC, #CryptoPrediction
```

---

## Agent 3: Hyperliquid Liquidation Alerts (MoonDev style)

**Task**: Real-time detection of Hyperliquid liquidation cascades.

**Prompt to Grok**:
```
Search X for tweets that mention:
- Hyperliquid liquidation
- HL liq
- Hyperliquid cascade
- BTC liquidation
- $BTC liq
- Crossing out liquidations

From crypto influencers like: @MoonDevOnYT, @Cabarossi, @CryptoKaleo, etc.

Collect:
- Liquidation size (if mentioned)
- Side (long or short)
- Time (timestamp of tweet)
- Any price context (BTC price before/after)

Goal: Build a real-time alert system that notifies when a cascade > $50k is reported.

Output: Real-time webhook or file with liquidation events. Include link to tweet for verification.

Also track if these cascades correlate with subsequent Polymarket 5-min market outcomes.
```

---

## Agent 4: Funding Rate & Perp Market Anomalies

**Task**: Detect unusual funding rate spikes or perp anomalies that might predict short-term moves.

**Prompt to Grok**:
```
Monitor tweets about:
- funding rate
- perpetual futures
- "funding is"
- "funding spike"
- "funding surge"
- "OI" or "open interest" spikes

Focus on: BTC, ETH, SOL.

Extract:
- Exchange mentioned (Binance, Bybit, Hyperliquid, OKX, etc.)
- Direction: positive funding (longs pay shorts = bullish skew) or negative?
- Magnitude if given (e.g., "0.1%")
- Time

Also watch for: "liquidation engine", "engine reset", "liquidation wave", "stop hunt"

Cross-reference: After a funding spike or perp anomaly, what happens to Polymarket 5-min BTC probability in next 5 minutes?

Build dataset: timestamp, funding_event, Polymarket_probability_before, Polymarket_probability_after, outcome.

Signal: funding spike contradictory to market direction might indicate reversal.
```

---

## Agent 5: Whale Wallet Activity Tracker

**Task**: Track known whale wallets on Polymarket (if addresses are shared).

**Prompt to Grok**:
```
Search X for wallet addresses (0x...) along with "Polymarket", "bet", "position", "trade".

If we can collect a list of addresses that have made large profitable bets (from tweets or from Simmer CopyTrader data), we can monitor them.

Your job: whenever a tweet mentions a wallet address AND Polymarket, record:
- wallet address
- timestamp
- action (bought YES, bought NO, closed)
- market approximate (BTC, ETH, etc.)
- size if mentioned

Create a database of "smart money moves".

Also: Use PolygonScan API (if available) to verify transaction history for those wallets? Might be out of scope but note if possible.

Goal: Can we copy these traders with a delay? Need to assess if their moves are predictive or just noise.
```

---

## Agent 6: News & Breaking Events Filter

**Task**: Identify breaking news that could affect BTC price in the next 5-15 minutes.

**Prompt to Grok**:
```
Monitor high-impact news sources:
- @CryptoNews, @CoinDesk, @TheBlock__, @Binance, @cz_binance
- Macro accounts: @NBCNewsBusiness, @ReutersTech, @Bloomberg
- Regulatory accounts: @SEC, @FTC, etc.

Look for keywords: "BTC", "Bitcoin", "ETF", "regulation", "inflation", "Fed", "interest rates", "China crypto", "adoption"

If a major news breaks (e.g., "SEC approves spot BTC ETF"), that will move BTC price instantly. Polymarket 5-min markets might lag.

Signal: If news is bullish BTC, but Polymarket YES price hasn't spiked yet, it's an opportunity.

But caution: markets may already price in expectation. We need speed.

Output: Breaking news events with timestamp and summary. Correlate with price action on Binance vs Polymarket to see lag.
```

---

## Agent 7: Influencer Recommendation Tracking

**Task**: See if crypto influencers are endorsing specific Polymarket bets.

**Prompt to Grok**:
```
Search for tweets where influencers explicitly recommend a Polymarket trade:

- "I just bet on..."
- "Load up on..."
- "This is free money"
- "Easy 10x" (though 5-min not 10x)
- "Bet YES on..."
- "Bet NO on..."

Track:
- Influencer handle
- Their follower count
- Market they recommend
- Side (YES/NO)
- Their confidence level (tone analysis)
- Whether they mention size?

We'll then track outcome of those markets to see if influencer recommendations have positive expectancy.

This is research: Are social signals predictive or just hype?

Collect at least 50 influencer-recommended trades to evaluate win rate.
```

---

## Agent 8: MoonDev Strategy Detection

**Task**: Specifically track MoonDevOnYT and anyone referencing his Hyperliquid strategy.

**Prompt to Grok**:
```
Target: @MoonDevOnYT and accounts replying to him or quoting his tweets.

Monitor for:
- Mentions of "Hyperliquid", "HL", "liquidation cascade", "5 min bot"
- Questions about his strategy
- Follow-up videos or streams
- People sharing results of using his method

Also search for: "moon dev data layer", "Hyperliquid Data Layer API", "moondevonyt"

Collect all tweets in this thread. Summarize new insights, modifications, user experiences.

Additionally, monitor GitHub for commits to moondevonyt/Hyperliquid-Data-Layer-API (via GitHub API or tweets about it). Track updates.

Goal: Stay up to date with MoonDev's latest developments; see if his edge holds or adapts.
```

---

## Agent 9: Simmer Skill Marketplace Signals

**Task**: Track which Simmer skills are performing well.

**Prompt to Grok**:
```
Search X for mentions of "simmer.markets", "Simmer SDK", "Polymarket skill".

Users often share:
- Skill slugs they're using
- Performance ("made $500 with this skill")
- Problems ("skill is down", "API errors")
- New skill launches

Collect:
- skill slug (e.g., "polymarket-fast-loop")
- Performance claims (numbers)
- User satisfaction signals
- Any patterns: which skill categories are profitable?

This helps us understand what others are using successfully; maybe we can replicate or improve.
```

---

## Agent 10: Polymarket Liquidity & Market Quality Reports

**Task**: Detect when Polymarket markets are broken, illiquid, or have anomalies.

**Prompt to Grok**:
```
Search for complaints about Polymarket:
- "liquidity dry"
- "wide spread"
- "order book empty"
- "market stuck"
- "cannot fill"
- "Polymarket down"

Also track: "new 5 min market added", "market closed", "market resolved early"

This helps the bot avoid trading in illiquid conditions. If multiple users report issues, we should pause trading.

Build a real-time "market health" score based on social volume and sentiment.
```

---

## Agent 11: Binance & Exchange Liquidations Correlation

**Task**: Cross-check Binance liquidations with Polymarket movements.

**Prompt to Grok**:
```
Search for tweets from liquidation tracking accounts:
- @binance_liquidations (bot accounts)
- @liqwatch
- @CryptoLiquidator
- Any account that tweets large liquidations in real-time

Collect:
- Exchange (Binance, Bybit, etc.)
- Symbol (BTC, ETH, etc.)
- Side (long/short)
- Size USD
- Timestamp

Then, we will manually (via our bot) check Polymarket 5-min markets for that symbol within next 5 minutes.

Goal: Can Binance liquidations predict Polymarket direction? If yes, that's an external data edge.
```

---

## Agent 12: Regulatory & Scam Alerts

**Task**: Watch for warnings about Polymarket that could affect our operation.

**Prompt to Grok**:
```
Monitor:
- "Polymarket blocked", "IP ban", "account suspended"
- "KYC required", "withdrawal delayed"
- "Polymarket exit scam", "rug"
- "SEC", "CFTC" actions against prediction markets
- Any geo-blocking news

If there's a major negative event, we may need to pause trading or withdraw funds.

Also track: positive news like "new liquidity", "institutional", "volume surge" – might indicate good environment.

Provide daily risk bulletin.
```

---

## Agent 13: General Crypto Price Action (for external data)

**Task**: Track BTC price movements and key levels that might influence 5-min markets.

**Prompt to Grok**:
```
From major crypto influencers (@CryptoCapo, @CryptoChad, @BTC_Archive, @Pentosh1, etc.):

Extract:
- Key price levels mentioned (e.g., "BTC at $85k resistance", "need to hold $84k")
- Technical analysis signals: "RSI oversold", "MACD cross", "VWAP"
- Sentiment: "bullish", "bearish", "neutral"

These human expectations might influence Polymarket traders, creating reflexive moves.

Our bot could use this as an additional sentiment signal if we can quantify it (e.g., number of bullet points saying "bullish").
```

---

## Implementation Notes for Grok Agents

- These agents should run continuously (or as often as Grok allows).
- Save output to files in `data/grok_alpha/YYYY-MM-DD.jsonl`
- Include source tweet URL and timestamp for verification.
- Deduplicate: same tweet may appear multiple times; use tweet ID as unique key.
- For each agent, also maintain a state file to track last processed tweet ID to avoid re-processing.

We will later ingest this data into our analysis pipeline to:
- Validate if whale wallets actually have predictive power
- Correlate social sentiment with price moves
- Detect liquidation events and feed them to our bot in near real-time

---

**Priority Agents**: 1 (Whale Tracker), 2 (BTC 5-min sentiment), 8 (MoonDev strategy), 11 (Binance liquidations). Start these four.

Lower priority: 3 (Hyperliquid liqs), 4 (funding rates), 5 (wallet activity), 6 (news), 7 (influencer recs), 9 (Simmer), 10 (liquidity alerts), 12 (regulatory), 13 (TA).

Deploy as many as you can. Each agent can be a separate script or thread. Use X API (if available) or rely on Grok's real-time feed (via his interface). Since we're using Hermes, we may need to simulate via web search? But the prompt is designed for Grok agents.

---

**To user**: You'll run these via your Gemini research or set up separate monitoring. We can later integrate the outputs into our bot's decision engine.