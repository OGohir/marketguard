# ---------------------------------------------------------------------------
# MARKETGUARD MAIN PROGRAM + INTERNAL TRADE PIPELINE
#
# - creates one shared queue for normalized trades
# - Coinbase puts its trades into the queue
# - Kraken puts its trades into the same queue
# - the trade processor takes trades out one at a time
# - all 3 jobs run at the same time using asyncio
#
# Flow:
#
# Coinbase ──► NormalizedTrade ──┐
#                                │
#                                ▼
#                           trade_queue
#                                │
#                                ▼
#                         trade_processor
#                                ▲
#                                │
# Kraken ───► NormalizedTrade ───┘
#
# Right now the processor only prints trades.
# Later it will send them to Kafka, P&L, risk, storage, etc.
# ---------------------------------------------------------------------------

import asyncio

from marketguard.exchanges.coinbase import stream_coinbase_trades
from marketguard.exchanges.kraken import stream_kraken_trades


async def process_trades(trade_queue):

    while True:

        # Wait until Coinbase or Kraken puts a trade into the queue.
        trade = await trade_queue.get()

        print(
            f"[{trade.exchange.upper()}] "
            f"{trade.symbol} | "
            f"${trade.price} | "
            f"{trade.quantity} BTC | "
            f"{trade.side.upper()} | "
            f"{trade.event_time}"
        )

        # Tell the queue that this trade finished processing.
        trade_queue.task_done()


async def main():

    print("Starting MarketGuard...\n")

    # Shared conveyor belt for trades from every exchange.
    trade_queue = asyncio.Queue()

    # Run Coinbase, Kraken, and our processor at the same time.
    await asyncio.gather(
        stream_coinbase_trades(trade_queue),
        stream_kraken_trades(trade_queue),
        process_trades(trade_queue),
    )


if __name__ == "__main__":
    asyncio.run(main())
