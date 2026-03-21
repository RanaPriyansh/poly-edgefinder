"""
Direct Polymarket CLOB data collection (without Simmer).

Uses py_clob_client to fetch order books directly.
Requires wallet private key for API derivation (but no real trades).
"""

import os
import json
import time
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Optional

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import BalanceAllowanceParams, AssetType
from py_order_utils.model import POLY_PROXY

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class PolymarketDirectCollector:
    def __init__(self, private_key: str, wallet_address: str = None, output_dir: str = "data/raw"):
        self.private_key = private_key
        self.wallet_address = wallet_address

        self.client = ClobClient(
            host="https://clob.polymarket.com",
            key=private_key,
            chain_id=137,  # Polygon
            funder=wallet_address,
            signature_type=POLY_PROXY,
        )
        # Derive API credentials
        self.client.set_api_creds(self.client.create_or_derive_api_creds())

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_all_markets(self) -> List[Dict]:
        """Fetch all active markets from Polymarket."""
        try:
            markets = self.client.get_markets()
            logger.info(f"Fetched {len(markets)} markets from Polymarket")
            return markets
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []

    def filter_btc_5min(self, markets: List[Dict]) -> List[Dict]:
        """Filter to BTC 5-minute up/down markets."""
        filtered = []
        for m in markets:
            question = m.get('question', '').lower()
            # Must contain btc and 5 min
            if 'btc' in question and ('5 min' in question or '5-minute' in question or '5min' in question):
                # Must be active (not closed/resolved)
                if m.get('closed', False):
                    continue
                filtered.append(m)
        logger.info(f"Filtered to {len(filtered)} BTC 5-min markets")
        return filtered

    def get_order_book(self, token_id: str) -> Optional[Dict]:
        """Fetch order book for a specific token."""
        try:
            book = self.client.get_order_book(token_id)
            return {
                'bids': [(b.price, b.size) for b in book.bids],
                'asks': [(a.price, a.size) for a in book.asks],
            }
        except Exception as e:
            logger.debug(f"Error fetching order book for {token_id}: {e}")
            return None

    def snapshot_market(self, market: Dict) -> Dict:
        """Take a full snapshot of one market."""
        market_id = market.get('id')
        try:
            # Get order book
            book = self.get_order_book(market_id)

            snapshot = {
                'timestamp': time.time(),
                'dt': datetime.datetime.utcnow().isoformat(),
                'market_id': market_id,
                'question': market.get('question'),
                'tokens': market.get('tokens', []),
                'resolution_time': market.get('resolution_time'),
                'category': market.get('category'),
            }

            if book:
                # Extract best bid/ask
                best_bid = book['bids'][0] if book['bids'] else (None, 0)
                best_ask = book['asks'][0] if book['asks'] else (None, 0)

                snapshot.update({
                    'best_bid_price': best_bid[0],
                    'best_bid_size': best_bid[1],
                    'best_ask_price': best_ask[0],
                    'best_ask_size': best_ask[1],
                })

                # Compute spread and imbalance
                if best_bid[0] and best_ask[0]:
                    snapshot['spread'] = best_ask[0] - best_bid[0]
                    snapshot['mid_price'] = (best_bid[0] + best_ask[0]) / 2
                    total_size = best_bid[1] + best_ask[1]
                    if total_size > 0:
                        snapshot['imbalance'] = (best_bid[1] - best_ask[1]) / total_size
                    else:
                        snapshot['imbalance'] = 0.0
                else:
                    snapshot['spread'] = None
                    snapshot['mid_price'] = None
                    snapshot['imbalance'] = None
            else:
                snapshot.update({
                    'best_bid_price': None,
                    'best_bid_size': 0,
                    'best_ask_price': None,
                    'best_ask_size': 0,
                    'spread': None,
                    'mid_price': None,
                    'imbalance': None,
                })

            return snapshot

        except Exception as e:
            logger.error(f"Error snapshotting market {market_id}: {e}")
            return {
                'timestamp': time.time(),
                'dt': datetime.datetime.utcnow().isoformat(),
                'market_id': market_id,
                'error': str(e),
            }

    def snapshot_all(self) -> List[Dict]:
        """Snapshot all BTC 5-min markets."""
        markets = self.get_all_markets()
        btc_5min = self.filter_btc_5min(markets)

        snapshots = []
        for market in btc_5min:
            snap = self.snapshot_market(market)
            snapshots.append(snap)

        logger.info(f"Snapshotted {len(snapshots)} BTC 5-min markets")
        return snapshots

    def save_snapshots(self, snapshots: List[Dict]):
        """Append to today's JSONL file."""
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        filepath = self.output_dir / f"{today}.jsonl"

        with open(filepath, 'a') as f:
            for s in snapshots:
                f.write(json.dumps(s) + '\n')

        logger.info(f"Saved {len(snapshots)} records to {filepath}")

    def run_loop(self, interval_seconds: int = 15):
        """Main loop."""
        logger.info(f"Starting Polymarket direct collector (interval={interval_seconds}s)")
        try:
            while True:
                try:
                    snapshots = self.snapshot_all()
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
    pk = os.getenv("POLYMARKET_WALLET_PRIVATE_KEY")
    if not pk:
        logger.error("POLYMARKET_WALLET_PRIVATE_KEY not set")
        return

    wallet = os.getenv("POLYMARKET_WALLET_ADDRESS")  # optional

    collector = PolymarketDirectCollector(pk, wallet)
    collector.run_loop(interval_seconds=15)


if __name__ == "__main__":
    main()