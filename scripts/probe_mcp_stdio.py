#!/usr/bin/env python3
"""Provider-free MCP stdio initialize/tools-list health probe."""
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
    non_json_stdout: list[str] = []
    assert proc.stdout is not None
    while time.monotonic() < deadline:
        remaining = max(0.0, deadline - time.monotonic())
        events = selector.select(remaining)
        if not events:
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
            non_json_stdout.append(stripped)
            continue
        if message.get("id") == request_id:
            return message, non_json_stdout
    return None, non_json_stdout


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", required=True)
    parser.add_argument("--arg", action="append", default=[])
    parser.add_argument("--cwd")
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args(argv)

    command = [args.command, *args.arg]
    proc = subprocess.Popen(
        command,
        cwd=args.cwd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    selector = selectors.DefaultSelector()
    assert proc.stdout is not None
    stderr_pipe = proc.stderr
    assert stderr_pipe is not None
    stderr_chunks: list[str] = []
    stderr_thread = threading.Thread(
        target=lambda: stderr_chunks.extend(stderr_pipe),
        name="mcp-probe-stderr-drain",
        daemon=True,
    )
    stderr_thread.start()
    selector.register(proc.stdout, selectors.EVENT_READ)
    deadline = time.monotonic() + args.timeout
    errors: list[str] = []
    non_json_stdout: list[str] = []
    initialize: dict[str, Any] | None = None
    tools_list: dict[str, Any] | None = None
    stderr_text = ""
    try:
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "token-eval-mcp-probe", "version": "1"},
                },
            },
        )
        initialize, noise = receive_json(proc, selector, 1, deadline)
        non_json_stdout.extend(noise)
        if initialize is None:
            errors.append("initialize response missing")
        elif "error" in initialize or not isinstance(initialize.get("result"), dict):
            errors.append("initialize response failed")
        else:
            send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
            send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
            tools_list, noise = receive_json(proc, selector, 2, deadline)
            non_json_stdout.extend(noise)
            if tools_list is None:
                errors.append("tools/list response missing")
            elif "error" in tools_list or not isinstance(tools_list.get("result", {}).get("tools"), list):
                errors.append("tools/list response failed")
            elif not tools_list["result"]["tools"]:
                errors.append("tools/list advertised no tools")
        if non_json_stdout:
            errors.append("non-JSON stdout preceded an MCP response")
    except (BrokenPipeError, OSError, ValueError) as exc:
        errors.append(f"stdio probe failed: {type(exc).__name__}: {exc}")
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)
        stderr_thread.join(timeout=2)
        stderr_text = "".join(stderr_chunks)
        selector.close()

    tool_names = []
    if tools_list:
        tool_names = sorted(
            str(tool.get("name"))
            for tool in tools_list.get("result", {}).get("tools", [])
            if isinstance(tool, dict) and tool.get("name")
        )
    receipt = {
        "passed": not errors,
        "initialize_passed": initialize is not None and "error" not in initialize,
        "tools_list_passed": tools_list is not None and "error" not in tools_list,
        "server_name": ((initialize or {}).get("result") or {}).get("serverInfo", {}).get("name"),
        "protocol_version": ((initialize or {}).get("result") or {}).get("protocolVersion"),
        "tool_names": tool_names,
        "non_json_stdout_lines": non_json_stdout,
        "stderr_present": bool(stderr_text.strip()),
        "errors": errors,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
