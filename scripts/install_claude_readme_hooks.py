#!/usr/bin/env python3
"""Materialize Claude Code hook JSON documented by a pinned tool README.

This adapter is intentionally narrow: it only renders the lowfat Claude Code
hook shown in lowfat's README. It does not add model-facing instructions or
change the tool's command surface.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


LOWFAT_HOOKS: dict[str, list[dict[str, Any]]] = {
    "PreToolUse": [
        {
            "matcher": "Bash",
            "hooks": [{"type": "command", "command": "lowfat hook"}],
        }
    ],
    "PostToolUse": [
        {
            "matcher": "Read",
            "hooks": [{"type": "command", "command": "lowfat post-read"}],
        }
    ],
}


def merge_settings(path: Path, additions: dict[str, list[dict[str, Any]]]) -> None:
    data: dict[str, Any] = {}
    if path.exists():
        loaded = json.loads(path.read_text())
        if not isinstance(loaded, dict):
            raise ValueError(f"Claude settings must be a JSON object: {path}")
        data = loaded
    hooks = data.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError(f"Claude settings hooks must be an object: {path}")
    for event, entries in additions.items():
        current = hooks.setdefault(event, [])
        if not isinstance(current, list):
            raise ValueError(f"Claude settings {event} must be a list: {path}")
        for entry in entries:
            if entry not in current:
                current.append(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", choices=["lowfat"], required=True)
    parser.add_argument("--settings", type=Path, required=True)
    args = parser.parse_args()
    additions = LOWFAT_HOOKS if args.tool == "lowfat" else {}
    merge_settings(args.settings, additions)
    print(f"installed {args.tool} README Claude Code hooks in {args.settings}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
