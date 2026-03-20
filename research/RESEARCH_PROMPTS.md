# Research Prompts for Gemini (and LLM Research Agents)

**Attach RESEARCH_CONTEXT.md before each query.**

---

## Category 1: Polymarket Ecosystem Understanding

### Prompt 1.1: Market Mechanics Deep Dive
```
Based on official Polymarket documentation (docs.polymarket.com, GitHub repos, etc), explain:

1. How are 5-minute and 15-minute markets structured? What exactly resolves them? (e.g., "Will BTC be above $85,000 at 12:40 PM ET?" vs "Up/Down" binary)
2. What are the exact fee structures? Is it truly 10% on every trade? Are there any fee discounts for volume?
3. How is liquidity provided? Is there an AMM or order book? What's the market maker system?
4. What are the minimum and maximum bet sizes?
5. Can markets be closed early or canceled? Under what conditions?
6. How are disputes handled? What if resolution is unclear?
7. What are the KYC/geographic restrictions? Can a bot operate from any VPS location?
8. What's the difference between trading via Simmer vs direct Polymarket API?

Provide links to official docs where possible.
```

### Prompt 1.2: API Capabilities & Limitations
```
Research the available APIs for Polymarket data access:

1. Simmer API (simmer.markets):
   - What endpoints are available for free?
   - Rate limits? Data freshness latency?
   - Does it provide full order book or just top of book?
   - Can we get historical resolved outcomes?
   - What's the difference between paper ($SIM) and live (USDC) modes?

2. Direct Polymarket CLOB (py_clob_client):
   - What methods are available? (get_markets, get_order_book, get_trades, etc.)
   - Rate limits? Authentication method?
   - Does it require wallet private key for read-only?
   - Can we get market resolution outcomes after they resolve?

3. Are there any unofficial APIs or WebSocket feeds?
   - Does Polymarket use GraphQL subscriptions for real-time updates?
   - Can we reverse-engineer the web app's network calls?

4. For each API, list:
   - Data latency (how stale is the data?)
   - Coverage (order book depth, trade history length)
   - Authentication requirements
   - Cost (free/paid)

Provide code examples if available.
```

### Prompt 1.3: Historical Data Availability
```
Investigate how to obtain historical data for backtesting:

1. Can we download past order book snapshots for resolved markets?
   - If yes: what's the retention period? How to access?
   - If no: what are our options? (e.g., start collecting now and wait)

2. Does Simmer provide historical market data via API?
   - Past probabilities?
   - Past order books?
   - Past trades?

3. Are there any public datasets or community projects that have archived Polymarket data?
   - GitHub repos with historical data
   - Dune Analytics queries
   - Kaggle datasets

4. What's the minimum viable backtest? (e.g., "we need 100 resolved 5-min BTC markets to get statistical significance")

Provide specific sources and access methods.
```

---

## Category 2: Existing Strategies Analysis (What Others Are Doing)

### Prompt 2.1: GitHub Bot Landscape
```
Review these GitHub repositories (and any others you find) and summarize:

1. ThinkEnigmatic/polymarket-bot-arena
   - Architecture: How many bots? How do they evolve?
   - What signal sources do they use?
   - What's their reported performance?
   - What are the key files to understand their strategy?

2. PolyScripts/polymarket-arbitrage-trading-bot-pack-5min-15min-kalshi
   - What "arbitrage" are they exploiting?
   - Cross-market between 5min/15min/1hr? How?
   - Are they claiming profitability? How?

3. angganurf/Automate-Polymarket-bot-BTC-5-15-min
   - How does it use Binance momentum?
   - What are the parameters: entry_threshold, min_momentum_pct, max_position?
   - What's the signal logic step-by-step?

4. lubluniky/polymarket-botkit (Rust)
   - What's the architecture? C core + Rust?
   - What risk management features?
   - Performance claims?

5. moondevonyt/Hyperliquid-Data-Layer-API
   - What data does it expose? (liquidations, positions, orderbook, funding)
   - How to run it? Docker? FastAPI?
   - What's the update frequency?
   - Rate limits?

6. Search for additional active repos (last commit < 3 months) related to "polymarket bot", "polymarket trading", "polymarket 5min". List top 5 stars and brief description.

For each repo, extract:
- Dependencies (what APIs/libraries they use)
- Configuration requirements (what keys/env vars)
- Strategy logic (where is the `analyze` or `decide` function?)
- Risk management (position sizing, stop losses)
- Known issues or limitations mentioned in README/Issues

Create a comparison table: Repo | Language | Edge | Simmer? | Live? | Stars | LastUpdated
```

### Prompt 2.2: MoonDev's Strategy Reconstruction
```
From MoonDevOnYT's content (YouTube videos, tweets, GitHub repos):
1. What is the exact "Hyperliquid liquidation cascade" edge?
   - Define: what constitutes a "cascade"? (size threshold, clustering rules)
   - What's the timing? How long after cascade do they enter?
   - What are the filters? (position proximity, funding rate, OI)
   - What's the direction of the bet? Opposite to cascade?

2. What parameters did he use in his stream?
   - Liquidation cluster thresholds: $25k-$100k, skip >$500k?
   - Position snapshot filters: min $10k value, within 15% of liq?
   - Timing: 2-3 minute delay, skip last 2 min of 5-min contract?
   - Bet sizing: $10-15 fixed or % of bankroll?

3. What hedging strategy? 80% hedge on Hyperliquid perps? In which direction?

4. Did he mention win rate, P&L, Sharpe? What were the backtest results?

5. What's his "Hyperliquid Data Layer API"? Is it open source? How to get data from it without his hosted version?
   - Is there a public demo endpoint?
   - Can we self-host? What's required?

6. Did he discuss risk management? Daily loss limits? Max position?

7. What modifications did he make during the 2.8-hour stream? Which parameters were tuned live?

8. Is the full bot code available anywhere? Or only the data layer?

Compile everything he's said into a single "MoonDev Strategy Spec" document.
```

### Prompt 2.3: Simmer Skill Marketplace
```
Explore Simmer's skill marketplace (simmer.markets/skills or similar).

1. List all available skills for Polymarket trading.
   - Which ones target 5-min or 15-min markets?
   - Which ones are free vs paid?

2. For the top 5 most popular skills (by volume or mentions):
   - What's their edge? (momancy, copy trading, etc.)
   - What parameters are configurable?
   - Are performance stats public? (win rate, total P&L)

3. Is the Simmer SDK open source? Where is it on GitHub?
   - How does it connect to Polymarket? (wallet handling, signing)
   - What's the safety model? (risk limits, kill switches)
   - Can we extend it or must we use their hosted API?

4. What's the "skills/building" documentation? How do you publish a skill?
   - Do we need to become a "skill developer"?
   - Are there revenue share models?

Summarize the Simmer ecosystem and where our bot would fit.
```

---

## Category 3: Data Structure & Collection

### Prompt 3.1: Order Book Signal Engineering
```
Research academic and industry literature on order book microstructure for short-term price prediction:

1. What is "order book imbalance" and how is it calculated?
   - Formula: (bid_size - ask_size) / (bid_size + ask_size)
   - Should we use top 5 levels or just top 1?
   - What time decay should apply? (imbalance changes every second)

2. What's the typical signal horizon? How long does imbalance predict direction?
   - 1 minute? 5 minutes? 30 seconds?
   - Provide citations or studies if available.

3. What thresholds are meaningful?
   - Imbalance > 0.6 considered "strong bid pressure"
   - Imbalance < -0.6 considered "strong ask pressure"
   - Are these optimal? Should they be dynamic (e.g., based on recent volatility)?

4. What about "order book slope" or "depth imbalance"? More advanced metrics.

5. How do we handle gaps? (e.g., sudden large market order that empties one side)

6. Are there known failure modes? (e.g., spoofing, quote stuffing)

Provide formulas, thresholds, and implementation notes.
```

### Prompt 3.2: Volume Spike Detection
```
Design a robust volume spike detection algorithm for Polymarket 5-min markets:

1. Input data: trade_history (list of {timestamp, price, size, side}) for last N minutes
2. We need to detect when volume exceeds "normal" by factor X
3. Challenges:
   - Market starts/stops: volume varies by time of day
   - Need adaptive baseline: maybe rolling 1-hour average?
   - Should weight recent trades more heavily?
4. Proposed logic:
   a. Compute rolling average volume over past 60 minutes (by 1-min buckets)
   b. Compute rolling standard deviation
   c. Signal if current 1-min volume > avg + 2*std OR > 3x avg
   d. Also require: at least 5 trades in that minute (not just one huge block)
5. After detecting spike, what direction signal?
   - Use trade sign imbalance (buy vs sell) during spike
   - Or use price direction following spike?
6. How long does the effect last? (Hold for 1-3 min?)
7. Avoid whipsaws: need confirmation?

Provide pseudocode and parameter recommendations.
```

### Prompt 3.3: Time Decay Patterns
```
Investigate how probability evolves as resolution time approaches:

1. For binary prediction markets (YES/NO), what is typical?
   - Does probability tend to move toward 0 or 1 as deadline nears?
   - Or does it stay near 50% until final seconds?
   - Is there a "resolution effect" where late traders overreact?

2. Can we find any studies or papers on prediction market resolution dynamics?

3. If we collect data: For each snapshot, record:
   - time_to_resolution (TTE) in seconds
   - current_probability
   - final outcome (after resolution)
   We can then compute: For markets that ended YES, what was the probability 5 min before? 1 min before? This tells us if there's drift.

4. Hypothesis: "Markets with probability near 50% in last 2 minutes are most volatile and unpredictable" → avoid trading them.

5. Another hypothesis: "If probability is 40% with 3 minutes left, and it's BTC-related, the actual price likely has 40% chance of being above strike" → This is just definition. But maybe there's lag: actual BTC price moves faster than market probability adjusts.

6. Design an analysis: bin markets by TTE (e.g., >10min, 5-10min, 2-5min, <2min). For each bin, compute:
   - Average absolute probability change per minute
   - Win rate if you always bet the direction of recent change (momentum)
   - Win rate if you bet opposite (mean reversion)

Summarize findings and recommendations for our bot.
```

---

## Category 4: External Data Integration

### Prompt 4.1: Binance Price Feed Integration
```
We want to compare Polymarket probability with actual BTC price momentum.

1. Get Binance USDT 1-minute klines (free WebSocket):
   - Symbol: BTCUSDT
   - Fields: open, high, low, close, volume
   - How to connect? Provide Python code using `websocket-client` or `ccxt`

2. Compute momentum metrics:
   - 1-min % change: (close_now - close_1min_ago) / close_1min_ago
   - 5-min % change (rolling)
   - RSI(14)
   - VWAP (volume-weighted average price) deviation

3. How to map BTC price change to Polymarket probability?
   - If BTC up 0.5% in last 5 min, Polymarket YES should be > 50%?
   - Actually: Polymarket is binary: above/below a specific price. Not directly % change.
   - But if the market is "Will BTC be above $85,000 at 12:40?" and current BTC is $84,500, then it needs +$500 (0.59%) in 5 min. So momentum matters.

4. Derive "required momentum" for each market:
   - Get strike price from question text
   - Get current BTC price from Binance
   - Compute (strike - current) / current = required % move in remaining time
   - Compare to recent 5-min momentum. If recent momentum > required, then probability should be high.

5. Build a signal: "BTC momentum suggests market is undervalued" if recent 5-min return exceeds required threshold by >0.3%

Provide formula and code to compute this signal.
```

### Prompt 4.2: Funding Rate Monitoring (If Available)
```
Research: Do funding rates on Polymarket or Hyperliquid provide an edge?

1. Polymarket: Does it have funding-like mechanism? (Not typical for CLOBs)
2. Hyperliquid: Yes, perpetuals have funding rates.
   - Can we access funding rates via MoonDev API?
   - What does high positive funding mean? (Longs paying shorts = bullish)
   - Does funding rate divergence between exchanges predict direction?
3. Idea: If Hyperliquid funding is extremely positive (e.g., 0.1% per hour) but Polymarket 5-min YES is only 52%, maybe bet NO (funding suggests crowded long, potential squeeze)?

Provide: Data source, API endpoint, interpretation guide, example.
```

### Prompt 4.3: Liquidation Data (Hyperliquid or Binance)
```
Investigate using liquidation data as a signal:

1. Where to get liquidation data?
   - Hyperliquid: `/api/liquidations/{timeframe}.json` from MoonDev API
   - Binance: `/fapi/v1/forceOrders` (public endpoint) for USDⓈ-M futures
   - Both free? Rate limits?

2. What constitutes a "liquidation cascade"?
   - Define: total USD value of liquidations in 5-min window > $X
   - Clustering: many liquidations of same side (longs or shorts) within 1-2 minutes
   - Significance: Is $50k cascade big? $500k? Ratio to typical volume?

3. Does cascade direction predict subsequent price movement?
   - After long liquidation cascade, price often continues down (liquidity hunt) or reverses (oversold)?
   - Need to find empirical evidence or cite studies.

4. Timing: How soon after cascade should we enter Polymarket?
   - Wait for cascade to fully execute? 1-2 minutes?
   - Avoid entering if cascade is ongoing (chaos)
   - Exit threshold: if price reverses 0.5%, maybe take profit

5. Provide backtest logic:
   - Historical data: get liquidations for past 3 months
   - Identify cascade events (algorithm)
   - Simulate: enter opposite direction on Polymarket 5-min market 2 min after cascade start
   - Hold until resolution (5 min total)
   - Compute win rate

Write the backtest pseudocode.
```

---

## Category 5: Statistical Validation

### Prompt 5.1: Hypothesis Testing Framework
```
Design a rigorous statistical testing framework for our edge hypotheses:

1. For each signal (e.g., imbalance > 0.6), we need to:
   - Generate trade signals on historical data
   - Match each signal with the actual outcome (YES wins or NO wins)
   - Compute win rate (correct signals / total signals)
   - Compute average profit per trade (including 10% fee)

2. How to avoid lookahead bias?
   - At time t, we only know data up to t. Cannot use future trades.
   - Our snapshots must be timestamped and ordered.

3. Statistical significance:
   - For N trades with win rate p, compute binomial confidence interval.
   - Null hypothesis: p = 0.5 (random)
   - Compute p-value. Reject null if p < 0.05 and win rate > 0.5.
   - But also consider economic significance: after 10% fee, break-even is 0.555... So we need p > 0.555 to be profitable.

4. Multiple testing problem:
   - If we test 20 hypotheses, some will show >55% by chance.
   - Use Bonferroni correction? Or simpler: require N > 50 and p > 0.6 for initial confidence.

5. Out-of-sample validation:
   - Split data into training (first 2/3) and testing (last 1/3)
   - Optimize parameters (if any) on training set only
   - Test on unseen data to verify edge persists

6. Walk-forward analysis:
   - Rolling window: train on 30 days, test next 7 days, roll forward
   - More robust than single train/test split.

Provide Python code structure for this validation framework. Include functions:
- `test_hypothesis(df, signal_func, outcome_col='outcome') -> results_dict`
- `compute_significance(n, wins) -> p_value, conf_interval`
- `walk_forward_analysis(df, window_days=30, test_days=7) -> performance_over_time`
```

### Prompt 5.2: Risk of Ruin & Position Sizing
```
Research Kelly Criterion and risk management for binary outcomes:

1. Given:
   - Win rate p (e.g., 0.60)
   - Average win size as fraction of bet: W (e.g., if you bet $10 and win, you get $10 * 0.9 after fee = $9 net profit, so W = 0.9)
   - Average loss size as fraction of bet: L (e.g., lose entire $10, so L = 1.0)

2. Kelly fraction: f* = (p * W - (1-p) * L) / (W * L)
   - If f* > 0, positive edge.
   - Bet f* of bankroll each round for maximal long-term growth.
   - In practice, use half-Kelly (f*/2) for safety.

3. Example: p=0.60, W=0.9, L=1.0
   f* = (0.6*0.9 - 0.4*1.0) / (0.9*1.0) = (0.54 - 0.4)/0.9 = 0.14/0.9 = 0.1556
   So Kelly says bet 15.6% of bankroll per trade. That's huge! Requires high conviction.

4. But our edge is probably smaller. Let's say p=0.56, W=0.9, L=1.0:
   f* = (0.56*0.9 - 0.44) / 0.9 = (0.504 - 0.44)/0.9 = 0.07/0.9 = 0.0778 (7.8%)
   Still high. But real edge likely even smaller.

5. Reality check: Polymarket 5-min markets have high variance. Even with 60% win rate, you can have 5 losses in a row.
   - Risk of ruin with Kelly: if you hit a bad streak, you draw down fast.
   - Use fractional Kelly (1/4 or 1/8) for robustness.

6. Also consider:
   - Minimum bet size (maybe $1)
   - Maximum bet size (liquidity constraint, maybe $10-20)
   - Daily loss limit (stop after -$X)

7. Write a Python function to compute optimal bet size given:
   - bankroll
   - win_rate
   - avg_win_pct (net after fee)
   - avg_loss_pct (usually 1.0)
   - kelly_fraction (default 0.5)
   - min_bet, max_bet

   Return: recommended bet size in $.

8. Also compute risk of ruin for a given bet fraction over 100 trades? Probably too complex, but we can estimate.

Provide formula and code.
```

### Prompt 5.3: Execution Slippage & Liquidity
```
Analyze the impact of liquidity on our ability to execute trades:

1. For a typical BTC 5-min market on Polymarket:
   - What's the typical best bid/ask size? (from collected data)
   - Can we reliably get $10 filled? $50? $100?
   - How does size affect price? (If we try to buy $100 YES, we might walk up the book, paying 0.60 -> 0.61 -> etc.)

2. Slippage model:
   - Assume order book depth: at best bid 0.61, size $200; next bid 0.60 size $500; etc.
   - If we buy $X, we fill at average price higher than best bid.
   - Compute expected slippage as a function of order size.

3. Market impact timing:
   - We have only 5 minutes total! If we detect signal and place order, we might miss 1 minute due to latency.
   - How fast can we execute? (API latency + order propagation)
   - By the time our order lands, has the price moved?

4. What's the typical order book update frequency? (Does it change every second? Every 5 seconds?)

5. Mitigation:
   - Use limit orders at mid-price? Might not fill.
   - Use market orders with size limits? Guarantee fill but pay slippage.
   - Split orders? Not feasible in 5-min window.

6. Backtest adjustment: In historical data, we assume we could fill at mid-price + half spread. Realistically, maybe worse.

Provide guidelines: maximum position size per market based on observed liquidity. Suggest conservative sizing if liquidity uncertain.
```

---

## Category 6: Technical Implementation

### Prompt 6.1: Simmer SDK Best Practices
```
We'll use Simmer SDK for paper trading and possibly live.

1. Installation: `pip install simmer-sdk`? What's the exact package name?

2. Authentication:
   - How to securely store API key?
   - How to handle claim flow? (Once claimed, can we trade live immediately?)

3. Trading workflow:
   - How to find active 5-min BTC markets using SDK?
   - How to get market context (probability, TTE, warnings)?
   - How to place an order: `client.trade(market_id, side, size, reasoning)`?
   - Does it automatically handle position sizing? Can we limit to $X per trade?

4. Error handling:
   - What exceptions might be raised? (Insufficient balance, market closed, rate limit)
   - How to retry? Exponential backoff?

5. Paper vs Live:
   - How to switch between `sim` and `polymarket` venues?
   - Is there a test mode where orders are simulated but not executed?
   - How to reset paper trading balance?

6. Position monitoring:
   - How to check open positions?
   - How to cancel orders?
   - How to get P&L?

7. Webhooks or callbacks? Or do we poll?

Provide a complete example script: "Buy $10 YES on the first active BTC 5-min market with probability < 0.45, with reasoning."
```

### Prompt 6.2: Direct Polymarket (py_clob_client) Deep Dive
```
If we need more control than Simmer, we'll use py_clob_client directly.

1. Setup:
   - How to install? `pip install py-clob-client`
   - What's the wallet setup? Need private key for read? For write?
   - How to derive API credentials? (`client.create_or_derive_api_creds()`)
   - How often do credentials expire?

2. Market discovery:
   - `client.get_markets()` returns what fields? How to filter to 5-min BTC?
   - Can we query by resolution time window?

3. Order book:
   - `client.get_order_book(token_id)` structure? (bids: list of Order objects with price, size)
   - How current is the order book? Latency?

4. Placing orders:
   - `client.create_order(OrderArgs(...))` what are required fields?
   - How to specify buy YES vs buy NO? (different token IDs)
   - Market vs limit? Which is better for 5-min windows?
   - What's the fee structure? 10% taken from the bet amount or from winnings?

5. Order status:
   - How to check if order filled? `client.get_orders()`?
   - How to cancel? `client.cancel_order(order_id)`

6. Balance & allowance:
   - `client.get_balance_allowance()` returns USDC balance and approved amount.
   - Need to approve USDC spending once? How?

7. Error codes: common failures (insufficient balance, market closed, price moved, rate limit)

Provide a complete example: "Find active BTC 5-min market, read order book, place $10 market order on YES side, check fill status."
```

### Prompt 6.3: Infrastructure & Reliability
```
Design a production-ready bot infrastructure:

1. Process management:
   - How to keep the bot running 24/7? (systemd, supervisor, docker)
   - How to auto-restart on crash?
   - How to handle updates? (code deploys without losing state)

2. State persistence:
   - Need to store: current positions, P&L, learning data, trade history
   - SQLite vs PostgreSQL? For low data volume, SQLite is fine.
   - Schema design: tables for trades, positions, signals, metrics
   - How to handle crashes? (atomic commits, journaling)

3. Monitoring:
   - Health check endpoint? (Streamlit dashboard can serve)
   - Logging: structured JSON logs to file, rotated daily
   - Metrics: number of signals per hour, error rate, latency
   - Alerting: Telegram on errors, daily P&L summary

4. Deployment:
   - Dockerfile? docker-compose with separate services: collector, analyzer, executor?
   - Or single process with threading?
   - Environment variables for secrets (never commit keys)

5. Security:
   - Who can access the VPS? SSH key only?
   - How to store wallet private key? (bashrc? separate file with 600 perms)
   - What if VPS is compromised? Limit wallet to $100 max.

6. Testing:
   - Unit tests for signal generation
   - Integration test with mock APIs
   - Dry-run mode: log what would have been done without executing

7. Backups:
   - Daily backup of database and logs to remote? (S3, Dropbox)
   - Git for code only (not data)

Provide a deployment checklist and architecture diagram (text description is fine).
```

---

## Category 7: Risk Management & Compliance

### Prompt 7.1: Regulatory & Platform Risks
```
Research legal and platform-specific risks:

1. Is automated trading on Polymarket allowed?
   - Check Terms of Service: Any clauses about bots?
   - Do they detect and ban bots? How? (IP rate limits, behavior analysis)
   - Have there been known cases of account bans for botting?

2. Geographic restrictions:
   - Which countries are blocked from Polymarket? (US? Canada? Others)
   - If our VPS is in a restricted country, does that matter? (IP-based detection)
   - VPN/proxy solutions? Risks?

3. KYC:
   - Polymarket requires KYC for withdrawals above certain amount?
   - If we use a small hot wallet with $100, maybe no KYC needed.
   - But if we withdraw to exchange, might trigger KYC.

4. Tax implications:
   - Is prediction market trading considered gambling? Tax treatment varies.
   - Need to track P&L for tax reporting? (We'll log all trades)

5. Smart contract risk:
   - Polymarket uses a set of smart contracts on Polygon.
   - Are they audited? Any past hacks?
   - If we connect wallet, what approvals do we give? Can we revoke?

6. Simmer's role:
   - Is Simmer a middleman that reduces counterparty risk?
   - What if Simmer shuts down? Can we withdraw positions?
   - Simmer's Terms of Service regarding automation?

Summarize key risks and mitigation strategies.
```

### Prompt 7.2: Drawdown & Position Sizing Math
```
Model the risk of ruin given various position sizing strategies:

1. Scenario:
   - Starting bankroll: $1000
   - Per-trade bet: X% of bankroll (e.g., 1%, 2%, 5%)
   - Win rate: p (e.g., 0.56, 0.60)
   - Net win multiplier: W = 0.9 (after 10% fee)
   - Net loss multiplier: L = 1.0 (lose entire bet)
   - Number of trades: N = 100

2. Simulate many sequences of N trades with independent Bernoulli(p) outcomes.
   - Track bankroll evolution.
   - Record maximum drawdown, final bankroll, probability of ruin (bankroll < $100).

3. Compare:
   - f=1% Kelly? (full Kelly)
   - f=0.5% (half Kelly)
   - f=0.25% (quarter Kelly)
   - Fixed $10 bet (not %)

4. Also model streaks:
   - What's the probability of 5 consecutive losses? (0.44^5 = 1.6% for p=0.56)
   - With 100 trades, almost certain to see some streaks.
   - Bet sizing must survive losing streaks without dropping below threshold.

5. Provide:
   - Table showing expected final bankroll after 100 trades for various f
   - Probability of ruin (bankroll < $100) for each f
   - Recommended f given our edge uncertainty (use half or quarter Kelly to be safe)

6. Implementation in backtester:
   - At each step, compute current bankroll.
   - Bet size = min(max_bet, bankroll * f)
   - But also never exceed a fixed fraction of "confidence" from signal? Could vary bet size by signal strength.

Provide Python simulation code and analysis.
```

---

## Category 8: Dashboard & Monitoring

### Prompt 8.1: Streamlit Dashboard Design
```
Design a Streamlit dashboard for our bot:

Pages:
1. **Overview**
   - Current active markets count
   - Bot status (running/stopped, last check)
   - Today's P&L (paper or live)
   - Current bankroll
   - Recent signals table (last 20 with timestamp, market, side, confidence, outcome if resolved)

2. **Market Explorer**
   - List of current active BTC 5-min markets
   - For each: question, resolution time, current probability, spread, volume
   - Color coding: strong signals (imbalance > 0.6) highlighted green/red
   - Option to manually inspect order book

3. **Signals**
   - Live feed of generated signals
   - Filter by side (YES/NO)
   - Show confidence and reasoning
   - Allow manual override (force trade/cancel)

4. **Positions**
   - Current open positions (from Simmer or direct)
   - Current profit/loss (unrealized)
   - Time to resolution
   - Buttons to close early

5. **Backtesting**
   - Upload historical data file
   - Select strategy (imbalance, volume spike, etc.)
   - Adjust parameters via sliders
   - Show results: equity curve, win rate, Sharpe, max drawdown
   - Export results

6. **Settings**
   - API key configuration (masked)
   - Risk limits: max position, daily loss
   - Trading mode toggle (paper/live)
   - Start/stop bot

Layout: Use st.sidebar for global controls. Use st.metric for KPI cards. Use st.dataframe for tables. Use st.line_chart for equity curve.

Provide a complete `app.py` structure with these pages.
```

### Prompt 8.2: Alerting & Notification System
 ```
Design a Telegram alert system:

1. Scenarios that need alerts:
   - Error: API failure, cannot fetch markets
   - Trade executed: "Bought $10 YES on BTC 5-min expiring 12:45 (probability 0.43)"
   - Position closed: "Position closed: +$4.20" or "-$9.50"
   - Daily summary: "Today: 12 trades, 7 wins, 5 losses, net +$12.50"
   - Critical: Daily loss limit reached, bot stopped
   - Warning: Signal confidence very low (<0.45)
   - System: Bot started/stopped, configuration changes

2. Implementation:
   - Use python-telegram-bot or simple requests to Bot API
   - Format messages with emojis: ✅ win, ❌ loss, ⚠️ warning
   - Include market details and reasoning
   - Throttle alerts: don't spam if many trades per minute. Batch them.

3. Configuration:
   - TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env
   - Which alerts are enabled? (config flags)
   - Quiet hours? (e.g., no alerts between 2-6 AM)

4. Provide a `alerts.py` module with:
   - `send_telegram(message, level='info')`
   - `send_daily_summary(trades_today)`
   - `send_error(exception)`

5. Test: How to verify bot is working? Maybe send a test alert on startup.

Write the module code.
```

---

## Category 9: Advanced Ideas (Optional)

### Prompt 9.1: Machine Learning Approach (If Data Sufficient)
```
If we gather enough data (thousands of resolved 5-min markets), could we use ML?

1. Feature engineering:
   - Order book features: imbalance, spread, depth at 5 levels
   - Volume features: recent trade count, volume sum, buy/sell ratio
   - Price features: mid-price, recent 1-min/5-min returns, RSI, volatility
   - Time features: hour of day, day of week, TTE
   - External: Binance momentum (if using)

2. Target: outcome (YES wins = 1, NO wins = 0)

3. Model selection:
   - Logistic regression (baseline)
   - Gradient boosting (XGBoost, LightGBM)
   - Random forest (robust to noise)

4. Training/validation:
   - Strict time-based split: train on older data, test on newer (no shuffling)
   - Avoid lookahead: features only from time t or earlier
   - Cross-validation with rolling origin

5. Evaluation:
   - Accuracy, precision, recall, F1
   - But more important: expected value per bet (using predicted probabilities)
   - Compare to simple threshold rules (e.g., imbalance > 0.6) - is ML better?

6. Implementation:
   - Use scikit-learn
   - Pipeline: imputer (for missing) → scaler → model
   - Hyperparameter tuning with Optuna? Maybe overkill.

7. Caution: Overfitting risk high with limited data. If we have <500 samples, ML is probably not reliable.

Provide code template: `train_model(df, features, target)` returning trained model and evaluation metrics.
```

### Prompt 9.2: Multi-Strategy Ensemble
```
How to combine multiple signals into a single decision:

1. Signals:
   - S1: Order book imbalance (threshold 0.6)
   - S2: Volume spike + direction
   - S3: Binance momentum divergence
   - S4: Time-of-day filter (only trade during high liquidity hours)
   - S5: Copy whale (if we can get that data)

2. Problem: Each signal has different confidence and may conflict.

3. Ensemble methods:
   - Simple: Take majority vote (if ≥2 signals say YES, bet YES)
   - Weighted: Assign weights based on backtest win rate. Compute weighted sum.
   - Machine learning: Logistic regression to combine signal outputs (as features) → outcome
   - Bayesian: Update prior 0.5 based on each signal's likelihood ratio

4. Position sizing variation:
   - If strong consensus (all signals YES), bet larger (up to Kelly fraction)
   - If weak (2-1 split), bet smaller (half size)
   - If conflict (2 vs 2) or low individual confidence, skip

5. Provide Python code:
   - `combine_signals(signal_list, weights=None) -> (side, confidence)`
   - `size_from_confidence(confidence, bankroll, kelly_fraction) -> bet_size`

6. Also consider: correlation between signals. If S1 and S3 are highly correlated, don't double-count.

Write the ensemble logic module.
```

---

## Category 10: Real-World Constraints

### Prompt 10.1: Latency & Execution Speed
```
Calculate realistic latency budget for our bot:

1. Steps from signal detection to order placed:
   - Detector reads data (Simmer API response) → 200ms?
   - Signal computation (imbalance calc, checks) → 10ms
   - Risk check (balance, limits) → 5ms
   - Order creation (py_clob_client) → 100ms? (network to Polygon)
   - Transaction signing (if external wallet) → 200ms?
   - Submit to Polymarket RPC → 500ms?
   Total: ~1000ms (1 second)

2. In 5-minute window, 1 second is acceptable (less than 0.5% of window).

3. But: data freshness. Simmer API might have 2-5 second delay. That could be critical if cascade happens fast.

4. Direct CLOB: maybe fresher? Does Polymarket provide WebSocket? If yes, we should subscribe to order book updates instead of polling.

5. Research: Does py_clob_client support WebSocket? Or only REST polling?

6. Worst case: We detect signal at T-3:00, place order at T-2:55. But market may have moved in those 5 seconds. Should we limit order with price cap? Or use market order and accept slippage?

7. Provide recommendations:
   - Use WebSocket if available, otherwise poll every 2-3 seconds (but watch rate limits)
   - Pre-warm connections (keep TCP socket open)
   - Run bot on same region as Polygon RPC (e.g., VPS in Europe? US?)
   - Use asynchronous I/O (asyncio) to reduce overhead

Write a "Performance Optimization" checklist.
```

### Prompt 10.2: Cost Analysis
```
Calculate total cost of running this bot:

1. Infrastructure:
   - VPS cost: $5-10/month for decent box (2 vCPU, 4GB RAM)
   - Total: ~$120/year

2. APIs:
   - Simmer: Free (no cost)
   - Binance: Free (public endpoints)
   - Hyperliquid: Free (MoonDev API open source, can self-host)
   - Polygon RPC: Free (public endpoints) or Alchemy/Infura free tier
   Total: $0

3. Potential losses:
   - Trading capital: $300-400 (risk: could lose some or all)
   - Expected win rate? If edge is 55%, EV per $10 bet = (0.55*$9) - (0.45*$10) = $4.95 - $4.50 = $0.45 profit per bet? Wait, that's wrong: if win, you get $10*0.9 = $9 profit? Actually: you bet $10, if win you receive $10 * (1/price - 1)? Let's recalc:
     Polymarket: You buy YES at $0.60 for $10 → you get 10/0.6 = 16.667 shares. If YES wins, each share worth $1 → $16.667, profit = $6.667 (66.67% return). If NO wins, shares worthless, loss = $10. So win_multiplier = 1/price - 1. But they said 10% fee: actually fee is taken from the pool? Let's check: On winning, you get $1 per share, but you paid $0.60 per share? Actually token price is probability. So if you buy at $0.60 and it resolves YES, you get $1 per share (100/60 = 1.666x). That's 66.7% gross profit. If fee is 10% on every trade, maybe they take 10% from the pool? Need exact.
   But Simmer docs said "10% fee". Need to clarify: Fee is deducted from winnings? Or from stake? Typically: if you bet $10 and win, you get $10 * (1/price) * 0.9? Or $10 - 10% fee on stake? Must research.

   Let's assume worst: You risk $10 to win $9 net (if YES at $0.50, you get 2x but fee 10%? Actually complicated.)
   We'll need accurate P&L calculation from Simmer docs.

4. Give break-even analysis:
   - If we bet $10 each, need to win 55.6% to break even (if net win = $9, loss = $10)
   - If we can achieve 60%, EV = 0.6*9 - 0.4*10 = 5.4 - 4 = $1.40 per bet → $140 per 100 bets

5. How many bets per day? 5-min BTC markets: maybe 50-100 per day if always active.

6. Gross profit potential: If edge real, could make $50-200/day. But that won't last as edge decays.

7. Provide realistic cost/profit projections.

Write a simple spreadsheet-like analysis with different scenarios.
```

---

## Category 11: Research Data Sources

### Prompt 11.1: Academic Papers on Prediction Markets
```
Find academic literature on prediction market efficiency, especially short-term:

1. Search terms: "prediction market microstrastructure", "short-term prediction markets", "binary options efficiency", "order flow in prediction markets"

2. Key papers to summarize:
   - "The Wisdom of Crowds" vs "Behavioral biases in prediction markets"
   - Papers on liquidity and fee impact
   - Any papers specifically on Polymarket or similar platforms (Augur, Omen, Kalshi)?

3. Key findings:
   - Are short-term (5-min) markets efficient? Or do they have persistent inefficiencies?
   - What are typical bid-ask spreads?
   - Do large trades move prices?
   - Is there mean reversion?

4. Provide citations and 1-sentence takeaways for each relevant paper.

5. Also look for industry reports: "State of Prediction Markets 2025" etc.

Summarize what academic research says about our potential for edge.
```

### Prompt 11.2: Crypto Trading Literature
```
Bring in knowledge from crypto spot/derivatives trading that may apply:

1. Order book imbalance strategies in traditional markets ( equities, forex). Does research show predictive power? For how long?

2. "Liquidity hunting" or "stop hunts" in crypto futures. Could that relate to Hyperliquid liquidations?

3. Funding rate arbitrage: When funding rates diverge between exchanges, does that predict spot price?

4. Copy trading: Does following top traders work? Or is it just herding?

5. Short-term momentum vs mean reversion: Which is dominant at 5-minute horizon on BTC?

6. Provide links to well-known trading blogs (AlgoTradingBlog, Sliced Grapes, etc.) that have studied these phenomena.

Extract actionable insights for our bot.
```

---

## END OF PROMPTS

**Instructions for Gemini:**
For each prompt above, you are to produce a comprehensive research report. Cite sources where possible. Provide code snippets where relevant. Include tables, formulas, and diagrams (ASCII if needed). Be objective: if evidence is weak, say so.

Focus on Prompts 1-7 first (core context). Prompts 8-11 are lower priority but useful for completeness.

All outputs should be in Markdown format, saved as separate files in the research/ directory with appropriate naming (e.g., `01_polymarket_mechanics.md`, `02_api_capabilities.md`, etc.)

Attach the RESEARCH_CONTEXT.md file to each query for full context.

Begin.