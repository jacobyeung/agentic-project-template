---
name: resume
description: Session-start bootstrap for this project. Reads AGENTS.md and the agent/agentic_information ledgers in the documented order, checks for in-flight work and uncommitted changes, and prints a tight standup (where we are / what's in flight / next step / blockers / do-not-rerun NO-GOs). Read-only. Use at the start of any working session.
version: 1.0.0
scope: project
---

# ruff: noqa: E501

# /resume — session-start standup

Rebuilds context fast at the start of a session by following this project's own
start ritual instead of guessing. **Read-only: never edit or commit here** — that
is `/handoff`'s job.

## Procedure

1. **Locate the project root.** From the cwd, walk up to the git root. Confirm it
   has `AGENTS.md` and `agent/agentic_information/`.

2. **Follow the documented read order.** Open `AGENTS.md` and read the files it
   tells you to read at session start, in that order. If it gives no explicit
   order, use the default for this template:
   `AGENTS.md` → `agent/agentic_information/CURRENT_STATE.md` →
   `agent/agentic_information/CLOSED_LOOP_LEDGER.md` →
   `agent/agentic_information/CAMPAIGN_LEDGER.md` →
   `agent/experiments/BEST_SCORES.md` (if present) → the relevant `docs/`.

3. **Check what's in flight.** Run whatever "active work" probe `AGENTS.md`
   documents. Generic fallbacks: `git log --oneline -5`; any job-queue or
   process check the project uses (e.g. `squeue -u "$USER"`, `tmux ls`,
   `ls agent/experiments/*/RUNNING 2>/dev/null`).

4. **Check working-tree state.** `git status -s`. Flag any uncommitted work from a
   prior session as a loose end.

5. **Scan for landmines.** Pull the Tried-And-Rejected / NO-GO entries from the
   closed-loop ledger so you don't re-propose a rejected approach without a new
   argument.

## Output (a standup, not a report)

- **Where we are:** 1–2 lines from CURRENT_STATE; current goal + primary metric.
- **In flight:** what's running, with ids/state.
- **Immediate next step:** the single documented next action.
- **Open blockers.**
- **Uncommitted work.**
- **Don't re-run:** the relevant NO-GOs.

End by asking what to pick up, or proceed if the next step is unambiguous.
