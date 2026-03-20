# Research Plan: Finding Edges in Polymarket 5/15-Min Crypto Markets

## Context
Polymarket 5-minute and 15-minute binary options on BTC (and potentially ETH, SOL) resolve based on the price at a future timestamp. The market trades in probabilities (0-1, representing % chance).

**Key questions:**
- What drives short-term price movements in these markets?
- Are there predictable patterns?
- Can we find signals that have >55% win rate?
- What's the maximum theoretical edge given fees?

## Polymarket Fee Structure
- **10% fee** on all trades (mentioned in Simmer docs: "Fast markets carry Polymarket's 10% fee")
- Means you need >55% win rate just to break even on even-money bets
- If you bet YES at $0.60 and it wins, you get $0.60 → $0.60 / $1.00 bet = -10% net
- Break-even: need to win 1.11x what you lose (including 10% fee)

## Data We Can Collect

### From Simmer API (Free, recommended for start)
- Market list: active/past markets
- Order book snapshots (Simmer provides context)
- Trade history
- Position tracking

### From Polymarket Direct (py_clob_client)
- Order book (bids/asks)
- Recent trades
- Market metadata (resolution time, question)

### External Price Feeds
- Binance BTC/USDT 1-minute candles (free WebSocket)
- CoinGecko spot price (free REST)
- Compare Polymarket probability to actual BTC price momentum

### Custom Data
- Order book imbalance: (bids_size - asks_size) / (bids_size + asks_size)
- Mid-price: (best_bid + best_ask) / 2
- Spread: best_ask - best_bid
- Volume in last N trades
- Time to resolution (TTE)

## Hypotheses to Test

### H1: Order Book Imbalance Predicts Short-Term Direction
- **Rationale**: If bids are much larger than asks, buying pressure may push price up
- **Signal**: imbalance > +0.6 (strong bid pressure) → bet YES
- **Signal**: imbalance < -0.6 (strong ask pressure) → bet NO
- **Time horizon**: next 1-3 minutes
- **Expected edge**: maybe 55-60% win rate

### H2: Volume Spike Precedes Continuation
- **Rationale**: Large trades may indicate institutional movement
- **Signal**: Volume in last 30s > 2x average → follow the direction of those trades
- **Edge**: if large trades are predominantly buying, price tends to continue rising short-term

### H3: Time Decay Creates Mean Reversion Near 50%
- **Rationale**: As resolution approaches, probability tends to move toward 0 or 1. In the middle, it's more volatile.
- **Signal**: When market is at exactly 50% with <5 min left → bet whichever side had recent momentum?
- Or: Avoid markets with <2 min left (too noisy)

### H4: Cross-Exchange Arbitrage (Polymarket vs. Binance)
- **Rationale**: Polymarket probability vs actual BTC 5-min return might diverge
- **Signal**: If BTC up 1% in last 5 min on Binance but Polymarket YES < 0.55 → bet YES
- **Edge**: Prediction markets lag spot price moves

### H5: Liquidity Patterns
- **Rationale**: Tight spreads indicate efficient pricing (no edge). Wide spreads may have mispricing.
- **Signal**: Skip markets with spread > 5¢
- Or: Bet when spread suddenly widens (someone unloaded large order at bad price)

### H6: Resolution-Time Bias
- **Rationale**: Many traders check positions in morning/evening. Human psychology may create patterns.
- **Signal**: Test win rates by hour of day (ET)
- Hypothesis: Certain hours have better/worse performance

### H7: Market-size Filtering
- **Rationale**: Very small markets (<$1k volume) may be manipulated or illiquid
- **Signal**: Only trade markets with 24h volume > $5k

## Research Methodology

### Phase 1: Data Collection (1-2 weeks)
1. Set up data collector that:
   - Polls Simmer API every 15 seconds for active BTC 5-min markets
   - Saves: market_id, timestamp, bid, ask, bid_size, ask_size, last_trade_price, volume_24h, time_to_resolution
   - Also records: actual market outcome when resolved (YES=1, NO=0)
2. Run continuously on VPS
3. At end of day, archive to `data/raw/YYYY-MM-DD.jsonl`

### Phase 2: Exploratory Analysis (1 week)
Using Jupyter notebooks (`notebooks/02_eda.ipynb`):
1. Load all collected data
2. Compute basic stats: average spread, average TTE, volume distribution
3. For resolved markets: attach outcome (win/loss) to each observation
4. Visualize:
   - Price series for winning vs losing markets
   - Order book imbalance vs outcome
   - Volume profiles

### Phase 3: Backtesting Hypotheses (1 week)
For each hypothesis (H1-H7):
1. Define exact entry rule (e.g., "buy YES when imbalance > 0.6 and TTE > 120s")
2. Apply rule to historical data (simulate trades)
3. Compute:
   - Win rate
   - Average win size (in $)
   - Average loss size (in $)
   - Total P&L (including 10% fee)
   - Sharpe ratio (if multiple trades per day)
4. Statistical significance: p-value < 0.05?

### Phase 4: Edge Selection
Pick 1-2 hypotheses that:
- Show win rate > 55% (after fee)
- Have sufficient trades (N > 50 for statistical reliability)
- Show consistency across time (not just one lucky week)

### Phase 5: Bot Implementation
Build a simple Python script that:
- Connects to Simmer API (paper mode first)
- Checks for new signals every 15s
- When signal meets criteria, places order (dollar amount capped at $10)
- Records all trades to SQLite
- Sends Telegram alerts

### Phase 6: Paper Trading (1 week)
- Run bot in Simmer $SIM mode
- Track P&L
- Validate that backtest results match live simulation

### Phase 7: Live (Small)
- Switch to live mode with $10-15 max bet
- Run for 3-5 days
- If profitable: gradually increase size up to $50/trade max

## Edges We Already Suspect (from GitHub/MoonDev)

From Bot Arena:
- Copy top whale wallets (CopyBot)
- Momentum from external price feed (Binance)
- Mean reversion on oversold/overbought

From MoonDev:
- Hyperliquid liquidation cascade → mean reversion bet
- Funding rate differentials
- Position clustering near liquidation

## Our Unique Angle

We'll **combine data sources**:
1. **Polymarket order book** (immediate signal)
2. **External BTC price** (Binance 1-min candles) for momentum
3. **Liquidation data** (if accessible from Binance or Hyperliquid)
4. **Funding rates** (if accessible)

We're not limited to one source. We'll test multiple signals and use a **weighted ensemble** if needed.

## Tools & Stack

- **Python**: pandas, numpy for analysis
- **Jupyter**: interactive exploration
- **SQLite**: storage (simple, no server needed)
- **Simmer SDK**: for market data and paper trading
- **Streamlit**: optional dashboard
- **Git**: version control (already have vault)

## Deliverables

1. `data/` - Collected raw and processed data
2. `notebooks/` - Analysis and backtesting notebooks
3. `src/` - Data collector, signal generator, bot
4. `README.md` - How to reproduce
5. `research_report.md` - Final conclusions: which edge worked, performance stats

## Risks

- **No edge exists**: Polymarket may be efficient at 5-min horizon. Then we pivot to 15-min or different strategy.
- **Data too limited**: Need months of data for statistical significance. May need to wait.
- **Fees eat all profits**: 10% is huge. Edge must be substantial.
- **Liquidity**: May not be able to enter/exit at desired prices in small markets.

## Success Criteria

- At least one hypothesis with >55% win rate on out-of-sample data
- Positive expected value per trade (after 10% fee)
- Maximum drawdown < 30% over 100 trades
- Bot can run autonomously for 1 week without manual intervention

---

**We start with data collection. Everything else depends on that.**

Next: Implement `src/data_collectors/simmer_collector.py`