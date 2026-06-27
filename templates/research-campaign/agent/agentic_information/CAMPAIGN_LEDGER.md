# Campaign Ledger

Append-only history for experiments, decisions, policies, and project-level context.
Do not rewrite history except to fix factual mistakes.

This file is historical, not the source of current operational policy. The active
resource, launch, environment, and evaluation rules live only in
`OPERATING_CONTRACT.md`. When policy changes, append a new decision row naming the old
revision it supersedes; do not rewrite the old row or interpret a newer-looking prose
note as an active override.

## Decision Log

| Date | Decision | Reason | Owner | Active source / supersession |
|---|---|---|---|---|
| `<date>` | `<decision>` | `<reason>` | `<owner>` | `<OPS-NNNN or durable document>` |

## Experiment History

| # | Date | Closed-loop row | Area | Experiment Tag | Contract Rev | Result | Verdict | Run Record |
|---:|---|---|---|---|---|---|---|---|
| 1 | `<date>` | `<CL-NNNN>` | `<area>` | `<tag>` | `<OPS-NNNN>` | `<metric plus uncertainty>` | `<verdict>` | `<experiment_dir>/RUN.md` |
