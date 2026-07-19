#!/usr/bin/env python3
"""Audit experiment artifacts against a run record's tool manifest.

The audit accepts one or more transcript/artifact files. Official runs should
include the model event stream plus environment-preflight artifacts such as
`codex-mcp-list.txt`, effective config, and rendered prompt snippets. A run is
excluded if any forbidden surface appears or model-visible external retrieval
occurs without an explicit allowance. Command coverage is descriptive and never
requires, prefers, or invalidates an agent's natural treatment-tool use.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_FORBIDDEN = [
    "lean-ctx",
    "mcp_lean_ctx",
    "ctx_read",
    "ctx_search",
    "ctx_shell",
    "ctx_graph",
    "codegraph",
    "serena",
    "rtk",
    "ponytail",
    "lowfat",
    "tokenjuice",
    "repomix",
    "mex",
    "cavemem",
    "cartog",
    "caveman",
]
PROFILE_AUTHORED_CROSS_REFERENCE_TERMS = {
    # Ponytail's own installed instructions recommend pairing it with Caveman
    # for terse prose. That product-authored text is not evidence that the
    # Caveman treatment was installed or invoked in a Ponytail lane.
    "artifact-ponytail-codex-plugin-v1": {"caveman"},
}
NETWORK_CLIENT_PATTERN = re.compile(
    r"(?:^|[;&|]\s*|\b(?:lowfat|sudo|env)\s+)(?P<client>curl|wget)\b",
    re.IGNORECASE,
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def tool_permissions(record: dict[str, Any]) -> dict[str, Any]:
    setup = record.get("setup", {})
    permissions = setup.get("tool_permissions", {})
    return permissions if isinstance(permissions, dict) else {}


def forbidden_for(record: dict[str, Any]) -> tuple[list[str], set[str]]:
    permissions = tool_permissions(record)
    forbidden = sorted(
        set(DEFAULT_FORBIDDEN) | set(permissions.get("forbidden_tools") or [])
    )
    allowed = set(permissions.get("allowed_token_saving_tools") or [])
    profile_id = permissions.get("profile_id")
    if isinstance(profile_id, str):
        allowed.update(PROFILE_AUTHORED_CROSS_REFERENCE_TERMS.get(profile_id, set()))
    return forbidden, allowed


def allowed_tool_commands_for(record: dict[str, Any]) -> dict[str, set[str]]:
    raw = tool_permissions(record).get("allowed_tool_commands") or {}
    if not isinstance(raw, dict):
        return {}
    return {
        str(tool).lower(): {str(command).lower() for command in commands or []}
        for tool, commands in raw.items()
    }


def forbidden_pattern(term: str) -> re.Pattern[str]:
    # Avoid false positives for short tool names embedded in code symbols, e.g.
    # `mex` inside Django's `JSONExact`. Hyphen/underscore are treated as token
    # characters because many forbidden tool surfaces use them.
    return re.compile(
        rf"(?<![A-Za-z0-9_-]){re.escape(term)}(?![A-Za-z0-9_-])",
        re.IGNORECASE,
    )


def scan_file(
    path: Path, forbidden: list[str], allowed: set[str]
) -> list[dict[str, str]]:
    text = path.read_text(errors="replace") if path.exists() else ""
    hits: list[dict[str, str]] = []
    for term in forbidden:
        if term in allowed:
            continue
        pattern = forbidden_pattern(term)
        match = pattern.search(text)
        if match:
            start = max(0, match.start() - 80)
            end = min(len(text), match.end() + 80)
            snippet = text[start:end].replace("\n", " ")
            hits.append(
                {"term": term, "artifact": str(path), "snippet": snippet}
            )
    return hits


def iter_json_events(path: Path):
    if not path.exists():
        return
    for line_number, line in enumerate(
        path.read_text(errors="replace").splitlines(), start=1
    ):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            yield line_number, event


def command_from_event(event: dict[str, Any]) -> str:
    item = event.get("item")
    if not isinstance(item, dict) or item.get("type") != "command_execution":
        return ""
    command = item.get("command")
    return command if isinstance(command, str) else ""


def structured_policy_hits(
    path: Path, record: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    external_hits: list[dict[str, Any]] = []
    pass_through_hits: list[dict[str, Any]] = []
    permissions = tool_permissions(record)
    external_allowed = bool(permissions.get("external_retrieval_allowed", False))
    allowed_commands = allowed_tool_commands_for(record)

    for line_number, event in iter_json_events(path):
        item = event.get("item")
        item_type = item.get("type") if isinstance(item, dict) else None
        if (
            not external_allowed
            and isinstance(item, dict)
            and item_type == "web_search"
        ):
            external_hits.append(
                {
                    "kind": "web_search",
                    "artifact": str(path),
                    "line": line_number,
                    "query": str(item.get("query") or "")[:500],
                }
            )

        command = command_from_event(event)
        if not command:
            continue
        if not external_allowed:
            match = NETWORK_CLIENT_PATTERN.search(command)
            if match:
                external_hits.append(
                    {
                        "kind": "network_client",
                        "artifact": str(path),
                        "line": line_number,
                        "client": match.group("client").lower(),
                        "command": command[:500],
                    }
                )

        for tool, commands in allowed_commands.items():
            invocation = re.compile(
                rf"(?<![A-Za-z0-9_.-]){re.escape(tool)}\s+"
                r"(?P<command>[A-Za-z0-9_.+-]+)",
                re.IGNORECASE,
            )
            for match in invocation.finditer(command):
                invoked = match.group("command").lower()
                if invoked not in commands:
                    pass_through_hits.append(
                        {
                            "tool": tool,
                            "command": invoked,
                            "artifact": str(path),
                            "line": line_number,
                            "shell_command": command[:500],
                        }
                    )

    return external_hits, pass_through_hits


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-output", type=Path, help="write machine-readable audit result"
    )
    parser.add_argument("run_record", type=Path)
    parser.add_argument("artifacts", nargs="+")
    args = parser.parse_args(argv)

    run_record = load_json(args.run_record)
    forbidden, allowed = forbidden_for(run_record)
    hits: list[dict[str, str]] = []
    external_hits: list[dict[str, Any]] = []
    pass_through_hits: list[dict[str, Any]] = []
    missing: list[str] = []
    for artifact_text in args.artifacts:
        artifact = Path(artifact_text)
        if not artifact.exists():
            missing.append(str(artifact))
            continue
        hits.extend(scan_file(artifact, forbidden, allowed))
        external, pass_through = structured_policy_hits(artifact, run_record)
        external_hits.extend(external)
        pass_through_hits.extend(pass_through)

    passed = not hits and not missing and not external_hits
    result = {
        "passed": passed,
        "run_record": str(args.run_record),
        "artifacts_scanned": [
            str(Path(path)) for path in args.artifacts if Path(path).exists()
        ],
        "missing_artifacts": missing,
        "forbidden_tool_hits": hits,
        "external_retrieval_hits": external_hits,
        "pass_through_tool_command_hits": pass_through_hits,
        "allowed_token_saving_tools": sorted(allowed),
        "allowed_tool_commands": {
            tool: sorted(commands)
            for tool, commands in allowed_tool_commands_for(run_record).items()
        },
    }
    if args.json_output:
        args.json_output.write_text(json.dumps(result, indent=2) + "\n")

    if missing:
        print("TOOL ISOLATION FAILED")
        print("missing required artifacts:")
        for artifact in missing:
            print(f"- {artifact}")
    if hits:
        print("TOOL ISOLATION FAILED")
        print("forbidden terms:", ", ".join(sorted({hit["term"] for hit in hits})))
        for hit in hits[:20]:
            print(f"- {hit['term']} in {hit['artifact']}: {hit['snippet']}")
    if external_hits:
        print("TOOL ISOLATION FAILED")
        print("external retrieval was observed")
        for hit in external_hits[:20]:
            print(f"- {hit['kind']} in {hit['artifact']}:{hit['line']}")
    if pass_through_hits:
        print("descriptive tool coverage: pass-through commands observed")
        for hit in pass_through_hits[:20]:
            print(
                f"- {hit['tool']} {hit['command']} in "
                f"{hit['artifact']}:{hit['line']}"
            )
    if not passed:
        return 1
    print("tool isolation audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
