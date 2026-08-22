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


def command(
    *,
    model: str,
    effort: str,
    prompt: str,
    mcp_config: Path | None = None,
    session_id: str | None = None,
) -> list[str]:
    args = [
        "claude",
        "--print",
        "--verbose",
        "--output-format", "stream-json",
        "--model", model,
        "--effort", effort,
        "--tools", "Bash,Edit,Read,Grep,Glob",
        "--permission-mode", "bypassPermissions",
        "--allow-dangerously-skip-permissions",
        "--no-chrome",
    ]
    if mcp_config is not None:
        args.extend(["--mcp-config", str(mcp_config), "--strict-mcp-config"])
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
    profile_id = str((record.get("profile") or {}).get("profile_id") or "")
    cfg = fixture.active_tool_config(record, profile_id)
    env = fixture.claude_env(
        claude_home,
        containerized=True,
        cfg=cfg,
        provider=str((record.get("agent") or {}).get("provider") or "anthropic"),
    )
    fixture.apply_model_network_isolation(env, prepend_denied_shell_to_path=False)
    # Keep treatment/session identifiers out of model-visible HOME, config, and cwd.
    # Controller evidence continues to use the real lane paths on the host.
    neutral_home = Path("/agent-home")
    neutral_repo = Path("/workspace")
    for key, suffix in {
        "CODEX_HOME": "",
        "HOME": "/home",
        "PYTHONUSERBASE": "/python-userbase",
        "XDG_CACHE_HOME": "/xdg-cache",
        "XDG_CONFIG_HOME": "/xdg-config",
        "XDG_DATA_HOME": "/xdg-data",
        "TMPDIR": "/tmp",
        "GOPATH": "/go",
        "GOCACHE": "/go-build-cache",
        "GOMODCACHE": "/go/pkg/mod",
        "CLAUDE_CONFIG_DIR": "/claude-config",
    }.items():
        env[key] = str(neutral_home) + suffix
    mounts = fixture.container_mounts_for_record(record, claude_home, include_repo=False, cfg=cfg)
    fixture.add_mount(mounts, claude_home, target=neutral_home, mode="rw")
    fixture.add_mount(mounts, repo, target=neutral_repo, mode="rw")
    agent = record.get("agent") or {}
    mcp_config = neutral_home / "claude-config" / "mcp.json"
    if not (claude_home / "claude-config" / "mcp.json").is_file():
        mcp_config = None
    cmd = command(
        model=str(agent.get("model", "claude-opus-5")),
        effort=str(agent.get("reasoning_effort", "medium")),
        prompt=prompt_path.read_text(),
        mcp_config=mcp_config,
        session_id=session_id,
    )
    proc = fixture.run_backend(
        cmd,
        backend="docker",
        docker_image=docker_image,
        cwd=neutral_repo,
        env=env,
        stdout_path=events_path,
        timeout=timeout,
        mounts=mounts,
    )
    captured, continuity_error = stream_continuity(events_path, session_id)
    return proc.returncode, captured, continuity_error
