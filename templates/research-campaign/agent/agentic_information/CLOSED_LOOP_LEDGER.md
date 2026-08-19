# Closed-Loop Ledger

Purpose: record hypotheses, predicted effects, tests, and verdicts. This is the
highest-authority file for what actually worked.

Status values: `pending`, `in_progress`, `blocked`, `done`, `reverted`, `no_go`,
`superseded`.

The predicted check is frozen before the run. Link every experiment to its durable
`RUN.md`; commands and numeric results without an artifact path are incomplete evidence.

Keep rows compact — target ≤150 words across the free-text cells. The narrative lives
in the run record or area report, referenced by path. Closed rows rotate to
`ledger_archive/` via `python agent/rotate_ledgers.py`; grep the archive index below
when an old row matters. Durable NO-GOs live in `TRIED_AND_REJECTED.md` (same
directory) — grep it before opening any new hypothesis.

## Archive index

- `<none yet>`

| ID | Date | Status | Area | Hypothesis / Fix | Evidence Before | Predicted Check | Smallest Decisive Test | Run Record / Evidence | Result | Verdict / Next Step |
|---|---|---|---|---|---|---|---|---|---|---|
| CL-0001 | `<date>` | pending | `<area>` | `<change>` | `<why this should help>` | `<falsifiable threshold stated before running>` | `<command>` | `<experiment_dir>/RUN.md` | `<empty until evaluated>` | `<keep/revert/retest>` |
