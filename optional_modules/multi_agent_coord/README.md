# Optional Module: Multi-Agent Coordination

Install this module when more than one coding agent, worker, branch, worktree, or
machine may work on the same project concurrently.

```bash
rsync -a optional_modules/multi_agent_coord/ /path/to/project/
chmod +x /path/to/project/agent/coord.py
```

Then add this pointer to the target project's `AGENTS.md`:

```markdown
If `agent/coord.py` exists, read `agent/COORD_PROTOCOL.md` before starting shared work.
Never start shared work without winning a lease.
```

The runtime `.coord/` directory is created by `coord.py` and should never be committed.

```gitignore
.coord/
```
