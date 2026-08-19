# Subagent Shared Context

The ONE campaign file a dispatched subagent may be pointed at. Briefs stay
self-contained for everything task-specific; this file holds only what every
subagent needs, so briefs do not repeat it. Keep it under ~500 words — every
subagent pointed here reads it in full.

Subagents do not read `CURRENT_STATE.md`, the ledgers, or the operating contract.
If a task needs a fact from those files, the dispatching session pastes that fact
into the brief.

## Environment

- Activate: `<ENV_ACTIVATION_ONE_LINER>`
- Repository root: `<REPOSITORY_ROOT>`
- Raw outputs go under `<OUTPUT_ROOT>` — never in git.

## Universal gotchas

Standing rules that apply to every subagent task (one line each; keep in sync with
the Standing Gotchas section of `AGENTS.md`):

- `<UNIVERSAL_GOTCHA_1>`
- `<UNIVERSAL_GOTCHA_2>`

## Report conventions

- Write the report to the exact path given in the brief.
- Report raw numbers and name the dataset/split/sample count; quote failures
  verbatim.
- End with: done / not-done, evidence paths, and any deviation from the brief.
