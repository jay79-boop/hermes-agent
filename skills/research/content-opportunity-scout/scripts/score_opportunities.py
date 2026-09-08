#!/usr/bin/env python3
"""Score content-opportunity candidates against the scout's rubric.

Reads a JSON array of candidates (from a file or stdin), computes a
weighted composite score for each, drops anything already seen in the
opportunities log (by normalized topic match), and prints the survivors
ranked highest first.

Candidate schema:
{
  "topic": "string, the specific angle",
  "source": "string, e.g. youtube/reddit/x/news",
  "url": "string",
  "evidence": "string, the concrete signal",
  "date": "YYYY-MM-DD",
  "scores": {
    "velocity": 0-10,
    "audience_fit": 0-10,
    "competitive_gap": 0-10,
    "durability": 0-10,
    "feasibility": 0-10
  }
}

Usage:
    python score_opportunities.py candidates.json
    python score_opportunities.py candidates.json --cutoff 7.5 --top 3
    python score_opportunities.py candidates.json --log ~/.hermes/content-scout/log.jsonl
    cat candidates.json | python score_opportunities.py - --log log.jsonl --append
"""
import argparse
import json
import re
import sys
from pathlib import Path

WEIGHTS = {
    "velocity": 0.25,
    "audience_fit": 0.25,
    "competitive_gap": 0.20,
    "durability": 0.15,
    "feasibility": 0.15,
}
DEFAULT_CUTOFF = 7.0
DEFAULT_TOP = 5


def normalize(text):
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def token_overlap(a, b):
    ta, tb = set(normalize(a).split()), set(normalize(b).split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def composite_score(scores):
    missing = [k for k in WEIGHTS if k not in scores]
    if missing:
        raise ValueError(f"missing score(s): {', '.join(missing)}")
    return round(sum(scores[k] * w for k, w in WEIGHTS.items()), 2)


def load_candidates(path):
    raw = sys.stdin.read() if path == "-" else Path(path).read_text()
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("candidates JSON must be a top-level array")
    return data


def load_seen_topics(log_path):
    if not log_path or not Path(log_path).exists():
        return []
    seen = []
    for line in Path(log_path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        topic = entry.get("topic")
        if topic:
            seen.append(topic)
    return seen


def is_duplicate(topic, seen_topics, threshold=0.6):
    return any(token_overlap(topic, seen) >= threshold for seen in seen_topics)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("candidates", help="Path to candidates JSON file, or '-' for stdin")
    parser.add_argument("--log", default=None, help="Path to the opportunities log (JSONL) for dedup / append")
    parser.add_argument("--cutoff", type=float, default=DEFAULT_CUTOFF, help=f"Minimum composite score to keep (default {DEFAULT_CUTOFF})")
    parser.add_argument("--top", type=int, default=DEFAULT_TOP, help=f"Max finalists to return (default {DEFAULT_TOP})")
    parser.add_argument("--append", action="store_true", help="Append the printed finalists to --log")
    args = parser.parse_args()

    candidates = load_candidates(args.candidates)
    seen_topics = load_seen_topics(args.log)

    scored = []
    for c in candidates:
        topic = c.get("topic", "").strip()
        if not topic:
            continue
        try:
            score = composite_score(c.get("scores", {}))
        except ValueError as e:
            print(f"skipping '{topic}': {e}", file=sys.stderr)
            continue
        dup = is_duplicate(topic, seen_topics)
        scored.append({**c, "composite": score, "duplicate": dup})

    scored.sort(key=lambda c: c["composite"], reverse=True)

    finalists = [c for c in scored if c["composite"] >= args.cutoff and not c["duplicate"]][: args.top]
    dropped_dupes = [c for c in scored if c["duplicate"]]
    below_cutoff = [c for c in scored if c["composite"] < args.cutoff and not c["duplicate"]]

    print(json.dumps({
        "finalists": finalists,
        "dropped_as_duplicate": [{"topic": c["topic"], "composite": c["composite"]} for c in dropped_dupes],
        "below_cutoff": [{"topic": c["topic"], "composite": c["composite"]} for c in below_cutoff],
    }, indent=2))

    if args.append and args.log and finalists:
        log_path = Path(args.log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a") as f:
            for c in finalists:
                f.write(json.dumps({"topic": c["topic"], "composite": c["composite"], "date": c.get("date")}) + "\n")
        print(f"appended {len(finalists)} finalist(s) to {log_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
