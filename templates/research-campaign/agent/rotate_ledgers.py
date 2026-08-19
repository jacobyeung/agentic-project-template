#!/usr/bin/env python3
"""Rotate closed ledger history into dated archive dirs and enforce word caps.

Live campaign files stay small enough to read at session start; history becomes
grep-only under agent/agentic_information/ledger_archive/<start>_<end>/.

  python agent/rotate_ledgers.py            # rotate closed history older than --days
  python agent/rotate_ledgers.py --check    # exit 1 if any live file exceeds its cap

Rotation rules:
- CLOSED_LOOP_LEDGER.md: table rows with a terminal status (done/no_go/reverted/
  superseded) and a date older than the cutoff move to the archive. If the live
  file is still over its word cap afterwards, the oldest remaining terminal rows
  move too. Open rows (pending/in_progress/blocked) never move.
- CAMPAIGN_LEDGER.md: Decision Log / Experiment History rows older than the cutoff
  move. Other sections never move.
Each run writes one ledger_archive/<date_start>_<date_end>/ directory (dates = span
of everything moved in that run) and appends one line to the "## Archive index"
section of each live file it touched.

A --check FAIL means close or rotate stale rows and trim CURRENT_STATE.md — do not
raise a cap to make the check pass.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AGI = REPO / "agent" / "agentic_information"
ARCHIVE_ROOT = AGI / "ledger_archive"

CLOSED = AGI / "CLOSED_LOOP_LEDGER.md"
CAMPAIGN = AGI / "CAMPAIGN_LEDGER.md"
CURRENT = AGI / "CURRENT_STATE.md"

TERMINAL = {"done", "no_go", "reverted", "superseded"}
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
PARTIAL_DATE_RE = re.compile(r"\d{4}-\d{2}(-\d{2})?")
ROW_ID_RE = re.compile(r"^\|\s*CL-\d+")

# Word caps for the live files (--check fails if exceeded).
CAPS = {
    CURRENT: 1_500,
    # Only open rows can hold the closed-loop ledger up — a FAIL here means stale
    # open rows need closing, not a bigger cap.
    CLOSED: 15_000,
    CAMPAIGN: 8_000,
}


def words(path: Path) -> int:
    return len(path.read_text().split()) if path.exists() else 0


def parse_date(text: str) -> dt.date | None:
    m = PARTIAL_DATE_RE.search(text)
    if not m:
        return None
    parts = m.group(0).split("-")
    y, mo = int(parts[0]), int(parts[1])
    d = int(parts[2]) if len(parts) == 3 else 1
    try:
        return dt.date(y, mo, d)
    except ValueError:
        return None


def cells(row: str) -> list[str]:
    return [c.strip().strip("*").strip() for c in row.split("|")]


def append_index(lines: list[str], entry: str) -> list[str]:
    """Ensure an '## Archive index' section near the top and append entry."""
    for i, line in enumerate(lines):
        if line.strip() == "## Archive index":
            j = i + 1
            while j < len(lines) and (lines[j].startswith("- ") or not lines[j].strip()):
                j += 1
            insert = j
            while insert > i + 1 and not lines[insert - 1].strip():
                insert -= 1
            return lines[:insert] + [entry] + lines[insert:]
    # No index yet: insert after the leading title/preamble (before first '## ' or table).
    at = len(lines)
    for i, line in enumerate(lines):
        if i > 0 and (line.startswith("## ") or line.startswith("| ")):
            at = i
            break
    return lines[:at] + ["## Archive index", "", entry, ""] + lines[at:]


def rotate_closed(lines: list[str], cutoff: dt.date, cap: int):
    kept, moved = [], []
    for line in lines:
        if ROW_ID_RE.match(line):
            c = cells(line)
            row_date = parse_date(c[2]) if len(c) > 3 else None
            status = c[3].lower() if len(c) > 3 else ""
            if status in TERMINAL and row_date and row_date < cutoff:
                moved.append(line)
                continue
        kept.append(line)

    # Cap enforcement: keep moving the oldest remaining terminal rows.
    def live_words():
        return len("\n".join(kept).split())

    while live_words() > cap:
        oldest_i, oldest_d = None, None
        for i, line in enumerate(kept):
            if ROW_ID_RE.match(line):
                c = cells(line)
                if len(c) > 3 and c[3].lower() in TERMINAL:
                    d = parse_date(c[2]) or dt.date.min
                    if oldest_d is None or d < oldest_d:
                        oldest_i, oldest_d = i, d
        if oldest_i is None:
            break  # nothing left that is safe to move
        moved.append(kept.pop(oldest_i))
    return kept, moved


def rotate_campaign(lines: list[str], cutoff: dt.date):
    """Move dated rows out of Decision Log (date col 1) / Experiment History (date col 2)."""
    kept, moved = [], []
    section, date_col = None, None
    for line in lines:
        if line.startswith("## "):
            section = line.strip()
            date_col = {"## Decision Log": 1, "## Experiment History": 2}.get(section)
        if (
            date_col is not None
            and line.startswith("|")
            and not re.match(r"^\|[\s:-]+\|", line)
            and not re.match(r"^\|\s*(Date|#)\s*\|", line)
        ):
            c = cells(line)
            d = parse_date(c[date_col]) if len(c) > date_col + 1 else None
            if d and d < cutoff:
                moved.append((section, line))
                continue
        kept.append(line)
    return kept, moved


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=14, help="age cutoff for closed history")
    ap.add_argument("--check", action="store_true", help="only enforce word caps")
    args = ap.parse_args()

    if args.check:
        ok = True
        for path, cap in CAPS.items():
            n = words(path)
            status = "PASS" if n <= cap else "FAIL"
            ok &= n <= cap
            print(f"[{status}] {path.relative_to(REPO)}: {n} words (cap {cap})")
        if not ok:
            print("Over cap: run `python agent/rotate_ledgers.py` and/or trim CURRENT_STATE.md.")
        return 0 if ok else 1

    cutoff = dt.date.today() - dt.timedelta(days=args.days)
    all_dates: list[dt.date] = []
    payloads: dict[str, list[str]] = {}  # archive filename -> lines
    new_live: dict[Path, list[str]] = {}

    # --- closed-loop ledger ---
    lines = CLOSED.read_text().splitlines()
    kept, moved = rotate_closed(lines, cutoff, CAPS[CLOSED])
    if moved:
        ids = [cells(r)[1] for r in moved]
        dates = [d for d in (parse_date(cells(r)[2]) for r in moved) if d]
        all_dates += dates
        head_row = next(l for l in kept if l.startswith("| ID |"))
        sep_row = kept[kept.index(head_row) + 1]
        payloads["CLOSED_LOOP_LEDGER.md"] = [
            "# Closed-Loop Ledger — archived rows",
            "",
            head_row,
            sep_row,
            *moved,
        ]
        entry = (
            f"- `ledger_archive/RANGE/CLOSED_LOOP_LEDGER.md` — {len(moved)} rows "
            f"({ids[0]}…{ids[-1]}, {min(dates)}…{max(dates)})"
        )
        new_live[CLOSED] = append_index(kept, entry)

    # --- campaign ledger ---
    lines = CAMPAIGN.read_text().splitlines()
    kept, moved_rows = rotate_campaign(lines, cutoff)
    if moved_rows:
        dates = [d for d in (parse_date(cells(r)[1]) or parse_date(r) for _, r in moved_rows) if d]
        all_dates += dates
        out = ["# Campaign Ledger — archived rows", ""]
        for section in ("## Decision Log", "## Experiment History"):
            rows = [r for s, r in moved_rows if s == section]
            if rows:
                out += [section + " (archived)", "", *rows, ""]
        payloads["CAMPAIGN_LEDGER.md"] = out
        entry = f"- `ledger_archive/RANGE/CAMPAIGN_LEDGER.md` — {len(moved_rows)} rows ({min(dates)}…{max(dates)})"
        new_live[CAMPAIGN] = append_index(kept, entry)

    if not payloads:
        print("nothing to rotate")
        return 0

    start, end = min(all_dates), max(all_dates)
    range_name = f"{start:%Y%m%d}_{end:%Y%m%d}"
    arch_dir = ARCHIVE_ROOT / range_name
    arch_dir.mkdir(parents=True, exist_ok=True)
    for name, content in payloads.items():
        out = arch_dir / name
        if out.exists():  # same-day rerun: append
            content = out.read_text().splitlines() + [""] + content
        out.write_text("\n".join(content) + "\n")
        print(f"archived -> {out.relative_to(REPO)}")

    for path, content in new_live.items():
        text = "\n".join(content) + "\n"
        text = text.replace("ledger_archive/RANGE/", f"ledger_archive/{range_name}/")
        path.write_text(text)
        print(f"rewrote {path.relative_to(REPO)} ({len(text.split())} words)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
