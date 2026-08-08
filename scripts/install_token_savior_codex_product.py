#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
from pathlib import Path
from typing import Any

GUIDANCE_RELATIVE_PATH = Path("CLAUDE.md")
BASH_REWRITER_RELATIVE_PATH = Path("hooks/bash_rewriter_hook.py")
CAPTURE_HOOK_RELATIVE_PATH = Path("hooks/tool_capture_hook.py")
BEGIN_MARKER = "<!-- TOKEN_SAVIOR_PRODUCT_GUIDANCE_BEGIN -->"
END_MARKER = "<!-- TOKEN_SAVIOR_PRODUCT_GUIDANCE_END -->"


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def source_commit(source_root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def product_guidance_block(source_root: Path) -> tuple[str, bytes]:
    source_bytes = (source_root / GUIDANCE_RELATIVE_PATH).read_bytes()
    source_text = source_bytes.decode("utf-8").rstrip()
    block = (
        f"{BEGIN_MARKER}\n"
        f"{source_text}\n"
        f"{END_MARKER}\n"
    )
    return block, source_bytes


def install_guidance(source_root: Path, repo: Path) -> tuple[Path, bytes]:
    block, source_bytes = product_guidance_block(source_root)
    destination = repo / "AGENTS.md"
    existing = destination.read_text(encoding="utf-8") if destination.exists() else ""
    if BEGIN_MARKER in existing or END_MARKER in existing:
        if existing.count(BEGIN_MARKER) != 1 or existing.count(END_MARKER) != 1:
            raise ValueError(f"malformed Token Savior managed block in {destination}")
        start = existing.index(BEGIN_MARKER)
        end = existing.index(END_MARKER, start) + len(END_MARKER)
        current_block = existing[start:end].rstrip() + "\n"
        if current_block != block:
            raise ValueError(f"existing Token Savior guidance differs from pinned source in {destination}")
        return destination, source_bytes
    separator = "" if not existing or existing.endswith("\n\n") else ("\n" if existing.endswith("\n") else "\n\n")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(existing + separator + block, encoding="utf-8")
    return destination, source_bytes


def command_handler(script: Path, timeout: int, status: str) -> dict[str, Any]:
    return {
        "type": "command",
        "command": f"/usr/bin/python3 {shlex.quote(str(script))}",
        "timeout": timeout,
        "statusMessage": status,
    }


def generated_hook_groups(source_root: Path) -> dict[str, list[dict[str, Any]]]:
    return {
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [
                    command_handler(
                        source_root / BASH_REWRITER_RELATIVE_PATH,
                        2,
                        "Token Savior is compacting the shell command",
                    )
                ],
            }
        ],
        "PostToolUse": [
            {
                "matcher": "Bash|WebFetch|Read|Grep|mcp__playwright__.*|mcp__token-savior__search_codebase|mcp__token-savior__get_function_source|mcp__token-savior__get_class_source",
                "hooks": [
                    command_handler(
                        source_root / CAPTURE_HOOK_RELATIVE_PATH,
                        5,
                        "Token Savior is compacting and capturing tool output",
                    )
                ],
            }
        ],
    }


def install_hooks(source_root: Path, codex_home: Path) -> Path:
    destination = codex_home / "hooks.json"
    if destination.exists():
        payload = json.loads(destination.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("hooks", {}), dict):
            raise ValueError(f"unsupported existing Codex hooks structure in {destination}")
    else:
        payload = {
            "description": "Codex-native host adapter for pinned product-authored Token Savior hooks.",
            "hooks": {},
        }
    hooks = payload.setdefault("hooks", {})
    generated = generated_hook_groups(source_root)
    for event, groups in generated.items():
        current = hooks.setdefault(event, [])
        for group in groups:
            command = group["hooks"][0]["command"]
            if not any(
                isinstance(existing, dict)
                and any(
                    isinstance(handler, dict) and handler.get("command") == command
                    for handler in existing.get("hooks", [])
                )
                for existing in current
            ):
                current.append(group)
    codex_home.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return destination


def install(
    source_root: Path,
    expected_commit: str,
    codex_home: Path,
    repo: Path,
    receipt: Path,
) -> dict[str, Any]:
    actual_commit = source_commit(source_root)
    if actual_commit != expected_commit:
        raise ValueError(
            f"Token Savior source commit mismatch: expected {expected_commit}, got {actual_commit}"
        )
    for relative in (
        GUIDANCE_RELATIVE_PATH,
        BASH_REWRITER_RELATIVE_PATH,
        CAPTURE_HOOK_RELATIVE_PATH,
    ):
        if not (source_root / relative).is_file():
            raise ValueError(f"missing pinned product surface: {source_root / relative}")

    guidance_path, source_guidance = install_guidance(source_root, repo)
    hooks_path = install_hooks(source_root, codex_home)
    payload = {
        "schema_version": 1,
        "source_root": str(source_root),
        "source_commit": actual_commit,
        "guidance_source_path": str(GUIDANCE_RELATIVE_PATH),
        "guidance_source_sha256": sha256_bytes(source_guidance),
        "guidance_content_origin": "verbatim-product-authored-claude-guidance",
        "guidance_host_mapping": "CLAUDE.md managed block materialized into repository AGENTS.md for Codex discovery",
        "installed_guidance_path": str(guidance_path),
        "installed_guidance_sha256": sha256_bytes(guidance_path.read_bytes()),
        "hook_source_paths": [str(BASH_REWRITER_RELATIVE_PATH), str(CAPTURE_HOOK_RELATIVE_PATH)],
        "hook_source_sha256": {
            str(relative): sha256_bytes((source_root / relative).read_bytes())
            for relative in (BASH_REWRITER_RELATIVE_PATH, CAPTURE_HOOK_RELATIVE_PATH)
        },
        "hook_host_mapping": "product hook commands mapped to Codex 0.144 hooks.json PreToolUse/PostToolUse schema",
        "installed_hooks_path": str(hooks_path),
        "installed_hooks_sha256": sha256_bytes(hooks_path.read_bytes()),
        "evaluator_authored_guidance": False,
        "host_adapter_authored_by_evaluator": True,
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materialize pinned Token Savior product guidance and hooks for Codex"
    )
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--codex-home", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    payload = install(
        args.source_root.resolve(),
        args.expected_commit,
        args.codex_home.resolve(),
        args.repo.resolve(),
        args.receipt.resolve(),
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
