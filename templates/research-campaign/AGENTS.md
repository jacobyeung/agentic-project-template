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

## 1. Fast Bootstrap (read little, grep the rest)

Read IN FULL — this set is small by design; keep the whole set under ~10k tokens:

1. This file.
2. `agent/agentic_information/CURRENT_STATE.md` — live snapshot (hard cap 1,500
   words): what is in flight, the immediate next step, open blockers, open
   closed-loop row ids.
3. `agent/agentic_information/OPERATING_CONTRACT.md` — active environment, resource
   limits, live-work command, launch rules, evaluation status. Confirm its revision
   matches the one quoted in `CURRENT_STATE.md`.

Everything else is **grep-on-demand — NEVER read end-to-end.** (In the live campaign
this template is distilled from, the ledger reached 181k words and bulk-reading it at
session start was the single largest token cost in the project.)

- `agent/agentic_information/TRIED_AND_REJECTED.md` — grep BEFORE opening any new
  hypothesis; do not rerun a NO-GO without a new mechanism.
- `agent/agentic_information/CLOSED_LOOP_LEDGER.md` (open + recent rows) and
  `agent/agentic_information/ledger_archive/` (rotated history; index at the top of
  each live file) — search by row id or topic when a specific prior experiment
  matters.
- `agent/agentic_information/CAMPAIGN_LEDGER.md` — history; primarily a write-target
  at session close.
- `agent/experiments/BEST_SCORES.md` — skim the table for the relevant area.
- Task-specific source, run records, reports, and deep-dive documents.

Then run the live-work discovery command from the operating contract and inspect
`git status --short` and `git log --oneline -5`. If live scheduler state, a `RUNNING`
marker, a run record, and `CURRENT_STATE.md` disagree, reconcile them before choosing
or relaunching work.

Size caps are mechanical, not aspirational: `python agent/rotate_ledgers.py` rotates
closed history into `ledger_archive/` (run it at every handoff; `--check` fails when
a live file exceeds its cap — that means close or rotate stale rows, not raise the
cap).

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
- launch, checkpoint, resume, cancellation, timeout, idle, and monitoring policies;
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

1. Grep `TRIED_AND_REJECTED.md` and existing `no_go` rows before proposing it.
2. Open a row in `CLOSED_LOOP_LEDGER.md` and state a falsifiable predicted effect and
   threshold before observing results.
3. Disclose the design before spending: the row (or its linked run record) states the
   full design and every delta versus the named incumbent/baseline in plain terms,
   and pre-registers the ablation controls that will make the result interpretable.
   A reviewer must never discover after an expensive run that the design differed
   from what they assumed.
4. Choose the smallest decisive test — the cheapest run that can still falsify the
   predicted check (one shard / one sample / one epoch) — and name the matched
   baseline. Scale up only after it survives.
5. Create the experiment directory and `RUN.md`.
6. The most useful pre-launch check is a diff, not a test suite: diff the new
   experiment's config/launcher against its named baseline and confirm the diff
   contains exactly the pre-registered deltas — nothing more. For config-only diffs
   on an already-proven stack, that diff review plus a short delta-smoke (reusing
   prior environment/import/data receipts) is sufficient; reserve full re-validation
   for changes that touch the contract surface (data schema, eval protocol, resource
   shape) or stale receipts. Prefer one decisive check over many weak ones.
7. Pass the launch gates in the operating contract; then set run state to
   `preflight_passed`.
8. Submit once, record the exact command and job/process id, and monitor it per the
   watcher rules in section 7.
9. Recover from a validated checkpoint when possible; confirm the prior process is
   terminal before replacement.
10. Evaluate with the active contract. Record provenance, uncertainty, and required
    output artifacts.
11. Compare with the preregistered threshold and relevant best. Keep, revert, retest,
    or mark `NO-GO` based on evidence; move durable NO-GOs to
    `TRIED_AND_REJECTED.md`.
12. Reconcile the run record, closed-loop ledger, campaign history, best-scores
    table, current state, and stale markers.

Launch latency target: on a proven stack, decision → submission takes minutes, not
hours. Reuse the newest proven launcher with a config delta; the diff review in step
6 is the gate. Hours spent in preflight mean you are rebuilding machinery instead of
diffing against it.

Row size: keep ledger rows compact — target ≤150 words across the free-text cells
(hypothesis, predicted check, result numbers, verdict, artifact pointers). The full
narrative lives in the run record or the area's report, referenced by path.

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

## 7. Delegation And Monitoring

Subagent briefs are self-contained. A dispatched subagent reads NOTHING from
`agent/agentic_information/` by default: every spawn prompt carries the goal,
done-criteria, exact files/paths, input/dataset selection, the specific standing
gotchas that apply, and the report path. Shared boilerplate that every subagent needs
(environment activation, universal gotchas, report conventions) lives once in
`agent/agentic_information/SUBAGENT_SHARED_CONTEXT.md`; briefs reference that one
file instead of repeating it. If a task builds on one specific prior experiment, the
brief names that one row or document and the subagent reads only it. Campaign state
stays with the orchestrating session — a subagent bootstrapping through the ledgers
is a defect. (Before this rule, subagents re-reading campaign state cost the source
campaign roughly 250k words per day across ~13 dispatches.)

Monitoring is cheap-cadence, never busy-wait. After submitting a job or subagent, do
not poll in agent turns every few seconds. Check at a minutes-scale cadence (5–10
minutes catches a dead job or subagent promptly), preferably via a watcher script
that sleeps in-process and exits with a clear code; then resume agent work. Before
arming any watcher, inspect the live state first — the event you are waiting for may
already have happened (arm-after-event races caused hour-long stalls in the source
campaign).

## 8. Research Intake

External reports and paper-derived candidates live in `reports/DeepResearch/`.

Each unprocessed report should be triaged:

```text
candidate -> prerequisites -> GO/NO-GO -> smallest probe -> A/B test -> verdict
```

Update both the report status table and the routed ledgers. Recheck time-sensitive
claims before spending substantial compute.

## 9. Result Routing

| Produced thing | Write it to |
|---|---|
| Live snapshot / one next action | `agent/agentic_information/CURRENT_STATE.md` (owner-keyed sections when several sessions run at once — overwrite only your own; analysis-only sessions skip it) |
| Active environment/resource/launch/eval policy | `agent/agentic_information/OPERATING_CONTRACT.md` |
| Fix / hypothesis verdict | `agent/agentic_information/CLOSED_LOOP_LEDGER.md` (compact row; narrative in the run record or report) |
| Durable NO-GO | `agent/agentic_information/TRIED_AND_REJECTED.md` (compact row + ledger-row pointer) |
| Experiment history / decision reason | `agent/agentic_information/CAMPAIGN_LEDGER.md` |
| Best eligible metric by area | `agent/experiments/BEST_SCORES.md` |
| Per-run control state and provenance | `agent/experiments/<area>/<experiment_tag>/RUN.md` |
| Compact evidence | `agent/experiments/<area>/<experiment_tag>/` |
| Large raw outputs | the external output root in `OPERATING_CONTRACT.md` |
| Build details / durable gotchas | `agent/agentic_information/<topic>_HANDOFF.md` or `<topic>_RESULT.md` |
| Research intake | `reports/DeepResearch/README.md` and the source report |

Routine findings belong in existing routed files. Create a deep-dive document only
when the result cannot be understood from the ledger and run artifacts.

## 10. Optional Multi-Agent Protocol

If `agent/coord.py` exists, read `agent/COORD_PROTOCOL.md` before starting shared work.

Rules in multi-agent mode:

- Never start an experiment without winning a lease.
- Heartbeat while running and mark work complete or failed.
- Treat `OPERATING_CONTRACT.md` as single-writer. `CURRENT_STATE.md` uses owner-keyed
  sections: each agent or session overwrites only its own section.
- Use the merge lock before merging to the protected branch.
- A lease coordinates ownership; it does not replace resource admission or preflight.

## 11. Autonomous Loop

```text
bootstrap (two-tier read) -> reconcile live work -> collect finished runs -> evaluate
-> close decisions -> choose one open row -> preregister/preflight -> admit resources
-> launch/observe/recover -> reconcile records -> verify -> commit -> repeat
```

At each loop boundary, prefer draining finished or invalid work over starting another
run. Stop only when the mission target is met, the user changes the objective, or a
real blocker requires authority or information that is unavailable.

## 12. Document Authority And Freshness

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
- Live files carry word caps (values in `agent/rotate_ledgers.py`). Run the rotation
  at every handoff; run `--check` before a handoff ends. A failed check means close
  or rotate stale rows and trim `CURRENT_STATE.md`, never raise the cap.
- When stale records disagree, inspect primary evidence, update the active source, and
  append a decision naming the superseded revision without rewriting old history.

## 13. Standing Gotchas

Keep only durable mechanisms and failure modes here:

- `<GOTCHA_OR_REJECTED_APPROACH_1>`
- `<GOTCHA_OR_REJECTED_APPROACH_2>`

Changing resource limits, current job ids, and temporary launch workarounds do not
belong here. Put them in the operating contract or current state and log the reason in
campaign history. Gotchas that every subagent needs are duplicated into
`agent/agentic_information/SUBAGENT_SHARED_CONTEXT.md` — keep the two in sync.
