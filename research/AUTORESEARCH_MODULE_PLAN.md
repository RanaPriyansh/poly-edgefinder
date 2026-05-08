# Autoresearch modularization plan

## Goal

Convert the one-off `autoresearch.py` orchestration pattern into reusable research modules, skills, and subagents that can serve Polymarket research first and other domains later.

## What exists today

### In `autoresearch.py`
The training-challenge script already contains a reusable loop shape:

1. generate hypotheses
2. run experiments
3. analyze results
4. write report
5. notify
6. persist cycle state

That file is generic in structure but tightly coupled in implementation to local modules, local folders, and Telegram/report side effects.

### In `poly-edgefinder`
The current Polymarket project has reusable domain pieces but not a reusable research orchestrator:

- collectors:
  - `src/data_collectors/simmer_collector.py`
  - `src/data_collectors/polymarket_direct.py`
- analytics:
  - `src/analysis/statistics.py`
- app loop / scanning:
  - `main.py`
- research specs and hypotheses:
  - `research/RESEARCH_CONTEXT.md`
  - `DEVELOPMENT_PLAN.md`

The repo is strong on data collection and early analysis, but weak on a generalized hypothesis -> experiment -> analysis loop.

## Components to extract into reusable modules

### 1. Research loop orchestration
Owns the generic cycle:
- context in
- hypotheses generated
- experiments executed
- insights produced
- artifacts saved
- events emitted

This is the main extraction from `autoresearch.py`.

### 2. Domain adapters
Per-domain implementations plugged into the research loop.

For Polymarket the first adapters should be:
- `PolymarketHypothesisGenerator`
- `PolymarketExperimentRunner`
- `PolymarketResultAnalyzer`
- `PolymarketReportWriter`

For other domains later, only these adapters need to change.

### 3. Skills
Small, composable units a subagent can call.

Recommended skills:
- market discovery skill
- snapshot collection skill
- descriptive stats skill
- hypothesis proposal skill
- hypothesis scoring skill
- signal backtest skill
- report synthesis skill
- notification skill

These should be callable independently, not only through one giant loop.

### 4. Subagents
Thin role-specialized wrappers around the skills.

Recommended first subagents:
- scout: finds candidate markets / datasets / anomalies
- experimenter: runs a hypothesis test or backtest
- analyst: computes metrics and extracts insights
- reporter: writes markdown / JSON summaries

### 5. Artifact and memory layer
Needed so multiple subagents can collaborate across runs.

Store:
- cycle state JSON
- experiment results
- candidate hypotheses
- report markdown
- optional evaluation metadata

## Minimal module design

Proposed package layout:

```text
src/
  research/
    __init__.py
    loop.py                 # generic orchestration contracts and default loop
  skills/
    market_discovery.py
    snapshot_stats.py
    hypothesis_generation.py
    backtest_skill.py
    reporting.py
  subagents/
    scout.py
    experimenter.py
    analyst.py
    reporter.py
  polymarket/
    research_adapters.py    # Polymarket implementations of generator/runner/analyzer/reporter
```

### Core contracts

`ResearchContext`
- domain
- objective
- constraints
- inputs

`ResearchHypothesis`
- id
- statement
- rationale
- metadata

`ResearchExperimentResult`
- hypothesis_id
- status
- score
- summary
- evidence

`ResearchInsight`
- hypothesis_id
- insight
- action
- confidence
- metadata

`ResearchLoop`
- accepts generator, runner, analyzer, reporter
- runs full cycle
- optionally emits events and stores artifacts

## How this maps to current Polymarket code

### Reuse directly
- `PolymarketDirectCollector.get_all_markets`
- `PolymarketDirectCollector.get_order_book`
- `PolymarketDirectCollector.snapshot_all`
- `MarketAnalyzer.load_all_data`
- `MarketAnalyzer.clean_data`
- `MarketAnalyzer.descriptive_stats`
- `SimpleStrategyBacktester.test_imbalance_strategy`

### Refactor next
- move BTC/5min filtering logic from `main.py` and `polymarket_direct.py` into one reusable skill
- normalize snapshot schemas between Simmer and direct Polymarket collectors
- separate signal generation from FastAPI app runtime
- turn `statistics.py` placeholder backtest into an experiment runner contract

### Avoid carrying over from `autoresearch.py`
- hardcoded folder layout assumptions
- hardcoded Telegram notifier dependency in the main loop
- challenge-specific naming like "hypotheses" if some domains need broader "research questions" later

## Recommended first implementation slice

Implemented in this repo now:
- `src/research/loop.py`
- `src/research/__init__.py`

This first slice gives:
- generic dataclasses for research context, hypotheses, experiments, insights, cycle result
- protocol-based extension points for generator, runner, analyzer, reporter, event sink
- a reusable `ResearchLoop` orchestration class
- simple JSON artifact storage
- simple markdown report writer

This is intentionally minimal and domain-agnostic.

## Next slice to build in Polymarket project

### 1. Create `src/polymarket/research_adapters.py`
Add:
- `PolymarketHypothesisGenerator`
  - seeds from `research/RESEARCH_CONTEXT.md`
  - initially returns static hypotheses like imbalance, spread tightening, momentum divergence
- `PolymarketExperimentRunner`
  - loads snapshots via `MarketAnalyzer`
  - routes each hypothesis to a concrete test function
- `PolymarketResultAnalyzer`
  - ranks experiments by score / sample size / significance proxy
- `PolymarketReportWriter`
  - writes markdown into `research/results/`

### 2. Add skill wrappers
Example:
- `snapshot_stats_skill(data_dir) -> stats`
- `imbalance_backtest_skill(data_dir, threshold) -> result`
- `hypothesis_generation_skill(context) -> hypotheses`

### 3. Add one command entrypoint
Example CLI:

```bash
python -m src.polymarket.research_run --objective "find first tradable signal" --data-dir data/raw
```

## Why this architecture works for multiple use cases

Because the orchestration becomes generic and the domain intelligence moves into replaceable adapters.

That supports:
- Polymarket signal discovery
- scientific experiment loops
- product research loops
- OSINT / market intelligence loops

Same loop, different skills and subagents.

## Key gaps found in current Polymarket repo

1. schema mismatch between Simmer snapshots and direct CLOB snapshots
2. analysis code expects `current_probability`, but direct snapshots mostly produce `mid_price`
3. no single normalized research dataset contract yet
4. no reusable experiment registry yet
5. backtesting is still a placeholder rather than a true experiment pipeline

## Recommended immediate priority order

1. normalize snapshot schema
2. add Polymarket research adapters on top of `ResearchLoop`
3. implement one real experiment: imbalance hypothesis
4. expose that as both a skill and a subagent action
5. then add more hypothesis modules
