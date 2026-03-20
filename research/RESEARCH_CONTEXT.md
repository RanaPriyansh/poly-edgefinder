# Research Context: Polymarket 5/15-Min Crypto Bot

## Mission Statement
Build a profitable automated trading bot for Polymarket's 5-minute and 15-minute cryptocurrency prediction markets (primarily BTC). We aim to discover a statistical edge through data analysis, not copy YouTube strategies.

## Current State (What We Know)

### Market Mechanics
- **Platform**: Polymarket (polygon-based, USDC)
- **Markets**: Binary YES/NO on "Will BTC be above X price at time Y?" or "Up/Down" direction bets
- **Time windows**: 5-minute and 15-minute intervals (fast markets)
- **Fee structure**: 10% on all trades (confirmed in Simmer docs)
- **Break-even win rate**: Need >55% to overcome 10% fee on even-money bets
- **Liquidity**: Varies by market; some have tight spreads, others wide

### Existing Strategies Observed (Not Necessarily Validated)
1. **Bot Arena (ThinkEnigmatic)**
   - 4 competing strategies: momentum, mean reversion, sentiment, hybrid
   - Bayesian learning by feature (price bucket, hour, momentum)
   - Copy trading whales (filters: skip NO bets, entry $0.40-$0.65, avoid 22:00 UTC)
   - Uses Simmer SDK for paper trading
   - Risk limits: $10/trade live, $50/day loss per bot

2. **MoonDev's Hyperliquid Strategy** (unverified claims)
   - Edge: Hyperliquid liquidation cascades → bet opposite direction on Polymarket 5-min
   - Filters: $25k-$100k cluster, positions within 15% of liq, 2-3min delay after cascade
   - Additional: Funding rate differentials, OI spikes
   - Claimed P&L: 100-245% on runs (unverified)
   - Hedge: 80% of position as perp on Hyperliquid
   - Uses proprietary Hyperliquid Data Layer API (open sourced)

3. **PolyScripts Pack** (commercial-ish)
   - Arbitrage between 5min, 15min, 1hr Polymarket markets
   - Copy trading integration
   - Cross-market (Polymarket vs Kalshi)

4. **Simmer FastLoop** (template skill)
   - Simple momentum: Binance 5-min price change vs Polymarket odds
   - Entry threshold: 0.05 (5¢ divergence), momentum threshold: 0.5%
   - Default bet: $5

### Our Current Tools
- **Data layer**: Simmer API (free, with $SIM sandbox) + Direct Polymarket CLOB (py_clob_client)
- **External data**: Binance WebSocket (free, no key), CoinGecko (free)
- **Analysis**: Python (pandas, numpy), Jupyter notebooks
- **Storage**: SQLite (local) → later PostgreSQL if needed
- **Infrastructure**: VPS (213.199.32.246) for 24/7 operation
- **Wallet**: 0x38f15fDfcd8D19E0B152D8bc7f0779A875da516E (Polymarket)
- **Budget**: $300-400 CAD initial capital, separate hot wallet

### Assumptions to Validate
- 5-min markets exist frequently enough (how many per day?)
- Order book data is accessible and timely (Simmer may lag; direct CLOB may be better)
- Liquidity sufficient to enter/exit at reasonable prices
- Fee of 10% is unavoidable (Polymarket takes 10% on every trade)
- We can get historical resolved market outcomes to backtest

### Unknowns (Need Research)
- What's the actual distribution of probabilities? Do markets cluster near 0/1 or stay near 50%?
- How many BTC 5-min markets per day? When are they most active?
- What are typical spreads? How does liquidity vary by time of day?
- Does order book imbalance actually predict price direction? For how long?
- Do external price moves (Binance) lead or lag Polymarket?
- Are there exploitable patterns around market resolution (last minute)?
- What's the optimal position sizing for 55-60% win rate?
- What are the best risk management practices specific to prediction markets?
- Are there any regulatory or account restrictions we need to consider?

---

## Research Objectives

### Phase 1: Descriptive Analysis (What Is)
- Characterize the Polymarket 5-min BTC ecosystem
- How many markets? Volume distribution? Spread distribution?
- When are markets most liquid?
- What's the typical resolution outcome distribution? (Is YES more likely than NO? Probably 50/50 if efficient)

### Phase 2: Hypothesis Generation (What Could Be)
- Test 10+ plausible signals (order book imbalance, volume spike, time decay, etc.)
- Identify which signals show correlation with outcomes
- Estimate effect size and statistical significance

### Phase 3: Backtesting (What Works)
- Simulate trades on historical data (paper trading)
- Calculate win rate, Sharpe ratio, max drawdown
- Verify edge persists out-of-sample

### Phase 4: Bot Implementation (What We'll Trade)
- Convert best hypothesis into automated trading rules
- Add risk management (position sizing, daily limits)
- Build monitoring dashboard

---

## Data We Will Collect

### Primary Sources
1. **Simmer API**
   - `/api/sdk/markets` - active markets list
   - `/api/sdk/context/{market_id}` - current probability, volume, TTE, warnings
   - `/api/sdk/briefing` - aggregated updates
   - `$SIM` paper trading results

2. **Polymarket Direct (py_clob_client)**
   - `client.get_markets()` - all markets
   - `client.get_order_book(token_id)` - full order book
   - `client.get_trades(token_id)` - recent trades
   - `client.get_balance_allowance()` - balance checks

3. **Binance**
   - WebSocket: `wss://stream.binance.com:9443/ws/btcusdt@kline_1m`
   - REST: `/api/v3/klines` for historical 1-min candles
   - No API key needed for public endpoints

4. **Hyperliquid Data Layer** (MoonDev's open source)
   - `/api/liquidations/5m.json`
   - `/api/positions/all.json`
   - `/api/orderbook/BTC`
   - Can self-host or use API key if rate-limited

### Data Schema (Per Snapshot)
```json
{
  "timestamp": 1234567890.123,
  "datetime": "2026-03-20T12:34:56Z",
  "market_id": "0xabc...",
  "question": "Will BTC be above $85,000 at 12:40 PM ET?",
  "resolution_time": "2026-03-20T17:40:00Z",
  "current_probability": 0.62,
  "best_bid_price": 0.61,
  "best_ask_price": 0.63,
  "best_bid_size": 1234.5,
  "best_ask_size": 987.6,
  "imbalance": 0.15,
  "spread": 0.02,
  "volume_24h": 45678.9,
  "time_to_resolution_seconds": 320,
  "outcome": null,  // Will fill after resolution: 1 (YES) or 0 (NO)
  "binance_price": 85678.90,  // Optional external price
  "binance_momentum_5min": 0.0023  // Optional 5-min % change
}
```

---

## Expected Deliverables from Research

For each hypothesis tested, we need:
1. **Data sample size** (N trades)
2. **Win rate** (before and after 10% fee)
3. **Average win size** ($ per $10 bet)
4. **Average loss size** ($ per $10 bet)
5. **Expectancy** = (win_rate * avg_win) - ((1-win_rate) * avg_loss)
6. **Sharpe ratio** if multiple trades per day
7. **Statistical significance** (p-value or confidence interval)
8. **Optimal position size** (Kelly criterion if applicable)

---

## Output Format

All research findings should be documented in markdown files with:
- Clear hypothesis statement
- Data used (date range, number of samples)
- Methodology (how tested)
- Results (tables, charts)
- Conclusion (keep/discard/refine)

---

## What We're NOT Doing

- NOT building a copy-trading bot (too much trust in others)
- NOT trying to predict 60+ second ahead with ML overkill
- NOT using complex neural networks (lack of data)
- NOT holding positions into last 2 minutes (chaotic)
- NOT risking more than 1-3% per trade
- NOT ignoring risk management

---

## Success Criteria

- **Minimum**: Find ONE hypothesis with >55% win rate on at least 50 historical trades
- **Stretch**: Two independent signals that each have >58% win rate
- **Ultimate**: Combine signals into ensemble with >60% win rate

---

## Timeline

- **Week 1**: Data collection running, gather at least 3-5 days of continuous snapshots
- **Week 2**: Exploratory analysis, generate initial hypotheses, test 3-5 most promising
- **Week 3**: Backtest refined hypotheses, pick 1-2 winners
- **Week 4**: Build simple bot, paper trade for 1 week
- **Week 5**: Live small scale, evaluate

---

**This document provides context for all research prompts. Attach this to every Gemini/Grok query so they understand the full picture.**