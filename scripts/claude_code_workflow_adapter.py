"""Claude Code runtime adapter for the shared warm-workflow controller."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


def session_ids(events_path: Path) -> list[str]:
    found: list[str] = []
    for line in events_path.read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        value = event.get("session_id")
        if isinstance(value, str) and value:
            found.append(value)
    return found


def stream_continuity(events_path: Path, requested_session_id: str | None) -> tuple[str | None, dict[str, Any] | None]:
    observed = session_ids(events_path)
    unique = sorted(set(observed))
    if len(unique) != 1 or (requested_session_id is not None and unique[0] != requested_session_id):
        return requested_session_id, {
            "events": str(events_path),
            "expected_session_id": requested_session_id,
            "observed_session_ids": unique,
            "message": "Claude Code stream did not prove exactly one persistent session",
        }
    return unique[0], None


def command(*, model: str, prompt: str, session_id: str | None = None) -> list[str]:
    args = [
        "claude",
        "--print",
        "--verbose",
        "--output-format", "stream-json",
        "--model", model,
        "--tools", "Bash,Edit,Read,Grep,Glob",
        "--permission-mode", "bypassPermissions",
        "--allow-dangerously-skip-permissions",
        "--no-chrome",
    ]
    if session_id:
        args.extend(["--resume", session_id])
    args.append(prompt)
    return args


def run_task(
    *,
    record: dict[str, Any],
    claude_home: Path,
    run_dir: Path,
    docker_image: str,
    prompt_path: Path,
    events_path: Path,
    session_id: str | None,
    timeout: int,
    fixture: Any,
) -> tuple[int, str | None, dict[str, Any] | None]:
    repo = fixture.rel_or_abs(record["target"]["repository_path"])
    env = fixture.claude_env(claude_home, containerized=True)
    fixture.apply_model_network_isolation(env)
    mounts = fixture.container_mounts_for_record(record, claude_home, include_repo=True)
    cmd = command(model=str(record.get("agent", {}).get("model", "claude-sonnet-5")), prompt=prompt_path.read_text(), session_id=session_id)
    proc = fixture.run_backend(
        cmd,
        backend="docker",
        docker_image=docker_image,
        cwd=repo,
        env=env,
        stdout_path=events_path,
        timeout=timeout,
        mounts=mounts,
    )
    captured, continuity_error = stream_continuity(events_path, session_id)
    return proc.returncode, captured, continuity_error
