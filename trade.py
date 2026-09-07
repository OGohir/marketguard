# ---------------------------------------------------------------------------
# NORMALIZED TRADE MODEL
#
# Coinbase and Kraken send trade information in different formats.
#
# This file creates ONE standard format that MarketGuard will use internally.
#
# Every trade, no matter which exchange it came from, will contain:
# - exchange      -> where the trade came from
# - symbol        -> what was traded, such as BTC-USD
# - trade_id      -> unique ID for that trade
# - price         -> price the trade happened at
# - quantity      -> amount of BTC traded
# - side          -> buy or sell
# - event_time    -> when the trade happened at the exchange
# - received_time -> when MarketGuard received the trade
#
# Flow:
# Coinbase/Kraken raw data -> NormalizedTrade -> rest of MarketGuard
#
# Decimal is used instead of normal floats because financial calculations
# should avoid small floating-point rounding errors.
# ---------------------------------------------------------------------------


from datetime import datetime

from decimal import Decimal

from pydantic import BaseModel


class NormalizedTrade(BaseModel):
    exchange: str
    symbol: str
    trade_id: str
    price: Decimal
    quantity: Decimal
    side: str
    event_time: datetime
    received_time: datetime
