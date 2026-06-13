---
name: codex
description: Dispatch a task to the Codex CLI (GPT-5.5) as an independent subagent that can write files and run commands. Use to OFFLOAD IMPLEMENTATION to GPT-5.5 instead of a Claude/Sonnet subagent when you have higher Codex limits, or to get an adversarial review / second opinion from a model that shares no context with you. Supports write-mode execution and read-only review.
version: 1.0.0
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

## Implementation-offload recipe

1. **Write a self-contained task spec** to a prompt file: goal, exact files to
   touch, constraints, and explicit **acceptance criteria** (which tests must
   pass). Codex starts cold and can't see your conversation.
2. **Optionally isolate** in a worktree:
   `git -C <repo> worktree add /tmp/cdx_<task> HEAD`, then point `-C` at it.
3. **Run it in the background** (xhigh runs take minutes):
   ```bash
   codex exec -m gpt-5.5 -s workspace-write -C "$REPO" \
     -o /tmp/codex_<task>.md - < /tmp/codex_<task>_prompt.md \
     > /tmp/codex_<task>.log 2>&1
   ```
   `-o <file>` captures Codex's final message; the redirect keeps the transcript.
4. **Verify before keeping.** `git -C "$REPO" diff` to read every change, run the
   acceptance tests yourself, and only then keep or commit. Codex is the worker;
   you own the merge.

## Review recipe

`codex exec -m gpt-5.5 -s read-only -C "$REPO" -o /tmp/codex_<task>.md - < prompt.md`.
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
