#!/usr/bin/env python3
"""Install verbatim jCodemunch guidance into an isolated OpenCode project."""
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
            if isinstance(value, str) and "## Code Exploration Policy" in value:
                return value
    raise ValueError(f"could not find {POLICY_SYMBOL} in {source_path}")


def extract_universal_guidance(source_root: Path) -> str:
    text = (source_root / UNIVERSAL_GUIDE_RELATIVE_PATH).read_text(encoding="utf-8")
    start_marker = "Use the live-policy tool when available:"
    end_marker = "# Step 5 — Draft the installed file contents"
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    return text[start:end].rstrip() + "\n"


def install(source_root: Path, expected_commit: str, repo: Path, receipt: Path) -> dict:
    source_root = source_root.resolve()
    repo = repo.resolve()
    actual_commit = source_commit(source_root)
    if actual_commit != expected_commit:
        raise ValueError(f"source commit mismatch: expected {expected_commit}, got {actual_commit}")
    policy = extract_product_policy(source_root).rstrip() + "\n"
    universal = extract_universal_guidance(source_root)
    content = (policy + "\n" + universal).encode("utf-8")
    destination = repo / "AGENTS.md"
    previous = destination.read_bytes() if destination.exists() else b""
    marker = "\n\n# jCodemunch product guidance (verbatim)\n"
    if previous and b"# jCodemunch product guidance (verbatim)" in previous:
        prefix = previous.split(marker.encode(), 1)[0]
        destination.write_bytes(prefix.rstrip() + marker.encode() + content)
    elif previous:
        destination.write_bytes(previous.rstrip() + marker.encode() + content)
    else:
        destination.write_bytes(content)
    installed = destination.read_bytes()
    payload = {
        "schema_version": 1,
        "source_root": str(source_root),
        "source_commit": actual_commit,
        "content_origin": "verbatim-product-authored-source-excerpts",
        "source_policy_path": str(POLICY_RELATIVE_PATH),
        "source_policy_sha256": sha256_bytes(policy.encode()),
        "universal_guide_path": str(UNIVERSAL_GUIDE_RELATIVE_PATH),
        "universal_guidance_sha256": sha256_bytes(universal.encode()),
        "installed_path": str(destination),
        "installed_sha256": sha256_bytes(installed),
        "preserved_existing_bytes": bool(previous),
        "evaluator_authored_guidance": False,
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(install(args.source_root, args.expected_commit, args.repo, args.receipt), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
