# Campaign Ledger

Append-only history for experiments, decisions, policies, and project-level context.
Do not rewrite history except to fix factual mistakes.

## Running Totals

- Rounds completed: `0`
- Experiments completed: `0`
- Promoted changes: `0`
- Reverted / no-go changes: `0`

## Standing Policies

- Use the authoritative evaluation command from `AGENTS.md`.
- Record every promoted or rejected mechanism in `CLOSED_LOOP_LEDGER.md`.
- Keep raw outputs under `agent/experiments/`.
- Commit after completing a coherent unit of work.

## Decision Log

| Date | Decision | Reason | Owner |
|---|---|---|---|
| `<date>` | `<decision>` | `<reason>` | `<owner>` |

## Experiment History

| # | Date | Area | Experiment Tag | Config Summary | Result | Verdict | Output |
|---:|---|---|---|---|---|---|---|
| 1 | `<date>` | `<area>` | `<tag>` | `<config>` | `<metric>` | `<verdict>` | `<path>` |
