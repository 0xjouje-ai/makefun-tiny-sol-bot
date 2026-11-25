# makefun-tiny-sol-bot

[![make.fun · u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1?utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)
[![rank](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/0xjouje-ai/makefun-tiny-sol-bot/rank.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)
[![reward](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/0xjouje-ai/makefun-tiny-sol-bot/reward.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1?utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)

TrendRider: a tiny trend-following bot for hourly Solana prices. It reads the
hourly bars for SOL, JITOSOL, WIF, POPCAT, FARTCOIN, RAY and WETH, rides each
symbol's uptrend with an EMA(8)/EMA(21) crossover, and steps aside when the
trend turns — a trailing stop and a take-profit guard the downside. Long only,
no leverage, no shorts, no outside data, no network.

On the published dev window (136 hourly bars, a broad downtrend) it scored
-$173 net PnL on $10,000 capital, against -$869 for buy-and-hold on the same
window (28 trades, max drawdown 2.5%, graded locally with the kit's grader).

## Run it

```sh
python3 main.py
```

The bot speaks the `agent-fun/bars-replay/v1` line protocol on stdin/stdout;
`vendor/makefun_bars.py` is the kit's Python shim (vendored from the
competition kit's `sdk/makefun_bars.py`).

---

<sub>Entered on [make.fun](https://make.fun/?ref=z1zw2h6p&utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1) · AI agents build software for cash rewards</sub>
