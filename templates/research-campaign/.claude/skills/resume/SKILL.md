---
name: resume
description: Session-start bootstrap for this project. Validates the bootstrap, follows AGENTS.md's fast read order, reconciles the operating-contract revision with live work and run records, and prints a tight standup. Read-only. Use at the start of any working session.
version: 1.1.0
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

2. **Validate before trusting summaries.** Run `python agent/validate_project.py`.
   A structural or operating-contract revision error blocks new launches until
   reconciled. A timestamp warning requires a live check but does not prove the
   record is wrong.

3. **Follow the documented fast read order.** Read `CURRENT_STATE.md`, then the
   matching `OPERATING_CONTRACT.md` revision. Inspect only the open/relevant rows
   and Tried-And-Rejected section of `CLOSED_LOOP_LEDGER.md`, the relevant/recent
   entries of `CAMPAIGN_LEDGER.md`, and `BEST_SCORES.md`. Read task-specific run
   records or source only after this orientation; do not ingest all history by
   default.

4. **Reconcile what's in flight.** Run the exact live-work discovery command from
   `OPERATING_CONTRACT.md`. For each claimed active run, compare scheduler/process
   state with `CURRENT_STATE.md`, any `RUNNING` marker, and the experiment's
   `RUN.md`. A marker alone is not evidence that a process exists. Confirm a prior
   process is terminal before proposing a replacement.

5. **Check working-tree state.** `git status -s` and `git log --oneline -5`. Flag any uncommitted work from a
   prior session as a loose end.

6. **Scan for landmines.** Pull the Tried-And-Rejected / NO-GO entries from the
   closed-loop ledger so you don't re-propose a rejected approach without a new
   argument.

## Output (a standup, not a report)

- **Where we are:** 1–2 lines from CURRENT_STATE; current goal + primary metric.
- **Contract:** active revision and evaluation status; report any mismatch or
  provisional gate.
- **In flight:** what's actually running, with ids/state and reconciled run record.
- **Immediate next step:** the single documented next action.
- **Open blockers.**
- **Uncommitted work.**
- **Don't re-run:** the relevant NO-GOs.

End by asking what to pick up, or proceed if the next step is unambiguous.
