# Quality Checklist

`scripts/check_platform_limits.py` catches hard length/pacing failures.
This is the judgment pass on top of that — go through it before returning
the packet.

## Per draft

- [ ] Opens with a hook from Phase 1's proof points, not a generic
      restatement of the topic ("Let's talk about X" is not a hook)
- [ ] The idea assigned to this platform (Phase 2) is actually the one
      used — don't let the easiest idea to write drift into every slot
- [ ] Every specific claim (stat, quote, example) traces back to something
      actually in the source — no invented numbers to make a line punchier
- [ ] Exactly one CTA, and it's concrete (not "let me know your thoughts")
- [ ] Reads like the voice/tone from the profile, not generic AI copy —
      if there's no profile, at least match the source material's register

## Across the packet

- [ ] No two platforms share an identical hook line — if the same line
      works for two platforms, the second one needs its own angle
- [ ] Every platform the user actually asked for has a draft; no
      platform they didn't ask for was generated anyway
- [ ] The mapping from Phase 2 (which idea went where) is shown to the
      user, not just the final copy — so they can veto a mismatch quickly

## First-line test

Cover everything after the first line/sentence of each draft. Would a
scroller stop on that line alone? If the honest answer is no, rewrite the
opener before moving on — the rest of the draft doesn't matter if the hook
doesn't work.
