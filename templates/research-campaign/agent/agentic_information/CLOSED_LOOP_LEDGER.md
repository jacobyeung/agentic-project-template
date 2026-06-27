# Closed-Loop Ledger

Purpose: record hypotheses, predicted effects, tests, and verdicts. This is the
highest-authority file for what actually worked.

Status values: `pending`, `in_progress`, `blocked`, `done`, `reverted`, `no_go`,
`superseded`.

The predicted check is frozen before the run. Link every experiment to its durable
`RUN.md`; commands and numeric results without an artifact path are incomplete evidence.

| ID | Date | Status | Area | Hypothesis / Fix | Evidence Before | Predicted Check | Smallest Decisive Test | Run Record / Evidence | Result | Verdict / Next Step |
|---|---|---|---|---|---|---|---|---|---|---|
| CL-0001 | `<date>` | pending | `<area>` | `<change>` | `<why this should help>` | `<falsifiable threshold stated before running>` | `<command>` | `<experiment_dir>/RUN.md` | `<empty until evaluated>` | `<keep/revert/retest>` |

## Tried And Rejected

Add durable `NO-GO` decisions here so agents do not rerun the same idea without a new
mechanism.

| Date | Area | Idea | Reason Rejected | Evidence |
|---|---|---|---|---|
| `<date>` | `<area>` | `<idea>` | `<reason>` | `<path or command>` |
