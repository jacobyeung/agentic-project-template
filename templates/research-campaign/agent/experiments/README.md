# Experiment Lifecycle And Run Record

Every experiment gets one self-describing directory:

```text
agent/experiments/<area>/<experiment_tag>/
```

Copy the run-record template below to `<experiment_dir>/RUN.md` before submission.
`RUN.md` and compact reviewable evidence are the tracked control record. Large raw
logs, checkpoints, predictions, and metric files live only at the external output root
named by the operating contract and are referenced here by path and digest.

## Lifecycle

Use these states and do not skip the decision stages:

```text
proposed -> preflight_passed -> submitted -> running -> finished
         -> evaluated -> decided -> archived
```

Terminal side paths are `blocked`, `failed`, `cancelled`, and `invalid`. `finished`
means execution ended, not that the hypothesis succeeded. `evaluated` means the
declared evaluation contract produced a valid artifact. `decided` means the ledger has
a keep, drop, retest, or no-go verdict.

The autonomous loop for one experiment is:

1. **Pre-register.** Link a closed-loop row, freeze the prediction and promotion or
   falsification threshold, name the matched baseline, and choose the smallest decisive
   test.
2. **Preflight.** Check theoretical feasibility and confounds where relevant, run the
   smoke test, freeze code/config/data identifiers, and perform resource admission
   against the current operating-contract revision.
3. **Submit.** Record the exact command and scheduler/process identifier immediately.
4. **Observe.** Reconcile the scheduler with markers and logs. Heartbeat long runs and
   diagnose stalls before blind resubmission.
5. **Recover.** Resume from a validated checkpoint when possible. Never create a
   duplicate run until the prior process is confirmed terminal.
6. **Evaluate.** Use the evaluation status and exact command in
   `OPERATING_CONTRACT.md`; record provenance and uncertainty with the result.
7. **Decide.** Compare with the registered threshold and relevant best, then close the
   ledger row. A score alone is not a verdict.
8. **Reconcile.** Update campaign history, best scores if eligible, current state, and
   cleanup markers. Commit tracked records separately from large raw artifacts.

## `RUN.md` Template

The hypothesis, predicted check, and matched baseline live in the closed-loop ledger
row — link it, do not repeat it. Every field below maps to a real failure mode: state
drift, unreproducible inputs, unrecoverable jobs, or a scheduler completion mistaken
for a verdict. Filling this in takes a minute; each line is one value or one command.

```markdown
# Run: <experiment_tag>

- State: proposed
- Owner: <agent-or-human>
- Closed-loop row: <CL-NNNN>
- Operating-contract revision: <OPS-NNNN>
- Last observed: <YYYY-MM-DD HH:MM TZ>

## Frozen Inputs

- Git commit (plus dirty-diff digest if dirty):
- Config path and digest:
- Data / checkpoint identifiers:
- Output path:

## Launch

- Baseline diff reviewed (exactly the pre-registered deltas): pending
- Smoke or delta-smoke result:
- Resource admission (observed total -> post-launch total):
- Exact launch command:
- Job / process identifier:

## Outcome

- Terminal state and reason:
- Exact evaluation command and metric artifact:
- Result vs registered threshold:
- Verdict (ledger row closed, best scores updated or ineligible):
```

The prediction is frozen in the ledger row before the run; do not edit it after
observing results. Append a dated correction that keeps the original text visible if
a factual mistake must be fixed. Anything else worth keeping (per-case drilldowns,
plots, manifests) goes in the experiment directory as ordinary files.
