# Platform Specs

Hard limits and structural conventions per platform. Hard limits are
enforced by `scripts/check_platform_limits.py`; the rest is judgment.

## X / Twitter thread

- **Hard limit**: 280 characters per tweet (standard accounts)
- **Structure**: hook tweet → 3-7 body tweets, one point each → closing
  tweet with CTA
- **Hook rules**: no "🧵" or "a thread on..." throat-clearing — open with
  the actual claim or question. First 3-4 words matter most (that's what
  shows in a quote-tweet or notification)
- **Numbering**: optional (`1/`, `2/`) — fine either way, be consistent
  within a thread

## LinkedIn post

- **Hard limit**: 3,000 characters
- **Fold**: only the first ~210 characters show before "see more" — the
  hook must fully land inside that window, not just start there
- **Structure**: short paragraphs (1-3 lines), one idea developed with a
  concrete proof point, plain-language CTA at the end
- **Avoid**: hashtag spam (0-3 is plenty), engagement-bait phrasing
  ("agree?"), walls of text with no line breaks

## Instagram (carousel + caption)

- **Caption hard limit**: 2,200 characters
- **Hashtag practical cap**: technically 30, but 3-5 relevant tags
  outperform 20 generic ones
- **Fold**: ~125 characters visible before "more" in feed
- **Carousel**: 4-8 slides after the title slide, one point per slide,
  terse (slides are skimmed, not read line by line)
- **Caption's job**: add context the slides didn't have room for — don't
  just repeat the slide text

## Shorts / Reels / TikTok script

- **Duration cap**: 60 seconds of spoken content for this skill's target
  format (adjust if the user specifies a different length)
- **Pacing estimate**: ~140 words per minute of natural spoken pace, so a
  60-second script tops out around 130-145 words — `check_platform_limits.py`
  estimates this from word count
- **Hook window**: first 3 seconds (roughly the first 6-10 spoken words)
  decide whether the viewer stays — write the literal words, not a
  description of the hook
- **Format**: beat-by-beat script with on-screen text cues noted separately
  from spoken lines

## Newsletter / blog recap

- **Subject line**: keep to ~60 characters so it doesn't truncate in most
  inbox previews
- **Structure**: lead with the payoff/conclusion, then the explanation —
  don't make the reader wait for the point
- **Standalone rule**: it must make sense to someone who never saw the
  original video/post

## YouTube description / community post (if repurposing back to YouTube itself)

- **Description hard limit**: 5,000 characters
- **Community post**: short, works well as a single core idea plus a
  question or poll to drive comments
