# Development Plan: Polymarket 5-Minute Crypto Bot

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Edge Finder                      │
├─────────────────────────────────────────────────────────────┤
│  Data Layer       │     Signal Layer      │  Execution Layer │
│  ─────────────    │  ─────────────────   │  ──────────────  │
│ • Simmer API      │  • Imbalance signal │  • Simmer SDK    │
│ • Direct CLOB     │  • Volume spike     │  • Direct CLOB   │
│ • Binance WS      │  • External momentum│  • Order manager │
│ • Hyperliquid API │  • Time decay       │  • Hedge manager │
│                   │  • Whale copy      │                  │
├─────────────────────────────────────────────────────────────┤
│          Risk & Position Sizing Layer                      │
│          - RiskEngine (limits, kill switch)                │
│          - Kelly calculator                               │
│          - Balance tracker                                │
├─────────────────────────────────────────────────────────────┤
│          Learning & Analytics Layer                        │
│          - Backtester                                      │
│          - Bayesian updater (optional)                     │
│          - Performance metrics                             │
├─────────────────────────────────────────────────────────────┤
│          Dashboard (Streamlit)                             │
│          - Live markets                                   │
│          - Signals                                        │
│          - Positions & P&L                                │
│          - Backtest                                       │
├─────────────────────────────────────────────────────────────┤
│          Persistence (SQLite)                              │
│          - markets, snapshots, trades, outcomes           │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 0: Setup & Infrastructure (Days 1-3)

**Goal**: Have continuous data collection running on VPS.

### Tasks
1. Deploy code to VPS (manual command)
2. Install system packages (Python3, venv)
3. Create `.env` with Simmer API key
4. Run collector in test mode for 1 minute → verify data output
5. Set up systemd service to auto-start on boot
6. Configure log rotation (`logrotate` or Python handler)

### Success Criteria
- `data/raw/2026-03-20.jsonl` exists and has >100 records per market
- No errors in logs after 5 minutes of continuous operation
- Can SSH into VPS and run `journalctl -u -poly-collector -f` to see live logs

---

## Phase 1: Exploratory Data Analysis (Days 4-7)

**Goal**: Understand the dataset.

### Tasks
1. Load first 24h of data into Jupyter notebook
2. Compute descriptive statistics:
   - Number of distinct BTC 5-min markets per day
   - Average spread (cents) and mid-price distribution
   - Order book imbalance distribution (mean, std, min/max)
   - Volume distribution (some markets very low volume?)
   - Time-to-resolution distribution (are they exactly 5 min? or variable?)
3. Visualizations:
   - Histogram of probabilities (should be roughly uniform? or clustered?)
   - Time series of one market's probability evolution from open to resolution
   - Heatmap of activity by hour-of-day (UTC)
4. Identify first resolved markets:
   - Markets that opened during our collection and have since resolved
   - Outcome known: YES=1, NO=0
   - Merge outcome with snapshot data (need to know when snapshot was taken relative to resolution)

### Deliverable
`research/01_descriptive_analysis.md` with charts and insights.

---

## Phase 2: Signal Development & Backtesting (Days 8-14)

**Goal**: Identify at least one signal with >55% win rate on historical data.

### Approach
For each hypothesis (from RESEARCH_PROMPTS responses):
1. Write Python function that takes a snapshot (dict) and returns `{action, side, confidence}`
   - `action`: "buy" or "hold"
   - `side`: "yes" or "no"
   - `confidence`: float 0-1 (probability signal is correct)
2. Apply signal to all historical snapshots (with known outcomes)
3. Simulate trade: if signal says buy with confidence > threshold, we bet fixed $10 (or Kelly size)
4. Record outcome: win (if side matches outcome) or loss
5. Compute statistics: win_rate, avg_win, avg_loss, total_pnl, Sharpe
6. Optimize parameters (if any) on training set, validate on test set
7. Document: `research/signals/IMBALANCE.md` (example)

### Promising Signals to Implement First (by priority)
1. **Order book imbalance** (simple, uses our collected data)
2. **Binance momentum divergence** (requires Binance data)
3. **Volume spike + direction** (uses trade data, may need to collect separately)
4. **Time decay pattern** (requires outcome; maybe avoid last 2 min)
5. **Spread tightening** (if we have enough data)

### Backtest Engine Module
File: `src/learning/backtester.py`
- Class `Backtester`
- Method `run(signal_func, df, position_size=10.0, fee=0.10) -> results`
- Handles trade sequencing, P&L calculation, metrics
- Supports train/test split and walk-forward

### Success Criteria
- At least one signal shows win rate > 55% on test set with N > 50 trades
- P&L positive after 10% fee per trade
- No overfitting: train and test performance similar

---

## Phase 3: Bot Construction (Days 15-21)

**Goal**: Turn the winning signal into an automated trading bot.

### Core Loop (`src/main.py`)
```python
while True:
    markets = fetch_active_markets()  # Simmer or direct
    for market in markets:
        snapshot = get_market_snapshot(market)
        signal = signal_engine.generate(snapshot)
        if signal['action'] == 'buy' and signal['confidence'] > MIN_CONFIDENCE:
            risk_ok, reason = risk_engine.check_trade(signal['suggested_amount'])
            if risk_ok:
                order = order_manager.place_order(market_id, signal['side'], signal['suggested_amount'])
                log_trade(order)
                if HEDGE_ENABLED: hedge_manager.open_hedge(...)
    sleep(CYCLE_INTERVAL)
```

### Key Components to Implement
1. **Config loader**: `config.yaml` → dict
2. **Signal registry**: import signal modules dynamically based on config
3. **RiskEngine**: as designed earlier, with daily reset at midnight UTC
4. **OrderManager abstraction**:
   - Base class with `place_order`, `get_balance`, `get_positions`
   - Subclass `SimmerOrderManager` using `simmer_sdk`
   - Subclass `DirectOrderManager` using `py_clob_client`
5. **HedgeManager** (optional, skip initially): opens perp on Hyperliquid opposite direction
6. **Logger**: structured JSON logs with rotation
7. **Alerts**: Telegram notifications on trade, error, daily summary

### Configuration (`config.yaml`)
```yaml
mode: paper  # or live
data_source: simmer  # or direct
signals:
  - imbalance:
      enabled: true
      threshold: 0.6
      tte_min: 60
  - binance_momentum:
      enabled: false  # until tested
risk:
  max_position_usd: 10.0
  daily_loss_limit_usd: 50.0
  max_trades_per_day: 100
  min_confidence: 0.55
hedge:
  enabled: false  # start without hedge
  ratio: 0.8
dashboard:
  port: 8501
alerts:
  telegram: true
```

### Testing
- Unit tests for each signal
- Mock API responses (use `responses` library for HTTP mocking)
- Dry-run mode: log intended trades but don't execute
- Run in paper mode for 24h to ensure stability

---

## Phase 4: Dashboard (Days 21-25)

**Goal**: Real-time monitoring UI.

### Pages (Streamlit)
1. **Overview**:
   - Metrics: Balance, Today P&L, Trades count
   - System status: collector running, last update
   - Active markets count
2. **Markets**:
   - DataFrame: all active BTC 5-min markets with columns: question, time left, probability, spread, volume, signal?
   - Click row to see order book depth chart (if data available)
3. **Signals**:
   - Live stream of generated signals (last 50)
   - Columns: time, market, side, confidence, reasoning, action taken
   - Color: green for YES, red for NO
4. **Positions**:
   - Current open positions (from Simmer/Direct)
   - Unrealized P&L
   - Time to resolution
5. **Backtest**:
   - Upload CSV of historical data
   - Select signal from dropdown
   - Adjust parameters with sliders
   - Show equity curve (matplotlib)
   - Show stats table

### Implementation
- Use `st.set_page_config` for layout
- Cache expensive operations with `@st.cache_data`
- Refresh every 30 seconds with `st.automatic_rerun` or button
- Store data in session_state for interactivity

---

## Phase 5: Paper Trading (Days 26-32)

**Goal**: Run bot in Simmer sandbox for 1 week.

### Steps
1. Ensure `.env` has `TRADING_MODE=paper` and `SIMMER_API_KEY`
2. Start bot: `python src/main.py`
3. Let it run unattended. Checkdashboard occasionally.
4. At end of week, compute:
   - Total trades
   - Win rate
   - Total P&L in $SIM
   - Compare to backtest results (should be similar)
5. Check for errors in logs; fix any crashes
6. Tune parameters if needed (only if consistent with backtest rationale)

### Acceptance
- Bot completed at least 50 trades in Simmer
- Win rate > 55% in paper trading
- No critical errors (memory leak, API bans)
- P&L positive

If paper trading fails, go back to Phase 2 (re-evaluate signal).

---

## Phase 6: Live Small Scale (Days 33-40)

**Goal**: Deploy with real money, small size.

### Pre-checks
1. Create separate Polymarket hot wallet, fund with $50-100 USDC on Polygon
2. Get private key, add to `.env` as `POLYMARKET_WALLET_PRIVATE_KEY`
3. Set `mode: live` and `max_position_usd: 10.0` in config
4. Verify Simmer agent is "claimed" and linked to wallet
5. Do a dry run with `--dry-run` flag (if implemented) to log intended trades without executing
6. Check: will we really trade? Confirm parameters.

### Live Run
1. Start bot in live mode
2. Enable Telegram alerts (high priority)
3. Monitor first few trades manually: check Polymarket UI to confirm order filled at expected price
4. Check wallet balance after each trade
5. If any anomaly, immediately stop bot (`kill` process)
6. Keep position size low ($10) even if max allows more

### Criteria to Continue
- First 10 trades: win rate >= 50% (not statistically significant yet)
- No unauthorized transactions
- No exceeded risk limits
- Daily loss < $10

If any major issue: pause, diagnose, restart in paper mode to debug.

### Scaling
If after 3 days live P&L positive and stable:
- Increase `max_position_usd` to $15
- Continue monitoring

After 1 week, if still profitable:
- Increase to $20, then $30 (max $50)
- But keep Kelly fraction conservative.

---

## Phase 7: Advanced Features (After 40 days, optional)

- Implement hedge with Hyperliquid perp
- Add second signal (ensemble)
- Bayesian learning (update signal weights based on recent performance)
- Copy whale integration (using Grok alpha or Simmer CopyTrader)
- Machine learning model (if enough data)
- Multi-asset: add ETH 5-min markets

---

## Code Structure Reference

```
poly-edgefinder/
├── src/
│   ├── data_collectors/
│   │   ├── simmer_collector.py
│   │   └── polymarket_direct.py
│   ├── signals/
│   │   ├── base.py          (Signal abstract class)
│   │   ├── imbalance.py
│   │   ├── volume_spike.py
│   │   ├── binance_momentum.py
│   │   └── registry.py      (signal registry)
│   ├── execution/
│   │   ├── order_manager.py
│   │   ├── risk_engine.py
│   │   ├── position_sizer.py
│   │   └── hedge_manager.py
│   ├── learning/
│   │   ├── backtester.py
│   │   ├── bayesian.py
│   │   └── metrics.py
│   ├── dashboard/
│   │   └── app.py
│   └── main.py
├── config.yaml
├── requirements.txt
├── .env
├── .gitignore
├── setup_vps.sh
├── systemd/
│   └── -poly-collector.service
└── notebooks/
    ├── 01_descriptive_analysis.ipynb
    ├── 02_signal_development.ipynb
    └── 03_backtest_results.ipynb
```

---

## Testing Checklist

- [ ] `src/data_collectors/simmer_collector.py` runs without errors, writes to file
- [ ] `src/analysis/statistics.py` loads collected data and computes stats
- [ ] Each signal module has unit test with mock snapshot
- [ ] Backtester produces consistent results on same input
- [ ] OrderManager dry-run mode logs correct SQL without executing
- [ ] RiskEngine rejects trade when limit hit
- [ ] Dashboard loads and displays data from DB
- [ ] Telegram bot sends test message

---

## Deployment Checklist

- [ ] Code committed to git (except .env)
- [ ] `requirements.txt` up to date
- [ ] `config.yaml` contains all required keys
- [ ] `.env` created on VPS with all secrets
- [ ] Systemd service enabled: `systemctl enable -poly-collector`
- [ ] Logs configured to write to file (not just stdout)
- [ ] Firewall allows port 22 and 8501 (if needed)
- [ ] Daily cron job to backup SQLite to remote location
- [ ] SSH key auth set up (disable password login if possible)
- [ ] Monitor first 24h manually: `tail -f logs/bot.log`

---

## Risk Mitigation Table

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| No edge found after data collection | Medium | Project halt | Have multiple hypotheses; try longer time horizon (15-min instead of 5-min) |
| Data too sparse (few markets) | Medium | Can't backtest | Extend collection duration to 2-4 weeks; supplement with Binance liquidations |
| Simmer API limits/stale data | Low | Poor signals | Switch to direct Polymarket CLOB (requires wallet) |
| Fee structure mis-modeled | Medium | Profit illusion | Verify exact fee calculation with Simmer docs or test trade |
| Liquidity insufficient to fill | Medium | Slippage losses | Limit order size to $10; use market orders only if spread < 2¢ |
| VPS crash or network outage | Medium | Data gaps, missed trades | Monitor with health checks; auto-restart via systemd; consider backup VPS |
| Wallet hack/compromise | Low | Total loss | Use dedicated hot wallet with minimal balance; never store large sums |
| Polymarket bans API usage | Low | Bot stops | Use rate limits conservatively; rotate user agents; have fallback direct CLOB |
| Regulatory seizure | Very low | Lose funds | Keep capital small; withdraw profits regularly to cold storage |

---

## Decision Points & Go/No-Go Criteria

1. **After 1 week data collection**:
   - Go if we have ≥100 resolved markets
   - No-go if < 20 resolved markets (data insufficient) → reconsider strategy

2. **After Phase 2 (backtesting)**:
   - Go if at least one signal has win rate > 55% and N > 50
   - No-go if no signal beats 52% → either data issues or no edge; stop or pivot

3. **After paper trading (1 week)**:
   - Go if paper P&L > 0 and stable (no large drawdowns)
   - No-go if losing in paper → signals not translating live

4. **After live small (3 days)**:
   - Go if live P&L > -$10 (not losing) and no technical issues
   - Scale up cautiously
   - No-go if losing > $20 → stop, investigate, revert to paper

---

## Maintenance Plan (Post-Launch)

- **Daily**: Check Telegram alerts, monitor balance, check daily P&L
- **Weekly**: Review trade history, update parameters if needed, backup data
- **Monthly**: Rotate API keys? Check for Simmer SDK updates
- **When errors occur**: Check logs, fix bug, redeploy
- **Quarterly**: Re-evaluate strategy performance; if declined, re-run research cycle

---

**Next Step**: Complete Phase 0 (VPS deployment) and start data collection. Then we will have real data to drive decisions.
