---
name: content-performance-tracker
description: "Pull real YouTube view/like counts (and, opt-in, X engagement) for shipped content and write them straight into the outcomes log — closes the loop content-opportunity-scout and content-repurposer's calibration reads, without typing numbers in by hand."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Content-Strategy, Analytics, YouTube, X, Calibration, Creator]
    related_skills: [content-opportunity-scout, content-repurposer]
---

# Content Performance Tracker

`content-opportunity-scout` and `content-repurposer` both learn from an
outcomes log — but only if something actually writes real numbers into it.
Without this skill, that means typing view counts in by hand after every
video, which nobody keeps up with for long. This skill fetches the real
numbers itself and writes them in the same format those two skills already
read.

**What this is not:** model retraining. It's a scheduled or on-demand data
pull that writes plain JSONL entries — the same log format, same
`calibrate.py`, same disclosed-not-silent rule those two skills already
follow.

## When to Use

- "Check how [video] did" / "pull the numbers on that Shorts I posted"
- "Update my outcomes log" / "log the performance on what I shipped this week"
- Periodically (daily/weekly), to keep calibration current without manual entry

## Cost — read this before setting anything up

- **YouTube: free.** `videos.list` costs 1 quota unit per call (up to 50
  video IDs per call) against a 10,000-unit/day default ceiling. At any
  personal-channel volume this never comes close to the limit.
- **X: NOT free.** As of February 2026 the X API v2 moved new developers to
  pay-per-use — about **$0.005 per post read**. `scripts/pull_x_stats.py`
  defaults to a dry run that only prints the read count and dollar estimate;
  it will not spend anything until you pass `--confirm-spend`. Treat X
  tracking as opt-in, and only for posts you explicitly list — this skill
  never searches or bulk-discovers posts on its own.
- If tracking X regularly, put the bearer token behind a spend-limited key
  if the provider offers one, and confirm auto-recharge is off wherever
  it's billed — this skill can show you the estimate, it can't enforce a
  spend cap on its own.

## Setup

1. **YouTube Data API v3 key** (free): Google Cloud Console → enable
   "YouTube Data API v3" → create an API key. Set `YOUTUBE_API_KEY`.
2. **X bearer token** (optional, paid — see **Cost** above): only set
   `X_API_BEARER_TOKEN` if you've decided the per-read cost is worth it.
3. **Shared paths**: reuse the same `outcomes.jsonl` and reuse (or start) a
   `baseline.json` next to it — see `references/baseline-methodology.md`
   for what that file is and why classification needs it.
4. **A shipped-items list**: this skill doesn't discover what you've
   published — you (or another skill) hand it a small JSON file of
   `{topic, video_id/post_id, format, date}` entries to check. If you also
   run `content-opportunity-scout`, its opportunities log is a natural
   source for what's been briefed and likely shipped; ask the user to
   confirm what actually went out before checking it.

## Procedure

### Phase 1 — Build the shipped-items list

Ask (or infer from the opportunities log, then confirm) which videos/posts
to check this run, each tagged with its **format** (`long`, `shorts`,
`thread`, `single_post`, etc. — format matters because baselines are
per-format, see `references/baseline-methodology.md`). Write it to a small
JSON file matching the schema in `scripts/pull_youtube_stats.py`'s or
`scripts/pull_x_stats.py`'s docstring.

### Phase 2 — Pull YouTube (default: just do it, it's free)

```bash
python scripts/pull_youtube_stats.py shipped.json \
  --baseline baseline.json --log outcomes.jsonl --append
```

Run without `--append` first if you want to eyeball the classification
before it's written.

### Phase 3 — Pull X (only if the user has opted in)

Always show the dry-run estimate first, unprompted:

```bash
python scripts/pull_x_stats.py shipped.json --baseline baseline.json --log outcomes.jsonl
```

That prints the read count and dollar estimate and spends nothing. Only
re-run with `--confirm-spend --append` after the user has seen the number
and said to proceed — never skip straight to `--confirm-spend` on your own.

### Phase 4 — Report what changed

Summarize what got logged: which items were newly classified (hit/ok/flop),
which came back `insufficient_baseline` (say so plainly — that's not a
flop, just not enough history yet), and which were skipped because they
were already in the log (dedup by `external_id`, automatic).

## Quick Reference

| Task | Command |
|---|---|
| Pull YouTube stats, preview only | `python scripts/pull_youtube_stats.py shipped.json --baseline baseline.json` |
| Pull YouTube stats, write to log | add `--log outcomes.jsonl --append` |
| Estimate X pull cost (spends nothing) | `python scripts/pull_x_stats.py shipped.json` |
| Actually pull X stats + write to log | add `--confirm-spend --append --baseline baseline.json --log outcomes.jsonl` |

## Pitfalls

- **Don't guess a classification with too little history.** Both scripts
  return `insufficient_baseline` (stored as `performance: null`) below 3
  same-format samples — never override that with a manual "ok" just to fill
  the field.
- **Don't mix formats in one baseline.** A Shorts view count and a
  long-form view count aren't comparable; each format keeps its own window
  in `baseline.json`.
- **Don't auto-spend on X.** `--confirm-spend` is a human decision, made
  after seeing the dry-run estimate — never default to it, never skip
  straight to it in an unattended run.
- **Don't re-fetch what's already logged.** Both scripts dedupe by
  `external_id` automatically — if a run seems to be re-pulling the same
  video every time, the log path is probably wrong, not the dedup logic.
- **`performance: null` is not a flop.** Say so explicitly when reporting
  results — a middling video and an unclassified-for-now video are
  different things and `calibrate.py` already treats them differently.

## Verification

Before reporting a run as complete, confirm: every newly-logged entry has a
`metric_value` that's a real, non-zero number the API actually returned
(not a fallback like 0 masking a failed lookup — both scripts print to
stderr, not silently skip, when a video/post ID doesn't resolve), and that
`already_logged` entries were genuinely skipped rather than duplicated.
