#!/usr/bin/env python3
"""Install Cartog's product-authored Codex guidance without replacing user AGENTS content."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

BEGIN = "<!-- CARTOG_PRODUCT_GUIDANCE_BEGIN"
END = "<!-- CARTOG_PRODUCT_GUIDANCE_END -->"
SOURCE_RELATIVE = Path("docs/agent-snippet.md")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_commit(source_root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=source_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def extract_guidance(document: str) -> str:
    heading = document.find("## Snippet (copy from here)")
    if heading < 0:
        raise ValueError("Cartog agent snippet heading was not found")
    fence = document.find("```markdown", heading)
    if fence < 0:
        raise ValueError("Cartog markdown guidance fence was not found")
    start = document.find("\n", fence)
    end = document.find("\n```", start)
    if start < 0 or end < 0:
        raise ValueError("Cartog markdown guidance fence is incomplete")
    guidance = document[start + 1 : end].strip()
    if "prefer cartog over grep" not in guidance or "mcp__cartog__cartog_search" not in guidance:
        raise ValueError("Cartog guidance is missing its documented routing contract")
    return guidance


def install_guidance(repo: Path, guidance: str) -> tuple[str | None, str, bool]:
    destination = repo / "AGENTS.md"
    before = destination.read_bytes() if destination.exists() else b""
    before_hash = sha256_bytes(before) if before else None
    text = before.decode("utf-8") if before else ""
    guidance_hash = sha256_bytes((guidance + "\n").encode())
    block = f"{BEGIN} sha256={guidance_hash} -->\n{guidance}\n{END}"

    begin = text.find(BEGIN)
    end = text.find(END)
    if (begin < 0) != (end < 0):
        raise ValueError("AGENTS.md contains an incomplete Cartog managed block")
    preserved_existing = bool(text.strip())
    if begin >= 0:
        end += len(END)
        updated = text[:begin].rstrip() + "\n\n" + block + text[end:]
    elif text.strip():
        updated = text.rstrip() + "\n\n" + block + "\n"
    else:
        updated = block + "\n"
    destination.write_text(updated)
    return before_hash, sha256_bytes(destination.read_bytes()), preserved_existing


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--binary-source", type=Path, required=True)
    parser.add_argument("--binary-destination", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    actual_commit = source_commit(args.source_root)
    if actual_commit != args.expected_commit:
        raise SystemExit(
            f"Cartog source identity mismatch: expected {args.expected_commit}, got {actual_commit}"
        )
    source_path = args.source_root / SOURCE_RELATIVE
    source_bytes = source_path.read_bytes()
    guidance = extract_guidance(source_bytes.decode("utf-8"))
    before_hash, after_hash, preserved_existing = install_guidance(args.repo, guidance)
    args.binary_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.binary_source, args.binary_destination)
    args.binary_destination.chmod(0o755)

    receipt = {
        "schema_version": 1,
        "profile_id": "retrieval-cartog-codex-product-v2",
        "source_root": str(args.source_root),
        "source_commit": actual_commit,
        "source_guidance_path": str(SOURCE_RELATIVE),
        "source_guidance_sha256": sha256_bytes(source_bytes),
        "installed_guidance_sha256": sha256_bytes((guidance + "\n").encode()),
        "destination": str(args.repo / "AGENTS.md"),
        "destination_before_sha256": before_hash,
        "destination_after_sha256": after_hash,
        "preserved_existing_content": preserved_existing,
        "binary_source": str(args.binary_source),
        "binary_destination": str(args.binary_destination),
        "binary_sha256": sha256_bytes(args.binary_destination.read_bytes()),
        "binary_mode": oct(args.binary_destination.stat().st_mode & 0o777),
        "official_codex_install_command": ["cartog", "ide", "--client", "codex", "--yes"],
        "mcp_server_args": ["serve", "--watch"],
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
