#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path

POLICY_RELATIVE_PATH = Path("src/jcodemunch_mcp/cli/init.py")
POLICY_SYMBOL = "_CLAUDE_MD_POLICY"
UNIVERSAL_GUIDE_RELATIVE_PATH = Path("AGENT_INSTALL_UNIVERSAL.md")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def source_commit(source_root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def extract_product_policy(source_root: Path) -> str:
    source_path = source_root / POLICY_RELATIVE_PATH
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if any(isinstance(target, ast.Name) and target.id == POLICY_SYMBOL for target in targets):
            if node.value is None:
                continue
            value = ast.literal_eval(node.value)
            if not isinstance(value, str) or "## Code Exploration Policy" not in value:
                raise ValueError(f"{POLICY_SYMBOL} is not the expected policy string")
            return value
    raise ValueError(f"could not find {POLICY_SYMBOL} in {source_path}")


def extract_universal_codex_guidance(source_root: Path) -> str:
    source_path = source_root / UNIVERSAL_GUIDE_RELATIVE_PATH
    text = source_path.read_text(encoding="utf-8")
    start_marker = "Use the live-policy tool when available:"
    end_marker = "# Step 5 — Draft the installed file contents"
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    return text[start:end].rstrip() + "\n"


def install(source_root: Path, expected_commit: str, codex_home: Path, receipt: Path) -> dict:
    actual_commit = source_commit(source_root)
    if actual_commit != expected_commit:
        raise ValueError(f"jcodemunch source commit mismatch: expected {expected_commit}, got {actual_commit}")
    policy = extract_product_policy(source_root).rstrip() + "\n"
    universal_guidance = extract_universal_codex_guidance(source_root)
    content = policy + "\n" + universal_guidance
    policy_bytes = policy.encode("utf-8")
    universal_bytes = universal_guidance.encode("utf-8")
    content_bytes = content.encode("utf-8")
    destination = codex_home / "AGENTS.md"
    codex_home.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.read_bytes() != content_bytes:
        raise ValueError(f"refusing to overwrite unrelated Codex guidance at {destination}")
    destination.write_bytes(content_bytes)
    payload = {
        "schema_version": 1,
        "source_root": str(source_root),
        "source_commit": actual_commit,
        "source_policy_path": str(POLICY_RELATIVE_PATH),
        "content_origin": "verbatim-product-authored-source-excerpts",
        "source_policy_sha256": sha256_bytes(policy_bytes),
        "universal_guide_path": str(UNIVERSAL_GUIDE_RELATIVE_PATH),
        "universal_guidance_sha256": sha256_bytes(universal_bytes),
        "composition": "policy + newline + universal-live-policy-and-native-tool-exceptions",
        "installed_path": str(destination),
        "installed_sha256": sha256_bytes(destination.read_bytes()),
        "evaluator_authored_guidance": False,
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Install product-authored jcodemunch policy into an isolated Codex home")
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--codex-home", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(install(args.source_root.resolve(), args.expected_commit, args.codex_home.resolve(), args.receipt.resolve()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
