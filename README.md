# Agentic Template

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
rsync -a ~/agentic-template/templates/software-project/ ~/my-project/
cd ~/my-project
git init
```

For a research or benchmark campaign:

```bash
mkdir -p ~/my-research-campaign
rsync -a ~/agentic-template/templates/research-campaign/ ~/my-research-campaign/
cd ~/my-research-campaign
git init
```

If multiple coding agents may work at the same time, install the optional coordination
module:

```bash
rsync -a ~/agentic-template/optional_modules/multi_agent_coord/ ~/my-project/
chmod +x ~/my-project/agent/coord.py
```

Then update the placeholders in `AGENTS.md` and start every agent session by reading it.

## Core Ideas

- `AGENTS.md` is the canonical bootstrap. It changes rarely.
- `CURRENT_STATE.md` is the short live snapshot. In multi-agent mode it is single-writer.
- `CLOSED_LOOP_LEDGER.md` records hypotheses, fixes, predicted checks, tests, and verdicts.
- `CAMPAIGN_LEDGER.md` is append-only project history and standing decisions.
- Raw outputs live under `experiments/`, `runs/`, or another explicit artifact directory.
- Optional `coord.py` provides leases, heartbeats, status files, completed work records, and a merge lock.

See [GUIDE.md](GUIDE.md) for the full operating model.
