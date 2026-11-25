"""Tiny SOL trend bot — make.fun bounty entry (bars-replay/v1).

Strategy: per-symbol EMA crossover trend-following on hourly bars, long only.
  - Indicators: EMA(8) fast and EMA(21) slow over each symbol's closes, seeded
    with the mean of the first span of closes. Every batch is read (warm-up
    batches included) so the indicators are already warm when trading starts.
  - Entry (decided on a bar's close, filled at the next open): fast EMA
    crosses above slow EMA, on a symbol not already held. A bar with zero
    volume signals nothing.
  - Exit (whole position): fast EMA crosses back below slow EMA, or the
    position falls 8% from the highest value it has reached since entry
    (trailing stop), or it is worth 150% or more of its cost
    (take-profit +50%). A refused exit is re-sent while its reason
    still holds.
  - Sizing: equity split over 7 slots, capped at the 25% max-weight cap
    and by the cash left in this reply. Sells go first, then buys, in
    universe order, at most max_orders_per_bar orders per reply.
    Slippage is capped at 100 bps (1%) past the close decided on.
  - Deterministic: float64 EMAs, no clock, no environment, no randomness,
    so the two grading runs produce identical action logs.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

FAST_SPAN = 8
SLOW_SPAN = 21
TRAIL_NUM, TRAIL_DEN = 92, 100  # exit at 92% of the position's peak value
TAKE_NUM, TAKE_DEN = 3, 2       # exit at 150% of cost
MAX_SLIPPAGE_BPS = 100
SLOTS = 7


class Ema:
    """One EMA: collects closes until its span is full, then tracks the value."""

    def __init__(self, span):
        self.span = span
        self.warm = []
        self.value = None

    def step(self, close):
        if self.value is not None:
            self.value += (2.0 / (self.span + 1)) * (close - self.value)
            return
        self.warm.append(close)
        if len(self.warm) == self.span:
            self.value = sum(self.warm) / self.span


class Series:
    """Per-symbol indicator state: fast/slow EMAs, last gap, and the exit flag."""

    def __init__(self):
        self.fast = Ema(FAST_SPAN)
        self.slow = Ema(SLOW_SPAN)
        self.gap = None   # fast - slow after the previous bar
        self.now = None   # fast - slow after this bar
        self.down = False  # set on a cross down, held while fast stays below slow

    def push(self, close):
        self.fast.step(close)
        self.slow.step(close)
        self.gap = self.now
        if self.fast.value is not None and self.slow.value is not None:
            self.now = self.fast.value - self.slow.value
        else:
            self.now = None
        if self.now is None or self.now >= 0:
            self.down = False


series = {}
peaks = {}  # symbol -> highest position value seen since entry (quote units)


def should_exit(state, symbol, held, s):
    if s.down:
        return True
    value = state.value(symbol, held.qty)
    if value * TRAIL_DEN <= peaks.get(symbol, value) * TRAIL_NUM:
        return True
    if value * TAKE_DEN >= held.cost * TAKE_NUM:
        return True
    return False


def on_batch(state, batch):
    cross_up = set()
    fresh = set()
    for bar in batch["bars"]:
        symbol = bar["symbol"]
        s = series.setdefault(symbol, Series())
        s.push(float(bar["c"]))
        fresh.add(symbol)
        if s.gap is None or s.now is None or bar.get("v") == "0":
            continue
        if s.now > 0 and s.gap <= 0:
            cross_up.add(symbol)
        if s.now < 0 and s.gap >= 0:
            s.down = True

    if state.warming_up:
        return []

    caps = state.hello["caps"]
    fees = state.hello["fees"]
    for symbol, held in state.positions.items():
        value = state.value(symbol, held.qty)
        if value > peaks.get(symbol, 0):
            peaks[symbol] = value
    for symbol in list(peaks):
        if symbol not in state.positions:
            del peaks[symbol]
    sells = []
    entries = []
    for item in state.hello["symbols"]:
        symbol = item["symbol"]
        if symbol not in fresh:
            continue
        s = series[symbol]
        held = state.positions.get(symbol)
        if held is not None:
            if should_exit(state, symbol, held, s):
                sells.append({
                    "side": "sell", "symbol": symbol, "qty": held.qty,
                    "max_slippage_bps": MAX_SLIPPAGE_BPS,
                })
        elif symbol in cross_up:
            entries.append(symbol)

    orders = sells[: caps["max_orders_per_bar"]]
    stake = state.equity // SLOTS
    by_weight = (caps["max_weight_bps"] * state.equity) // 10_000
    room = SLOTS - len(state.positions)
    cash = state.cash
    for symbol in entries:
        if room <= 0 or len(orders) >= caps["max_orders_per_bar"]:
            break
        size = stake if stake < by_weight else by_weight
        if cash < size:
            size = cash
        if size <= 0 or size < int(fees["min_notional_quote_units"]):
            break
        orders.append({
            "side": "buy", "symbol": symbol, "notional_quote_units": size,
            "max_slippage_bps": MAX_SLIPPAGE_BPS,
        })
        cash -= size
        room -= 1
    return orders


makefun_bars.run(on_batch)
