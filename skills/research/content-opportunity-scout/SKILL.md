---
name: content-opportunity-scout
description: "Scan trends, competitor content, and audience signals across your niche, score each candidate for leverage, and turn the winners into ready-to-shoot briefs with hooks and angles."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Content-Strategy, Trend-Research, YouTube, Social-Media, Opportunity-Scouting, Creator]
    related_skills: [content-repurposer, content-performance-tracker]
    requires_toolsets: [web]
---

# Content Opportunity Scout

Goes out, finds what is actually moving in your niche right now, throws out
the noise, and hands back a short list of content ideas good enough to shoot
today — each with a hook, an angle, and the receipts to back it up.

This is a **workflow skill**: it doesn't wrap one API, it drives a
scan → filter → score → brief pipeline using the `web_search` / `web_extract`
tools plus the helper script in `scripts/`.

## When to Use

- "Find me video ideas" / "what should I make content about"
- "What's trending in [niche] right now"
- "Scan for content opportunities"
- Run on a schedule (daily/weekly cron job) to keep a running idea backlog
- Before a content batch/planning session, to seed the slate

## Prerequisites

- `web` toolset (`web_search`, `web_extract`) — required
- A filled-out profile — see **Setup** below. Without it the agent has to
  guess your niche and audience, which defeats the point.
- Nothing else. No API keys required for the baseline sources. Optional
  richer sources (YouTube Data API, X API v2, Google Trends API) are noted
  in `references/source-map.md` but are not required — everything works
  through plain search/fetch.

## Setup (one time)

1. Copy `references/profile.template.md` somewhere durable (e.g.
   `~/.hermes/content-scout/profile.md`) and fill it in: niches, audience,
   formats you make, voice, competitors to watch, topics to avoid, and a
   freshness window.
2. Pick a path for the opportunities log — a flat file the agent appends
   accepted ideas to so it never pitches you the same thing twice
   (e.g. `~/.hermes/content-scout/log.jsonl`). It's created automatically
   on first run if missing.
3. Pick a path for the outcomes log (e.g.
   `~/.hermes/content-scout/outcomes.jsonl`) — see **Getting better over
   time** below. This is what lets the skill actually improve instead of
   repeating the same scan forever; skip it and the skill still works,
   it just never calibrates.
4. On every run, read the profile file first. If the user has no profile
   yet, ask 4-5 quick questions (niches, audience, formats, competitors,
   topics to avoid) instead of guessing, then offer to save the answers
   into the template for next time.

## Procedure

### Phase 0 — Load context

Read the profile file and the tail of the opportunities log (last ~50
entries is enough) so you know what's already been pitched and what's
off-limits.

### Phase 0.5 — Calibrate (skip on first run, no history yet)

```bash
python scripts/calibrate.py ~/.hermes/content-scout/outcomes.jsonl
```

If it returns real calibration notes (not "insufficient data"), state them
up front and use them to lean Phase 1's scanning effort and Phase 3's
scoring toward what has actually hit for this user — e.g. spend more scan
budget on a source type with a proven hit rate. Never use it to skip a
source type entirely or to override a rubric score; it's a lean, not a
override. If the log doesn't exist yet or has no shipped entries, say so
in one line and move on — that's expected before the first outcomes are
logged.

### Phase 1 — Multi-source scan

For each niche in the profile, run the query patterns in
`references/source-map.md` across at least 4 independent source types
(e.g. video platform + forum/community + short-form social + news/newsletter).
Never rely on a single source — that's an echo chamber, not research.

For every candidate capture:
- `topic` — the specific angle, not just the broad subject
- `source` + `url`
- `evidence` — the concrete signal (view count, upvotes, comment velocity,
  "X posts about this in the last 48h", a stat, a launch, a controversy)
- `date` — how fresh

Target 15-30 raw candidates before moving on. Fewer than that means the
scan wasn't broad enough — expand source types or query variants.

### Phase 2 — Dedupe & filter

Drop a candidate if any of these are true:
- It (or something functionally identical) is already in the opportunities
  log
- It matches a "topics to avoid" entry in the profile
- It's stale relative to the profile's freshness window
- It has only one weak source and no corroboration

### Phase 3 — Score

Run what's left through `scripts/score_opportunities.py` using the rubric
in `references/scoring-rubric.md` (Trend Velocity, Audience Fit,
Competitive Gap, Durability, Feasibility — each 0-10, weighted). Only
candidates at or above the cutoff in the rubric (default 7.0/10 composite)
move to briefing. If nothing clears the bar, say so plainly instead of
briefing a mediocre idea — a short honest list beats a padded one.

```bash
python scripts/score_opportunities.py candidates.json --log ~/.hermes/content-scout/log.jsonl
```

### Phase 4 — Brief the finalists (default top 5, or fewer if fewer clear the bar)

For each finalist produce:

1. **Working title**
2. **3 hook variants** — pull from different hook families (curiosity gap,
   contrarian take, receipts/data-led, "stolen lesson", negative frame) so
   the user has real options, not three phrasings of the same idea
3. **One-sentence thesis/angle** — the actual point of view, not just the topic
4. **Why now** — the specific evidence from Phase 1, not a vague trend claim
5. **Recommended format + length** (matched to what the profile says the
   user actually makes)
6. **Proof points to cite on-screen** — the sources, so the claim survives a
   fact-check
7. **Risk** — what could make this flop or age badly in a week
8. **Suggested CTA**

### Phase 5 — Output & log

Return a ranked markdown report (finalists first, then a one-line list of
"scanned but didn't clear the bar" for transparency). Append every briefed
finalist to the opportunities log so the next run doesn't repeat it.

### Phase 6 — Record outcomes (whenever the user reports back)

This is a separate, later conversation, not part of every run: whenever
the user mentions how a previously briefed idea actually performed once
shipped, append one line to the outcomes log per
`references/outcomes-log-format.md`. This is what Phase 0.5 reads next
time — the skill only gets better if outcomes actually get logged, so
prompt for this ("how did the trading-bot video do?") when it's been a
while since a finalist was briefed and hasn't been followed up on.

## Getting better over time

This skill does not retrain or fine-tune anything — it's a feedback log,
not a model update. `references/outcomes-log-format.md` defines the
schema and `scripts/calibrate.py` computes hit rates per source type (or
any field) once at least 5 shipped outcomes exist for a group. Below that
threshold it says so plainly instead of guessing. Every calibration note
that changes behavior gets stated in the run's output — this should never
be an invisible adjustment.

## Quick Reference

| Phase | Tool | Output |
|---|---|---|
| 0. Load context | Read profile + log tail | Niche/audience constraints, seen-before list |
| 0.5. Calibrate | `scripts/calibrate.py` | Disclosed lean toward what's historically worked (or "not enough data") |
| 1. Scan | `web_search`, `web_extract` | 15-30 raw candidates w/ evidence |
| 2. Filter | manual | Deduped, on-topic, fresh candidates |
| 3. Score | `scripts/score_opportunities.py` | Composite score per candidate |
| 4. Brief | manual, using `references/scoring-rubric.md` hook families | Full brief per finalist |
| 5. Output | append to log | Ranked report + updated log |
| 6. Record outcomes | append to outcomes log | Feeds next run's calibration |

## Pitfalls

- **Single-source trends** — one viral tweet isn't a trend, it's an anecdote.
  Require corroboration across source types before scoring high on Trend
  Velocity.
- **Bubble scanning** — searching only the user's own niche vocabulary
  misses the exact adjacent-niche crossover that performs best. Vary query
  phrasing, not just topics.
- **Saturated ideas scored high on Velocity alone** — a topic can be
  exploding and still be a bad pick if 50 competitors already covered it.
  That's what Competitive Gap is for; don't let a high Velocity score
  paper over a low Gap score.
- **Recency without durability** — a same-week newsjack has a shelf life;
  say so in the brief instead of presenting it as evergreen.
- **Guessing the audience** — if there's no profile, ask; don't invent a
  niche and audience from the topic alone.

## Verification

Before finalizing, confirm each finalist has at least 2 independent
sources behind its "why now" evidence, and that its Competitive Gap score
was checked against an actual search for existing coverage (not assumed).
State plainly which claims are sourced vs. inferred.
