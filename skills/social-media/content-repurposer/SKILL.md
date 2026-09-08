---
name: content-repurposer
description: "Turn one long-form piece (video, transcript, blog, newsletter) into native, platform-fit versions for X, LinkedIn, Instagram, and Shorts/Reels/TikTok — not copy-paste, reshaped and re-hooked per platform."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Content-Strategy, Repurposing, Cross-Platform, YouTube, X, LinkedIn, Instagram, Shorts]
    related_skills: [youtube-content, content-opportunity-scout, content-performance-tracker]
    requires_toolsets: [web]
---

# Content Repurposer

Takes one source (a video, its transcript, a blog post, a newsletter, a
script) and produces genuinely native versions for other platforms — each
with its own hook, its own structure, and its own length — instead of the
same paragraph pasted five times with different headers on top. That
copy-paste version is what this skill exists to avoid.

## When to Use

- "Repurpose this video/post for other platforms"
- "Turn this into an X thread / LinkedIn post / Shorts script"
- "Break this down for [platform]"
- "What else can I get out of this piece of content"
- Right after `content-opportunity-scout` ships a brief and the user has now
  recorded/written the long-form piece — this is the next step

## Prerequisites

- `web` toolset (`web_search`, `web_extract`) — only needed if the source is
  a URL rather than pasted text
- For a YouTube source, use the **`youtube-content`** skill first to pull
  the transcript (`scripts/fetch_transcript.py --text-only --timestamps`)
  — don't re-implement transcript fetching here
- No API keys required otherwise

## Setup — voice & platform context

Before writing anything, establish:

1. **Voice/audience** — if the user already has a `content-opportunity-scout`
   profile (see that skill's `references/profile.template.md`), reuse its
   Voice/Tone, Audience, and Formats sections instead of asking again.
   Otherwise ask: which platforms do they actually post to, and how would
   they describe their voice in a few words?
2. **Target platforms** — ask which of X, LinkedIn, Instagram,
   Shorts/Reels/TikTok, and newsletter/blog they want. Don't generate all
   five by default if the user only posts to two — that's noise, not help.
3. **Calibration (skip on first run)** — run
   `python scripts/calibrate.py ~/.hermes/content-scout/outcomes.jsonl`.
   If it returns real notes (not "insufficient data"), state them and use
   them to inform Phase 2's idea-to-platform mapping and which hook family
   to reach for first — never to skip a platform the user asked for.

## Procedure

### Phase 1 — Extract the core ideas

Read the full source and pull out **3-6 core ideas**, not chronological
chunks. Each core idea needs:

- The claim/insight in one sentence
- The strongest proof point from the source (a stat, example, quote, or
  demo moment) — this is what makes the repurposed post credible instead
  of generic
- Why someone would actually care (the emotional or practical stake)

If the source doesn't yield at least 3 distinct ideas, say so — don't
manufacture filler ideas just to hit a number.

### Phase 2 — Map ideas to platforms

Not every idea fits every platform. Build a quick matrix: which 1-2 core
ideas are strongest for which target platform, based on
`references/platform-specs.md`. A dense technical proof point might be the
LinkedIn post; the single most surprising line might be the Shorts hook;
a contrarian take might be the X thread opener. Picking the right idea per
platform matters more than reformatting the same one everywhere.

### Phase 3 — Write native versions

For each target platform, using `references/platform-specs.md` for
length/structure rules and pulling from the same hook families used by
`content-opportunity-scout` (curiosity gap, contrarian take, receipts/data,
stolen lesson, negative frame) so the opener actually earns the click:

- **X/Twitter thread**: hook tweet (the single strongest line, under 280
  chars, no "thread 🧵" throat-clearing), 3-7 follow-up tweets each making
  one point, closing tweet with a clear CTA
- **LinkedIn post**: story or contrarian-take lead in the first ~210
  characters (that's what's visible before "see more"), short paragraphs,
  one idea developed with the proof point, no hashtag spam
- **Instagram carousel**: a title slide with the hook, 4-8 content slides
  (one point per slide, terse), a caption that adds context the slides
  don't repeat, first ~125 caption characters doing the hook's job again
- **Shorts/Reels/TikTok script**: hook line in the first 3 seconds (write
  the literal words spoken), a beat-by-beat script with on-screen text
  cues, staying under ~60 seconds of spoken content
- **Newsletter/blog recap**: a section that stands alone for someone who
  hasn't seen the original — subject line under ~60 chars, a lead that
  states the payoff before the explanation

Skip any platform the user didn't ask for.

### Phase 4 — Validate

Run `scripts/check_platform_limits.py` against the drafted copy to catch
hard failures before they cost the user a rewrite: over the character
limit, a Shorts script that actually runs long at natural speaking pace,
a LinkedIn hook that gets cut off mid-sentence at the "see more" fold.

```bash
python scripts/check_platform_limits.py drafts.json
```

Then do the judgment pass `references/quality-checklist.md` covers — the
script catches length, not quality.

### Phase 5 — Package & log

Return one packet with every platform version clearly labeled, plus the
source ideas they came from (so the user can sanity-check the mapping).
If the user also runs `content-opportunity-scout`, offer to append this
topic to that skill's opportunities log as shipped — keeps the two skills
from ever suggesting or re-repurposing the same thing.

### Phase 6 — Record outcomes (whenever the user reports back)

A separate, later step: when the user says how a repurposed post actually
performed once posted, append one line per platform to the outcomes log
(`references/outcomes-log-format.md`). This is what Phase 0's calibration
step reads next time — ask for this follow-up when it's been a while
since a packet shipped and nothing's been logged yet.

## Getting better over time

Not model retraining — a feedback log. `scripts/calibrate.py` reports hit
rates per platform or hook family once at least 5 shipped outcomes exist
for a group (fewer than that, it says so instead of guessing), and any
note it produces gets stated in the packet's output, never applied
silently. See `references/outcomes-log-format.md` for the schema — the
same log file can be shared with `content-opportunity-scout` since a
piece of content's scouting, repurposing, and real-world performance is
one continuous story.

## Quick Reference

| Phase | Tool | Output |
|---|---|---|
| 0. Setup | Read profile + `scripts/calibrate.py` | Voice/platform context, disclosed calibration lean |
| 1. Extract | manual read of source | 3-6 core ideas w/ proof points |
| 2. Map | manual, `platform-specs.md` | idea → platform matrix |
| 3. Write | manual, hook families | Native draft per target platform |
| 4. Validate | `scripts/check_platform_limits.py` | Pass/fail on length & pacing |
| 5. Package | manual | Labeled packet, optional log entry |
| 6. Record outcomes | append to outcomes log | Feeds next run's calibration |

## Pitfalls

- **Copy-paste repurposing** — the same paragraph under five different
  headers is not repurposing, it's reformatting, and audiences on a second
  platform can tell. Every version needs its own hook and its own shape.
- **Wrong idea for the platform** — the most quotable line isn't always the
  best LinkedIn hook, and the most data-dense point isn't a good Shorts
  script. Match idea to platform in Phase 2 before writing.
- **Ignoring the fold** — LinkedIn and Instagram both truncate hard; a hook
  that pays off on the 4th sentence is wasted if the fold cuts at the 2nd.
- **Shorts scripts that run long** — spoken word count, not read time,
  determines whether a script fits 60 seconds. Always check with the
  script's pacing estimate, don't eyeball it.
- **Hashtag/CTA spam** — one clear CTA per post beats three vague ones;
  same for hashtags on Instagram (3-5 relevant beats 20 generic).

## Verification

Before returning the packet, confirm: every requested platform has a
draft, every draft passed `check_platform_limits.py`, no two platforms
share an identical hook line, and every claim in the drafts traces back to
something actually in the source (no invented stats or examples).
