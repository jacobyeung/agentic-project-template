---
name: codex
description: Dispatch a task to the Codex CLI (GPT-5.5) as an independent subagent that can write files and run commands. Use to OFFLOAD IMPLEMENTATION to GPT-5.5 instead of a Claude/Sonnet subagent when you have higher Codex limits, or to get an adversarial review / second opinion from a model that shares no context with you. Supports write-mode execution and read-only review.
version: 1.1.0
scope: project
---

# ruff: noqa: E501

# /codex — GPT-5.5 as a working subagent

The `codex` CLI runs GPT-5.5 as a subagent that **shares no context with you.**
Whether it can write/execute depends on the sandbox flag (and on
`~/.codex/config.toml`). Two primary uses:

1. **Offload implementation.** When you'd otherwise spawn a Claude/Sonnet subagent
   for self-contained work and your Codex budget is larger, dispatch Codex
   instead. It writes the code and runs the tests; **you review the diff and
   verify before keeping it.**
2. **Independent review.** Because it shares none of your context, it's a real
   second opinion — adversarial code review before an expensive commit, design
   pre-mortems, verdict/stats/claim attacks.

## Modes (pick the least-privilege one that works)

| Goal | Sandbox flag | Notes |
|---|---|---|
| Implement: edit repo + run tests | `-s workspace-write -C <repo>` | **Recommended for offloading.** Writes confined to the repo. `--add-dir <dir>` to also write another dir. |
| Implement: needs network / outside-repo writes / job submission | `-s danger-full-access` | Most powerful. **Isolate in a git worktree** so it can't disturb your live tree. |
| Review / second opinion only | `-s read-only` | Cannot modify files; the safe default for any "just look" task. |

## Model tier and effort (choose per task, pass explicitly)

Tier choice is judgment per task, never a mechanical default. Planning-class work
(spec design, architecture — anywhere a misread wastes a build round) leans the
strongest tier; routine implementation the middle tier; mechanical transforms the
cheapest. Pass BOTH the model and the reasoning effort explicitly on EVERY dispatch
(`-m <model> -c model_reasoning_effort=<low|medium|high>`). Keep a mid-tier default
in `~/.codex/config.toml` so an unflagged dispatch bills a mid cell — but the
default is a backstop, not a choice.

## Implementation-offload recipe

1. **Write a self-contained task spec** to a prompt file: goal, exact files to
   touch, constraints, and explicit **acceptance criteria** (which tests must
   pass). Codex starts cold and can't see your conversation. Do not tell it to
   read the project's agent-state files (`agent/agentic_information/`); paste the
   facts it needs into the spec.
2. **Optionally isolate** in a worktree:
   `git -C <repo> worktree add /tmp/cdx_<task> HEAD`, then point `-C` at it.
3. **Run it in the background** (high-effort runs take minutes):
   ```bash
   codex exec -m <model> -c model_reasoning_effort=<effort> \
     -s workspace-write -C "$REPO" \
     -o /tmp/codex_<task>.md - < /tmp/codex_<task>_prompt.md \
     > /tmp/codex_<task>.log 2>&1
   ```
   `-o <file>` captures Codex's final message; the redirect keeps the transcript.
   Check the output file at a minutes-scale cadence (5–10 min); never busy-wait
   in agent turns.
4. **Verify before keeping.** `git -C "$REPO" diff` to read every change, run the
   acceptance tests yourself, and only then keep or commit. Codex is the worker;
   you own the merge.

## Review recipe

`codex exec -m <model> -c model_reasoning_effort=<effort> -s read-only -C "$REPO" -o /tmp/codex_<task>.md - < prompt.md`.
Prompt it to attack/refute, default-to-skeptical, cite `file:line`, and end with a
BLOCKER/OK or PASS/FAIL verdict. Treat findings as claims to verify, not ground truth.

## Notes

- `--output-schema <schema.json>` makes Codex's final message conform to a schema;
  `--skip-git-repo-check` runs outside a git repo.
- Codex auto-discovers skills from `~/.codex/skills/` and this repo's
  `.codex/skills/` (when launched with `-C <repo>`), so it shares this project's
  skill set.
- Log a significant deployment (e.g. a pre-commit gate) in
  `CLOSED_LOOP_LEDGER.md` with the token count and transcript path.
