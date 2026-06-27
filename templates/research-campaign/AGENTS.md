# AGENTS.md - Canonical Bootstrap

If you are a coding agent working in this repo, read this file first.

This file is the stable entry point and contains durable process rules. Live status
lives in `agent/agentic_information/CURRENT_STATE.md`. Mutable environment, resource,
launch, and evaluation policy lives in
`agent/agentic_information/OPERATING_CONTRACT.md`; do not duplicate it here.

## 0. Mission

Project: `<PROJECT_NAME>`

Mission: `<MISSION>`

Primary metric: `<PRIMARY_METRIC>`

Target: `<TARGET>`

Default operating mode: autonomous, closed-loop experimentation. Do real work each
session, verify it, update the routed records, and commit coherent verified units.

## 1. Fast Bootstrap

Start with a consistency check from the repository root:

```bash
python agent/validate_project.py
```

Resolve structural errors and an operating-contract revision mismatch before launching
new work. A freshness warning is a prompt to verify live state, not proof that the
record is wrong.

Then read and inspect in this order:

1. `agent/agentic_information/CURRENT_STATE.md` for the one-screen snapshot, open row
   ids, blockers, and single immediate action.
2. `agent/agentic_information/OPERATING_CONTRACT.md` for the active environment,
   resource limits, live-work command, launch rules, and evaluation status. Confirm its
   revision matches `CURRENT_STATE.md`.
3. The open or relevant rows plus `Tried And Rejected` in
   `agent/agentic_information/CLOSED_LOOP_LEDGER.md`. Do not reread the entire ledger
   unless the task requires it.
4. The relevant decisions and newest experiment entries in
   `agent/agentic_information/CAMPAIGN_LEDGER.md`. It is history, not active policy.
5. `agent/experiments/BEST_SCORES.md` for authoritative bests and their evidence.
6. Run the live-work discovery command from the operating contract, then inspect
   `git status --short` and `git log --oneline -5`.
7. Read only the task-specific source, run records, reports, or deep-dive documents.

If live scheduler state, a `RUNNING` marker, a run record, and `CURRENT_STATE.md`
disagree, reconcile them before choosing or relaunching work.

## 2. Repository And Quality Gates

Fill in durable repository-specific rules that do not change from run to run:

- Source roots: `<SOURCE_ROOTS>`
- Project quality gate: `<QUALITY_GATE>`
- Protected paths or outputs: `<PROTECTED_PATHS>`
- Commit policy: `<COMMIT_POLICY>`

Runtime commands and mutable operational constraints belong in the operating contract.

## 3. Operating Contract

`agent/agentic_information/OPERATING_CONTRACT.md` is the only active source for:

- environment activation, data roots, and output roots;
- resource limits, counting rules, packing, and serialization;
- the live-run discovery command and job-name/accounting convention;
- launch, checkpoint, resume, cancellation, timeout, and idle policies;
- evaluation readiness, exact command, required artifact, baseline matching, noise
  floor, and promotion threshold.

Never launch from a command copied out of an old ledger entry. Run resource admission
immediately before submission and record both observed and post-launch totals in the
experiment's `RUN.md`.

## 4. Experiment Conventions

Tracked experiment contracts and compact evidence live under:

```text
agent/experiments/<area>/<experiment_tag>/
```

Use self-describing tags:

```text
experiment_<round_or_date>_<short_lever>
```

Large raw artifacts live at the output root in the operating contract. Each experiment
must be reproducible from frozen inputs. Record the code revision and dirty diff,
config and digest, data/checkpoint identifiers, environment, exact commands, baseline,
and output path. Keep tracked control metadata separate from large raw artifacts.

Copy the `RUN.md` template and use the state machine in
`agent/experiments/README.md`. A scheduler completion is not an experimental verdict.

## 5. Preflight And Closed-Loop Process

For every meaningful hypothesis or fix:

1. Check `Tried And Rejected` and existing `no_go` rows before proposing it.
2. Open a row in `CLOSED_LOOP_LEDGER.md` and state a falsifiable predicted effect and
   threshold before observing results.
3. Choose the smallest decisive test and name the matched baseline.
4. Create the experiment directory and `RUN.md`.
5. Pass project-specific feasibility, confound, smoke, and resource-admission gates;
   then set run state to `preflight_passed`.
6. Submit once, record the exact command and job/process id, and observe or heartbeat
   the run.
7. Recover from a validated checkpoint when possible; confirm the prior process is
   terminal before replacement.
8. Evaluate with the active contract. Record provenance, uncertainty, and required
   output artifacts.
9. Compare with the preregistered threshold and relevant best. Keep, revert, retest, or
   mark `NO-GO` based on evidence.
10. Reconcile the run record, closed-loop ledger, campaign history, best-scores table,
    current state, and stale markers.

Results from a `not_implemented` or `provisional` evaluation contract are exploratory.
They can select a follow-up but cannot become a campaign-best or final claim.

## 6. Failure Analysis

Run deeper analysis when a result changed behavior, regressed unexpectedly, exposed an
unknown failure mode, or failed operationally in a way that could invalidate evidence.
Bypass expensive analysis for pure confirmation runs where the registered check itself
is decisive.

When dispatching analysis agents, require:

- `errors.md` or equivalent per-case drilldown in the experiment directory;
- `evaluator_agent_<area>.out` or equivalent full analysis output;
- exact evidence: path, trace/log step, command, return value, and last-good to
  first-bad pivot;
- certainty and predicted follow-up checks.

Operational failures and scientific falsifications are different. Mark corrupt,
confounded, or contract-violating evidence `invalid`; do not turn it into a `NO-GO`.

## 7. Research Intake

External reports and paper-derived candidates live in `reports/DeepResearch/`.

Each unprocessed report should be triaged:

```text
candidate -> prerequisites -> GO/NO-GO -> smallest probe -> A/B test -> verdict
```

Update both the report status table and the routed ledgers. Recheck time-sensitive
claims before spending substantial compute.

## 8. Result Routing

| Produced thing | Write it to |
|---|---|
| Live snapshot / one next action | `agent/agentic_information/CURRENT_STATE.md` |
| Active environment/resource/launch/eval policy | `agent/agentic_information/OPERATING_CONTRACT.md` |
| Fix / hypothesis verdict | `agent/agentic_information/CLOSED_LOOP_LEDGER.md` |
| Experiment history / decision reason | `agent/agentic_information/CAMPAIGN_LEDGER.md` |
| Best eligible metric by area | `agent/experiments/BEST_SCORES.md` |
| Per-run control state and provenance | `agent/experiments/<area>/<experiment_tag>/RUN.md` |
| Raw outputs | `agent/experiments/<area>/<experiment_tag>/` or the contract's output root |
| Build details / durable gotchas | `agent/agentic_information/<topic>_HANDOFF.md` or `<topic>_RESULT.md` |
| Research intake | `reports/DeepResearch/README.md` and the source report |

Routine findings belong in existing routed files. Create a deep-dive document only
when the result cannot be understood from the ledger and run artifacts.

## 9. Optional Multi-Agent Protocol

If `agent/coord.py` exists, read `agent/COORD_PROTOCOL.md` before starting shared work.

Rules in multi-agent mode:

- Never start an experiment without winning a lease.
- Heartbeat while running and mark work complete or failed.
- Treat `CURRENT_STATE.md` and `OPERATING_CONTRACT.md` as single-writer files unless
  the project explicitly says otherwise.
- Use the merge lock before merging to the protected branch.
- A lease coordinates ownership; it does not replace resource admission or preflight.

## 10. Autonomous Loop

```text
validate bootstrap -> reconcile live work -> collect finished runs -> evaluate
-> close decisions -> choose one open row -> preregister/preflight -> admit resources
-> launch/observe/recover -> reconcile records -> verify -> commit -> repeat
```

At each loop boundary, prefer draining finished or invalid work over starting another
run. Stop only when the mission target is met, the user changes the objective, or a
real blocker requires authority or information that is unavailable.

## 11. Document Authority And Freshness

Use this precedence when records disagree:

1. The user's current instruction sets the objective and permitted scope.
2. `OPERATING_CONTRACT.md` is authoritative for current mutable operations.
3. Live scheduler/process inspection is authoritative for whether work is actually
   running; `RUN.md` is authoritative for that run's declared provenance and state.
4. `CLOSED_LOOP_LEDGER.md` is authoritative for experimental verdicts.
5. `CAMPAIGN_LEDGER.md` is append-only history and rationale, including superseded
   policy; it never silently overrides the operating contract.
6. `CURRENT_STATE.md` is a short cache for fast orientation and must point to the
   sources above.
7. `AGENTS.md` is authoritative for durable process and routing, not changing values.

Freshness rules:

- Give mutable policy an explicit operating-contract revision. Bump it on every active
  policy change and update the revision in current state in the same change.
- Do not repeat active numeric limits or commands in gotchas, ledgers, handoffs, or
  bootstrap prose. Link to the operating contract instead.
- Avoid manually maintained totals that can be derived from ledger rows.
- Every current-state result points to a run record or metric artifact. Keep at most
  three recent results and exactly one immediate next action.
- Run `python agent/validate_project.py` before a launch and at handoff. Treat warnings
  as verification prompts and errors as blockers to new launches.
- When stale records disagree, inspect primary evidence, update the active source, and
  append a decision naming the superseded revision without rewriting old history.

## 12. Standing Gotchas

Keep only durable mechanisms and failure modes here:

- `<GOTCHA_OR_REJECTED_APPROACH_1>`
- `<GOTCHA_OR_REJECTED_APPROACH_2>`

Changing resource limits, current job ids, and temporary launch workarounds do not
belong here. Put them in the operating contract or current state and log the reason in
campaign history.
