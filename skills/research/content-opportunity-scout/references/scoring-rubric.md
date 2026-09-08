# Scoring Rubric

Score every surviving candidate 0-10 on each criterion, then compute the
weighted composite. `scripts/score_opportunities.py` does the arithmetic —
this file defines what each number means so the scores are consistent
run to run.

| Criterion | Weight | 0 | 5 | 10 |
|---|---|---|---|---|
| Trend Velocity | 0.25 | No corroborated signal, one weak mention | Growing steadily across 1-2 sources | Accelerating across 3+ independent source types in the freshness window |
| Audience Fit | 0.25 | Off-niche, audience won't recognize why they'd click | Adjacent to core niche | Squarely what this audience already searches for or asks about |
| Competitive Gap | 0.20 | 10+ recent videos/posts already cover this exact angle | A few competitors have touched it, no dominant take | Nobody in the watched competitor list has this specific angle yet |
| Durability | 0.15 | Dead by tomorrow, pure newsjack | Relevant for a few weeks | Evergreen — still true and useful in 6+ months |
| Feasibility | 0.15 | Requires access/resources/skills the profile's formats don't support | Doable but needs unusual prep | Shootable with the profile's existing formats, no special access needed |

**Composite = Σ(score × weight)**, out of 10.

## Cutoff

Default: only brief candidates scoring **≥ 7.0** composite. The profile can
override this. If nothing clears the bar, report that honestly instead of
briefing the highest score anyway — a 6.2 is not a good idea just because
it's the best of a bad batch.

## Notes on scoring honestly

- **Velocity ≠ Gap.** An exploding topic that 50 other creators already
  nailed is high Velocity, low Gap — don't let one prop up the composite
  and hide the other.
- **Don't grade on a curve mid-batch.** Score each candidate against the
  fixed anchors above, not relative to the other candidates in this run.
- **Feasibility is about this user**, not content creators in general — a
  format that needs a camera crew scores low even if it's a great idea,
  unless the profile says that's a format they make.
