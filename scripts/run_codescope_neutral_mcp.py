#!/usr/bin/env python3
"""Run CodeScope's MCP server without its mandatory uptake instructions.

The pinned upstream server injects ``ALWAYS prefer`` / ``follow strictly``
routing text in the MCP initialize response. That would violate this research
repository's natural-use contract. This adapter preserves the official server,
auto-indexer, tool schemas, and tool responses while removing only the optional
MCP ``instructions`` field from the initialize result.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--codescope-bin", type=Path, required=True)
    parser.add_argument("--repo-name")
    return parser.parse_args()


def sanitize_response(line: bytes) -> bytes:
    try:
        payload = json.loads(line)
        result = payload.get("result")
        if isinstance(result, dict) and "protocolVersion" in result:
            result.pop("instructions", None)
            return (json.dumps(payload, separators=(",", ":")) + "\n").encode()
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass
    return line


def proxy_stdio(child: subprocess.Popen[bytes]) -> None:
    assert child.stdin is not None and child.stdout is not None
    selector = selectors.DefaultSelector()
    selector.register(sys.stdin.buffer, selectors.EVENT_READ, "request")
    selector.register(child.stdout, selectors.EVENT_READ, "response")
    response_buffer = b""
    while selector.get_map():
        if child.poll() is not None and child.stdout not in [key.fileobj for key in selector.get_map().values()]:
            break
        for key, _mask in selector.select(timeout=0.5):
            chunk = os.read(key.fd, 65536)
            if not chunk:
                selector.unregister(key.fileobj)
                if key.data == "request":
                    child.stdin.close()
                elif response_buffer:
                    sys.stdout.buffer.write(response_buffer)
                    sys.stdout.buffer.flush()
                    response_buffer = b""
                continue
            if key.data == "request":
                child.stdin.write(chunk)
                child.stdin.flush()
                continue
            response_buffer += chunk
            while b"\n" in response_buffer:
                line, response_buffer = response_buffer.split(b"\n", 1)
                sys.stdout.buffer.write(sanitize_response(line + b"\n"))
                sys.stdout.buffer.flush()


def main() -> int:
    args = parse_args()
    repo = args.repo.resolve()
    binary = args.codescope_bin.resolve()
    if not binary.is_file():
        raise SystemExit(f"CodeScope binary not found: {binary}")
    repo_name = args.repo_name or f"eval-{repo.name}"
    state_dir = Path.home() / ".codescope"
    state_dir.mkdir(parents=True, exist_ok=True)
    start_log = (state_dir / "evaluation-start.log").open("ab")
    env = os.environ.copy()
    env["PATH"] = f"{binary.parent}:{env.get('PATH', '')}"
    env.pop("CODESCOPE_OTLP_ENDPOINT", None)

    start = subprocess.run(
        [str(binary), "start"],
        stdin=subprocess.DEVNULL,
        stdout=start_log,
        stderr=subprocess.STDOUT,
        env=env,
        check=False,
    )
    if start.returncode:
        raise SystemExit(f"codescope start exited {start.returncode}; see {start_log.name}")

    child = subprocess.Popen(
        [str(binary), "mcp", str(repo), "--repo", repo_name, "--auto-index"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr.buffer,
        env=env,
    )

    def terminate(_signum: int, _frame: object) -> None:
        child.terminate()

    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)
    try:
        proxy_stdio(child)
        return child.wait()
    finally:
        if child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
        subprocess.run(
            [str(binary), "stop"],
            stdin=subprocess.DEVNULL,
            stdout=start_log,
            stderr=subprocess.STDOUT,
            env=env,
            timeout=15,
            check=False,
        )
        start_log.close()


if __name__ == "__main__":
    raise SystemExit(main())
