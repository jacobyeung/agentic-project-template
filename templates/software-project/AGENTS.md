# AGENTS.md - Canonical Bootstrap

If you are a coding agent working in this repo, read this file first.

This file is durable project guidance. Live status belongs in
`agent/agentic_information/CURRENT_STATE.md`.

## 0. Mission

Project: `<PROJECT_NAME>`

Mission: `<MISSION>`

Primary quality gate: `<QUALITY_GATE>`

Default operating mode: implement the requested work end to end, verify it, update the
right ledger, and commit when the change is coherent.

## 1. Read Current State First

Read these before making changes:

1. `agent/agentic_information/CURRENT_STATE.md` - live priorities, active work, blockers.
2. `agent/agentic_information/CLOSED_LOOP_LEDGER.md` - bugs, fixes, tests, verdicts.
3. `agent/agentic_information/CAMPAIGN_LEDGER.md` - decisions, releases, rejected approaches.
4. `docs/ARCHITECTURE.md` - high-level code structure.
5. `docs/TESTING.md` - test commands and quality gates.

## 2. Environment

Fill this in:

```bash
# Install
<INSTALL_COMMAND>

# Run locally
<RUN_COMMAND>

# Test
<TEST_COMMAND>

# Lint / format
<LINT_COMMAND>
```

Do not introduce a new package manager, framework, or service without recording the
decision in `CAMPAIGN_LEDGER.md`.

## 3. Working Rules

- Prefer existing project patterns over new abstractions.
- Keep edits scoped to the task.
- Add tests proportional to risk and blast radius.
- Do not rewrite unrelated files or revert user changes.
- Preserve public behavior unless the task explicitly changes it.
- Update docs when behavior, setup, or commands change.

## 4. Quality Gate

Before finishing, run:

```bash
<QUALITY_GATE_COMMAND>
```

If the full gate is too expensive, run the smallest relevant subset and explain what
was not run.

## 5. Closed-Loop Fix Process

For nontrivial bugs, regressions, migrations, or risky refactors:

1. Add a row to `CLOSED_LOOP_LEDGER.md`.
2. State the suspected cause and predicted check.
3. Implement the fix.
4. Run the test or reproduction.
5. Record the verdict.

## 6. Result Routing

| Produced thing | Write it to |
|---|---|
| Live task status | `agent/agentic_information/CURRENT_STATE.md` |
| Bug/fix/test verdict | `agent/agentic_information/CLOSED_LOOP_LEDGER.md` |
| Project decision / release note / rejected approach | `agent/agentic_information/CAMPAIGN_LEDGER.md` |
| Architecture change | `docs/ARCHITECTURE.md` |
| Test command change | `docs/TESTING.md` |
| Raw/generated run output | `runs/` or another explicit artifact directory |

## 7. Optional Multi-Agent Protocol

If `agent/coord.py` exists, read `agent/COORD_PROTOCOL.md` before starting shared work.

Rules in multi-agent mode:

- Claim work before starting.
- Publish status through `coord.py status`.
- Heartbeat while long-running work is active.
- Mark work complete or failed.
- Use the merge lock before merging to `main`.
- Treat `CURRENT_STATE.md` as single-writer unless the project says otherwise.

## 8. Standing Gotchas

Maintain durable project memory here:

- `<GOTCHA_OR_REJECTED_APPROACH_1>`
- `<GOTCHA_OR_REJECTED_APPROACH_2>`
