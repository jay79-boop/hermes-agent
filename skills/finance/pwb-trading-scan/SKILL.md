---
name: pwb-trading-scan
description: "Bridge to your pwb-toolbox screeners (crypto_scan, season_scan) — runs your existing scan scripts and relays their output, without reimplementing any screening logic."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Trading, Screener, Finance, pwb-toolbox, Crypto, Seasonality]
---

# PWB Trading Scan

A thin bridge to the screeners already living in your `pwb-toolbox` checkout —
`tools/crypto_scan.py` (evidence-backed crypto momentum) and
`tools/season_scan.py` (statistically-gated seasonality, with permutation
tests, split-half validation, and FDR correction before it calls anything a
pattern). This skill runs those scripts and relays their output. It does not
re-derive signals, does not re-score anything, and does not know better than
the tools it's calling — if either script's output looks wrong, that's a
pwb-toolbox bug to fix over there, not something to patch around here.

## When to Use

- "Any crypto setups worth a look" / "run the crypto scan"
- "What's the seasonality on [ticker]" / "check the season scan"
- "Refresh my seasonal data" / "rebuild the watchlist"

## Boundary — read this before running anything

This skill only runs the **read-only** subcommands listed in **Quick
Reference** below and relays their output close to verbatim. It never places
an order, never calls a broker or execution script, and never sizes a
position. Both screeners already say this about their own output — treat it
as binding, not decoration: a scan result is a candidate for a pre-trade pack
and a paper trade against a locked thesis, not a trade signal by itself.

If asked to size a position, place a trade, or "just buy it": decline, and
point back to pwb-toolbox's own `pre-trade-pack` and `backtest-trust` skills
and its trade journal — those exist specifically to gate that decision, and
this bridge has no business shortcutting them. Never reach for anything under
`tools/ib_server`, `tools/execution`, or `pwb_toolbox/execution` from here.

## Prerequisites

- The `pwb-toolbox` checkout already exists with its own venv already set up.
  This skill doesn't install or repair that — if a command fails on a missing
  package, tell the user to run pwb-toolbox's own setup
  (`.venv\Scripts\python.exe -m pip install -r requirements-dev.txt` from
  that repo, per its `docs/local-checkout.md`) and stop there. Don't try to
  pip-install things from inside this skill.
- Checkout path: **`C:\Users\Gexio\OneDrive\pwb-toolbox`** — the canonical
  one. A second checkout exists at `C:\Users\Gexio\pwb-toolbox` (no
  `OneDrive` in the path) and can be stale; never use it. Always spell the
  full path out in the `cd` rather than assuming the shell's current
  directory.

## How to Run (Windows PowerShell)

Every command starts with the `cd` on its own line.

**Crypto momentum scan** — fetches live, no setup step needed:
```powershell
cd "C:\Users\Gexio\OneDrive\pwb-toolbox"
.\.venv\Scripts\python.exe tools\crypto_scan.py scan --top 8
```

**Seasonality** — first run on a fresh checkout needs `fetch` before
`report` has data to work with:
```powershell
cd "C:\Users\Gexio\OneDrive\pwb-toolbox"
.\.venv\Scripts\python.exe tools\season_scan.py fetch
```
```powershell
cd "C:\Users\Gexio\OneDrive\pwb-toolbox"
.\.venv\Scripts\python.exe tools\season_scan.py report
```

**One ticker's seasonal read** (needs `report` to have run first — reads its
JSON output, doesn't recompute):
```powershell
cd "C:\Users\Gexio\OneDrive\pwb-toolbox"
.\.venv\Scripts\python.exe tools\season_scan.py context AAPL
```

**Overnight vs. intraday split** (also reads `report`'s JSON):
```powershell
cd "C:\Users\Gexio\OneDrive\pwb-toolbox"
.\.venv\Scripts\python.exe tools\season_scan.py overnight
```

## Procedure

1. Pick the screener that answers the question: crypto momentum →
   `crypto_scan`; a calendar/seasonal pattern on a ticker or the whole
   universe → `season_scan`.
2. Run the matching command from **How to Run** — nothing outside `scan`,
   `fetch`, `report`, `context`, `overnight`, `watchlist`.
3. If `season_scan.py report` prints "No data... Run fetch first", that's the
   documented two-step order, not a failure — run `fetch`, then `report`
   again.
4. Relay the output close to verbatim. Both tools already spent real effort
   on presentation — aligned columns, plain-language verdicts like
   "CONVICTED strong month" / "candidate only ({reason})" / "noise; the
   calendar says nothing here". Don't paraphrase a table into prose and lose
   the numbers behind it.
5. Close with the same framing the tools themselves print: a candidate for a
   pre-trade pack and a paper trade against a locked thesis, sized from
   ATR%, never from conviction. If the user wants to act on it, that's the
   next stop — not this skill.

## Quick Reference

| Question | Command |
|---|---|
| Crypto momentum setups today | `tools\crypto_scan.py scan --top 8` |
| Crypto scan, custom universe | `tools\crypto_scan.py scan --symbols BTC-USD ETH-USD --top 5` |
| Refresh seasonality data | `tools\season_scan.py fetch` |
| Full seasonality report (also writes an HTML report + watchlist) | `tools\season_scan.py report` |
| One ticker's seasonal read | `tools\season_scan.py context AAPL` |
| Overnight vs. intraday split | `tools\season_scan.py overnight` |
| Rewrite the TradingView watchlist | `tools\season_scan.py watchlist` |

## Example Output (crypto_scan)

```
BTC regime: risk-on (above 50d, positive 28d)

symbol      score       7d      28d   vs 50d   volume  ATR%/d  setup
------------------------------------------------------------------------
SOL-USD    +1.84   +12.3%   +28.1%    +9.4%    +41.2%    5.8%  breakout, rising volume
...

Ranks are relative to this universe today, not forecasts. Anything here
is a candidate for a pre-trade pack and a paper trade against a locked
thesis — position sized from ATR%, never from conviction.
```

## Pitfalls

- **Don't invent a subcommand.** Both scripts argparse-reject anything
  unlisted — good, but check **Quick Reference** first rather than guessing
  one (`crypto_scan.py trade` doesn't exist).
- **`.venv\Scripts\python.exe`, not a bare `python`.** Running the system
  Python instead of the checkout's venv fails on missing `backtrader`/
  `yfinance`/`pandas` with an import error that looks unrelated to the real
  problem — always the full venv path.
- **Two checkouts exist on this machine.** Only the `OneDrive` one is
  canonical; the other can be stale. Spell the full path out every time,
  never assume the current directory.
- **This skill ends at relaying output.** No position sizing, no order
  placement, no trade approval — those live in pwb-toolbox's own gated
  tools. See **Boundary** above.

## Verification

Confirm the output actually contains scan rows before presenting it as a
finding — both scripts print an explicit failure message on no data
("no symbol had enough history to scan", "No data... Run fetch first",
"{sym} is not in the scan") rather than a silent empty table, so check for
that message rather than assuming any printed text is a valid result.
