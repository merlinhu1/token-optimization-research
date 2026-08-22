#!/usr/bin/env python3
"""Install Serena's documented Codex hooks without replacing existing hooks."""
import argparse
import json
from pathlib import Path

HOOKS = {
    "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "serena-hooks remind --client=codex"}]}],
    "SessionStart": [{"matcher": "startup|resume", "hooks": [{"type": "command", "command": "serena-hooks activate --client=codex"}]}],
    "SessionEnd": [{"hooks": [{"type": "command", "command": "serena-hooks cleanup --client=codex"}]}],
}


def install(codex_home: Path) -> None:
    path = codex_home / "hooks.json"
    document = json.loads(path.read_text()) if path.exists() else {}
    installed = document.setdefault("hooks", {})
    for event, entries in HOOKS.items():
        target = installed.setdefault(event, [])
        target.extend(entry for entry in entries if entry not in target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-home", type=Path, required=True)
    args = parser.parse_args()
    install(args.codex_home.resolve())
