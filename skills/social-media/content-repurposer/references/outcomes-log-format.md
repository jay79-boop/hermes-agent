# Outcomes Log — How This Skill Gets Better Over Time

Be precise with the user about what this is: **not** model training, not
weight updates — a plain feedback log that `scripts/calibrate.py` reads to
find patterns in what has actually worked, so future runs lean toward
those patterns instead of treating every run as if it were the first.
It's bounded, always disclosed, and never silently overrides what the
user asked for.

## The log

One JSONL file, one line per real-world outcome. Share the same file with
`content-opportunity-scout`'s outcomes log if the user runs both skills —
a piece of content's lifecycle (scouted → repurposed → posted → performed)
is one story, not two unrelated logs.

Default path suggestion: `~/.hermes/content-scout/outcomes.jsonl`.

### Entry schema (all fields optional except `date` and `topic`)

```json
{
  "date": "2026-09-08",
  "topic": "AI trading bot backtests going viral",
  "platform": "shorts",
  "hook_family": "receipts",
  "shipped": true,
  "performance": "hit",
  "metric_type": "views",
  "metric_value": 42000
}
```

- `platform`: which repurposed version this entry is about (`x`,
  `linkedin`, `instagram`, `shorts`, `newsletter`, `youtube`)
- `hook_family`: which hook pattern that platform's draft used
- `performance`: `hit` / `ok` / `flop` — the user's own call, trust it
  over any metric if they disagree. Can also be JSON `null` — see below.
- `metric_type`/`metric_value`: optional, whatever the user tracks
- `external_id`: the platform's own ID for the post (a YouTube video ID, an
  X post ID) — only present on entries `content-performance-tracker` wrote
  automatically. Used to dedupe: that skill never re-fetches or re-logs the
  same ID.
- `performance: null` — written by `content-performance-tracker` when a new
  post doesn't yet have enough same-format history to rank against. This is
  NOT the same as a flop: `calibrate.py`'s `hit_rate()` excludes null
  entries from both the numerator and denominator so an unclassified entry
  never quietly deflates the rate.

## Auto-filling this log

`content-performance-tracker` (a separate skill) can fill this log
automatically instead of typing outcomes in by hand: point it at shipped
YouTube videos and/or X posts and it pulls real numbers, classifies them
against a rolling per-format baseline, and appends entries here. This skill
doesn't require it — manual entries work exactly the same.

## How calibration uses it

`scripts/calibrate.py --group-by platform` (or `--group-by hook_family`)
reports each group's hit rate, but only acts on groups with **at least 5
shipped entries** — below that it reports insufficient data. Above that,
a meaningfully above/below-average group produces a one-line note (e.g.
"shorts drafts using the contrarian hook are hitting 75% vs a 40% overall
average across 8 shipped posts") that Phase 2/3 uses to reach for that
combination first — stated out loud in the packet, never applied silently,
and never used to skip a platform the user explicitly asked for.

## Recording an outcome

```bash
python3 -c "
import json
entry = {'date': '2026-09-08', 'topic': 'TOPIC', 'platform': 'shorts', 'hook_family': 'receipts', 'shipped': True, 'performance': 'hit', 'metric_type': 'views', 'metric_value': 42000}
open('OUTCOMES_LOG_PATH', 'a').write(json.dumps(entry) + '\n')
"
```
