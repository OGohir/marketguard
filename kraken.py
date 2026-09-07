# ---------------------------------------------------------------------------
# KRAKEN LIVE MARKET DATA + NORMALIZATION
#
# - connects to Kraken live BTC/USD trades
# - converts Kraken data into our NormalizedTrade format
# - changes BTC/USD into MarketGuard's standard BTC-USD name
# - sends every finished trade into the shared trade queue
#
# Flow:
# Kraken -> WebSocket -> JSON -> NormalizedTrade -> trade_queue
# ---------------------------------------------------------------------------

import json

from datetime import datetime, timezone

import websockets

from marketguard.models.trade import NormalizedTrade


KRAKEN_WEBSOCKET_URL = "wss://ws.kraken.com/v2"


async def stream_kraken_trades(trade_queue):

    print("Connecting to Kraken...")

    async with websockets.connect(KRAKEN_WEBSOCKET_URL) as websocket:

        print("Connected to Kraken!")

        subscribe_message = {
            "method": "subscribe",
            "params": {
                "channel": "trade",
                "symbol": ["BTC/USD"],
                "snapshot": False,
            },
        }

        await websocket.send(json.dumps(subscribe_message))

        print("Listening for Kraken BTC-USD trades...\n")

        async for message in websocket:

            data = json.loads(message)

            if data.get("channel") == "trade":

                trades = data.get("data", [])

                for trade in trades:

                    normalized_trade = NormalizedTrade(
                        exchange="kraken",
                        symbol="BTC-USD",
                        trade_id=str(trade.get("trade_id")),
                        price=str(trade.get("price")),
                        quantity=str(trade.get("qty")),
                        side=trade.get("side"),
                        event_time=trade.get("timestamp"),
                        received_time=datetime.now(timezone.utc),
                    )

                    # Put the finished trade onto MarketGuard's shared queue.
                    await trade_queue.put(normalized_trade)
