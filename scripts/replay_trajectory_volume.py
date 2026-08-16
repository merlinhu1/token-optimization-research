#!/usr/bin/env python3
"""Measure how much terminal output a tool admits into context, at zero variance.

A live evaluation measures two things at once: how many steps the agent takes, and what
each step costs. Step count is nondeterministic -- the same model on the same task under
the same harness has been observed 40 steps apart on one replicate and 47 on the next --
so a tool effect smaller than that swing cannot be resolved without many paid replicates.

This instrument removes the first factor by construction. It takes the action trajectory a
completed session actually produced, holds it fixed, and measures only what a tool does to
the output volume of those exact commands. Two configurations measured this way differ by
the tool alone: there is no sampling error, because nothing is sampled, and no provider
spend, because no model runs.

What it measures
----------------
Terminal output admitted into context, per command and in total, as a ratio against the
unfiltered trajectory. Ratios are reported rather than token counts because the comparison
is the result; an absolute token figure here would be an estimate of a quantity the live
runs already measure exactly.

What it does not measure
------------------------
Anything that changes which commands the agent issues. A retrieval tool that finds the
right file in two greps instead of nine does not show up here at all -- its trajectory is
a different trajectory, and holding the trajectory fixed is precisely what this instrument
does. Treat a favourable ratio as evidence about display-layer compression only, and read
it alongside a live sample rather than instead of one.

Usage
-----
    replay_trajectory_volume.py extract SESSION_DIR [-o trajectory.json]
    replay_trajectory_volume.py measure TRAJECTORY.json --filter 'tool --stdin' [--label id]

The filter is any command that reads the raw output of one agent command on stdin and
writes what the agent would have seen on stdout, which is the contract terminal-compression
hooks already implement.
"""
from __future__ import annotations

import argparse
import gzip
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_NAME = "evidence.jsonl.gz"
EVENTS_PATH = "codex-events.jsonl"
FILTER_TIMEOUT_SECONDS = 120


def _events_text(session: Path) -> str:
    """Return the recorded Codex event stream for a session directory or evidence bundle."""
    bundle = session if session.is_file() else session / EVIDENCE_NAME
    if not bundle.is_file():
        raise SystemExit(f"no evidence bundle at {bundle}")
    with gzip.open(bundle, "rt") as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("path") == EVENTS_PATH:
                return record.get("content") or ""
    raise SystemExit(f"{bundle} contains no {EVENTS_PATH}")


def extract_trajectory(session: Path) -> dict[str, Any]:
    """Freeze the command trajectory a session produced, with the output each command gave."""
    commands: list[dict[str, Any]] = []
    for line in _events_text(session).splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "item.completed":
            continue
        item = event.get("item") or {}
        if item.get("type") != "command_execution":
            continue
        commands.append({
            "index": len(commands),
            "command": item.get("command") or "",
            "exit_code": item.get("exit_code"),
            "output": item.get("aggregated_output") or "",
        })
    if not commands:
        raise SystemExit(f"{session} recorded no command executions to replay")
    return {
        "schema_version": 1,
        "source_session": session.name,
        "command_count": len(commands),
        "commands": commands,
    }


def apply_filter(text: str, filter_command: str | None) -> str:
    """Return what the agent would have seen after a tool processed one command's output."""
    if not filter_command:
        return text
    try:
        completed = subprocess.run(
            filter_command,
            shell=True,
            input=text,
            capture_output=True,
            text=True,
            timeout=FILTER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise SystemExit(f"filter timed out after {FILTER_TIMEOUT_SECONDS}s: {filter_command}") from exc
    if completed.returncode != 0:
        # A filter that fails has not compressed anything; counting its empty stdout as a
        # reduction would report a broken tool as the best one in the study.
        raise SystemExit(
            f"filter exited {completed.returncode}: {filter_command}\n{completed.stderr[:2000]}"
        )
    return completed.stdout


def measure(trajectory: dict[str, Any], filter_command: str | None, label: str) -> dict[str, Any]:
    """Measure admitted output for one configuration against the same fixed trajectory."""
    per_command: list[dict[str, Any]] = []
    baseline_total = 0
    admitted_total = 0
    for entry in trajectory["commands"]:
        raw = entry["output"]
        admitted = apply_filter(raw, filter_command)
        baseline_total += len(raw)
        admitted_total += len(admitted)
        per_command.append({
            "index": entry["index"],
            "command": entry["command"][:200],
            "baseline_characters": len(raw),
            "admitted_characters": len(admitted),
        })
    return {
        "label": label,
        "filter_command": filter_command,
        "source_session": trajectory.get("source_session"),
        "command_count": len(per_command),
        "baseline_characters": baseline_total,
        "admitted_characters": admitted_total,
        # The comparison is the result. A ratio below 1 means the tool admitted less than
        # the bare trajectory did; 1.0 means it changed nothing.
        "admitted_ratio": round(admitted_total / baseline_total, 6) if baseline_total else None,
        "variance": "none; the trajectory is held fixed and no model is invoked",
        "measures": "terminal output volume only, not which commands the agent chose to run",
        "per_command": per_command,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="mode", required=True)

    extract = sub.add_parser("extract", help="freeze a session's command trajectory")
    extract.add_argument("session", type=Path)
    extract.add_argument("-o", "--output", type=Path)

    run = sub.add_parser("measure", help="measure admitted output for one configuration")
    run.add_argument("trajectory", type=Path)
    run.add_argument("--filter", dest="filter_command", default=None)
    run.add_argument("--label", default="bare")
    run.add_argument("-o", "--output", type=Path)

    args = parser.parse_args(argv)

    if args.mode == "extract":
        payload: dict[str, Any] = extract_trajectory(args.session)
    else:
        trajectory = json.loads(args.trajectory.read_text())
        payload = measure(trajectory, args.filter_command, args.label)

    rendered = json.dumps(payload, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n")
        print(f"wrote {args.output}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
