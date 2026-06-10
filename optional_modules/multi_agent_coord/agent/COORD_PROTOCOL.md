# Multi-Agent Coordination Protocol

This protocol prevents coding agents from duplicating work, clobbering shared state,
or racing merges. It is implemented by `agent/coord.py` using only the Python standard
library and a runtime `.coord/` directory.

The hard rule:

> Do not start shared work unless you successfully claimed its lease with `coord.py`.
> Do not merge to `main` without the merge lock.

## 1. Runtime `.coord/`

`coord.py` creates this tree:

```text
.coord/
  LEASES/       <work_id>.lock/lease.json
  COMPLETED/    <work_id>.lock/lease.json
  FAILED/       <work_id>.lock/lease.json
  STATUS/       <agent_id>.json
  RUN_QUEUE.jsonl
  MAIN_MERGE.lock/info.json
```

`.coord/` is shared filesystem state, not git state. Add it to `.gitignore`.

Set `AGENT_COORD_DIR` when agents run from multiple worktrees, machines, containers,
or nodes:

```bash
export AGENT_COORD_DIR=/shared/path/project/.coord
```

`coord.py` prints the resolved coordination directory on every command. Confirm every
agent points at the same directory.

`AGENT_ID` is optional. By default, the current git worktree name is used.

## 2. Work Identity

Work IDs are deterministic names:

```text
work_id  = <category>__<exp_tag>__<split>__<seed>__<config_hash>
group_id = <category>__<exp_tag>__<split>__<config_hash>
```

For software projects, map the fields generically:

| Field | Software meaning | Research meaning |
|---|---|---|
| `category` | component / issue area | category / benchmark area |
| `exp_tag` | task or branch tag | experiment tag |
| `split` | milestone / test suite | dataset split |
| `seed` | attempt id / worker id | sample seed |
| `config` | relevant settings | prompt/model/config |

Example:

```bash
python agent/coord.py work-id \
  --category api \
  --exp-tag auth-timeout-fix \
  --split regression \
  --seed attempt1 \
  --config "python=3.11|pytest=auth"
```

## 3. Free-Explore Loop

Default mode:

```bash
python agent/coord.py reap
python agent/coord.py list
ls .coord/STATUS 2>/dev/null || true

WID=$(python agent/coord.py work-id \
  --category <area> \
  --exp-tag <task_tag> \
  --split <split_or_suite> \
  --seed <attempt> \
  --config "<config_summary>")

python agent/coord.py claim "$WID" --command "<command>" || exit 1
python agent/coord.py status --state running --work-id "$WID" --note "<short note>"

# Heartbeat in another shell/process during long work:
python agent/coord.py heartbeat "$WID" --note "still running"

# On success:
python agent/coord.py complete "$WID" --result "<result>"

# On failure:
python agent/coord.py fail "$WID" --error "<error>"
```

After completion, update the durable project ledger. `coord.py complete` is the
machine record; the markdown ledger is the human-readable verdict.

## 4. Optional Queue

`RUN_QUEUE.jsonl` is optional. Use it only when a human or coordinator wants to publish
a fixed batch for workers to drain.

```bash
python agent/coord.py add \
  --category <area> \
  --exp-tag <task_tag> \
  --split <split> \
  --seed <attempt> \
  --config "<config_summary>" \
  --command "<command>" \
  --smoke "<gate>"

python agent/coord.py next
```

Do not use the queue as the durable history. The ledgers are the history.

## 5. Current State

In multi-agent mode, `CURRENT_STATE.md` should be single-writer unless the project has
an explicit merge process for it. Workers publish status through:

```bash
python agent/coord.py status --state running --work-id "$WID" --note "<note>"
```

## 6. Merge Lock

Serialize merges to `main`:

```bash
python agent/coord.py merge-lock acquire
git pull --rebase origin main
<run quality gate>
git checkout main
git merge --no-ff <task-branch>
python agent/coord.py merge-lock release
```

Never force-push `main`, merge a failing gate, or merge another agent's unfinished work.

## 7. Command Reference

| Command | Purpose |
|---|---|
| `work-id` / `group-id` | print deterministic IDs |
| `add` | append a queue row |
| `next` | atomically claim first queue row |
| `claim <work_id>` | atomically claim a specific work item |
| `heartbeat <work_id>` | refresh lease liveness |
| `complete <work_id>` | move active lease to `COMPLETED/` |
| `fail <work_id>` | move active lease to `FAILED/` |
| `list` | list active leases |
| `reap` | move stale leases to `FAILED/` |
| `status` | write `.coord/STATUS/<agent_id>.json` |
| `merge-lock acquire|release` | serialize merges |
| `commit -m` | commit with `[agent_id][work_id]` prefix |
| `selftest` | dry-run coordination self-check |
