#!/usr/bin/env python3
"""coord.py - multi-agent work coordination via atomic-mkdir leases.

Stdlib only. Every agent (Claude Code, Cursor, Codex) calls this identically.
The coordination dir is SHARED FILESYSTEM state and is NEVER committed to git
(the .coord/ tree is created at runtime by this script).

Coord-dir resolution (PRINTED on every run so a wrong dir is obvious):
  1. $AGENT_COORD_DIR if set  <-- use this for cross-worktree / cross-machine runs:
        export AGENT_COORD_DIR=/shared/path/project/.coord
  2. else  <main-worktree>/.coord   (parent of `git rev-parse --git-common-dir`)
     Convenient for same-machine worktrees, but risks split-brain across machines
     or containers. Prefer option 1 when coordination really matters.

work_id  = <category>__<exp_tag>__<split>__<seed>__<config_hash>   (one work item)
group_id = <category>__<exp_tag>__<split>__<config_hash>           (related work group)

The atomic primitive is os.mkdir(LEASES/<work_id>.lock): if two agents race to
claim the same work_id, only one mkdir succeeds. The loser picks another task.

Full protocol: agent/COORD_PROTOCOL.md
"""
import argparse
import errno
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

WORK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


# ---------------------------------------------------------------- primitives
def now_iso():
    return datetime.now(timezone.utc).isoformat()


def agent_id():
    """Stable per-agent id. You don't need to set AGENT_ID — by default each git
    worktree is its own agent (distinct + stable across calls). Set AGENT_ID only
    if you want a custom label, or to distinguish two agents sharing ONE worktree."""
    a = os.environ.get("AGENT_ID")
    if a:
        return a
    top = git("rev-parse", "--show-toplevel")
    if top:
        return os.path.basename(top)
    return f"{os.environ.get('USER', 'unknown')}@{socket.gethostname()}"


def safe_filename(s):
    return re.sub(r"[^A-Za-z0-9._-]", "_", s)


def git(*args):
    try:
        out = subprocess.run(["git", *args], capture_output=True, text=True)
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None


def resolve_coord_dir():
    env = os.environ.get("AGENT_COORD_DIR")
    if env:
        return os.path.abspath(env)
    gitdir = git("rev-parse", "--path-format=absolute", "--git-common-dir")
    if not gitdir:
        rel = git("rev-parse", "--git-common-dir")
        gitdir = os.path.abspath(rel) if rel else None
    if gitdir:
        return os.path.join(os.path.dirname(gitdir), ".coord")
    return os.path.abspath(".coord")


def pid_alive(pid):
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
    except OSError as e:
        return e.errno == errno.EPERM  # alive but owned by another user
    except (ValueError, TypeError):
        return False
    return True


def write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def validate_work_id(work_id):
    if not WORK_ID_RE.match(work_id):
        sys.exit(f"ERROR: invalid work_id {work_id!r} (allowed: [A-Za-z0-9._-], no '/' or spaces)")
    return work_id


# ----------------------------------------------------------------- coord dir
class Coord:
    def __init__(self, root):
        self.root = root
        self.leases = os.path.join(root, "LEASES")
        self.completed = os.path.join(root, "COMPLETED")
        self.failed = os.path.join(root, "FAILED")
        self.status = os.path.join(root, "STATUS")
        self.queue = os.path.join(root, "RUN_QUEUE.jsonl")
        self.merge_lock = os.path.join(root, "MAIN_MERGE.lock")

    def ensure(self):
        for d in (self.leases, self.completed, self.failed, self.status):
            os.makedirs(d, exist_ok=True)
        if not os.path.exists(self.queue):
            open(self.queue, "a").close()

    def lease_dir(self, work_id):
        return os.path.join(self.leases, work_id + ".lock")

    def completed_dir(self, work_id):
        return os.path.join(self.completed, work_id + ".lock")

    def failed_dir(self, work_id):
        return os.path.join(self.failed, work_id + ".lock")

    def is_active(self, work_id):
        return os.path.isdir(self.lease_dir(work_id))

    def is_completed(self, work_id):
        return os.path.isdir(self.completed_dir(work_id))

    def is_failed(self, work_id):
        return os.path.isdir(self.failed_dir(work_id))

    def read_queue(self):
        rows = []
        if not os.path.exists(self.queue):
            return rows
        with open(self.queue) as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    rows.append(json.loads(ln))
                except json.JSONDecodeError:
                    pass
        return rows


# --------------------------------------------------------------- id builders
def build_ids(category, exp_tag, split, seed, config=None, config_hash=None):
    if config_hash is None:
        if config is None:
            sys.exit("ERROR: need --config or --config-hash")
        config_hash = hashlib.sha256(config.encode()).hexdigest()[:10]
    work_id = f"{category}__{exp_tag}__{split}__{seed}__{config_hash}"
    group_id = f"{category}__{exp_tag}__{split}__{config_hash}"
    return validate_work_id(work_id), validate_work_id(group_id), config_hash


# ------------------------------------------------------------------- actions
def do_claim(c, work_id, fields, force=False):
    """Atomic claim. Returns (won: bool, reason: str)."""
    validate_work_id(work_id)
    if c.is_completed(work_id) and not force:
        return False, "already-completed"
    try:
        os.mkdir(c.lease_dir(work_id))  # <-- atomic coordination point
    except FileExistsError:
        return False, "lease-held"
    lease = {
        "work_id": work_id,
        "group_id": fields.get("group_id"),
        "agent_id": agent_id(),
        "pid": fields.get("pid") or os.getpid(),
        "host": socket.gethostname(),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "commit": git("rev-parse", "--short", "HEAD"),
        "command": fields.get("command"),
        "smoke": fields.get("smoke"),
        "started_at": now_iso(),
        "last_heartbeat": now_iso(),
        "status": "running",
    }
    for k in ("category", "exp_tag", "split", "seed", "config_hash", "source"):
        if fields.get(k) is not None:
            lease[k] = fields[k]
    write_json(os.path.join(c.lease_dir(work_id), "lease.json"), lease)
    return True, "claimed"


def move_lease(c, work_id, dest_dir, **updates):
    src = c.lease_dir(work_id)
    if not os.path.isdir(src):
        sys.exit(f"ERROR: no active lease for {work_id}")
    lease = read_json(os.path.join(src, "lease.json"))
    lease.update(updates)
    write_json(os.path.join(src, "lease.json"), lease)
    dst = os.path.join(dest_dir, work_id + ".lock")
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.move(src, dst)
    return dst


def age_seconds(iso):
    try:
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except Exception:
        return None


# ----------------------------------------------------------------- commands
def cmd_work_id(c, a):
    work_id, group_id, _ = build_ids(a.category, a.exp_tag, a.split, a.seed, a.config, a.config_hash)
    print(work_id)


def cmd_group_id(c, a):
    _, group_id, _ = build_ids(a.category, a.exp_tag, a.split, a.seed or "0", a.config, a.config_hash)
    print(group_id)


def cmd_add(c, a):
    work_id, group_id, config_hash = build_ids(
        a.category, a.exp_tag, a.split, a.seed, a.config, a.config_hash
    )
    row = {
        "work_id": work_id,
        "group_id": group_id,
        "category": a.category,
        "exp_tag": a.exp_tag,
        "split": a.split,
        "seed": a.seed,
        "config_hash": config_hash,
        "command": a.command,
        "smoke": a.smoke,
        "source": a.source,
        "added_at": now_iso(),
        "added_by": agent_id(),
    }
    with open(c.queue, "a") as f:
        f.write(json.dumps(row) + "\n")
    print(work_id)


def cmd_next(c, a):
    for row in c.read_queue():
        wid = row.get("work_id")
        if not wid:
            continue
        if c.is_completed(wid) or c.is_active(wid):
            continue
        if c.is_failed(wid) and not a.include_failed:
            continue
        won, reason = do_claim(c, wid, row)
        if won:
            print(json.dumps(row))
            return
    sys.exit(3)  # nothing claimable


def cmd_claim(c, a):
    fields = {"command": a.command, "smoke": a.smoke, "group_id": a.group_id, "pid": a.pid}
    won, reason = do_claim(c, a.work_id, fields, force=a.force)
    if won:
        print(f"CLAIMED {a.work_id}")
        return
    print(f"LOST {a.work_id} ({reason})")
    sys.exit(1)


def cmd_heartbeat(c, a):
    src = c.lease_dir(a.work_id)
    lp = os.path.join(src, "lease.json")
    if not os.path.isdir(src):
        sys.exit(f"ERROR: no active lease for {a.work_id}")
    lease = read_json(lp)
    lease["last_heartbeat"] = now_iso()
    if a.status:
        lease["status"] = a.status
    if a.note:
        lease["note"] = a.note
    write_json(lp, lease)
    print(f"HEARTBEAT {a.work_id} @ {lease['last_heartbeat']}")


def cmd_complete(c, a):
    move_lease(c, a.work_id, c.completed, status="completed",
               ended_at=now_iso(), result=a.result)
    print(f"COMPLETED {a.work_id}")


def cmd_fail(c, a):
    move_lease(c, a.work_id, c.failed, status="failed",
               ended_at=now_iso(), error=a.error)
    print(f"FAILED {a.work_id}")


def cmd_list(c, a):
    rows = []
    for name in sorted(os.listdir(c.leases)):
        if not name.endswith(".lock"):
            continue
        lease = read_json(os.path.join(c.leases, name, "lease.json"))
        hb = age_seconds(lease.get("last_heartbeat", ""))
        stale = hb is None or hb > a.stale_min * 60
        same_host = lease.get("host") == socket.gethostname()
        pid_note = "" if (not same_host or pid_alive(lease.get("pid"))) else " pid-dead"
        rows.append({**lease, "_hb_age_s": hb, "_stale": stale, "_pid_note": pid_note})
    if a.json:
        print(json.dumps(rows, indent=2))
        return
    if not rows:
        print("(no active leases)")
        return
    for r in rows:
        flag = " STALE" if r["_stale"] else ""
        hb = f"{int(r['_hb_age_s'])}s" if r["_hb_age_s"] is not None else "?"
        print(f"{r.get('work_id'):60s} {r.get('agent_id',''):24s} pid={r.get('pid')} "
              f"host={r.get('host')} hb={hb}{flag}{r['_pid_note']}")


def cmd_reap(c, a):
    reaped = []
    for name in sorted(os.listdir(c.leases)):
        if not name.endswith(".lock"):
            continue
        wid = name[:-5]
        lease = read_json(os.path.join(c.leases, name, "lease.json"))
        # Liveness is heartbeat-driven (the lease pid is often the ephemeral
        # claim process, not the worker). A fresh claim has a recent heartbeat,
        # giving the runner up to --stale-min to start heartbeating.
        ref = lease.get("last_heartbeat") or lease.get("started_at") or ""
        age = age_seconds(ref)
        if age is None or age > a.stale_min * 60:
            why = "no-timestamp" if age is None else f"stale>{a.stale_min}m"
            move_lease(c, wid, c.failed, status="failed", ended_at=now_iso(),
                       error=f"reaped: {why}")
            reaped.append((wid, why))
    for wid, why in reaped:
        print(f"REAPED {wid} ({why})")
    if not reaped:
        print("(nothing to reap)")


def cmd_status(c, a):
    path = os.path.join(c.status, safe_filename(agent_id()) + ".json")
    st = read_json(path)
    st.update({
        "agent_id": agent_id(),
        "host": socket.gethostname(),
        "pid": os.getpid(),
        "updated_at": now_iso(),
        "state": a.state,
    })
    if a.work_id:
        st["work_id"] = a.work_id
    if a.note:
        st["note"] = a.note
    write_json(path, st)
    print(f"STATUS {agent_id()} -> {a.state}")


def cmd_merge_lock(c, a):
    if a.op == "acquire":
        try:
            os.mkdir(c.merge_lock)
        except FileExistsError:
            info = read_json(os.path.join(c.merge_lock, "info.json"))
            print(f"MERGE-LOCK HELD by {info.get('agent_id')} (pid={info.get('pid')}, "
                  f"since {info.get('acquired_at')})")
            sys.exit(1)
        write_json(os.path.join(c.merge_lock, "info.json"), {
            "agent_id": agent_id(), "pid": os.getpid(),
            "host": socket.gethostname(), "acquired_at": now_iso(),
        })
        print("MERGE-LOCK ACQUIRED")
    elif a.op == "release":
        if not os.path.isdir(c.merge_lock):
            print("MERGE-LOCK not held")
            return
        info = read_json(os.path.join(c.merge_lock, "info.json"))
        if info.get("agent_id") != agent_id() and not a.force:
            sys.exit(f"ERROR: merge-lock held by {info.get('agent_id')}, not you "
                     f"(use --force to break)")
        shutil.rmtree(c.merge_lock)
        print("MERGE-LOCK RELEASED")


def cmd_commit(c, a):
    msg = f"[{agent_id()}][{a.work_id or '-'}] {a.message}"
    rc = subprocess.run(["git", "commit", "-m", msg]).returncode
    sys.exit(rc)


def cmd_selftest(c, a):
    """Self-contained dry run in a temp coord dir. Serves as the merge gate
    for coord.py-only changes. Exits 0 on PASS, 1 on FAIL."""
    tmp = tempfile.mkdtemp(prefix="coord_selftest_")
    tc = Coord(tmp)
    tc.ensure()
    ok = True

    def check(cond, label):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        ok = ok and cond

    wid = "selftest__exp__default__s1__deadbeef00"
    won1, _ = do_claim(tc, wid, {"group_id": "g", "command": "echo hi"})
    check(won1, "first claim wins")
    won2, reason = do_claim(tc, wid, {})
    check((not won2) and reason == "lease-held", "second claim loses (atomic)")
    move_lease(tc, wid, tc.completed, status="completed", ended_at=now_iso())
    check(tc.is_completed(wid) and not tc.is_active(wid), "complete moves lease")
    won3, reason = do_claim(tc, wid, {})
    check((not won3) and reason == "already-completed", "completed work not re-claimable")

    # merge lock
    os.mkdir(tc.merge_lock)
    held = True
    try:
        os.mkdir(tc.merge_lock)
        held = False
    except FileExistsError:
        pass
    check(held, "merge-lock is exclusive")
    shutil.rmtree(tc.merge_lock)

    shutil.rmtree(tmp, ignore_errors=True)
    print("SELFTEST", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


# ---------------------------------------------------------------------- main
def add_id_args(p, with_seed=True):
    p.add_argument("--category", required=True)
    p.add_argument("--exp-tag", required=True)
    p.add_argument("--split", default="default")
    if with_seed:
        p.add_argument("--seed", required=True)
    else:
        p.add_argument("--seed", default=None)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--config", help="config string; hashed to config_hash")
    g.add_argument("--config-hash", help="precomputed config hash")


def main():
    ap = argparse.ArgumentParser(description="Multi-agent run coordination (atomic-mkdir leases).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("work-id", help="print work_id"); add_id_args(p); p.set_defaults(fn=cmd_work_id)
    p = sub.add_parser("group-id", help="print group_id"); add_id_args(p, with_seed=False); p.set_defaults(fn=cmd_group_id)

    p = sub.add_parser("add", help="append a row to RUN_QUEUE.jsonl (coordinator/human)")
    add_id_args(p)
    p.add_argument("--command", required=True, help="shell command that runs this work")
    p.add_argument("--smoke", default=None, help="cheap gate command for this work")
    p.add_argument("--source", default="manual", help="e.g. closed_loop_ledger / coordinator / human")
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser("next", help="claim the first unclaimed queue row; prints its JSON")
    p.add_argument("--include-failed", action="store_true", help="also retry FAILED work")
    p.set_defaults(fn=cmd_next)

    p = sub.add_parser("claim", help="atomically claim a specific work_id")
    p.add_argument("work_id")
    p.add_argument("--command", default=None)
    p.add_argument("--smoke", default=None)
    p.add_argument("--group-id", default=None)
    p.add_argument("--pid", type=int, default=None, help="worker pid to record (default: this process)")
    p.add_argument("--force", action="store_true", help="claim even if marked completed")
    p.set_defaults(fn=cmd_claim)

    p = sub.add_parser("heartbeat", help="refresh a lease's heartbeat")
    p.add_argument("work_id"); p.add_argument("--status", default=None); p.add_argument("--note", default=None)
    p.set_defaults(fn=cmd_heartbeat)

    p = sub.add_parser("complete", help="mark work done (lease -> COMPLETED/)")
    p.add_argument("work_id"); p.add_argument("--result", default=None)
    p.set_defaults(fn=cmd_complete)

    p = sub.add_parser("fail", help="mark work failed (lease -> FAILED/)")
    p.add_argument("work_id"); p.add_argument("--error", default=None)
    p.set_defaults(fn=cmd_fail)

    p = sub.add_parser("list", help="show active leases")
    p.add_argument("--stale-min", type=int, default=30); p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser("reap", help="recover dead-pid / stale leases -> FAILED")
    p.add_argument("--stale-min", type=int, default=30)
    p.set_defaults(fn=cmd_reap)

    p = sub.add_parser("status", help="write this agent's status (single-writer per agent)")
    p.add_argument("--state", required=True, help="e.g. running / idle / blocked")
    p.add_argument("--work-id", default=None); p.add_argument("--note", default=None)
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("merge-lock", help="serialize merges to main")
    p.add_argument("op", choices=["acquire", "release"]); p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_merge_lock)

    p = sub.add_parser("commit", help="git commit with [agent_id][work_id] prefix")
    p.add_argument("-m", "--message", required=True); p.add_argument("--work-id", default=None)
    p.set_defaults(fn=cmd_commit)

    p = sub.add_parser("selftest", help="dry-run self-check (coord.py merge gate)")
    p.set_defaults(fn=cmd_selftest)

    args = ap.parse_args()
    coord_root = resolve_coord_dir()
    print(f"[coord] dir={coord_root}", file=sys.stderr)
    c = Coord(coord_root)
    c.ensure()
    args.fn(c, args)


if __name__ == "__main__":
    main()
