# Why self-relative, not an absolute threshold

"40,000 views is a hit" means nothing without knowing what normal is for
this channel — a hit for a 2,000-subscriber channel and a flop for a
500,000-subscriber one. Rather than invent a number, this skill ranks every
new video/post against a **rolling window of the same creator's own past
results in the same format** (long-form vs. Shorts, thread vs. single post
— never mix formats in one comparison, they have completely different
normal ranges).

## The window

`baseline.json` stores, per format, the last **20** results (oldest dropped
as new ones arrive). 20 is a judgment call: long enough that a couple of
outlier flops or a lucky viral hit don't swing the whole baseline, short
enough that a channel's baseline actually moves as it grows instead of
comparing this month's video against something from two years ago.

## The tiers

Each new value is ranked against the stored window:

- **hit** — top third of the window
- **ok** — middle third
- **flop** — bottom third

## The honesty rule

Fewer than **3** prior same-format entries in the window: report
`insufficient_baseline` (stored as `performance: null` in the outcomes log,
never guessed as `ok`). Ranking a value against 0-2 prior points isn't a
real comparison — it's a coin flip dressed as data, and `calibrate.py`
already excludes null-performance entries from its hit-rate math for
exactly this reason (see `outcomes-log-format.md` in
`content-opportunity-scout`/`content-repurposer`).

## What this does NOT do

- It does not compare across creators or channels — there's no "good" or
  "bad" in absolute terms, only "better or worse than this channel's own
  recent normal."
- It does not account for external shocks (a video going viral off-platform,
  a post riding a news cycle) — a hit from luck and a hit from a genuinely
  strong idea look identical here. That's fine for calibration purposes
  (both are worth leaning toward more of), just don't over-read a single
  data point as proof of a specific hook or angle working.
- It does not backfill history from before this skill started running — the
  baseline only grows from here forward. A channel with years of past
  videos doesn't get instant context; it takes the first ~3 tracked results
  in a format before this skill can classify anything in that format.
