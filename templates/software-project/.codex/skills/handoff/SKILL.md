---
name: handoff
description: Session-close for this project. Reviews in-flight/finished work, then writes findings ONLY to the canonical files named in AGENTS.md's result-routing table (CURRENT_STATE + ledgers; optional agent/agentic_information/<TOPIC>_HANDOFF.md for deep dives) — never inventing a new path or file. Commits completed verified work (raw artifacts stay off git) and reports done/remaining/next-step. Use before ending a session or as a mid-session checkpoint.
version: 1.0.0
scope: project
---

# ruff: noqa: E501

# /handoff — session-close + commit checkpoint

Closes a session cleanly: review what happened, write findings to the durable
files this project already designates, commit completed units, and leave a
resume-ready handoff. Inverse of `/resume`. Run at session end or mid-session as a
checkpoint — never let verified work sit uncommitted.

**Core invariant — no random directories.** Every write goes to a location named
in the `AGENTS.md` Result-Routing table. Do not create new handoff files, new
top-level files, or invented names. A finding with "nowhere to go" goes in
`CURRENT_STATE.md` or a ledger — never a fresh file you made up.

## Procedure

1. **Read the routing.** Open `AGENTS.md`; read its Result-Routing table and any
   Git Hygiene rules. That table — not this skill — decides *where* things go;
   this skill enforces *that you obey it*.

2. **Account for every task you ran.** Report anything still running (ids/state).
   For finished work, read its outputs/logs and summarize the result; never claim
   success without looking.

3. **Write findings to the canonical targets only:**

   | Produced thing | Goes to (verify against the project's table) |
   |---|---|
   | Live snapshot / next step / blockers | `agent/agentic_information/CURRENT_STATE.md` — **single-writer; overwrite, keep short** |
   | Fix / hypothesis verdict | `agent/agentic_information/CLOSED_LOOP_LEDGER.md` (close the row; terminal status; move durable NO-GOs to Tried-And-Rejected) |
   | Decision / experiment history | `agent/agentic_information/CAMPAIGN_LEDGER.md` (append-only) |
   | Best metric by area | `agent/experiments/BEST_SCORES.md`, if present (never claim a win inside the noise floor) |
   | Build details / gotchas worth a deep-dive | `agent/agentic_information/<TOPIC>_HANDOFF.md` or `<TOPIC>_RESULT.md` — only if routing lists this slot, and only for a genuine deep-dive |

   For routine close, CURRENT_STATE + the ledgers are enough. Don't create a
   `<TOPIC>_HANDOFF.md` just to have one.

4. **Do NOT touch these:** the root `HANDOFF_CURRENT.md` is a stable pointer stub
   (it redirects to AGENTS.md + CURRENT_STATE.md) — leave it as-is. No new root
   files, no new directories, no `notes.md` / `SESSION_*.md` / dated files.
   `<TOPIC>` must be a real area, not a free-form label.

5. **Commit completed, verified units.** Follow Git Hygiene. One coherent unit per
   commit, descriptive message. **Before staging, verify no large/raw artifacts
   are included** — raw outputs live under `experiments/` or `runs/`, never in
   git. `git status -s` first; stage deliberately (not blind `git add -A`). Commit
   on the current branch; don't force-push. If a unit isn't verified, leave it
   uncommitted and say so.

## Output

Report files written (each a routed target — name them), committed units (hashes +
one-liners), still-running work, and what's left. If a finding seemed to want a
home outside the routing table, say so and ask rather than inventing a path.
