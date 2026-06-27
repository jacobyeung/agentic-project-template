#!/usr/bin/env python3
"""Validate the research-campaign bootstrap and detect stale policy references."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path


REQUIRED_HEADINGS = {
    "AGENTS.md": (
        "# AGENTS.md - Canonical Bootstrap",
        "## 1. Fast Bootstrap",
        "## 3. Operating Contract",
        "## 11. Document Authority And Freshness",
    ),
    "agent/agentic_information/CURRENT_STATE.md": (
        "# Current State",
        "## Snapshot",
        "## In Flight",
        "## Immediate Next Action",
        "## Goal Gate",
    ),
    "agent/agentic_information/OPERATING_CONTRACT.md": (
        "# Operating Contract",
        "## Resource Budget",
        "## Live Work Discovery",
        "## Launch Contract",
        "## Evaluation Contract",
    ),
    "agent/agentic_information/CLOSED_LOOP_LEDGER.md": (
        "# Closed-Loop Ledger",
        "## Tried And Rejected",
    ),
    "agent/agentic_information/CAMPAIGN_LEDGER.md": (
        "# Campaign Ledger",
        "## Decision Log",
        "## Experiment History",
    ),
    "agent/experiments/README.md": (
        "# Experiment Lifecycle And Run Record",
        "## Lifecycle",
        "## `RUN.md` Template",
    ),
    "agent/experiments/BEST_SCORES.md": ("# Best Scores",),
}

REQUIRED_CUSTOMIZATION = re.compile(r"<[A-Z][A-Z0-9_-]*>")
ANY_PLACEHOLDER = re.compile(r"<[^>\n]+>")
REVISION = re.compile(r"^Revision:\s*`([^`]+)`", re.MULTILINE)
STATE_REVISION = re.compile(
    r"^- Operating contract:\s*`([^`]+)`", re.MULTILINE
)
CONTRACT_STATUS = re.compile(r"^Contract status:\s*`([^`]+)`", re.MULTILINE)
EVALUATION_STATUS = re.compile(r"^Evaluation status:\s*`([^`]+)`", re.MULTILINE)
RUN_STATE = re.compile(r"^- State:\s*`?([^`\n]+?)`?\s*$", re.MULTILINE)
RUN_REVISION = re.compile(
    r"^- Operating-contract revision:\s*`?([^`\n]+?)`?\s*$", re.MULTILINE
)
DATE_PREFIX = re.compile(r"(\d{4}-\d{2}-\d{2})")
LEDGER_ROW = re.compile(
    r"^\|\s*(CL-\d{4})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|",
    re.MULTILINE,
)

ACTIVE_RUN_STATES = {"preflight_passed", "submitted", "running"}
ALL_RUN_STATES = ACTIVE_RUN_STATES | {
    "proposed",
    "blocked",
    "finished",
    "evaluated",
    "decided",
    "archived",
    "failed",
    "cancelled",
    "invalid",
}
FILLED_RUN_STATES = ALL_RUN_STATES - {"proposed", "blocked"}
LEDGER_STATES = {
    "pending",
    "in_progress",
    "blocked",
    "done",
    "reverted",
    "no_go",
    "superseded",
}
PROJECT_RECORDS_WITHOUT_PLACEHOLDERS = {
    "agent/agentic_information/CURRENT_STATE.md",
    "agent/agentic_information/OPERATING_CONTRACT.md",
    "agent/agentic_information/CLOSED_LOOP_LEDGER.md",
    "agent/agentic_information/CAMPAIGN_LEDGER.md",
    "agent/experiments/BEST_SCORES.md",
}


def read_required(root: Path, errors: list[str]) -> dict[str, str]:
    documents: dict[str, str] = {}
    for relative, headings in REQUIRED_HEADINGS.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing required file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        documents[relative] = text
        for heading in headings:
            if heading not in text:
                errors.append(f"{relative}: missing heading {heading!r}")
    return documents


def check_skill_mirrors(root: Path, errors: list[str]) -> None:
    codex = root / ".codex/skills"
    claude = root / ".claude/skills"
    codex_files = {
        path.relative_to(codex): path.read_bytes()
        for path in codex.rglob("*")
        if path.is_file()
    }
    claude_files = {
        path.relative_to(claude): path.read_bytes()
        for path in claude.rglob("*")
        if path.is_file()
    }
    if codex_files.keys() != claude_files.keys():
        errors.append(".codex/skills and .claude/skills contain different files")
        return
    for relative in codex_files:
        if codex_files[relative] != claude_files[relative]:
            errors.append(f"skill mirrors differ: {relative}")


def age_warning(
    text: str,
    label: str,
    prefix: str,
    max_age_days: int,
    warnings: list[str],
) -> None:
    line = next((line for line in text.splitlines() if line.startswith(prefix)), None)
    if line is None:
        warnings.append(f"{label}: missing {prefix.rstrip(':')!r} timestamp")
        return
    match = DATE_PREFIX.search(line)
    if not match:
        warnings.append(f"{label}: timestamp has no YYYY-MM-DD date in {line!r}")
        return
    try:
        observed = date.fromisoformat(match.group(1))
    except ValueError:
        warnings.append(f"{label}: invalid date in {line!r}")
        return
    age = (date.today() - observed).days
    if age < 0:
        warnings.append(f"{label}: timestamp is {-age} days in the future")
        return
    if age > max_age_days:
        warnings.append(
            f"{label}: timestamp is {age} days old (warning threshold {max_age_days})"
        )


def check_run_records(
    root: Path,
    current_revision: str | None,
    errors: list[str],
    warnings: list[str],
) -> None:
    for path in sorted((root / "agent/experiments").glob("**/RUN.md")):
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        state_match = RUN_STATE.search(text)
        revision_match = RUN_REVISION.search(text)
        if not state_match:
            errors.append(f"{relative}: cannot parse run state")
            continue
        state = state_match.group(1)
        if state not in ALL_RUN_STATES:
            errors.append(f"{relative}: unknown run state {state!r}")
            continue
        if state in FILLED_RUN_STATES:
            placeholders = sorted(set(ANY_PLACEHOLDER.findall(text)))
            for token in placeholders:
                errors.append(f"{relative}: unresolved run-record placeholder {token}")
        if state in ACTIVE_RUN_STATES:
            if not revision_match:
                errors.append(f"{relative}: active run has no operating-contract revision")
            elif current_revision and revision_match.group(1) != current_revision:
                warnings.append(
                    f"{relative}: active run uses {revision_match.group(1)!r}, "
                    f"current contract is {current_revision!r}; recheck admission"
                )


def check_ledger(text: str, errors: list[str]) -> None:
    seen: set[str] = set()
    for match in LEDGER_ROW.finditer(text):
        experiment_id = match.group(1)
        status = match.group(3).strip()
        if experiment_id in seen:
            errors.append(f"CLOSED_LOOP_LEDGER.md: duplicate id {experiment_id}")
        seen.add(experiment_id)
        if status not in LEDGER_STATES:
            errors.append(
                f"CLOSED_LOOP_LEDGER.md: {experiment_id} has invalid status "
                f"{status!r}; allowed={sorted(LEDGER_STATES)}"
            )


def validate(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    documents = read_required(root, errors)
    check_skill_mirrors(root, errors)

    state = documents.get("agent/agentic_information/CURRENT_STATE.md", "")
    contract = documents.get(
        "agent/agentic_information/OPERATING_CONTRACT.md", ""
    )

    if not args.template:
        for relative in (
            "AGENTS.md",
        ):
            tokens = REQUIRED_CUSTOMIZATION.findall(documents.get(relative, ""))
            for token in sorted(set(tokens)):
                errors.append(f"{relative}: unresolved required placeholder {token}")
        for relative in sorted(PROJECT_RECORDS_WITHOUT_PLACEHOLDERS):
            tokens = ANY_PLACEHOLDER.findall(documents.get(relative, ""))
            for token in sorted(set(tokens)):
                errors.append(f"{relative}: unresolved record placeholder {token}")

        check_ledger(
            documents.get("agent/agentic_information/CLOSED_LOOP_LEDGER.md", ""),
            errors,
        )

    contract_revision = REVISION.search(contract)
    state_revision = STATE_REVISION.search(state)
    if not contract_revision:
        errors.append("OPERATING_CONTRACT.md: cannot parse Revision")
    if not state_revision:
        errors.append("CURRENT_STATE.md: cannot parse operating-contract revision")
    if contract_revision and state_revision:
        if contract_revision.group(1) != state_revision.group(1):
            errors.append(
                "operating-contract revision mismatch: "
                f"contract={contract_revision.group(1)!r}, "
                f"current_state={state_revision.group(1)!r}"
            )

    if not args.template:
        contract_status = CONTRACT_STATUS.search(contract)
        if not contract_status or contract_status.group(1) not in {
            "ready",
            "provisional",
            "blocked",
        }:
            errors.append(
                "OPERATING_CONTRACT.md: Contract status must be ready, provisional, "
                "or blocked"
            )
        elif contract_status.group(1) != "ready":
            warnings.append(
                f"OPERATING_CONTRACT.md: contract status is {contract_status.group(1)!r}"
            )
        evaluation_status = EVALUATION_STATUS.search(contract)
        if not evaluation_status or evaluation_status.group(1) not in {
            "not_implemented",
            "provisional",
            "authoritative",
        }:
            errors.append(
                "OPERATING_CONTRACT.md: Evaluation status must be not_implemented, "
                "provisional, or authoritative"
            )
        elif evaluation_status.group(1) != "authoritative":
            warnings.append(
                "OPERATING_CONTRACT.md: evaluation is not authoritative; results "
                "are ineligible for campaign-best promotion"
            )

        check_run_records(
            root,
            contract_revision.group(1) if contract_revision else None,
            errors,
            warnings,
        )

        age_warning(
            state,
            "CURRENT_STATE.md",
            "Last updated:",
            args.state_max_age_days,
            warnings,
        )
        age_warning(
            contract,
            "OPERATING_CONTRACT.md",
            "Last verified:",
            args.contract_max_age_days,
            warnings,
        )

    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    mode = "template" if args.template else "project"
    print(f"PASS: {mode} bootstrap is structurally consistent ({len(warnings)} warning(s))")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="project root (default: parent of this script's agent directory)",
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="allow required customization placeholders while checking structure",
    )
    parser.add_argument("--state-max-age-days", type=int, default=3)
    parser.add_argument("--contract-max-age-days", type=int, default=30)
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(validate(parse_args()))
