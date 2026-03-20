"""
Basic statistical analysis of collected Polymarket data.

- Descriptive stats: spreads, volumes, TTE distributions
- Hypothesis testing: imbalance → price move?
- Backtesting engine for simple strategies
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)

    def load_all_data(self) -> pd.DataFrame:
        """Load all JSONL files into a DataFrame."""
        all_files = list(self.data_dir.glob("*.jsonl"))
        if not all_files:
            raise FileNotFoundError(f"No JSONL files found in {self.data_dir}")

        records = []
        for file in all_files:
            with open(file, 'r') as f:
                for line in f:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        df = pd.DataFrame(records)
        logger.info(f"Loaded {len(df)} records from {len(all_files)} files")
        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic cleaning: drop missing values, convert types."""
        # Keep only successful snapshots
        if 'error' in df.columns:
            df = df[df['error'].isna()]

        # Convert timestamp to datetime
        df['datetime'] = pd.to_datetime(df['dt'], utc=True)

        # Convert numeric columns
        numeric_cols = ['best_bid_price', 'best_ask_price', 'best_bid_size', 'best_ask_size',
                        'current_probability', 'volume_24h', 'time_to_resolution_seconds',
                        'imbalance', 'spread', 'mid_price']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows with missing critical data
        df = df.dropna(subset=['market_id', 'current_probability'])

        logger.info(f"Cleaned data: {len(df)} records")
        return df

    def descriptive_stats(self, df: pd.DataFrame) -> Dict:
        """Compute descriptive statistics."""
        stats = {
            'total_snapshots': len(df),
            'unique_markets': df['market_id'].nunique(),
            'date_range': (df['datetime'].min(), df['datetime'].max()),
            'spread_mean': df['spread'].mean() if 'spread' in df.columns else None,
            'spread_median': df['spread'].median() if 'spread' in df.columns else None,
            'imbalance_mean': df['imbalance'].mean() if 'imbalance' in df.columns else None,
            'imbalance_std': df['imbalance'].std() if 'imbalance' in df.columns else None,
            'probability_mean': df['current_probability'].mean(),
            'probability_std': df['current_probability'].std(),
            'tte_mean': df['time_to_resolution_seconds'].mean() if 'time_to_resolution_seconds' in df.columns else None,
        }
        return stats

    def prepare_for_backtest(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data for backtesting.
        Need: market_id, datetime, probability, imbalance, outcome (when available)
        """
        # For backtest, we need resolved markets with known outcomes.
        # This requires storing outcome separately later.
        # For now, return cleaned df with essential columns.
        cols_needed = ['market_id', 'datetime', 'current_probability']
        if 'imbalance' in df.columns:
            cols_needed.append('imbalance')
        if 'mid_price' in df.columns:
            cols_needed.append('mid_price')

        return df[cols_needed].copy()


class SimpleStrategyBacktester:
    """Backtest a simple rule-based strategy."""

    def __init__(self, analyzer: MarketAnalyzer):
        self.analyzer = analyzer

    def test_imbalance_strategy(self, df: pd.DataFrame,
                                 threshold: float = 0.6,
                                 min_balance_size: float = 0.0,
                                 tte_min: float = 60) -> Dict:
        """
        Test: When order book imbalance is strongly positive (bids > asks),
        bet YES. When strongly negative, bet NO.

        Hold for a fixed duration (next 1-3 minutes?) - need resolution outcomes
        For now, this is a sketch — full backtest requires outcome data.
        """
        # This is a placeholder — real backtest needs resolved trades
        signals = []

        for _, row in df.iterrows():
            if pd.isna(row.get('imbalance')):
                continue
            if row.get('time_to_resolution_seconds', 0) < tte_min:
                continue

            imb = row['imbalance']
            if abs(imb) >= threshold:
                side = 'yes' if imb > 0 else 'no'
                signals.append({
                    'market_id': row['market_id'],
                    'datetime': row['datetime'],
                    'side': side,
                    'probability': row['current_probability'],
                    'imbalance': imb,
                })

        logger.info(f"Imbalance strategy generated {len(signals)} signals")
        return {
            'signals': signals,
            'num_signals': len(signals),
            'threshold': threshold,
        }

    # More strategies to be added...


def main():
    """Quick test: load data, print stats."""
    import sys
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python statistics.py <data_dir>")
        sys.exit(1)

    analyzer = MarketAnalyzer(sys.argv[1])
    df = analyzer.load_all_data()
    df = analyzer.clean_data(df)

    stats = analyzer.descriptive_stats(df)
    print("\n=== Descriptive Statistics ===")
    for k, v in stats.items():
        print(f"{k}: {v}")

    backtester = SimpleStrategyBacktester(analyzer)
    result = backtester.test_imbalance_strategy(df)
    print(f"\nImbalance strategy (thresh={result['threshold']}): {result['num_signals']} signals")


if __name__ == "__main__":
    main()