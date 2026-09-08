#!/usr/bin/env python3
"""Check drafted copy against the hard limits in references/platform-specs.md.

Catches length/pacing failures before they cost the user a rewrite. Does
NOT judge quality — that's references/quality-checklist.md's job.

Input JSON (any subset of keys, all optional):
{
  "x_thread": ["tweet 1 text", "tweet 2 text", ...],
  "linkedin": "full post text",
  "instagram_caption": "full caption text",
  "shorts_script": "the literal spoken words",
  "newsletter_subject": "subject line text",
  "youtube_description": "full description text"
}

Usage:
    python check_platform_limits.py drafts.json
    cat drafts.json | python check_platform_limits.py -
"""
import argparse
import json
import sys
from pathlib import Path

TWITTER_CHAR_LIMIT = 280
LINKEDIN_CHAR_LIMIT = 3000
LINKEDIN_FOLD = 210
INSTAGRAM_CAPTION_LIMIT = 2200
INSTAGRAM_FOLD = 125
SHORTS_MAX_SECONDS = 60
SPEAKING_WPM = 140
NEWSLETTER_SUBJECT_LIMIT = 60
YOUTUBE_DESC_LIMIT = 5000


def check_x_thread(tweets):
    results = []
    for i, tweet in enumerate(tweets, 1):
        length = len(tweet)
        results.append({
            "tweet": i,
            "chars": length,
            "limit": TWITTER_CHAR_LIMIT,
            "pass": length <= TWITTER_CHAR_LIMIT,
        })
    return results


def check_fold(text, hard_limit, fold, label):
    length = len(text)
    return {
        "chars": length,
        "limit": hard_limit,
        "pass": length <= hard_limit,
        "fold_at": fold,
        "note": f"first {fold} chars are what's visible before '{label}' truncates" if length > fold else "fits within the visible fold",
    }


def check_shorts_script(text):
    words = len(text.split())
    est_seconds = round(words / SPEAKING_WPM * 60, 1)
    max_words = int(SPEAKING_WPM * SHORTS_MAX_SECONDS / 60)
    return {
        "words": words,
        "estimated_seconds": est_seconds,
        "max_seconds": SHORTS_MAX_SECONDS,
        "max_words_at_natural_pace": max_words,
        "pass": est_seconds <= SHORTS_MAX_SECONDS,
    }


def check_simple_limit(text, limit):
    length = len(text)
    return {"chars": length, "limit": limit, "pass": length <= limit}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("drafts", help="Path to drafts JSON file, or '-' for stdin")
    args = parser.parse_args()

    raw = sys.stdin.read() if args.drafts == "-" else Path(args.drafts).read_text()
    drafts = json.loads(raw)

    report = {}
    all_pass = True

    if "x_thread" in drafts:
        report["x_thread"] = check_x_thread(drafts["x_thread"])
        all_pass = all_pass and all(r["pass"] for r in report["x_thread"])

    if "linkedin" in drafts:
        report["linkedin"] = check_fold(drafts["linkedin"], LINKEDIN_CHAR_LIMIT, LINKEDIN_FOLD, "see more")
        all_pass = all_pass and report["linkedin"]["pass"]

    if "instagram_caption" in drafts:
        report["instagram_caption"] = check_fold(drafts["instagram_caption"], INSTAGRAM_CAPTION_LIMIT, INSTAGRAM_FOLD, "more")
        all_pass = all_pass and report["instagram_caption"]["pass"]

    if "shorts_script" in drafts:
        report["shorts_script"] = check_shorts_script(drafts["shorts_script"])
        all_pass = all_pass and report["shorts_script"]["pass"]

    if "newsletter_subject" in drafts:
        report["newsletter_subject"] = check_simple_limit(drafts["newsletter_subject"], NEWSLETTER_SUBJECT_LIMIT)
        all_pass = all_pass and report["newsletter_subject"]["pass"]

    if "youtube_description" in drafts:
        report["youtube_description"] = check_simple_limit(drafts["youtube_description"], YOUTUBE_DESC_LIMIT)
        all_pass = all_pass and report["youtube_description"]["pass"]

    if not report:
        print("no recognized keys in input — see --help for the expected schema", file=sys.stderr)
        sys.exit(1)

    print(json.dumps({"all_pass": all_pass, "results": report}, indent=2))
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
