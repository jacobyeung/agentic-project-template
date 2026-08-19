# Guide

This template is for projects where coding agents need durable memory, repeatable
workflows, and clear rules for updating state. It works for a single agent, but it is
especially useful when the project runs for many days or multiple agents share work.

The templates distill a live autonomous research campaign. The launch contracts
encode these failure boundaries: admission and submission share one
critical section; queued resource branches count unless provably serialized;
completion belongs to artifacts one attempt produced; scientific inputs are frozen
and content-identified; retries name exact outputs/task subsets; and data/checkpoint
schemas bind results to their true inputs. Where the scheduler supports held
submission, bind a one-use admission receipt to the actual job id and adapter digest
before release; an exported flag is not authorization. Projects provide
scheduler-specific implementations for these contracts.

Context economy is mechanical, not aspirational. Agents read a small live set in
full and grep everything else; live files carry word caps; and
`agent/rotate_ledgers.py` rotates closed rows into `ledger_archive/`, with `--check`
enforcing the caps. Subagent briefs are self-contained, with shared boilerplate in
one designated file rather than subagents reading campaign state. Watchers sleep
in-process and report at a minutes-scale cadence; agent-turn polling loops burn
model quota for nothing. Checks are few and
decisive: the pre-launch gate is a diff against the named baseline showing exactly
the pre-registered deltas, so a launch on a proven stack takes minutes, not hours;
and an expensive run must run its standard evaluation in its own chain or disclose
the gap explicitly.

## Which Template To Use

Use `templates/research-campaign/` when the core loop is:

```text
hypothesis -> experiment -> metric -> analysis -> next hypothesis
```

Examples: benchmark optimization, model ablations, perception tool campaigns, data
quality studies, scientific pipelines, paper-support experiments.

Use `templates/software-project/` when the core loop is:

```text
issue/feature -> implementation -> tests -> review -> release/merge
```

Examples: apps, services, CLIs, libraries, internal tools, data products.

## File Roles

`AGENTS.md` is the stable entry point for all coding agents. It should contain durable
rules: mission, repo layout, quality gates, update routing, coordination, known gotchas,
and links to current operations. Avoid putting changing commands, limits, or status
here.

`agent/agentic_information/CURRENT_STATE.md` is the volatile snapshot. It answers:
where are we, what is in flight, what is the immediate next step, and what is blocked.
Keep it to one screen (hard word cap) and treat it as a cache: its results and run
states should point to durable evidence. When several sessions run at once its
sections are owner-keyed — each writer overwrites only its own section.

`agent/agentic_information/OPERATING_CONTRACT.md` is the revisioned source for current
environment, resource, launch, recovery, and evaluation policy in a research campaign.
This separation matters because numeric limits and commands change more often than the
bootstrap process. Update the active contract once, bump its revision, log the reason
in append-only history, and have current state reference the new revision.

`agent/agentic_information/CLOSED_LOOP_LEDGER.md` records cause-and-effect work. Every
nontrivial fix or experiment should say what it was expected to change, how it was
tested, what happened, and whether it was kept. Rows stay compact (~150 words; the
narrative lives in the run record). In the research template, closed rows rotate to
`agent/agentic_information/ledger_archive/` via `agent/rotate_ledgers.py`, durable
NO-GOs live in `TRIED_AND_REJECTED.md`, and history is grep-only — never read a
ledger end-to-end.

`agent/agentic_information/CAMPAIGN_LEDGER.md` is append-only history. It records
decisions, attempts, rejected options, and historical policy changes. Current mutable
policy belongs in the research template's operating contract.

`agent/agentic_information/SUBAGENT_SHARED_CONTEXT.md` (research template) is the one
campaign file a dispatched subagent may be pointed at: environment activation,
universal gotchas, report conventions. Briefs stay self-contained for everything
task-specific; subagents never bootstrap through the ledgers.

`agent/experiments/` or `runs/` stores immutable control records and compact evidence;
do not treat a summary ledger as the only record of a run. In the research template,
large raw artifacts live at the external output root named by the operating contract,
while each tracked experiment gets a short `RUN.md` carrying its state, frozen
inputs, resource admission, exact launch command, job identity, and outcome; the
hypothesis and predicted check live in the linked closed-loop row, not duplicated.

## Update Routing

Use this rule in every project:

| Produced thing | Write it to |
|---|---|
| Live status | `CURRENT_STATE.md`, or `.coord/STATUS/<agent>.json` in multi-agent mode |
| Active environment/resource/launch/eval policy (research) | `OPERATING_CONTRACT.md` |
| Fix or experiment verdict | `CLOSED_LOOP_LEDGER.md` (compact row) |
| Durable NO-GO (research) | `TRIED_AND_REJECTED.md` |
| Project history / decisions | `CAMPAIGN_LEDGER.md` |
| One run's state and provenance (research) | `<experiment_dir>/RUN.md` |
| Raw outputs | the external output root named by `OPERATING_CONTRACT.md` |
| Architecture notes | `docs/ARCHITECTURE.md` or a named handoff/result doc |

## Recommended Research Agent Loop

```text
1. Bootstrap with the two-tier read order and reconcile current state with live work.
2. Read the current operating-contract revision and grep the relevant open/no-go rows.
3. Collect and evaluate finished work before launching more.
4. Choose one unowned hypothesis and preregister its falsifiable threshold,
   design deltas, and controls.
5. Create its run record, freeze inputs, review the diff against the named
   baseline, and admit resources.
6. Launch once, monitor at a minutes-scale cadence, and recover rather than
   duplicate it.
7. Evaluate under the declared contract and decide against the registered threshold.
8. Reconcile the run record, ledgers, best scores, current state, and markers.
9. Verify the project gate, rotate/check the ledgers, and commit one coherent unit.
```

In multi-agent mode, claim a lease before step 4, heartbeat while running, and mark the
lease complete or failed. Ownership coordination does not replace resource admission.

## Preventing Stale Or Contradictory Documents

Keep stable process, current policy, live state, evidence, and history in different
files. In particular:

- Do not repeat active numeric resource limits or launch/evaluation commands in
  `AGENTS.md`, gotchas, handoffs, or append-only history.
- Treat old campaign-ledger policies as history. Append a new decision that names the
  superseded revision and links to the current operating contract; do not rewrite the
  old row.
- Do not maintain hand-counted totals when they can be derived from ledger rows.
- Put no more than three decision-relevant results and exactly one next action in
  `CURRENT_STATE.md`.
- Record the policy revision used by every active job and experiment. A revision
  mismatch is an actionable stale-state signal.
- Run `python agent/rotate_ledgers.py` at every handoff and `--check` before the
  session ends (research template). A failing cap means close or rotate stale rows
  and trim `CURRENT_STATE.md`, never raise the cap.
- Prefer one decisive check over many weak ones. The highest-value pre-launch check
  is a diff of the new experiment against its named baseline showing exactly the
  planned deltas; add further gates only when they have caught a real defect.

## Skills

Both templates ship reusable agent skills under `.claude/skills/` (for Claude Code)
and `.codex/skills/` (for Codex). Each tool auto-discovers them when it runs in the
project, so a freshly copied template comes with them already wired. They
operationalize the loop and routing rules above:

- `resume` — session-start standup: reads `AGENTS.md` and the ledgers in order and
  reports where things stand. Read-only.
- `handoff` — session-close: writes findings only to the routed files, commits
  completed work, and never invents a file path.
- `closed-loop` — open or close a `CLOSED_LOOP_LEDGER.md` row in the project's schema.
- `summary` — how to write a recap for a reader who did not watch the work.
- `codex` — dispatch Codex as an independent subagent, to offload implementation or
  get a second opinion. Pick tier and effort per task and pass them explicitly on
  every dispatch; write self-contained briefs (subagents never read campaign state).

Edit or delete any skill per project. Keep the `.claude/` and `.codex/` copies in
sync, or symlink one directory to the other.

## Multi-Agent Coordination

The coordination module is optional. Install it only when simultaneous agents, workers,
or machines may touch the same project.

```bash
rsync -a optional_modules/multi_agent_coord/ /path/to/project/
chmod +x /path/to/project/agent/coord.py
```

Then read `/path/to/project/agent/COORD_PROTOCOL.md` and add a short pointer from the
project's `AGENTS.md`.

The runtime `.coord/` directory is intentionally not committed. It contains leases,
completed work records, failed work records, per-agent status files, an optional queue,
and a merge lock.

## Customization Checklist

Before using a copied template:

- Replace `<PROJECT_NAME>`, `<MISSION>`, `<PRIMARY_METRIC>`, and `<QUALITY_GATE>`.
- Fill in `OPERATING_CONTRACT.md`, including environment, resource counting,
  live-discovery, recovery, and evaluation readiness.
- Define where raw outputs go.
- Define the required test/evaluation command and mark whether it is not implemented,
  provisional, or authoritative.
- Decide who may write `CURRENT_STATE.md` (owner-keyed sections when several
  sessions run at once).
- Fill `SUBAGENT_SHARED_CONTEXT.md` before the first dispatch, or delete it if the
  project never dispatches subagents.
- Add known gotchas and rejected approaches as they are discovered.
- Add `.coord/` to `.gitignore` if using the optional coordination module.
- Keep the word caps in `agent/rotate_ledgers.py` as shipped unless the project has
  a stated reason; a failing `--check` means rotate or trim, not raise the cap.
- Commit the initialized template before starting substantive work.

## Naming Guidance

Keep `CLOSED_LOOP_LEDGER.md` and `CAMPAIGN_LEDGER.md`. They are generic and useful.

Keeping `agentic_information/` is also reasonable. In this template it means
"information for coding agents operating the repo." If a team finds the name confusing,
`agent_state/` or `agent_ops/` are acceptable aliases, but pick one and use it
consistently.
