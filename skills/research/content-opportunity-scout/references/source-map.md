# Source Map

Query patterns for Phase 1 scanning, using only `web_search` / `web_extract`
(no API keys needed). Swap `<topic>` / `<niche>` for the profile's niches,
and run variants with different phrasing — not just different topics — to
avoid bubble scanning.

## Video platforms

```
web_search("<niche> site:youtube.com")
web_search("<niche> trending 2026")
web_extract(["https://www.youtube.com/results?search_query=<niche>&sp=CAI%253D"])  # sorted by upload date
```
Look at upload recency + view count relative to channel size (a 50k-sub
channel's 2M-view upload two days old is a much stronger signal than a
5M-sub channel's normal-performing upload).

## Communities / forums

```
web_search("<niche> site:reddit.com")
web_search("<niche> site:reddit.com/r/<relevant_subreddit>")
web_search("<niche> forum discussion")
```
Sort mentally by comment velocity and upvote ratio where visible, not raw
post count.

## Short-form social

```
web_search("<niche> site:x.com")
web_search("<niche> site:tiktok.com")
```
X/TikTok trends move fast — weight recency heavily here, and treat a single
viral post as an anecdote, not a trend, until corroborated elsewhere.

## News / newsletters / blogs

```
web_search("<niche> news this week")
web_search("<niche> newsletter roundup")
```
Good for "why now" evidence and for catching the story before the video
platforms have caught up to it.

## Competitor-specific

```
web_search("<competitor name> <niche>")
web_extract(["<competitor channel/profile URL>"])
```
Use this specifically to populate the Competitive Gap score — has anyone on
the watched list already made this?

## Optional richer sources (not required)

If the user later connects them, these give stronger signal than search
scraping alone:
- **YouTube Data API** — `search.list` + `videos.list` for real view/like
  counts and precise publish timestamps
- **Google Trends** (`trends.google.com`, or the `pytrends` library) — actual
  search-interest curves instead of inferring velocity from search results
- **X API v2** — real engagement counts instead of inferring from search
  snippets

None of these are required to run the skill; they just tighten the
Trend Velocity scoring.
