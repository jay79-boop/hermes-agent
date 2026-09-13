"""Install the personal `reflect` skill into `~/.claude/skills/reflect/SKILL.md`.

Claude Code (and, once uploaded, claude.ai chat and Cowork) load a personal
skill from the user-level skills directory, which makes it the right home for
a skill meant to run at the end of ANY session, not just one working in this
repository. The source of that skill is `docs/reflect-skill/SKILL.md` in this
repository, so a session on any surface can read and revise it, and git
carries the history.

This writes that source, verbatim minus its repo-only leading comment, to
`~/.claude/skills/reflect/SKILL.md`. Unlike `install_global_instructions.py`
there is no existing file to splice into -- a skill is its own standalone
file -- so this is a straight copy, backed up first if something is already
there.

Run it once, on the machine whose sessions should get the skill:

    python tools/install_reflect_skill.py          # install or refresh
    python tools/install_reflect_skill.py --check  # report, change nothing
    python tools/install_reflect_skill.py --diff   # show what would change

A cloud session cannot do this: `~/.claude` there belongs to a container that
is reclaimed when the session ends. It has to run where the sessions actually
run.

Deliberately ASCII-only and stdlib-only. Windows PowerShell 5.1 reads a
BOM-less file as Windows-1252, and one non-ASCII byte can stop a script
parsing at all.
"""

import argparse
import difflib
import os
import re
import shutil

SOURCE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "docs",
    "reflect-skill",
    "SKILL.md",
)

# The source opens with an HTML comment explaining the source/installer split
# to a reader of the repository. That explanation is about the file, not part
# of the skill, so it stays out of the installed copy.
LEADING_COMMENT = re.compile(r"\A\s*<!--.*?-->\s*", re.DOTALL)


def claude_home():
    return os.path.join(os.path.expanduser("~"), ".claude")


def load_source(path=SOURCE):
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    return LEADING_COMMENT.sub("", text, count=1).strip("\n") + "\n"


def install(home, body, check=False, show_diff=False):
    target_dir = os.path.join(home, "skills", "reflect")
    path = os.path.join(target_dir, "SKILL.md")
    existing = ""
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as handle:
            existing = handle.read()

    if existing == body:
        return "current", path

    state = "missing" if not existing else "stale"

    if show_diff:
        before = existing.splitlines(keepends=True)
        after = body.splitlines(keepends=True)
        print("".join(difflib.unified_diff(before, after, "installed", "source")))
    if check or show_diff:
        return state, path

    os.makedirs(target_dir, exist_ok=True)
    if os.path.isfile(path):
        shutil.copyfile(path, path + ".bak")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(body)
    return "added" if state == "missing" else "refreshed", path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check", action="store_true", help="report what would change, write nothing"
    )
    parser.add_argument(
        "--diff", action="store_true", help="show the change as a diff, write nothing"
    )
    args = parser.parse_args(argv)

    home = claude_home()
    if not os.path.isdir(home):
        print("No %s on this machine." % home)
        print("Run this where Claude Code actually runs -- not in a cloud session.")
        return 1

    print("Claude Code home: %s" % home)
    if args.check or args.diff:
        print("(reporting only, nothing will be written)\n")
    else:
        print("")

    state, path = install(home, load_source(), check=args.check, show_diff=args.diff)
    print("  skills/reflect  %-18s %s" % (state, path))

    if args.check or args.diff:
        if state != "current":
            print("\nNothing was changed. Re-run without --check/--diff to install.")
        return 0

    if state != "current":
        print("\nDone.")
        if os.path.isfile(path + ".bak"):
            print("The previous file was copied to SKILL.md.bak first.")
    print("Type /reflect at the end of any Claude Code session to use it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
