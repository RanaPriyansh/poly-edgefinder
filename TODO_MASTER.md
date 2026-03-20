# Master TODO: Polymarket Edge Finder Project

**Last Updated**: 2026-03-20
**Status**: Research Phase Started - Code Infrastructure Ready

---

## Legend
- [ ] Not started
- [x] Completed
- [~] In progress
- [!] Blocked / waiting for input
- [>] Deferred (low priority)

---

## Category A: Data Collection (Infrastructure)

### A.1: Deploy to VPS
- [~] Copy project to VPS /opt/thielon-poly-edgefinder
- [~] Run setup_vps.sh (installs Python, venv, dependencies)
- [!] Add Simmer API key to .env (waiting on user)
- [ ] Verify collector runs (test 30 seconds)
- [ ] Set up as systemd service for auto-start on boot
- [ ] Configure log rotation (logrotate)

### A.2: Data Pipeline
- [ ] Simmer collector: verify it captures order book imbalance correctly
- [ ] If Simmer lacks order book depth, enable Polymarket direct collector (requires wallet PK)
- [ ] Add Binance 1-min price feed (WebSocket connection)
- [ ] Implement data validation: detect missing fields, corrupted records
- [ ] Set up daily archiving: raw JSONL → compressed (gzip) after 24h
- [ ] Create backup to remote storage (e.g., rsync to Dropbox or S3)

### A.3: Data Storage Schema
- [ ] Design SQLite schema: markets, snapshots, trades, outcomes
- [ ] Write ETL: raw JSONL → SQLite (daily batch)
- [ ] Add indexes on (market_id, datetime) for fast queries
- [ ] Test queries: "fetch all snapshots for market X in last 24h"

---

## Category B: Research & Analysis

### B.1: Initial Descriptive Analysis (Week 1-2)
- [ ] Load first 24h of collected data into pandas
- [ ] Compute basic stats: number of markets per day, avg spread, avg volume, avg TTE
- [ ] Plot distributions: histogram of probabilities (0-1), spreads, imbalances
- [ ] Identify typical active hours (UTC) for BTC 5-min markets
- [ ] Estimate number of trade opportunities per day
- [ ] Document findings in `research/01_descriptive_analysis.md`

### B.2: Hypothesis Testing (Week 2-3)
For each hypothesis, we need to:
- [ ] Implement signal generator function
- [ ] Align signals with outcomes (need resolved markets data)
- [ ] Compute win rate, expectancy, Sharpe
- [ ] Assess statistical significance
- [ ] Decide keep/discard

Hypotheses to test (minimum 10):

- [ ] H1: Order book imbalance (|imb|>0.6) → follow direction (next 1-3 min)
- [ ] H2: Volume spike (1-min vol > 2x avg) → follow trade direction
- [ ] H3: Binance momentum divergence (Binance 5-min return > required return + threshold)
- [ ] H4: Time decay pattern (specific TTE ranges have predictable drift)
- [ ] H5: Spread contraction precedes moves (when spread tightens from wide, direction?)
- [ ] H6: Market probability extreme (>0.8 or <0.2) continues? Or reverts?
- [ ] H7: Hour-of-day effect (some hours have higher win rates)
- [ ] H8: Cross-market: 5-min vs 15-min on same BTC question (arb)
- [ ] H9: Resolution rush: last 60 seconds have predictable direction? (Probably avoid)
- [ ] H10: Quote freshness: stale order book (no updates >5s) = predictable drift?

Write results in `research/02_hypothesis_results.md` with table summarizing all.

### B.3: Backtest Engine
- [ ] Build event-driven backtester that simulates trades on historical snapshots
- [ ] Incorporate: order book data, resolution outcomes (once we have them)
- [ ] Include fee calculation (10% accurate)
- [ ] Slippage model (realistic fill price)
- [ ] Run backtests on all promising hypotheses
- [ ] Perform train/test split (60/40) and walk-forward validation
- [ ] Generate reports: equity curves, drawdowns, Sharpe ratios

### B.4: External Data Integration Checks
- [ ] Verify Binance WebSocket subscription works (no lag)
- [ ] Test Binance kline retrieval (historical and live)
- [ ] If using Hyperliquid API: deploy MoonDev's data layer and test endpoints
- [ ] Check for rate limits (does Binance restrict after X connections?)

---

## Category C: Development (Bot Construction)

### C.1: Architecture & Core Components
- [ ] Finalize bot architecture diagram (text description)
- [ ] Write main loop: cycle every 15 seconds
    1. Fetch active markets (Simmer or direct)
    2. For each market, compute signals (load modules)
    3. Apply risk checks (balance, daily loss, position limits)
    4. If signal confidence above threshold, place order
    5. Log trade to database
    6. Send alerts if configured
- [ ] Implement signal registry: dynamic loading of signal modules (plugins)
- [ ] Implement order manager abstraction: SimmerSDKOrderer vs DirectCLOBOrderer
- [ ] Implement position manager: track open positions, P&L

### C.2: Risk Management Module
- [ ] Implement `RiskEngine` class:
  - `check_trade(proposed_size, current_balance)` -> bool + reason
  - `record_fill(fill)` -> update daily P&L
  - `kill_switch_activated` flag
- [ ] Daily loss limit: reset at midnight UTC, stop trading if exceeded
- [ ] Max position limit: enforce per-market and total
- [ ] Max trades per hour: avoid spamming
- [ ] Balance check: don't bet if balance too low

### C.3: Position Sizing
- [ ] Implement Kelly calculator (given win rate, avg win/loss)
- [ ] Initially use fixed $10 bets until we have reliable win_rate estimate
- [ ] Later: dynamic sizing based on confidence (stronger signal → larger bet up to Kelly)
- [ ] Cap max bet at $20 (liquidity constraint)

### C.4: Signal Modules (Implement Top 2-3)
Based on research, pick best hypotheses. For each:
- [ ] Create module: `src/signals/imbalance_signal.py`
- [ ] Function `generate_signal(market_snapshot) -> {action, side, confidence, reasoning, size}`
- [ ] Unit test with synthetic data

### C.5: Order Execution
- [ ] Implement Simmer order placement:
  - `client.trade(market_id, side, size, reasoning)`
  - Handle errors (insufficient balance, market closed, rate limit)
  - Retry logic (exponential backoff)
- [ ] Implement direct Polymarket order placement (fallback)
  - `client.create_order(...)`
  - Need to handle token IDs for YES/NO
- [ ] Test on paper (Simmer $SIM) first

### C.6: Dashboard
- [ ] Set up Streamlit app skeleton (`dashboard/app.py`)
- [ ] Page: Overview (KPI cards)
- [ ] Page: Active Markets (table with filters)
- [ ] Page: Signals (live feed)
- [ ] Page: Positions (open positions and P&L)
- [ ] Page: Backtest (upload data, run strategy, show results)
- [ ] Connect to same database as bot
- [ ] Deploy on VPS (port 8501), set up nginx reverse proxy? Optional.

### C.7: Alerting
- [ ] Implement `alerts.py` (Telegram notifications)
- [ ] Config: which alerts enabled?
- [ ] Test: send test message on startup
- [ ] Throttle: batch multiple trades into one summary every 5 minutes to avoid spam

### C.8: Configuration Management
- [ ] Use `config.yaml` for all tunable parameters (already created)
- [ ] Load at startup, allow runtime changes via dashboard (save to YAML)
- [ ] Validate config on load (required fields, ranges)

### C.9: Logging & Observability
- [ ] Set up structured logging (JSON format)
- [ ] Log levels: DEBUG, INFO, WARNING, ERROR
- [ ] Rotate logs daily (logrotate or Python RotatingFileHandler)
- [ ] Include trade_id in logs for tracing
- [ ] Add metrics: number of signals evaluated, trades placed, errors

### C.10: Testing Suite
- [ ] Unit tests for signal functions (test with known inputs → expected outputs)
- [ ] Unit tests for risk engine (should reject oversized trades)
- [ ] Mock tests for order manager (no real API calls)
- [ ] Integration test: simulate 1 hour of data → verify no crashes
- [ ] Run tests on every commit (set up GitHub Actions if repo public)

### C.11: Documentation
- [ ] README.md: How to set up, configure, run
- [ ] STRATEGY.md: Detailed explanation of chosen edge(s)
- [ ] API_KEYS.md: Where to get each key, security precautions
- [ ] TROUBLESHOOTING.md: Common errors and fixes

---

## Category D: Deployment & Live Operation

### D.1: Paper Trading (1 week)
- [ ] Switch config to Simmer paper mode (`venue: sim`)
- [ ] Run bot continuously for 7 days
- [ ] Collect: number of signals generated, trades placed (Simmer orders)
- [ ] Simulate P&L based on outcomes (Simmer will auto-redeem)
- [ ] Verify no crashes, memory leaks
- [ ] Analyze paper trading results: Are we making money in $SIM?

### D.2: Live Preparation
- [ ] Create dedicated hot wallet on Polymarket (separate from main)
- [ ] Fund with $50-100 USDC on Polygon
- [ ] Get wallet private key
- [ ] Set up external wallet mode in Simmer (or direct Polymarket)
- [ ] Test connection: can read balance? can place $1 test trade?

### D.3: Live Trading (Small)
- [ ] Set config to live mode, max position $10
- [ ] Run for 3-5 days with real money
- [ ] Monitor via Telegram alerts and dashboard
- [ ] Compare live results to paper simulation
- [ ] Be ready to stop immediately if losing > $20

### D.4: Scale or Pivot
- [ ] If profitable and stable: increase max position gradually (to $20, $30, $50)
- [ ] If losing: stop, analyze root cause, refine strategy
- [ ] After 30 days of live, evaluate: continue or stop

---

## Category E: Research Enhancements (Parallel)

### E.1: Grok Alpha Integration
- [ ] Set up Grok agent scripts (or manual searches) for whale tracking
- [ ] Store results in `data/grok_alpha/`
- [ ] Ingest into analysis: correlate whale bets with outcomes
- [ ] Potentially add "copy whale" signal if edge found

### E.2: Machine Learning Experiment
- [ ] Once we have 500+ resolved trades, train simple logistic regression
- [ ] Compare ML vs rule-based performance
- [ ] Document results

### E.3: Additional Data Sources
- [ ] Investigate: Can we get historical order books for backtesting? (MoonDev's data layer has historical liquidations, maybe positions too?)
- [ ] Try: CoinGecko spot price 1-min candles (REST) as fallback to Binance
- [ ] Consider: Adding ETH 5-min markets after BTC strategy proven

---

## Category F: Security & Compliance

### F.1: Security Audit
- [ ] Review all code for hardcoded secrets (none allowed)
- [ ] Ensure .env is in .gitignore
- [ ] Use read-only wallet for data collection? (private key only needed for order placement)
- [ ] Set up firewall on VPS (only ports 22, 8501 open)
- [ ] Install fail2ban to prevent brute force
- [ ] Use SSH key instead of password (disable root SSH? Use sudo user)

### F.2: Compliance Checks
- [ ] Verify VPS location is not restricted (use IP lookup)
- [ ] Check Polymarket ToS re: automation (risk of ban)
- [ ] Keep trading capital small (< $500) to minimize KYC risk
- [ ] Plan for withdrawal: how to move funds from hot wallet to cold storage?

---

## Category G: Performance Optimization (Later)

- [ ] Switch to asynchronous I/O (asyncio) for concurrent market fetching
- [ ] Use WebSocket instead of REST polling if available (Polymarket push updates)
- [ ] Cache static data (market list) to reduce API calls
- [ ] Profile CPU/memory usage; optimize hotspots
- [ ] Consider migrating from SQLite to PostgreSQL if data grows > 1GB

---

## Category H: Community & Publication

- [ ] Write blog post: "How I built a Polymarket 5-min bot from scratch"
- [ ] Open source the code (GitHub) — remove secrets, add license (MIT)
- [ ] Share findings on X/Twitter (_thread about edge discovery_)
- [ ] Consider joining Simmer skill marketplace (if we have a working strategy)

---

## Current Blockers

1. [!] **Simmer API key** needed to start data collection (user must register)
2. [!] **Decision**: Use Simmer only, or also direct Polymarket? (direct requires wallet private key)
3. [!] **Research**: Need to confirm fee structure exact calculation (10% how applied)
4. [~] **VPS setup**: manual deployment pending user action

---

## Quick Wins (Low-hanging fruit)

Once collector is running:
1. Collect 24h data → compute descriptive stats → immediately understand market density
2. Test imbalance signal on that data (even without outcomes, we can see signal frequency)
3. Get first resolved market outcomes after 24-48h (markets from day 1 start resolving)
4. That gives us our first backtest with real outcomes

---

## Timeline (Revised)

| Week | Tasks | Expected Outcome |
|------|-------|------------------|
| 1 | Deploy, collect data, descriptive analysis | 5-10 days of snapshots; understand market activity patterns |
| 2 | Hypothesis testing, backtest top 3 signals | Identify 1-2 promising edges (win rate > 55%) |
| 3 | Build bot skeleton, implement top signal, paper trade | Bot runs autonomously on $SIM, logs trades |
| 4 | Paper trade evaluation, refine strategy | Confidence in edge; decide to go live or not |
| 5 | Live small, monitor closely | Real P&L data, compare to paper |
| 6+ | Scale if profitable, or iterate/improve if not | Grow capital or pivot |

---

## Done Items (Recent)

- [x] Project structure created
- [x] Simmer collector module written
- [x] Polymarket direct collector written (backup)
- [x] Basic analysis module written (statistics, placeholder backtest)
- [x] Setup script for VPS
- [x] Systemd service file
- [x] Research context document (RESEARCH_CONTEXT.md)
- [x] Research prompts for Gemini (RESEARCH_PROMPTS.md)
- [x] Grok alpha prompts (GROK_ALPHA_PROMPTS.md)
- [x] This TODO master list
- [x] Deployment package created

---

## Next Immediate Actions (User)

1. **Get Simmer API key** (register via curl, claim, save key)
2. **Deploy to VPS** using manual commands provided
3. **Edit .env** on VPS to add Simmer key
4. **Run collector test**: `source venv/bin/activate && python -m src.data_collectors.simmer_collector`
5. **Confirm data** appears in `data/raw/YYYY-MM-DD.jsonl`
6. **Share first results** (descriptive stats) after 6+ hours of collection

## Next Immediate Actions (Me / Hermes)

After user deployment:
1. Instruct on how to collect first day of data
2. Once data collected, run analysis notebook to produce descriptive stats
3. Generate report: "Here's what we found in the data so far"
4. Recommend which hypotheses to test first based on data availability
5. Implement first signal module and backtest
6. Iterate: refine signal based on backtest results

---

**Goal**: By [date 2 weeks from now], have a paper-trading bot with at least one validated edge showing >55% win rate on out-of-sample test.

**Success metric**: Positive expectancy per trade after 10% fee.
