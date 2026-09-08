#!/usr/bin/env python3
"""Pull real engagement counts for shipped X/Twitter posts and turn them
into outcome-log entries — the auto-fill for content-repurposer's Phase 6.

NOT free. As of Feb 2026 the X API v2 moved new developers to pay-per-use:
about $0.005 per post read (public_metrics: like/retweet/reply/quote counts
via app-only auth — organic impression_count needs the post author's own
OAuth user-context token, which this script does not implement, so it is
never requested). Spend-safety layers apply:

  - This script NEVER discovers or searches for tweets on its own — it only
    looks up the exact IDs you pass in. No bulk pulls, no accidental scope
    creep.
  - It prints the exact read count and dollar estimate BEFORE calling the
    API, and refuses to call unless you pass --confirm-spend. Dry-running
    it (the default) costs nothing.
  - Keep the bearer token on a spend-limited key if the provider offers one,
    and check auto-recharge is off wherever this is billed — this script
    has no way to enforce either of those, only to make you look at the
    estimate before it spends anything.

Input: a JSON file listing shipped posts to check, e.g.:
[
  {"topic": "AI trading bot backtests", "post_id": "1234567890123456789", "format": "thread", "date": "2026-09-08"}
]

Usage:
    python pull_x_stats.py shipped.json                       # estimate only, no spend
    python pull_x_stats.py shipped.json --confirm-spend --baseline baseline.json --log outcomes.jsonl --append
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://api.x.com/2/tweets"
COST_PER_READ_USD = 0.005
BASELINE_WINDOW = 20
MIN_BASELINE_SAMPLES = 3


def fetch_stats(post_ids, bearer_token):
    out = {}
    for i in range(0, len(post_ids), 100):
        chunk = post_ids[i : i + 100]
        params = {"ids": ",".join(chunk), "tweet.fields": "public_metrics"}
        url = f"{API_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer_token}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for item in data.get("data", []):
            m = item.get("public_metrics", {})
            out[item["id"]] = {
                "likes": m.get("like_count", 0),
                "retweets": m.get("retweet_count", 0),
                "replies": m.get("reply_count", 0),
                "quotes": m.get("quote_count", 0),
                "text": item.get("text", ""),
            }
    return out


def engagement_score(stats):
    return stats["likes"] + 2 * stats["retweets"] + 2 * stats["quotes"] + stats["replies"]


def classify(value, history):
    if len(history) < MIN_BASELINE_SAMPLES:
        return "insufficient_baseline", f"only {len(history)} prior sample(s) for this format; need {MIN_BASELINE_SAMPLES}+"
    sorted_hist = sorted(history)
    n = len(sorted_hist)
    lower_third = sorted_hist[n // 3 - 1] if n // 3 >= 1 else sorted_hist[0]
    upper_third = sorted_hist[(2 * n) // 3] if (2 * n) // 3 < n else sorted_hist[-1]
    if value >= upper_third:
        return "hit", f"top third vs last {n} same-format posts (>= {upper_third})"
    if value <= lower_third:
        return "flop", f"bottom third vs last {n} same-format posts (<= {lower_third})"
    return "ok", f"middle third vs last {n} same-format posts"


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
    parser.add_argument("shipped", help="JSON file listing shipped posts to check (see docstring schema)")
    parser.add_argument("--bearer-token", default=None, help="X API bearer token (default: X_API_BEARER_TOKEN env var)")
    parser.add_argument("--baseline", default=None, help="Path to baseline.json (rolling per-format engagement history)")
    parser.add_argument("--log", default=None, help="Path to the outcomes JSONL log, for dedup and --append")
    parser.add_argument("--confirm-spend", action="store_true", help="Actually call the API. Without this flag, only the cost estimate is printed and nothing is spent.")
    parser.add_argument("--append", action="store_true", help="Append new outcome entries to --log and save the updated baseline (only takes effect with --confirm-spend)")
    args = parser.parse_args()

    shipped = json.loads(Path(args.shipped).read_text())
    already_logged = load_existing_ids(args.log)
    to_fetch = [s for s in shipped if s["post_id"] not in already_logged]
    skipped_dupes = [s["post_id"] for s in shipped if s["post_id"] in already_logged]

    if not to_fetch:
        print(json.dumps({"status": "nothing_to_fetch", "already_logged": skipped_dupes}, indent=2))
        return

    estimate = {
        "reads": len(to_fetch),
        "estimated_cost_usd": round(len(to_fetch) * COST_PER_READ_USD, 4),
        "already_logged_skipped": skipped_dupes,
    }

    if not args.confirm_spend:
        print(json.dumps({"status": "dry_run", "would_spend": estimate, "note": "pass --confirm-spend to actually call the API"}, indent=2))
        return

    bearer_token = args.bearer_token or os.environ.get("X_API_BEARER_TOKEN")
    if not bearer_token:
        print("no bearer token: pass --bearer-token or set X_API_BEARER_TOKEN", file=sys.stderr)
        sys.exit(1)

    stats = fetch_stats([s["post_id"] for s in to_fetch], bearer_token)
    baseline = load_baseline(args.baseline)

    entries = []
    for s in to_fetch:
        pid = s["post_id"]
        if pid not in stats:
            print(f"no stats returned for {pid} (deleted, protected, or bad ID?)", file=sys.stderr)
            continue
        st = stats[pid]
        score = engagement_score(st)
        fmt = s.get("format", "unknown")
        label, note = classify(score, baseline.get(fmt, []))
        entry = {
            "date": s.get("date"),
            "topic": s.get("topic", st["text"][:80]),
            "platform": "x",
            "external_id": pid,
            "shipped": True,
            "performance": None if label == "insufficient_baseline" else label,
            "performance_note": note,
            "metric_type": "engagement_score",
            "metric_value": score,
            "likes": st["likes"],
            "retweets": st["retweets"],
            "replies": st["replies"],
        }
        entries.append(entry)
        baseline = update_baseline(baseline, fmt, score)

    print(json.dumps({"spent_usd": estimate["estimated_cost_usd"], "fetched": entries, "already_logged": skipped_dupes}, indent=2))

    if args.append:
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
