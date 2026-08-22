#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def codex_event(event_name: str, repo: Path, tool_input: dict[str, Any], tool_response: dict[str, Any] | None = None) -> dict[str, Any]:
    event: dict[str, Any] = {
        "session_id": "provider-free-token-savior-hook-probe",
        "turn_id": "probe-turn",
        "cwd": str(repo),
        "hook_event_name": event_name,
        "model": "provider-free-probe",
        "permission_mode": "dontAsk",
        "tool_name": "Bash",
        "tool_input": tool_input,
        "tool_use_id": "probe-tool-use",
        "transcript_path": None,
    }
    if tool_response is not None:
        event["tool_response"] = tool_response
    return event


def run_hook(script: Path, event: dict[str, Any], env: dict[str, str]) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    proc = subprocess.run(
        ["/usr/bin/python3", str(script)],
        input=json.dumps(event),
        text=True,
        capture_output=True,
        env=env,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"hook {script} exited {proc.returncode}: {proc.stderr.strip()}")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"hook {script} returned invalid JSON: {proc.stdout!r}") from exc
    return proc, payload


def probe(source_root: Path, repo: Path, state_dir: Path, receipt: Path) -> dict[str, Any]:
    rewrite_script = source_root / "hooks/bash_rewriter_hook.py"
    capture_script = source_root / "hooks/tool_capture_hook.py"
    for script in (rewrite_script, capture_script):
        if not script.is_file():
            raise ValueError(f"missing product hook script: {script}")
    state_dir.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ,
        "PROJECT_ROOT": str(repo),
        "WORKSPACE_ROOTS": str(repo),
        "TS_HOME": str(state_dir),
        "TS_BASH_REWRITE": "1",
        "TS_BASH_COMPACT": "1",
        "TS_CAPTURE_DISABLED": "0",
    }

    pre_proc, pre = run_hook(
        rewrite_script,
        codex_event("PreToolUse", repo, {"command": "git status"}),
        env,
    )
    pre_specific = pre.get("hookSpecificOutput", {})
    rewritten = pre_specific.get("updatedInput", {}).get("command", "")
    if pre_specific.get("hookEventName") != "PreToolUse" or rewritten == "git status" or "--porcelain=v2" not in rewritten:
        raise RuntimeError(f"Token Savior PreToolUse rewrite did not activate: {pre}")

    pytest_output = (
        "============================= test session starts =============================\n"
        "platform linux -- Python 3.13.5\n"
        "collected 100 items\n"
        + "\n".join(f"tests/test_{index}.py . [ 50%]" for index in range(100))
        + "\n============================= 100 passed in 1.23s =============================\n"
    )
    post_proc, post = run_hook(
        capture_script,
        codex_event(
            "PostToolUse",
            repo,
            {"command": "pytest -q"},
            # A Bash PostToolUse response carries .stdout/.stderr, not .content: 4.21.0 hands
            # stdout to the compactor so the two streams stay split, so a .content-shaped
            # event would present an empty stdout and never compact.
            {"stdout": pytest_output, "stderr": ""},
        ),
        env,
    )
    post_specific = post.get("hookSpecificOutput", {})
    compact_context = post_specific.get("additionalContext", "")
    if post_specific.get("hookEventName") != "PostToolUse" or "[token-savior:compact]" not in compact_context or "100 passed" not in compact_context:
        raise RuntimeError(f"Token Savior PostToolUse compaction did not activate: {post}")

    payload = {
        "schema_version": 1,
        "provider_calls": 0,
        "source_root": str(source_root),
        "source_hooks": {
            "pre_tool_use": {"path": str(rewrite_script), "sha256": sha256_file(rewrite_script)},
            "post_tool_use": {"path": str(capture_script), "sha256": sha256_file(capture_script)},
        },
        "codex_event_contract": "Codex 0.144 PreToolUse/PostToolUse command-hook JSON",
        "pre_tool_use": {
            "passed": True,
            "input_command": "git status",
            "rewritten_command": rewritten,
            "stderr": pre_proc.stderr,
        },
        "post_tool_use": {
            "passed": True,
            "input_bytes": len(pytest_output.encode("utf-8")),
            "additional_context": compact_context,
            "stderr": post_proc.stderr,
        },
        "passed": True,
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Provider-free Token Savior Codex hook probe")
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(probe(args.source_root.resolve(), args.repo.resolve(), args.state_dir.resolve(), args.receipt.resolve()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
