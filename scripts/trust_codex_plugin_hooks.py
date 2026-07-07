#!/usr/bin/env python3
"""Trust the reviewed hooks of one installed Codex plugin without a model call."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import selectors
import subprocess
import time
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--plugin-id", required=True)
    parser.add_argument("--expected-events", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=30.0)
    return parser.parse_args()


class AppServer:
    def __init__(self, codex: str, timeout: float) -> None:
        self.timeout = timeout
        self.proc = subprocess.Popen(
            [codex, "app-server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=os.environ.copy(),
        )
        assert self.proc.stdin is not None
        assert self.proc.stdout is not None
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.proc.stdout, selectors.EVENT_READ)

    def send(self, payload: dict[str, Any]) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
        self.proc.stdin.flush()

    def response(self, request_id: int) -> dict[str, Any]:
        deadline = time.monotonic() + self.timeout
        assert self.proc.stdout is not None
        while time.monotonic() < deadline:
            events = self.selector.select(max(0.0, deadline - time.monotonic()))
            if not events:
                break
            line = self.proc.stdout.readline()
            if not line:
                break
            message = json.loads(line)
            if message.get("id") == request_id:
                if "error" in message:
                    raise RuntimeError(f"Codex app-server request {request_id} failed: {message['error']}")
                return message
        stderr = ""
        if self.proc.poll() is not None and self.proc.stderr is not None:
            stderr = self.proc.stderr.read().strip()
        raise RuntimeError(f"timed out waiting for Codex app-server request {request_id}: {stderr}")

    def close(self) -> None:
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)


def list_plugin_hooks(server: AppServer, cwd: Path, plugin_id: str, request_id: int) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    server.send({"method": "hooks/list", "id": request_id, "params": {"cwds": [str(cwd.resolve())]}})
    response = server.response(request_id)["result"]
    entries = response.get("data", [])
    if len(entries) != 1:
        raise RuntimeError(f"hooks/list returned {len(entries)} cwd entries; expected one")
    entry = entries[0]
    hooks = [hook for hook in entry.get("hooks", []) if hook.get("pluginId") == plugin_id]
    return hooks, list(entry.get("warnings", [])), list(entry.get("errors", []))


def main() -> int:
    args = parse_args()
    expected_events = {event.strip() for event in args.expected_events.split(",") if event.strip()}
    if not expected_events:
        raise SystemExit("--expected-events must name at least one hook event")
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    server = AppServer(args.codex, args.timeout)
    try:
        server.send({
            "method": "initialize",
            "id": 0,
            "params": {
                "clientInfo": {
                    "name": "token_optimization_hook_qualification",
                    "title": "Token optimization hook qualification",
                    "version": "1",
                }
            },
        })
        initialize = server.response(0)["result"]
        server.send({"method": "initialized", "params": {}})
        before, warnings, errors = list_plugin_hooks(server, args.cwd, args.plugin_id, 1)
        if warnings or errors:
            raise RuntimeError(f"hook discovery warnings/errors: warnings={warnings!r} errors={errors!r}")
        discovered_events = {str(hook.get("eventName")) for hook in before}
        if discovered_events != expected_events:
            raise RuntimeError(
                f"plugin {args.plugin_id} hook events differ: expected={sorted(expected_events)!r} discovered={sorted(discovered_events)!r}"
            )
        if not before or any(not hook.get("enabled") for hook in before):
            raise RuntimeError(f"plugin {args.plugin_id} did not expose enabled hooks")
        states = {
            str(hook["key"]): {"trusted_hash": str(hook["currentHash"])}
            for hook in before
        }
        server.send({
            "method": "config/batchWrite",
            "id": 2,
            "params": {
                "edits": [{
                    "keyPath": "hooks.state",
                    "value": states,
                    "mergeStrategy": "upsert",
                }],
                "reloadUserConfig": True,
            },
        })
        server.response(2)
        after, warnings, errors = list_plugin_hooks(server, args.cwd, args.plugin_id, 3)
        if warnings or errors:
            raise RuntimeError(f"post-trust hook discovery warnings/errors: warnings={warnings!r} errors={errors!r}")
        if len(after) != len(before) or any(hook.get("trustStatus") != "trusted" for hook in after):
            raise RuntimeError(f"plugin {args.plugin_id} hooks were not all trusted")
        receipt = {
            "schema_version": 1,
            "provider_calls": 0,
            "codex_home": str(initialize.get("codexHome", "")),
            "plugin_id": args.plugin_id,
            "cwd": str(args.cwd.resolve()),
            "expected_events": sorted(expected_events),
            "hook_count": len(after),
            "hooks": [
                {
                    "key": hook["key"],
                    "event_name": hook["eventName"],
                    "enabled": hook["enabled"],
                    "current_hash": hook["currentHash"],
                    "trust_status": hook["trustStatus"],
                    "source": hook["source"],
                    "plugin_id": hook["pluginId"],
                }
                for hook in after
            ],
            "passed": True,
        }
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    finally:
        server.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
