# Current State

Last updated: `<LAST_UPDATED>` by `<UPDATED_BY>`

Keep this file to one screen. It is a cache of the live situation, not evidence and not
history. Every result and decision below must point to its durable source.

## Snapshot

- Mission: `<MISSION>`
- Current best: `<CURRENT_BEST_WITH_EVIDENCE_POINTER>`
- Target: `<TARGET>`
- Active round: `<ROUND_OR_PHASE>`
- Operating contract: `<OPS_REVISION>`
- Open closed-loop rows: `<OPEN_CLOSED_LOOP_ROWS>`

## In Flight

This table is observational. Reconcile it with the live-discovery command in
`OPERATING_CONTRACT.md`; do not infer that a process exists from a marker alone.

| Work | Owner | Job / process ID | Started | Last observed | State | Contract rev | Run record |
|---|---|---|---:|---:|---|---|---|
| `<work_id>` | `<owner>` | `<id>` | `<time>` | `<time>` | `<submitted/running/blocked>` | `<contract-rev>` | `<experiment_dir>/RUN.md` |

## Latest Results

Keep at most the three results needed to choose the next action. The closed-loop and
campaign ledgers remain authoritative.

| Date | Closed-loop row | Experiment | Result with uncertainty | Verdict | Evidence |
|---|---|---|---:|---|---|
| `<date>` | `<closed-loop-row>` | `<tag>` | `<metric>` | `<promote/drop/retest>` | `<RUN.md or metric artifact>` |

## Blockers

- `<none or blocker>`

## Immediate Next Action

`<ONE_CONCRETE_ACTION_WITH_OWNER_AND_SUCCESS_CHECK>`

Do not list a menu. If the next action is an experiment, name its closed-loop row and
the smallest decisive test.

## Goal Gate

- Status: `<GOAL_STATUS>`
- Evidence: `<GOAL_EVIDENCE_POINTER>`
