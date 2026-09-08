#!/usr/bin/env python3
"""Pull real view/like/comment counts for shipped YouTube videos and turn
them into outcome-log entries — the auto-fill for content-opportunity-scout's
and content-repurposer's Phase 6 (record outcomes), so calibration has real
numbers instead of relying on someone typing them in.

Free: YouTube Data API v3's videos.list costs 1 quota unit per call and
accepts up to 50 IDs per call, against a 10,000 unit/day default ceiling.
No OAuth needed — a plain API key (YOUTUBE_API_KEY env var, or --api-key)
with the YouTube Data API v3 enabled in Google Cloud Console is enough for
public statistics. This does NOT use the YouTube Analytics API (watch time,
retention, traffic source) — that needs OAuth consent and is out of scope.

Classification is self-relative, not an invented absolute threshold: each
new video's view count is ranked against a rolling window of the same
format's past view counts (baseline.json), because "40k views" means nothing
without knowing what normal is for this channel. Top third of the window =
hit, bottom third = flop, middle = ok. Fewer than 3 prior entries in that
format = "insufficient_baseline", reported honestly rather than guessed.

Input: a JSON file listing shipped videos to check, e.g.:
[
  {"topic": "AI trading bot backtests", "video_id": "dQw4w9WgXcQ", "format": "long", "date": "2026-09-08"},
  {"topic": "3 no-code AI wins", "video_id": "abc123XYZ00", "format": "shorts", "date": "2026-09-07"}
]

Usage:
    python pull_youtube_stats.py shipped.json --baseline baseline.json
    python pull_youtube_stats.py shipped.json --baseline baseline.json --log outcomes.jsonl --append
    python pull_youtube_stats.py shipped.json --api-key YOUR_KEY --dry-run
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://www.googleapis.com/youtube/v3/videos"
BASELINE_WINDOW = 20
MIN_BASELINE_SAMPLES = 3


def fetch_stats(video_ids, api_key):
    """Call videos.list once per <=50 IDs. Returns {video_id: {views, likes, comments, title}}."""
    out = {}
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i : i + 50]
        params = {
            "part": "statistics,snippet",
            "id": ",".join(chunk),
            "key": api_key,
        }
        url = f"{API_URL}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for item in data.get("items", []):
            stats = item.get("statistics", {})
            out[item["id"]] = {
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)) if "likeCount" in stats else None,
                "comments": int(stats.get("commentCount", 0)) if "commentCount" in stats else None,
                "title": item.get("snippet", {}).get("title", ""),
            }
    return out


def classify(value, history):
    """Rank value against history (a list of past values for the same format).
    Returns (label, note)."""
    if len(history) < MIN_BASELINE_SAMPLES:
        return "insufficient_baseline", f"only {len(history)} prior sample(s) for this format; need {MIN_BASELINE_SAMPLES}+"
    sorted_hist = sorted(history)
    n = len(sorted_hist)
    lower_third = sorted_hist[n // 3 - 1] if n // 3 >= 1 else sorted_hist[0]
    upper_third = sorted_hist[(2 * n) // 3] if (2 * n) // 3 < n else sorted_hist[-1]
    if value >= upper_third:
        return "hit", f"top third vs last {n} same-format videos (>= {upper_third})"
    if value <= lower_third:
        return "flop", f"bottom third vs last {n} same-format videos (<= {lower_third})"
    return "ok", f"middle third vs last {n} same-format videos"


def load_baseline(path):
    if not path or not Path(path).exists():
        return {}
    return json.loads(Path(path).read_text())


def update_baseline(baseline, fmt, value, window=BASELINE_WINDOW):
    history = baseline.setdefault(fmt, [])
    history.append(value)
    if len(history) > window:
        del history[: len(history) - window]
    return baseline


def load_existing_ids(log_path):
    if not log_path or not Path(log_path).exists():
        return set()
    seen = set()
    for line in Path(log_path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("external_id"):
            seen.add(entry["external_id"])
    return seen


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("shipped", help="JSON file listing shipped videos to check (see docstring schema)")
    parser.add_argument("--api-key", default=None, help="YouTube Data API v3 key (default: YOUTUBE_API_KEY env var)")
    parser.add_argument("--baseline", default=None, help="Path to baseline.json (rolling per-format view history)")
    parser.add_argument("--log", default=None, help="Path to the outcomes JSONL log, for dedup and --append")
    parser.add_argument("--append", action="store_true", help="Append new outcome entries to --log and save the updated baseline")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and classify but don't write anything")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("no API key: pass --api-key or set YOUTUBE_API_KEY", file=sys.stderr)
        sys.exit(1)

    shipped = json.loads(Path(args.shipped).read_text())
    already_logged = load_existing_ids(args.log)
    to_fetch = [s for s in shipped if s["video_id"] not in already_logged]
    skipped_dupes = [s["video_id"] for s in shipped if s["video_id"] in already_logged]

    if not to_fetch:
        print(json.dumps({"status": "nothing_to_fetch", "already_logged": skipped_dupes}, indent=2))
        return

    stats = fetch_stats([s["video_id"] for s in to_fetch], api_key)
    baseline = load_baseline(args.baseline)

    entries = []
    for s in to_fetch:
        vid = s["video_id"]
        if vid not in stats:
            print(f"no stats returned for {vid} (private, deleted, or bad ID?)", file=sys.stderr)
            continue
        st = stats[vid]
        fmt = s.get("format", "unknown")
        label, note = classify(st["views"], baseline.get(fmt, []))
        entry = {
            "date": s.get("date"),
            "topic": s.get("topic", st["title"]),
            "platform": "youtube",
            "external_id": vid,
            "shipped": True,
            # null, not a guessed label, when there isn't enough same-format
            # history yet to rank against — calibrate.py's hit_rate() only
            # counts entries with a real hit/ok/flop, so this correctly sits
            # out of the hit-rate math instead of quietly deflating it.
            "performance": None if label == "insufficient_baseline" else label,
            "performance_note": note,
            "metric_type": "views",
            "metric_value": st["views"],
            "likes": st["likes"],
            "comments": st["comments"],
        }
        entries.append(entry)
        baseline = update_baseline(baseline, fmt, st["views"])

    print(json.dumps({"fetched": entries, "already_logged": skipped_dupes}, indent=2))

    if args.append and not args.dry_run:
        if args.log:
            log_path = Path(args.log)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a") as f:
                for e in entries:
                    f.write(json.dumps(e) + "\n")
        if args.baseline:
            Path(args.baseline).write_text(json.dumps(baseline, indent=2))


if __name__ == "__main__":
    main()
