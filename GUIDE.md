# Guide

This template is for projects where coding agents need durable memory, repeatable
workflows, and clear rules for updating state. It works for a single agent, but it is
especially useful when the project runs for many days or multiple agents share work.

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
Keep it to one screen and treat it as a cache: its results and run states should point
to durable evidence.

`agent/agentic_information/OPERATING_CONTRACT.md` is the revisioned source for current
environment, resource, launch, recovery, and evaluation policy in a research campaign.
This separation matters because numeric limits and commands change more often than the
bootstrap process. Update the active contract once, bump its revision, log the reason
in append-only history, and have current state reference the new revision.

`agent/agentic_information/CLOSED_LOOP_LEDGER.md` records cause-and-effect work. Every
nontrivial fix or experiment should say what it was expected to change, how it was
tested, what happened, and whether it was kept.

`agent/agentic_information/CAMPAIGN_LEDGER.md` is append-only history. It records
decisions, attempts, rejected options, and historical policy changes. Current mutable
policy belongs in the research template's operating contract.

`agent/experiments/` or `runs/` stores immutable outputs. Do not treat a markdown ledger
as the only record of a run. In the research template, each experiment also gets a
tracked `RUN.md` control record containing preregistration, frozen inputs, resource
admission, job identity, evaluation provenance, and reconciliation status.

`reports/DeepResearch/` is optional. Use it when external research reports, papers, or
candidate technologies feed the project.

## Update Routing

Use this rule in every project:

| Produced thing | Write it to |
|---|---|
| Live status | `CURRENT_STATE.md`, or `.coord/STATUS/<agent>.json` in multi-agent mode |
| Active environment/resource/launch/eval policy (research) | `OPERATING_CONTRACT.md` |
| Fix or experiment verdict | `CLOSED_LOOP_LEDGER.md` |
| Project history / decisions | `CAMPAIGN_LEDGER.md` |
| One run's state and provenance (research) | `<experiment_dir>/RUN.md` |
| Raw outputs | `experiments/`, `runs/`, or equivalent |
| Architecture notes | `docs/ARCHITECTURE.md` or a named handoff/result doc |
| Research candidate status | `reports/DeepResearch/README.md` plus relevant report file |

## Recommended Research Agent Loop

```text
1. Validate the bootstrap and reconcile current state with live work.
2. Read the current operating-contract revision and the relevant open/no-go rows.
3. Collect and evaluate finished work before launching more.
4. Choose one unowned hypothesis and preregister its falsifiable threshold.
5. Create its run record, freeze inputs, pass preflight, and admit resources.
6. Launch once, observe it, and recover rather than duplicate it.
7. Evaluate under the declared contract and decide against the registered threshold.
8. Reconcile the run record, ledgers, best scores, current state, and markers.
9. Verify the project gate and commit one coherent unit.
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
- Use `python agent/validate_project.py` before launch and handoff. Structural errors
  block new launches; age warnings trigger live verification.

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
- `codex` — dispatch GPT-5.5 as an independent subagent, to offload implementation
  or get a second opinion.

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
- Decide who may write `CURRENT_STATE.md`.
- Add known gotchas and rejected approaches as they are discovered.
- Add `.coord/` to `.gitignore` if using the optional coordination module.
- Run `python agent/validate_project.py`; resolve every error before the first launch.
- Commit the initialized template before starting substantive work.

## Naming Guidance

Keep `CLOSED_LOOP_LEDGER.md` and `CAMPAIGN_LEDGER.md`. They are generic and useful.

Keeping `agentic_information/` is also reasonable. In this template it means
"information for coding agents operating the repo." If a team finds the name confusing,
`agent_state/` or `agent_ops/` are acceptable aliases, but pick one and use it
consistently.
