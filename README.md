# Agentic Project Template

Reusable project scaffolding for long-running coding-agent work.

This repository packages a domain-neutral agent-operations structure. It provides two
starter templates:

- `templates/research-campaign/` for research, benchmark, ablation, model, or experiment campaigns.
- `templates/software-project/` for normal software projects, products, libraries, and apps.

The name `agentic_information/` refers to the operational memory used by coding
agents such as Codex, Claude Code, Cursor, and similar tools. It is not tied to any
domain-specific agent inside the target project.

## Quick Start

Create a new project from one template:

```bash
mkdir -p ~/my-project
rsync -a ~/agentic-project-template/templates/software-project/ ~/my-project/
cd ~/my-project
git init
```

For a research or benchmark campaign:

```bash
mkdir -p ~/my-research-campaign
rsync -a ~/agentic-project-template/templates/research-campaign/ ~/my-research-campaign/
cd ~/my-research-campaign
git init
```

If multiple coding agents may work at the same time, install the optional coordination
module:

```bash
rsync -a ~/agentic-project-template/optional_modules/multi_agent_coord/ ~/my-project/
chmod +x ~/my-project/agent/coord.py
```

For a research campaign, replace the required bootstrap placeholders and remove or
fill every sample row in the live records. At every session handoff, rotate closed
ledger history and verify the live records stay under their word caps:

```bash
python agent/rotate_ledgers.py          # rotate closed history to ledger_archive/
python agent/rotate_ledgers.py --check  # fail if a live file exceeds its cap
```

For either template, start every agent session with `AGENTS.md`; its bootstrap section
names the small set of live records to read in full — everything else is grep-only.

## Core Ideas

- `AGENTS.md` is the canonical bootstrap. It changes rarely.
- `CURRENT_STATE.md` is the short live snapshot, under a hard word cap. When several
  sessions run at once its sections are owner-keyed: each writer owns only its own section.
- Research templates keep mutable environment, resource, launch, and evaluation rules
  in one revisioned `OPERATING_CONTRACT.md` instead of copying them into bootstrap or
  history files.
- `CLOSED_LOOP_LEDGER.md` records hypotheses, fixes, predicted checks, tests, and verdicts
  in compact rows; history is grep-only and rotates to `ledger_archive/` under word caps
  enforced by `agent/rotate_ledgers.py` (research template).
- `CAMPAIGN_LEDGER.md` is append-only project history and decision rationale.
- Every research run has a durable `RUN.md` that separates scheduler completion,
  evaluation, and scientific verdicts.
- Tracked run directories contain control records and compact evidence; large raw
  artifacts live under the explicit external output root in the operating contract.
- Subagent briefs are self-contained: shared boilerplate lives once in
  `SUBAGENT_SHARED_CONTEXT.md`; subagents never bootstrap through the ledgers.
- Optional `coord.py` provides leases, heartbeats, status files, completed work records, and a merge lock.

See [GUIDE.md](GUIDE.md) for the full operating model.
