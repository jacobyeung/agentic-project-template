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
rules: mission, repo layout, environment, test gates, update rules, coordination rules,
and known gotchas. Avoid putting rapidly changing status here.

`agent/agentic_information/CURRENT_STATE.md` is the volatile snapshot. It answers:
where are we, what is in flight, what is the immediate next step, and what is blocked.
Keep it short.

`agent/agentic_information/CLOSED_LOOP_LEDGER.md` records cause-and-effect work. Every
nontrivial fix or experiment should say what it was expected to change, how it was
tested, what happened, and whether it was kept.

`agent/agentic_information/CAMPAIGN_LEDGER.md` is append-only history. It records
decisions, attempts, rejected options, and long-lived policies.

`agent/experiments/` or `runs/` stores immutable outputs. Do not treat a markdown ledger
as the only record of a run.

`reports/DeepResearch/` is optional. Use it when external research reports, papers, or
candidate technologies feed the project.

## Update Routing

Use this rule in every project:

| Produced thing | Write it to |
|---|---|
| Live status | `CURRENT_STATE.md`, or `.coord/STATUS/<agent>.json` in multi-agent mode |
| Fix or experiment verdict | `CLOSED_LOOP_LEDGER.md` |
| Project history / decisions | `CAMPAIGN_LEDGER.md` |
| Raw outputs | `experiments/`, `runs/`, or equivalent |
| Architecture notes | `docs/ARCHITECTURE.md` or a named handoff/result doc |
| Research candidate status | `reports/DeepResearch/README.md` plus relevant report file |

## Recommended Agent Loop

```text
1. Read AGENTS.md.
2. Read CURRENT_STATE.md.
3. Read CLOSED_LOOP_LEDGER.md and CAMPAIGN_LEDGER.md.
4. Check active work.
5. Choose one unowned task.
6. Implement, run, or analyze.
7. Verify with the project gate.
8. Record the result in the right ledger.
9. Commit.
```

In multi-agent mode, step 5 becomes: claim a lease with `agent/coord.py` before doing
work, heartbeat while running, and mark it complete or failed.

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
- Fill in the environment commands.
- Define where raw outputs go.
- Define the required test/evaluation command.
- Decide who may write `CURRENT_STATE.md`.
- Add known gotchas and rejected approaches as they are discovered.
- Add `.coord/` to `.gitignore` if using the optional coordination module.
- Commit the initialized template before starting substantive work.

## Naming Guidance

Keep `CLOSED_LOOP_LEDGER.md` and `CAMPAIGN_LEDGER.md`. They are generic and useful.

Keeping `agentic_information/` is also reasonable. In this template it means
"information for coding agents operating the repo." If a team finds the name confusing,
`agent_state/` or `agent_ops/` are acceptable aliases, but pick one and use it
consistently.
