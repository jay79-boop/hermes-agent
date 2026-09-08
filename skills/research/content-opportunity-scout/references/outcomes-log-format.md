# Outcomes Log — How These Skills Get Better Over Time

Be precise with the user about what this is: **not** model training, not
weight updates — a plain feedback log that `scripts/calibrate.py` reads to
find patterns in what has actually worked, so future runs weight scanning
and scoring toward those patterns instead of treating every run as if it
were the first. It's bounded and disclosed, never a silent behavior change.

## The log

One JSONL file, one line per real-world outcome, appended to whenever the
user reports back on a briefed idea (or a repurposed post) that actually
shipped. Same file can be shared with the `content-repurposer` skill's
calibration — a piece of content's lifecycle (scouted → repurposed →
posted → performed) is one story, not two unrelated logs.

Default path suggestion: `~/.hermes/content-scout/outcomes.jsonl`
(same directory as the opportunities log from `profile.template.md`).

### Entry schema (all fields optional except `date` and `topic` — fill in
whatever applies to this skill's part of the pipeline)

```json
{
  "date": "2026-09-08",
  "topic": "AI trading bot backtests going viral",
  "niche": "no-code AI automation",
  "source_type": "youtube",
  "hook_family": "receipts",
  "composite_score": 8.15,
  "shipped": true,
  "performance": "hit",
  "metric_type": "views",
  "metric_value": 42000
}
```

- `performance`: one of `hit`, `ok`, `flop` — the user's own qualitative
  call, always trust their read over the metric if they disagree
- `metric_type`/`metric_value`: optional, whatever the user tracks (views,
  watch time, replies, saves, sign-ups)
- `source_type`/`composite_score`: filled in when the idea came from
  `content-opportunity-scout`
- `hook_family`/(a `platform` field, defined in `content-repurposer`'s
  copy of this doc): filled in when reporting on a repurposed post
- `external_id`: the platform's own ID for the shipped item (a YouTube
  video ID, an X post ID) — only present on entries written by
  `content-performance-tracker`. Used to dedupe: that skill never fetches
  or logs the same ID twice.
- `performance` can also be JSON `null`, not just `hit`/`ok`/`flop` —
  written by `content-performance-tracker` when there isn't yet enough
  same-format history to classify a new number as relatively good or bad.
  `calibrate.py`'s `hit_rate()` excludes null-performance entries from
  both the numerator and denominator, so an unclassified entry never
  quietly drags the rate down the way counting it as a non-hit would.

## Auto-filling this log

Typing outcomes in by hand works, but `content-performance-tracker` (a
separate skill) can fill this log automatically: point it at your shipped
YouTube videos and/or X posts and it pulls real view/engagement numbers
and appends entries here itself, classified against a rolling per-format
baseline instead of an invented absolute threshold. See that skill's
`SKILL.md` if it's installed — this skill doesn't require it, manual entries
work exactly the same.

## How calibration uses it

`scripts/calibrate.py` groups entries by a field (default `source_type`)
and reports each group's hit rate, but only acts on groups with **at least
5 shipped entries** — below that, it reports "insufficient data" rather
than a misleadingly confident number. Above that threshold, if a group's
hit rate is meaningfully above or below the overall average, calibration
surfaces a one-line note (e.g. "reddit-sourced ideas are hitting 80% vs a
45% overall average across 7 shipped ideas") that Phase 0.5 uses to lean
scanning effort and scoring slightly toward what's working — never to
override the rubric, and always stated out loud in the run's output so the
user can see and veto the adjustment.

## Recording an outcome

At the end of a run, or whenever the user mentions how a past idea did,
append one line to the log:

```bash
python3 -c "
import json
entry = {'date': '2026-09-08', 'topic': 'TOPIC', 'source_type': 'youtube', 'shipped': True, 'performance': 'hit', 'metric_type': 'views', 'metric_value': 42000}
open('OUTCOMES_LOG_PATH', 'a').write(json.dumps(entry) + '\n')
"
```

Or just append the JSON line directly — no dependency beyond stdlib.
