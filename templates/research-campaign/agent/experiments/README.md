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

```markdown
# Run: <experiment_tag>

- State: proposed
- Owner: <agent-or-human>
- Closed-loop row: <CL-NNNN>
- Operating-contract revision: <OPS-NNNN>
- Created: <YYYY-MM-DD HH:MM TZ>
- Last observed: <YYYY-MM-DD HH:MM TZ>

## Preregistration

- Hypothesis:
- Predicted check and threshold:
- Matched baseline:
- Smallest decisive test:
- Failure interpretation:

## Frozen Inputs

- Git commit and dirty diff path:
- Source/worktree content digest (or clean-tree assertion):
- Config path and digest:
- Data artifact and order/split digests:
- Checkpoint schema, resolved architecture/arguments, and branch:
- Environment identifier:
- Output path:

## Preflight

- Feasibility / mechanism argument:
- Pathological or confounded cases:
- Smoke-test command and result:
- Live resource observation:
- Requested resources and post-launch total:
- Preflight verdict: pending

## Execution

- Exact launch command:
- Required artifacts and expected formats:
- Run-manifest path and attempt number:
- Job/process identifier:
- Scheduler dependencies or array throttle:
- Checkpoint/resume command:
- Terminal state and reason:
- Artifact fingerprints attributed to this attempt:
- Retry output/task subset and protocol-change acknowledgement (if any):

## Evaluation

- Evaluation-contract status:
- Exact evaluation command:
- Metric artifact:
- Data split, filter, and sample count:
- Baseline result:
- Candidate result and uncertainty:

## Decision And Reconciliation

- Registered threshold met: pending
- Verdict: pending
- Closed-loop ledger updated: no
- Campaign ledger updated: no
- Best scores updated or ineligible reason:
- Current state updated: no
- Stale markers removed: no
```

Do not edit preregistered predictions after observing results. Append a dated correction
that makes the original text visible if a factual mistake must be fixed.
