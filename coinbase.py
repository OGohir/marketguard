# ---------------------------------------------------------------------------
# COINBASE LIVE MARKET DATA + NORMALIZATION
#
# - connects to Coinbase live BTC-USD trades
# - converts Coinbase data into our NormalizedTrade format
# - changes Coinbase maker-side into our standard taker-side
# - sends each finished trade into MarketGuard's shared trade queue
#
# Flow:
# Coinbase -> WebSocket -> JSON -> NormalizedTrade -> trade_queue
# ---------------------------------------------------------------------------

import json

from datetime import datetime, timezone

import websockets

from marketguard.models.trade import NormalizedTrade


COINBASE_WEBSOCKET_URL = "wss://advanced-trade-ws.coinbase.com"


async def stream_coinbase_trades(trade_queue):

    print("Connecting to Coinbase...")

    async with websockets.connect(COINBASE_WEBSOCKET_URL) as websocket:

        print("Connected to Coinbase!")

        subscribe_message = {
            "type": "subscribe",
            "product_ids": ["BTC-USD"],
            "channel": "market_trades",
        }

        await websocket.send(json.dumps(subscribe_message))

        print("Listening for Coinbase BTC-USD trades...\n")

        async for message in websocket:

            data = json.loads(message)

            events = data.get("events", [])

            for event in events:

                trades = event.get("trades", [])

                for trade in trades:

                    maker_side = trade.get("side")

                    # Coinbase gives us the maker side.
                    # We flip it so MarketGuard stores the taker side.
                    if maker_side == "BUY":
                        normalized_side = "sell"

                    elif maker_side == "SELL":
                        normalized_side = "buy"

                    else:
                        normalized_side = "unknown"

                    normalized_trade = NormalizedTrade(
                        exchange="coinbase",
                        symbol="BTC-USD",
                        trade_id=str(trade.get("trade_id")),
                        price=trade.get("price"),
                        quantity=trade.get("size"),
                        side=normalized_side,
                        event_time=trade.get("time"),
                        received_time=datetime.now(timezone.utc),
                    )

                    # Put the finished trade onto MarketGuard's shared queue.
                    await trade_queue.put(normalized_trade)
