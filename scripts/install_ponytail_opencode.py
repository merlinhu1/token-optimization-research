#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source-root", type=Path, required=True)
    p.add_argument("--expected-commit", required=True)
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    args = p.parse_args()
    source = args.source_root.resolve()
    repo = args.repo.resolve()
    actual_commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if actual_commit != args.expected_commit:
        raise SystemExit(f"Ponytail source commit mismatch: expected {args.expected_commit}, got {actual_commit}")
    source_plugin = source / ".opencode/plugins/ponytail.mjs"
    source_rules = source / "AGENTS.md"
    if not source_plugin.is_file() or not source_rules.is_file():
        raise SystemExit("Ponytail OpenCode source surface is incomplete")
    dest = repo / ".opencode/plugins/ponytail.mjs"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_plugin, dest)
    agents = repo / "AGENTS.md"
    previous = agents.read_text(encoding="utf-8") if agents.exists() else ""
    marker = "# Ponytail product guidance (verbatim)"
    rules = source_rules.read_text(encoding="utf-8")
    if marker in previous:
        previous = previous.split(marker, 1)[0].rstrip()
    agents.write_text(previous.rstrip() + "\n\n" + marker + "\n" + rules, encoding="utf-8")
    payload = {
        "source_root": str(source),
        "source_plugin_sha256": hashlib.sha256(source_plugin.read_bytes()).hexdigest(),
        "installed_plugin": str(dest),
        "installed_plugin_sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
        "guidance_sha256": hashlib.sha256(rules.encode()).hexdigest(),
        "evaluator_authored_guidance": False,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
