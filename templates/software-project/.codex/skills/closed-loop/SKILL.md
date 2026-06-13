---
name: closed-loop
description: Open or close a row in agent/agentic_information/CLOSED_LOOP_LEDGER.md with the correct format. Matches the ledger's existing column schema exactly, enforces stating the predicted check BEFORE running, and checks the Tried-And-Rejected list before re-running a NO-GO. Use when starting a hypothesis/experiment or recording its verdict.
version: 1.0.0
scope: project
---

# ruff: noqa: E501

# /closed-loop — log a hypothesis or its verdict

Keeps the closed-loop ledger — the highest-authority record of what actually
worked — consistent. Adapts to this project's ledger schema rather than imposing
one.

## Procedure

1. **Read the local ledger header.** Open
   `agent/agentic_information/CLOSED_LOOP_LEDGER.md`, read the **table header row**
   and the **Status values** line, and match those columns and that status
   vocabulary exactly. The baseline schema is
   `ID | Date | Status | Area | Hypothesis/Fix | Predicted Check | Test Command | Result | Verdict/Next Step`,
   but a project may add columns (e.g. an "Evidence Before" column) or link rows
   to a hypothesis registry — honor whatever the header shows.

2. **Pick a mode:**
   - **Open** (before running): assign the next `CL-NNNN` id, status
     `pending`/`in_progress`, fill the Hypothesis/Fix and — required — the
     **Predicted Check stated BEFORE running** (the falsifiable threshold). Leave
     Result/Verdict blank.
   - **Close** (after running): fill Result + Verdict/Next-Step and set a terminal
     status (`done`/`reverted`/`no_go`/`superseded`). Move durable NO-GOs to the
     Tried-And-Rejected list.

3. **Guard against repeats.** Before opening a row, scan Tried-And-Rejected / prior
   `no_go` rows — don't re-propose a rejected approach without a new argument, and
   state what's new if you do.

4. **Honor any project-specific gate.** If `AGENTS.md` defines a pre-registration
   requirement for this domain (e.g. a feasibility or theoretical-possibility
   argument that must be stated before experimenting), include it in the row.

5. **Run the smallest decisive test first** (one shard/clip/epoch; small model/data
   before large). Keep the change only if the recorded evidence supports it.

## Output

The exact markdown row(s) to add or edit, with column count matching the local
header. Edit the ledger in place; confirm the id and status used.
