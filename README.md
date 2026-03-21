# Thielon Polymarket Edge Finder

[![GitHub](https://img.shields.io/badge/GitHub-000000?logo=github)](https://github.com/thielon-apps/thielon-poly-edgefinder)
[![License](https://img.shields.io/github/license/thielon-apps/thielon-poly-edgefinder)](https://github.com/thielon-apps/thielon-poly-edgefinder/blob/main/LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/thielon-apps/thielon-poly-edgefinder)](https://github.com/thielon-apps/thielon-poly-edgefinder/commits/main)

**Research-driven bot development for 5-minute crypto prediction markets.**

## Status

**Phase**: Research Phase (Week 1)
**Current**: Infrastructure ready, awaiting Simmer API key to start data collection.

## Quick Start

1. **Get Simmer API key**:
   ```bash
   curl -X POST https://api.simmer.markets/api/sdk/agents/register \
     -H "Content-Type: application/json" \
     -d '{"name": "thielon-poly-bot", "description": "Trades BTC 5-min"}'
   ```
   Save the `api_key` from response.

2. **Deploy to VPS**:
   ```bash
   # On your local machine:
   scp -r /root/obsidian-hermes-vault/projects/thielon-poly-edgefinder root@213.199.32.246:/opt/
   # Then on VPS:
   cd /opt/thielon-poly-edgefinder
   bash setup_vps.sh
   ```

3. **Configure**:
   Edit `.env` and add:
   ```env
   SIMMER_API_KEY=sk_live_xxxxxxxx
   ```

4. **Run collector**:
   ```bash
   source venv/bin/activate
   python -m src.data_collectors.simmer_collector
   ```
   Press Ctrl+C after 30s to test. Data writes to `data/raw/YYYY-MM-DD.jsonl`.

5. **Set up as service** (optional):
   ```bash
   cp systemd/thielon-poly-collector.service /etc/systemd/system/
   systemctl enable thielon-poly-collector
   systemctl start thielon-poly-collector
   ```

## Project Structure

```
thielon-poly-edgefinder/
├── src/                    # Source code
│   ├── data_collectors/   # Data collection (Simmer, direct Polymarket)
│   ├── analysis/          # Statistics, backtesting
│   ├── signals/           # Trading signals (to implement)
│   ├── execution/         # Order placement, risk (to implement)
│   ├── learning/          # Backtester, metrics (to implement)
│   └── dashboard/         # Streamlit UI (to implement)
├── research/              # Research documents
│   ├── RESEARCH_CONTEXT.md
│   ├── RESEARCH_PROMPTS.md    (for Gemini)
│   └── GROK_ALPHA_PROMPTS.md  (for X/Twitter)
├── data/                  # Raw and processed data (gitignored)
├── notebooks/             # Jupyter analysis
├── logs/                  # Application logs
├── systemd/               # Service files
├── TODO_MASTER.md         # Full task list
├── DEVELOPMENT_PLAN.md    # Architecture & phases
├── requirements.txt
├── config.yaml
└── .env.example

```

## Documentation Files

- `README.md` - This file
- `DEVELOPMENT_PLAN.md` - Architecture and implementation phases
- `TODO_MASTER.md` - Comprehensive task checklist
- `research/RESEARCH_CONTEXT.md` - Mission, knowns, unknowns
- `research/RESEARCH_PROMPTS.md` - Prompts for Gemini deep research
- `research/GROK_ALPHA_PROMPTS.md` - Prompts for X/Twitter alpha

## Current Tasks

### Immediate (User)
1. Register for Simmer API key
2. Deploy code to VPS (run setup script)
3. Configure `.env` with API key
4. Confirm collector runs and writes data

### Immediate (Hermes)
After data collection starts:
1. Analyze first 24h of data
2. Produce descriptive statistics report
3. Recommend which hypotheses to test first
4. Implement top signal(s) in code
5. Build backtester
6. Validate edge

## Research Questions

We need to answer:
- How many BTC 5-min markets exist per day?
- What are typical spreads and liquidity?
- Does order book imbalance predict direction? (target: >55% win rate)
- Can we combine with Binance momentum for higher edge?
- How many trades per day can we realistically execute?

See `research/RESEARCH_PROMPTS.md` for full list.

## Contact

Bot: Hermes Agent (Thielon mode)

---

**Note**: This project is in early research stage. Do not risk real money until after 1 week of paper trading with validated edge.
