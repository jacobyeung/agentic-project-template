# Operating Contract

Revision: `<OPS_REVISION>`

Last verified: `<LAST_VERIFIED>` by `<VERIFIED_BY>`

Contract status: `<CONTRACT_STATUS>`

Allowed values are `ready`, `provisional`, and `blocked`.

`ready` means the contract is complete for normal launches. `provisional` allows only
the explicitly scoped exploratory work whose limitation is recorded in `RUN.md`.
`blocked` permits reconciliation and analysis but no new launch.

This file is the single current source of truth for environment, resource, launch,
and evaluation policy. `AGENTS.md` contains durable process rules; the campaign
ledger records historical policy decisions. Do not copy active limits or commands
into either file.

When any active policy changes, update this file in place, bump the revision, append
the reason to `CAMPAIGN_LEDGER.md`, and update the revision referenced by
`CURRENT_STATE.md`. The new append-only decision entry must name the revision it
supersedes; old rows remain unchanged as historical evidence.

## Environment

```bash
# Python / runtime
<PYTHON_OR_RUNTIME_COMMAND>

# Install or environment activation
<INSTALL_COMMAND>

# CPU-safe smoke check
<SMOKE_TEST_COMMAND>
```

- Repository root: `<REPOSITORY_ROOT>`
- Data root: `<DATA_ROOT>`
- Raw output root: `<OUTPUT_ROOT>`
- Use the pinned environment unless the task explicitly changes it.

## Resource Budget

Every limit below is a simultaneous-allocation limit unless the counting rule says
otherwise. Count running work plus queued work that can become concurrent. For arrays,
count the throttle multiplied by resources per task; for multi-process jobs, count the
whole allocation.

| Resource | Scope | Hard limit | Counting rule | Admission check | Enforcement |
|---|---|---:|---|---|---|
| `<RESOURCE>` | `<RESOURCE_SCOPE>` | `<LIMIT>` | `<HOW_TO_SUM_CONCURRENT_USE>` | `<ADMISSION_COMMAND>` | `<ENFORCEMENT>` |

Rules:

- Run the admission check immediately before every submission and record the observed
  total plus the post-launch total in the experiment's `RUN.md`.
- All cooperating launchers must hold one shared lock (or use an equivalent
  scheduler-enforced transaction) from the live observation through submission. A
  check followed by an unlocked submit has a race under multiple agents.
- Count every queued branch that may become concurrent. Collapse only relationships
  proven serialized by an array throttle, singleton lane, or explicit dependency
  chain; do not assume an arbitrary dependency prevents overlap.
- A job that would exceed a hard limit must not be submitted, even if the scheduler
  might leave it pending.
- State whether packing is required, allowed, or forbidden: `<PACKING_POLICY>`.
- State whether full-size jobs must be serialized: `<SERIALIZATION_POLICY>`.
- Use this job-name prefix for project accounting: `<JOB_NAME_PREFIX>`.

## Live Work Discovery

The authoritative discovery command is:

```bash
<LIVE_RUN_DISCOVERY_COMMAND>
```

Also inspect durable run state under `agent/experiments/` and reconcile stale
`RUNNING` markers against the scheduler before trusting either source alone.

## Launch Contract

- Scheduler or execution backend: `<EXECUTION_BACKEND>`
- Canonical launcher or command: `<LAUNCH_COMMAND>`
- Checkpoint/resume policy: `<CHECKPOINT_AND_RESUME_POLICY>`
- Timeout or idle-reaping policy: `<TIMEOUT_POLICY>`
- Cancellation command: `<CANCELLATION_COMMAND>`

`<LAUNCH_COMMAND>` must implement the shared admission-to-submission critical section
for cooperating projects. Direct backend submission is forbidden because it bypasses
that transaction, provenance checks, and retry scoping. Document any external callers
that do not honor the shared lock as an explicit residual race.

If the backend supports held submission, prefer this transaction: issue one owner-only
admission receipt from the clean admitted snapshot, submit the job held, bind the
receipt to the returned backend job id plus adapter digest/task subset, then release.
The runtime consumes that exact receipt. Do not treat a caller-exported boolean or
unbound token as authorization.

No experiment may launch until all of these are true:

- Contract status is `ready`, or it is `provisional` and the permitted scope and
  limitation are explicit in `RUN.md`.
- A closed-loop row exists with a falsifiable predicted check stated before the run.
- The smallest decisive test has been selected.
- The experiment directory contains a `RUN.md` copied from the template in
  `agent/experiments/README.md` and its state is `preflight_passed`.
- Inputs, code revision, config, baseline, and output path are frozen or identified.
- The exact launcher is tracked and the scientific source/config/preregistration
  worktree is clean. If dirty launches are intentionally allowed for smokes, persist a
  content digest or patch—not merely a list of dirty paths.
- The resource admission check passes under this contract revision.
- The smoke check passes, and any project-specific feasibility or confound gate is
  documented.

## Evaluation Contract

Evaluation status: `<EVALUATION_STATUS>`

Allowed values are `not_implemented`, `provisional`, and `authoritative`.

```bash
<EVALUATION_COMMAND>
```

- Required output: `<EVALUATION_OUTPUT>`
- Primary metric and direction: `<PRIMARY_METRIC_AND_DIRECTION>`
- Matched-baseline requirements: `<BASELINE_MATCHING_RULES>`
- Noise-floor requirement: `<SEED_OR_UNCERTAINTY_RULE>`
- Promotion threshold: `<PROMOTION_THRESHOLD>`

Results produced while status is `not_implemented` or `provisional` are exploratory.
They may guide the next test but must not be promoted as a campaign-best or final claim.
Every reported result must include the exact command, artifact path, data split, sample
count, baseline, and contract revision.

Dataset indices must be bound to the exact ordered data artifact they index. Pin and
verify a full artifact digest or a documented per-sample/order fingerprint; counts
alone do not establish population identity.

## Artifact And Checkpoint Contract

- A process exit code and scheduler `COMPLETED` state are not completion. A successful
  attempt must create or change every declared nonempty artifact; structured artifacts
  must parse, and their fingerprints must be recorded atomically with terminal state.
- A prior artifact may be skipped only when its succeeded manifest, required-artifact
  set, and current fingerprints all match. Filename existence is insufficient.
- Training checkpoints use a supported schema version and persist the fully resolved
  architecture, config digest, training arguments, and branch identity. Legacy
  checkpoints may remain read-only but must not resume silently under current aliases.
- Retries name the exact failed/stale output set. Array retries also name the exact task
  subset, with one output per task. Command or code changes require an explicit,
  recorded protocol-change acknowledgement or a new output directory.

## Recovery And Cleanup

- A running job must have a scheduler/process identifier and last-observed time in both
  its `RUN.md` and `CURRENT_STATE.md`.
- On restart, verify the process is gone before resubmitting. Prefer resume from the
  last valid checkpoint over a duplicate fresh launch.
- A stale `running` record is retryable only after its scheduler identity is confirmed
  absent. A retry acknowledgement for one output must not authorize unrelated work.
- On failure or cancellation, preserve logs, record the terminal state, remove stale
  `RUNNING` markers, and decide whether the evidence is valid, invalid, or incomplete.
- On completion, evaluate once with the contract above, route the verdict to the
  ledgers, update best scores only when promotion criteria pass, and leave one concrete
  next action in `CURRENT_STATE.md`.
