#!/usr/bin/env python3
"""Check whether OpenCode can sustain generation, not merely answer.

This detects a provider that cannot generate at all. It does NOT predict whether a
lane will complete: on 2026-09-26 it returned ~330 words in 13-15s both immediately
before and immediately after a two-hour lane that reached step 3.

Use it to rule out a dead provider cheaply, never as a launch gate on its own. A
pass means "the provider answers a few hundred words right now", which is weaker
than "a six-task lane carrying a large cached context will finish".

Exit codes: 0 sustained generation OK, 1 too slow, 2 could not run the probe.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "scripts/opencode_workflow_adapter.py"
OPENCODE = Path("/opt/data/.local/bin/opencode")
OPENCODE_SHA = "7c4d91c84d2bfdeabb59257e3490c5e5acb08f2aacb3e42f3ddc296a1c3f1aca"
SOURCE_AUTH = Path(os.environ.get("TOKEN_EVAL_CODEX_HOME", Path.home() / ".codex")) / "auth.json"

PROMPT = (
    "Write roughly {words} words explaining how a hash table resolves collisions. "
    "Cover separate chaining and open addressing. Plain prose, no code."
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--words", type=int, default=300, help="target generation length")
    ap.add_argument("--timeout", type=int, default=180, help="seconds before declaring the provider too slow")
    ap.add_argument("--min-words", type=int, default=120, help="shortest reply accepted as sustained generation")
    args = ap.parse_args(argv)

    if not SOURCE_AUTH.is_file():
        print(f"probe: no credential at {SOURCE_AUTH}", file=sys.stderr)
        return 2

    tmp = Path(tempfile.mkdtemp(prefix="opencode-throughput-"))
    try:
        codex_home = tmp / ".codex"
        codex_home.mkdir()
        shutil.copy2(SOURCE_AUTH, codex_home / "auth.json")
        out = tmp / "last.txt"
        env = os.environ.copy()
        env.update(
            HOME=str(tmp),
            CODEX_HOME=str(codex_home),
            XDG_CONFIG_HOME=str(tmp / "cfg"),
            XDG_DATA_HOME=str(tmp / "data"),
            XDG_CACHE_HOME=str(tmp / "cache"),
            XDG_STATE_HOME=str(tmp / "state"),
        )
        cmd = [
            "/usr/bin/python3", str(ADAPTER),
            "--opencode-binary", str(OPENCODE),
            "--expected-opencode-sha256", OPENCODE_SHA,
            "--treatment", "bare",
            "exec", "--model", "gpt-5.6-sol",
            "--config", 'model_reasoning_effort="medium"',
            "--output-last-message", str(out),
            PROMPT.format(words=args.words),
        ]
        started = time.monotonic()
        try:
            subprocess.run(cmd, env=env, timeout=args.timeout, capture_output=True)
        except subprocess.TimeoutExpired:
            print(
                f"FAIL provider did not generate ~{args.words} words within {args.timeout}s. "
                "Do not launch. Cause not established by this probe."
            )
            return 1
        elapsed = time.monotonic() - started
        words = len(out.read_text().split()) if out.is_file() else 0
        if words < args.min_words:
            print(f"FAIL generated only {words} words in {elapsed:.0f}s (floor {args.min_words}); do not launch.")
            return 1
        print(f"OK {words} words in {elapsed:.0f}s ({words / max(elapsed, 1):.1f} words/s). Provider answers; this does NOT predict that a lane will complete.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
