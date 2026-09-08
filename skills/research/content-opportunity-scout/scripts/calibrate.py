#!/usr/bin/env python3
"""Find what has actually been working, from the outcomes log.

This is NOT model training and does not change any weights on disk — it
reads `outcomes.jsonl` (schema in references/outcomes-log-format.md),
groups shipped entries by a field (default source_type), and reports each
group's hit rate. Groups below --min-n are marked insufficient_data rather
than given a misleadingly confident number. Use the output to lean Phase 0.5
scanning/scoring toward what's working — never to silently override the
rubric, and always disclose the note in the run's output.

Usage:
    python calibrate.py outcomes.jsonl
    python calibrate.py outcomes.jsonl --group-by hook_family
    python calibrate.py outcomes.jsonl --min-n 3
"""
import argparse
import json
import sys
from pathlib import Path

DEFAULT_MIN_N = 5
MEANINGFUL_DELTA = 0.20  # a group's hit rate must differ from overall by this much to get called out


def load_entries(path):
    entries = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"skipping malformed line: {e}", file=sys.stderr)
    return entries


def hit_rate(entries):
    shipped = [e for e in entries if e.get("shipped")]
    if not shipped:
        return None, 0
    hits = sum(1 for e in shipped if e.get("performance") == "hit")
    return hits / len(shipped), len(shipped)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("log", help="Path to the outcomes JSONL log")
    parser.add_argument("--group-by", default="source_type", help="Field to group by (default: source_type)")
    parser.add_argument("--min-n", type=int, default=DEFAULT_MIN_N, help=f"Minimum shipped entries in a group before trusting its hit rate (default {DEFAULT_MIN_N})")
    args = parser.parse_args()

    if not Path(args.log).exists():
        print(json.dumps({"status": "no_log_yet", "message": f"{args.log} does not exist — nothing to calibrate on yet, this is expected on the first run."}))
        return

    entries = load_entries(args.log)
    overall_rate, overall_n = hit_rate(entries)

    if overall_rate is None:
        print(json.dumps({"status": "no_shipped_outcomes", "message": "Log exists but has no entries with shipped=true yet."}))
        return

    groups = {}
    for e in entries:
        if not e.get("shipped"):
            continue
        key = e.get(args.group_by)
        if key is None:
            continue
        groups.setdefault(key, []).append(e)

    notes = []
    group_stats = {}
    for key, group_entries in groups.items():
        rate, n = hit_rate(group_entries)
        insufficient = n < args.min_n
        group_stats[key] = {"hit_rate": round(rate, 2) if rate is not None else None, "n": n, "insufficient_data": insufficient}
        if not insufficient and rate is not None:
            delta = rate - overall_rate
            if abs(delta) >= MEANINGFUL_DELTA:
                direction = "above" if delta > 0 else "below"
                notes.append(
                    f"{args.group_by}='{key}' is hitting {rate:.0%} vs a {overall_rate:.0%} overall average "
                    f"across {n} shipped ideas ({direction} average by {abs(delta):.0%}) — worth leaning toward it a bit, not overriding the rubric."
                )

    print(json.dumps({
        "status": "ok",
        "overall_hit_rate": round(overall_rate, 2),
        "overall_shipped_n": overall_n,
        "group_by": args.group_by,
        "groups": group_stats,
        "calibration_notes": notes if notes else ["Not enough data yet for a confident calibration note — keep logging outcomes."],
    }, indent=2))


if __name__ == "__main__":
    main()
