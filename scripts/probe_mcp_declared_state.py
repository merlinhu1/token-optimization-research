#!/usr/bin/env python3
"""Ask a running MCP server whether the state a profile declares is actually there.

Deliberately a separate script from ``probe_mcp_stdio.py`` rather than a flag on it. That probe's
SHA-256 is hashed into every execution descriptor, so editing it re-identifies every protocol in
the corpus and orphans the designated baseline protocols. This file is not hashed into the
descriptor, so the verification can evolve without re-identifying the apparatus it verifies.

A handshake proves a server starts. It does not prove the state the profile claims. Four
jCodeMunch lanes across both runtimes declared ``tool_state: warm-index``, passed their handshake,
and then had the model rebuild the index in-session because the controller's warm state was keyed
to a path the server never resolved.
"""
from __future__ import annotations

import argparse
import json
import selectors
import subprocess
import sys
import threading
import time
from typing import Any


def send(proc: subprocess.Popen[str], payload: dict[str, Any]) -> None:
    assert proc.stdin is not None
    proc.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
    proc.stdin.flush()


def receive_json(
    proc: subprocess.Popen[str], selector: selectors.BaseSelector, request_id: int, deadline: float
) -> tuple[dict[str, Any] | None, list[str]]:
    noise: list[str] = []
    assert proc.stdout is not None
    while time.monotonic() < deadline:
        if not selector.select(max(0.0, deadline - time.monotonic())):
            break
        line = proc.stdout.readline()
        if not line:
            break
        stripped = line.strip()
        if not stripped:
            continue
        try:
            message = json.loads(stripped)
        except json.JSONDecodeError:
            noise.append(stripped)
            continue
        if message.get("id") == request_id:
            return message, noise
    return None, noise


def result_text(tool_call: dict[str, Any] | None) -> str:
    """Flatten a tools/call result to the text a caller can assert on."""
    result = (tool_call or {}).get("result")
    if not isinstance(result, dict):
        return ""
    parts = [
        str(block.get("text", ""))
        for block in result.get("content", [])
        if isinstance(block, dict) and block.get("text")
    ]
    if result.get("structuredContent") is not None:
        parts.append(json.dumps(result["structuredContent"], sort_keys=True))
    return "\n".join(parts)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", required=True)
    parser.add_argument("--arg", action="append", default=[])
    parser.add_argument("--cwd")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--call-tool", required=True)
    parser.add_argument("--call-arguments", default="{}")
    parser.add_argument("--require", action="append", default=[],
                        help="substring the tool result must contain; repeat for several")
    args = parser.parse_args(argv)

    proc = subprocess.Popen(
        [args.command, *args.arg],
        cwd=args.cwd,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1,
    )
    selector = selectors.DefaultSelector()
    assert proc.stdout is not None and proc.stderr is not None
    stderr_chunks: list[str] = []
    stderr_pipe = proc.stderr
    threading.Thread(
        target=lambda: stderr_chunks.extend(stderr_pipe), daemon=True
    ).start()
    selector.register(proc.stdout, selectors.EVENT_READ)
    deadline = time.monotonic() + args.timeout
    errors: list[str] = []
    tool_call: dict[str, Any] | None = None
    try:
        send(proc, {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18", "capabilities": {},
                "clientInfo": {"name": "token-eval-declared-state-probe", "version": "1"},
            },
        })
        initialize, _ = receive_json(proc, selector, 1, deadline)
        if initialize is None or "error" in initialize:
            errors.append("initialize failed")
        else:
            send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
            try:
                arguments = json.loads(args.call_arguments)
            except json.JSONDecodeError as exc:
                arguments = None
                errors.append(f"--call-arguments is not JSON: {exc}")
            if arguments is not None:
                send(proc, {
                    "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                    "params": {"name": args.call_tool, "arguments": arguments},
                })
                tool_call, _ = receive_json(proc, selector, 2, deadline)
                if tool_call is None:
                    errors.append(f"tools/call {args.call_tool} response missing")
                elif "error" in tool_call:
                    errors.append(f"tools/call {args.call_tool} returned an error")
    except (BrokenPipeError, OSError, ValueError) as exc:
        errors.append(f"declared-state probe failed: {type(exc).__name__}: {exc}")
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)
        selector.close()

    text = result_text(tool_call)
    missing = [needle for needle in args.require if needle not in text]
    if missing:
        errors.append(f"tool result did not report {missing}")
    receipt = {
        "passed": not errors,
        "tool": args.call_tool,
        "arguments": args.call_arguments,
        "result_text": text[:4000],
        "missing_required_substrings": missing,
        "errors": errors,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
