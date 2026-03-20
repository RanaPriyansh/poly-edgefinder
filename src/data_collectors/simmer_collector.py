"""
Poll Simmer API for active Polymarket BTC 5-min markets and collect order book snapshots.

Usage:
    python -m src.data_collectors.simmer_collector

Stores data to data/raw/YYYY-MM-DD.jsonl
"""

import os
import json
import time
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class SimmerCollector:
    def __init__(self, api_key: str, output_dir: str = "data/raw"):
        self.api_key = api_key
        self.base_url = "https://api.simmer.markets"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_active_markets(self, query: str = "btc", window: str = "5") -> List[Dict]:
        """Fetch active markets from Simmer."""
        try:
            resp = self.session.get(f"{self.base_url}/api/sdk/markets", params={"q": query, "limit": 50})
            resp.raise_for_status()
            markets = resp.json()

            # Filter to desired window (5min or 15min)
            filtered = []
            for m in markets:
                question = m.get('question', '').lower()
                if window in question or f"{window}-min" in question or f"{window}min" in question:
                    filtered.append(m)

            logger.info(f"Found {len(filtered)} active {window}-min BTC markets")
            return filtered
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []

    def get_market_context(self, market_id: str) -> Optional[Dict]:
        """Get detailed context for a market (order book, volume, etc)."""
        try:
            resp = self.session.get(f"{self.base_url}/api/sdk/context/{market_id}")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.debug(f"Error fetching context for {market_id}: {e}")
            return None

    def get_market_order_book(self, context: Dict) -> Dict:
        """Extract order book and key metrics from context."""
        # Simmer context structure (from docs)
        # Returns: current_probability, volume_24h, time_to_resolution_seconds, warnings
        # For full order book, we might need a separate call to Polymarket directly
        # But Simmer may provide best bid/ask in context

        data = {
            'timestamp': time.time(),
            'dt': datetime.datetime.utcnow().isoformat(),
            'market_id': context.get('market_id'),
            'current_probability': context.get('current_probability'),  # YES probability
            'volume_24h': context.get('volume_24h', 0),
            'time_to_resolution_seconds': context.get('time_to_resolution_seconds', 0),
            'warnings': context.get('warnings', []),
        }

        # Simmer might also include order book fields
        # Let's check what's actually available
        if 'order_book' in context:
            ob = context['order_book']
            data['best_bid'] = ob.get('bids', [[None, 0]])[0][0]
            data['best_ask'] = ob.get('asks', [[None, 0]])[0][0]
            data['bid_size'] = ob.get('bids', [[None, 0]])[0][1]
            data['ask_size'] = ob.get('asks', [[None, 0]])[0][1]
        else:
            data['best_bid'] = None
            data['best_ask'] = None
            data['bid_size'] = 0
            data['ask_size'] = 0

        return data

    def calculate_imbalance(self, bid_size: float, ask_size: float) -> float:
        """Order book imbalance: positive = bid heavy, negative = ask heavy."""
        total = bid_size + ask_size
        if total == 0:
            return 0.0
        return (bid_size - ask_size) / total

    def snapshot_all_markets(self, window: str = "5"):
        """Take one snapshot of all active markets."""
        markets = self.get_active_markets(window=window)
        snapshots = []

        for market in markets:
            market_id = market.get('id')
            if not market_id:
                continue

            ctx = self.get_market_context(market_id)
            if not ctx:
                continue

            snapshot = self.get_market_order_book(ctx)
            # Add market metadata
            snapshot.update({
                'question': market.get('question'),
                'category': market.get('category'),
                'resolution_time': market.get('resolution_time'),
            })

            # Compute imbalance if we have sizes
            if snapshot['bid_size'] and snapshot['ask_size']:
                snapshot['imbalance'] = self.calculate_imbalance(
                    snapshot['bid_size'], snapshot['ask_size']
                )
            else:
                snapshot['imbalance'] = None

            snapshots.append(snapshot)

        logger.info(f"Collected {len(snapshots)} market snapshots")
        return snapshots

    def save_snapshots(self, snapshots: List[Dict]):
        """Append snapshots to today's JSONL file."""
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        filepath = self.output_dir / f"{today}.jsonl"

        with open(filepath, 'a') as f:
            for s in snapshots:
                f.write(json.dumps(s) + '\n')

        logger.info(f"Appended {len(snapshots)} records to {filepath}")

    def run_loop(self, interval_seconds: int = 15):
        """Main collection loop."""
        logger.info(f"Starting Simmer collector (interval={interval_seconds}s)")
        try:
            while True:
                try:
                    snapshots = self.snapshot_all_markets(window="5")
                    if snapshots:
                        self.save_snapshots(snapshots)
                    time.sleep(interval_seconds)
                except KeyboardInterrupt:
                    logger.info("Shutting down")
                    break
                except Exception as e:
                    logger.error(f"Loop error: {e}")
                    time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Collector stopped")


def main():
    api_key = os.getenv("SIMMER_API_KEY")
    if not api_key:
        logger.error("SIMMER_API_KEY not set in environment")
        return

    collector = SimmerCollector(api_key)
    collector.run_loop(interval_seconds=15)


if __name__ == "__main__":
    main()