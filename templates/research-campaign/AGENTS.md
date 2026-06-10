# AGENTS.md - Canonical Bootstrap

If you are a coding agent working in this repo, read this file first.

This file is the stable entry point. It changes rarely. Live status lives in
`agent/agentic_information/CURRENT_STATE.md`.

## 0. Mission

Project: `<PROJECT_NAME>`

Mission: `<MISSION>`

Primary metric: `<PRIMARY_METRIC>`

Target: `<TARGET>`

Default operating mode: autonomous, closed-loop experimentation. Do real work each
session, verify it, update the ledgers, and commit.

## 1. Read Current State First

Read these before choosing work:

1. `agent/agentic_information/CURRENT_STATE.md` - live snapshot and immediate next step.
2. `agent/agentic_information/CLOSED_LOOP_LEDGER.md` - hypotheses, fixes, tests, verdicts.
3. `agent/agentic_information/CAMPAIGN_LEDGER.md` - append-only experiment history and decisions.
4. `agent/experiments/BEST_SCORES.md` - best-known metrics by area.
5. Active processes or runs using the project-specific discovery command: `<LIVE_RUN_DISCOVERY_COMMAND>`.

## 2. Environment

Fill this in for the project:

```bash
# Python / runtime
<PYTHON_OR_RUNTIME_COMMAND>

# Install
<INSTALL_COMMAND>

# Test or smoke check
<SMOKE_TEST_COMMAND>
```

Use the pinned environment unless the task is explicitly to change it.

## 3. Authoritative Evaluation

The authoritative evaluation command is:

```bash
<EVALUATION_COMMAND>
```

Rules:

- Trust this command over ad hoc metrics.
- Record the exact command and output path for every result.
- Account for run-to-run noise before promoting a change.
- Compare against the relevant per-area best, not just the immediately previous run.

## 4. Experiment Conventions

Raw experiment outputs live under:

```text
agent/experiments/<area>/<experiment_tag>/
```

Use self-describing tags:

```text
experiment_<round_or_date>_<short_lever>
```

Each experiment must be reproducible from frozen inputs. Copy or version prompts,
configs, scripts, datasets, and model/tool settings that affect the result.

## 5. Closed-Loop Process

For every meaningful hypothesis or fix:

1. Add or update a row in `CLOSED_LOOP_LEDGER.md`.
2. State the predicted effect before running.
3. Run the smallest decisive test first.
4. Record the actual result.
5. Keep the change only if the evidence supports it.
6. Revert or mark `NO-GO` when the predicted effect does not appear.

Prefer high-certainty, mechanistic fixes over broad score-screening.

## 6. Failure Analysis

Run deeper analysis when a result changed behavior, regressed unexpectedly, or exposes
unknown failure modes. Bypass expensive analysis for pure confirmation runs where the
score itself is the verdict.

When dispatching analysis agents, require them to produce:

- `errors.md` or equivalent per-case drilldown in the experiment directory.
- `evaluator_agent_<area>.out` or equivalent full analysis output.
- Exact evidence: trace step, command, return value, last-good to first-bad pivot.
- Predicted follow-up checks.

## 7. Research Intake

External reports and paper-derived candidates live in `reports/DeepResearch/`.

Each unprocessed report should be triaged:

```text
candidate -> prerequisites -> GO/NO-GO -> build/probe -> A/B test -> verdict
```

Update both the report status table and the ledgers.

## 8. Result Routing

| Produced thing | Write it to |
|---|---|
| Live state | `agent/agentic_information/CURRENT_STATE.md` |
| Fix / hypothesis verdict | `agent/agentic_information/CLOSED_LOOP_LEDGER.md` |
| Experiment history / standing decision | `agent/agentic_information/CAMPAIGN_LEDGER.md` |
| Best metric by area | `agent/experiments/BEST_SCORES.md` |
| Raw outputs | `agent/experiments/<area>/<experiment_tag>/` |
| Build details / gotchas | `agent/agentic_information/<TOPIC>_HANDOFF.md` or `<TOPIC>_RESULT.md` |
| Research intake | `reports/DeepResearch/README.md` and the source report |

## 9. Optional Multi-Agent Protocol

If `agent/coord.py` exists, read `agent/COORD_PROTOCOL.md` before starting shared work.

Rules in multi-agent mode:

- Never start an experiment without winning a lease.
- Heartbeat while running.
- Mark work `complete` or `fail`.
- Treat `CURRENT_STATE.md` as single-writer unless the project explicitly says otherwise.
- Use the merge lock before merging to `main`.

## 10. Autonomous Loop

Default loop:

```text
read state -> drain pending ledger rows -> collect finished runs -> score -> analyze if warranted -> choose next work -> run -> record verdict -> commit
```

Keep going until the mission target is met or the user changes the objective.

## 11. Standing Gotchas

Maintain this section as durable project memory:

- `<GOTCHA_OR_REJECTED_APPROACH_1>`
- `<GOTCHA_OR_REJECTED_APPROACH_2>`
