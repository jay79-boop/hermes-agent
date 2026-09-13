<!--
Source of truth for the personal `reflect` skill, installed to
`~/.claude/skills/reflect/SKILL.md` on the owner's machine by
`tools/install_reflect_skill.py`. Edit here, run the installer there. A cloud
session can revise this file and hand over the one-line paste, but cannot
write `~/.claude` itself -- that belongs to a container reclaimed when the
session ends.

This fork is public, so the skill body below stays impersonal: no full name,
city, or biographical detail beyond what `global-instructions.md` already
carries in this repository.
-->
---
name: reflect
description: "End-of-session reflection: pulls durable facts, tone corrections, and workflow preferences out of the conversation, files them without bloating memory, and drafts a new skill for anything that looks like it will recur. Invoke as /reflect at the end of any chat, Claude Code, or Cowork session."
version: 1.0.0
author: Hermes Agent personal tools
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [reflection, memory, workflow, self-improvement]
    related_skills: [gexio-machine]
---

# Reflect

## Why this exists

Without this skill, "save what matters from this session" is a prompt the
owner has to remember and retype every time, and the result depends on
whatever gets typed that day. `/reflect` is that prompt turned into a fixed
procedure: run it, and the same categories get checked, the same files get
updated the same way, and memory does not quietly grow past the point where
it still gets read.

## What `/reflect` does, in order

1. **Re-read the session.** Everything since the conversation started, or
   since the last `/reflect` in this same conversation if it already ran
   once.

2. **Sort what it finds into four bins.** Nothing gets written yet; sort
   first.
   - **Machine/handoff facts** -- something about the owner's machine, shell,
     or how work has to reach them (a new PowerShell trap, a path, a
     checkout quirk). This is what `gexio-machine` exists for.
   - **Repo-specific facts** -- true of this one repository, not the owner in
     general (a build quirk, a test convention, a gotcha in this codebase).
   - **Durable personal facts / tone corrections / workflow preferences** --
     true of the owner across repos and surfaces (how they like answers
     formatted, a standing constraint, a correction to how Claude behaved).
   - **Recurring patterns** -- something this session did that has visibly
     come up before, or that the owner flags as something they will want
     again.
   - Anything that is specific to this one conversation and won't matter
     next time (a one-off debugging detail, a fact only relevant to the task
     just finished) goes in none of these bins. Leave it out.

3. **File each bin, never silently.**
   - *Machine/handoff facts*: propose one line to add to `gexio-machine`
     (or the equivalent machine skill on whatever surface is running).
     Never edit that skill file as part of `/reflect` itself -- say what you
     would add and let the owner say yes, matching that skill's own rule
     that it is never updated silently.
   - *Repo-specific facts*: propose an addition to this repository's
     `CLAUDE.md` (or open one if none exists). These never go into the
     cross-repo memory file -- a fact true of one repo, filed globally, is
     noise everywhere else.
   - *Durable personal facts / tone corrections / workflow preferences*:
     see "Updating memory without bloating it" below.
   - *Recurring patterns*: see "Drafting a new skill" below.

4. **Update memory without bloating it.**

   The memory file (`MEMORY.md`, wherever this surface keeps it -- commonly
   `~/.claude/MEMORY.md` on Claude Code) has a hard read ceiling: entries
   past roughly 24 KB are silently dropped at load, with no error. Writing
   the full reflection into it is how it gets there. So:

   - The full, dated reflection entry goes into a **log file next to this
     skill**, not into `MEMORY.md` directly: `~/.claude/skills/reflect/LOG.md`
     (or, in a cloud session with no reach to `~/.claude`, the working
     repository's own `.claude/reflect-log/LOG.md` -- say plainly that this
     is the fallback and why).
   - `MEMORY.md` itself gets **exactly one pointer line**, added once and
     never duplicated, wrapped in its own markers so a repeat `/reflect`
     recognizes and skips it:
     ```
     <!-- reflect-skill:pointer:start -->
     Session reflections are logged in ~/.claude/skills/reflect/LOG.md (see ARCHIVE.md there for older entries) -- run /reflect to add to it.
     <!-- reflect-skill:pointer:end -->
     ```
     If `MEMORY.md` doesn't exist yet, create it with just that block.
   - Anything that actually belongs in `MEMORY.md` on its own merits (a
     short-form fact the owner clearly wants surfaced every session, not
     just logged) can still go there directly, in addition to the pointer --
     but keep it to the kind of one-liner `MEMORY.md` already holds. Don't
     let `/reflect` become the reason it grows past the ceiling it is
     trying to protect.
   - Before appending, check `LOG.md`'s size. Past roughly 20 KB, move
     entries older than the most recent few into `ARCHIVE.md` in the same
     folder first -- the same split `MEMORY.md`/`ARCHIVE.md` already use.
   - Each log entry: a date heading, then 3-8 bullet lines. Terse. This is a
     log to skim later, not a transcript.

5. **Draft a new skill for recurring patterns -- don't just mention it.**

   When something in bin 4 looks like it will come up again (a multi-step
   workflow run more than once, an explicit "we keep doing this," a
   correction that's really a missing capability), create an actual draft:

   - Pick the right home: a personal, cross-repo habit goes to
     `~/.claude/skills/<name>/SKILL.md` (or this repo's own
     `personal-tools/docs/<name>-skill/SKILL.md` +
     `personal-tools/tools/install_<name>_skill.py` pair if it should ship
     the same way this skill does); something specific to the product this
     repository builds goes under this repo's own top-level `skills/`
     tree instead, matching the category conventions already there.
   - Write a real stub: frontmatter (`name`, `description`, `version`,
     `platforms`), a "Why this exists" section describing the pattern just
     observed, and a "TODO" section marking what still needs filling in.
     Not a placeholder file -- something the owner can read and finish.
   - Say plainly that it's a draft, where it landed, and that it isn't
     wired into anything until they review it. Never install or invoke a
     drafted skill as part of the same `/reflect` run.

6. **Close with a short summary.** For this run: what got written to
   `LOG.md` (and its running size), what got proposed for `gexio-machine`
   or a repo `CLAUDE.md` (awaiting a yes), what skill(s) got drafted and
   where, and anything sorted out in step 2 that was deliberately left
   filed nowhere. Keep it to what changed -- this is a status line, not a
   replay of the reasoning.

## Constraints

- Additive by default. `/reflect` proposes edits to `gexio-machine` and to a
  repo's `CLAUDE.md`; it does not make them. It writes its own log and the
  `MEMORY.md` pointer directly, since those are its own files to maintain.
- A cloud session cannot reach `~/.claude`. Say so, and use the working
  repository as the fallback location for both the log and any drafted
  skill, exactly as noted above.
- Keep entries and drafts free of anything that shouldn't sit in a file a
  future session (possibly on a different surface, possibly a subagent)
  will read verbatim -- no secrets, no credentials, no session transcripts
  pasted wholesale.
