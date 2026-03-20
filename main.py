import os
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from collections import deque

import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# Import collector
import sys
sys.path.append('src')
from data_collectors.polymarket_direct import PolymarketDirectCollector

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Thielon Edge Finder")

@dataclass
class MarketSignal:
    market_id: str
    question: str
    outcome: str
    probability: float
    imbalance: float
    signal: str  # "BUY_YES", "BUY_NO", "HOLD"
    confidence: float
    timestamp: datetime
    volume: float

class EdgeFinderBot:
    def __init__(self):
        self.private_key = os.getenv("POLYMARKET_WALLET_PRIVATE_KEY")
        self.wallet_address = os.getenv("POLYMARKET_WALLET_ADDRESS")
        self.collector = None
        self.signals: List[MarketSignal] = []
        self.markets_cache: List[Dict] = []
        self.running = False
        self.scan_interval = int(os.getenv("SCAN_INTERVAL_SECONDS", "30"))
        self.imbalance_threshold = float(os.getenv("IMBALANCE_THRESHOLD", "0.2"))
        self.max_signals_history = 1000

    async def initialize(self):
        """Initialize collector with credentials"""
        if not self.private_key:
            logger.warning("No private key provided; collector will not be initialized")
            return False
        try:
            self.collector = PolymarketDirectCollector(
                private_key=self.private_key,
                wallet_address=self.wallet_address,
                output_dir="data/raw"
            )
            # Test connection
            markets = self.collector.get_all_markets()
            logger.info(f"Collector initialized. Found {len(markets)} total markets.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize collector: {e}")
            return False

    async def scan(self):
        """Perform one scan cycle"""
        if not self.collector:
            return

        try:
            # Fetch all markets
            all_markets = self.collector.get_all_markets()
            self.markets_cache = all_markets

            # Filter to BTC 5min (and 15min later)
            btc_markets = self._filter_btc_markets(all_markets)
            logger.info(f"Filtered to {len(btc_markets)} BTC markets")

            # Generate signals
            new_signals = []
            for market in btc_markets:
                signal = await self._analyze_market(market)
                if signal and signal.signal != "HOLD":
                    new_signals.append(signal)
                    logger.info(f"Signal: {signal.market_id} {signal.signal} imbalance={signal.imbalance:.3f}")

            # Update signals history
            self.signals.extend(new_signals)
            if len(self.signals) > self.max_signals_history:
                self.signals = self.signals[-self.max_signals_history:]

            logger.info(f"Scan complete. {len(new_signals)} new signals.")
        except Exception as e:
            logger.error(f"Scan error: {e}")

    def _filter_btc_markets(self, markets: List[Dict]) -> List[Dict]:
        """Filter to BTC 5-minute and 15-minute markets"""
        filtered = []
        for m in markets:
            question = m.get('question', '').lower()
            if 'btc' not in question:
                continue
            # Include 5min or 15min
            if any(x in question for x in ['5 min', '5-minute', '5min', '15 min', '15-minute', '15min']):
                # Must be active
                if m.get('closed', False):
                    continue
                filtered.append(m)
        return filtered

    async def _analyze_market(self, market: Dict) -> Optional[MarketSignal]:
        """Analyze a single market and generate signal"""
        market_id = market.get('id')
        question = market.get('question', '')

        # Get order book
        book = self.collector.get_order_book(market_id)
        if not book:
            return None

        # Extract best bid/ask for YES token
        bids = book.get('bids', [])
        asks = book.get('asks', [])

        if not bids or not asks:
            return None

        best_bid_price, best_bid_size = bids[0]
        best_ask_price, best_ask_size = asks[0]

        # Calculate order book imbalance
        total_size = best_bid_size + best_ask_size
        if total_size == 0:
            return None
        imbalance = (best_bid_size - best_ask_size) / total_size

        # Current YES probability from mid price
        mid_price = (best_bid_price + best_ask_price) / 2

        # Determine signal
        signal_type = "HOLD"
        confidence = 0.0

        if imbalance > self.imbalance_threshold:
            signal_type = "BUY_YES"
            confidence = min(1.0, imbalance * 2)
        elif imbalance < -self.imbalance_threshold:
            signal_type = "BUY_NO"
            confidence = min(1.0, abs(imbalance) * 2)

        if signal_type == "HOLD":
            return None

        # Get volume
        volume = float(market.get('volume', 0))

        return MarketSignal(
            market_id=market_id,
            question=question,
            outcome="YES" if signal_type == "BUY_YES" else "NO",
            probability=mid_price,
            imbalance=imbalance,
            signal=signal_type,
            confidence=confidence,
            timestamp=datetime.utcnow(),
            volume=volume
        )

    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            "initialized": self.collector is not None,
            "markets_cached": len(self.markets_cache),
            "signals_generated": len(self.signals),
            "last_scan": datetime.utcnow().isoformat() if self.running else None,
        }

    def get_recent_signals(self, limit: int = 50) -> List[Dict]:
        """Get recent signals"""
        recent = self.signals[-limit:] if self.signals else []
        return [asdict(s) for s in recent]

    def get_markets_with_signals(self) -> List[Dict]:
        """Get markets with latest signals"""
        # Create a map of market_id -> signal
        signal_map = {s.market_id: s for s in self.signals[-100:]}
        result = []
        for m in self.markets_cache[-100:]:
            market_id = m.get('id')
            if market_id in signal_map:
                s = signal_map[market_id]
                result.append({
                    "market_id": market_id,
                    "question": m.get('question'),
                    "probability": s.probability,
                    "volume": s.volume,
                    "signal": s.signal,
                    "confidence": s.confidence,
                    "imbalance": s.imbalance
                })
        return result

bot = EdgeFinderBot()

@app.get("/")
async def root():
    return {"status": "ok", "service": "thielon-edgefinder", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
async def health():
    initialized = await bot.initialize()
    if not initialized:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "reason": "collector not initialized"})
    return {"status": "healthy"}

@app.get("/status")
async def status():
    return bot.get_status()

@app.get("/signals")
async def signals(limit: int = 50):
    return {"signals": bot.get_recent_signals(limit)}

@app.get("/markets")
async def markets():
    return {"markets": bot.get_markets_with_signals()}

async def background_scanner():
    """Background scanning loop"""
    await bot.initialize()
    bot.running = True
    while True:
        try:
            await bot.scan()
        except Exception as e:
            logger.error(f"Background scan failed: {e}")
        await asyncio.sleep(bot.scan_interval)

@app.on_event("startup")
async def startup():
    asyncio.create_task(background_scanner())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)