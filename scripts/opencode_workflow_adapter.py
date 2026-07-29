#!/usr/bin/env python3
"""Run OpenCode behind the workflow runner's narrow Codex-wrapper boundary.

The workflow controller still owns fixture setup, prompt sequencing, container
isolation, and verification. This adapter translates only the agent-runtime
boundary: Codex-shaped launch arguments become OpenCode ``run`` arguments, raw
OpenCode JSONL is retained, and small normalized continuity/usage events are
emitted for the existing controller.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_OPENCODE_BINARY = Path(
    os.environ.get(
        "TOKEN_EVAL_OPENCODE_BINARY",
        "/opt/data/tool-candidates/opencode-runtime/node_modules/opencode-ai/bin/opencode.exe",
    )
)
UV_BINARY = Path("/opt/data/opt/uv/uv")
HEADROOM_WHEEL = Path(
    "/opt/data/tool-candidates/headroom/dist/headroom_ai-0.28.0-cp310-abi3-linux_x86_64.whl"
)
SERENA_ROOT = Path("/opt/data/tool-candidates/serena")
CARTOG_BINARY = Path("/opt/data/tool-candidates/cartog/target/release/cartog")
TREATMENT_PROFILES = {
    "bare",
    "tokenjuice",
    "serena",
    "snip",
    "cartog",
    "headroom",
}
PLUGIN_TREATMENTS = {"tokenjuice", "snip"}


def verify_binary_sha256(binary: Path, expected_sha256: str) -> str:
    if not binary.is_file():
        raise ValueError(f"OpenCode binary is missing: {binary}")
    actual = hashlib.sha256(binary.read_bytes()).hexdigest()
    if actual != expected_sha256:
        raise ValueError(
            f"OpenCode binary SHA-256 mismatch: expected {expected_sha256}, got {actual}"
        )
    return actual


@dataclass(frozen=True)
class CompatArgs:
    model: str
    variant: str
    directory: Path | None
    last_message_path: Path
    session_id: str | None
    prompt_from_stdin: bool
    prompt: str | None


@dataclass(frozen=True)
class NormalizedRun:
    session_id: str
    usage: dict[str, int]
    last_text: str
    normalized_events: list[dict[str, Any]]


def _value_after(args: list[str], index: int, option: str) -> tuple[str, int]:
    if index + 1 >= len(args):
        raise ValueError(f"{option} requires a value")
    return args[index + 1], index + 2


def parse_codex_exec_args(args: list[str]) -> CompatArgs:
    """Parse only the two exact Codex argv shapes emitted by the controller."""
    if not args or args[0] != "exec":
        raise ValueError("adapter requires a codex exec argument shape")
    index = 1
    resume = index < len(args) and args[index] == "resume"
    if resume:
        index += 1

    model: str | None = None
    variant: str | None = None
    directory: Path | None = None
    last_message_path: Path | None = None
    positionals: list[str] = []
    options_without_values = {
        "--strict-config",
        "--json",
        "--ignore-rules",
        "--dangerously-bypass-hook-trust",
    }
    options_with_values = {"--color", "--disable"}

    while index < len(args):
        item = args[index]
        if item == "--model":
            model, index = _value_after(args, index, item)
            continue
        if item in {"-c", "--config"}:
            value, index = _value_after(args, index, item)
            if value.startswith("model_reasoning_effort="):
                variant = value.split("=", 1)[1].strip().strip('"').strip("'")
            continue
        if item == "--cd":
            value, index = _value_after(args, index, item)
            directory = Path(value)
            continue
        if item == "--output-last-message":
            value, index = _value_after(args, index, item)
            last_message_path = Path(value)
            continue
        if item in options_without_values:
            index += 1
            continue
        if item in options_with_values:
            _, index = _value_after(args, index, item)
            continue
        if item.startswith("-") and item != "-":
            raise ValueError(f"unsupported Codex compatibility option: {item}")
        positionals.append(item)
        index += 1

    if model is None:
        raise ValueError("Codex compatibility arguments are missing --model")
    if last_message_path is None:
        raise ValueError("Codex compatibility arguments are missing --output-last-message")
    if not variant:
        raise ValueError("Codex compatibility arguments are missing model_reasoning_effort")

    session_id: str | None = None
    if resume:
        if len(positionals) < 2:
            raise ValueError("Codex resume compatibility arguments are missing session and prompt")
        session_id = positionals.pop(0)
    if len(positionals) != 1:
        raise ValueError("Codex compatibility arguments must contain exactly one prompt")
    prompt_value = positionals[0]
    return CompatArgs(
        model=model if "/" in model else f"openai/{model}",
        variant=variant,
        directory=directory,
        last_message_path=last_message_path,
        session_id=session_id,
        prompt_from_stdin=prompt_value == "-",
        prompt=None if prompt_value == "-" else prompt_value,
    )


def build_opencode_command(
    binary: Path,
    parsed: CompatArgs,
    prompt: str,
    *,
    pure: bool = True,
) -> list[str]:
    command = [
        str(binary),
        "run",
        "--format",
        "json",
        "--model",
        parsed.model,
        "--variant",
        parsed.variant,
        "--auto",
    ]
    if pure:
        command.append("--pure")
    if parsed.directory is not None:
        command.extend(["--dir", str(parsed.directory)])
    if parsed.session_id is not None:
        command.extend(["--session", parsed.session_id])
    command.append(prompt)
    return command


def build_headroom_command(native_command: list[str], *, port: int) -> list[str]:
    """Wrap one native OpenCode invocation with Headroom's official product command."""
    return [
        str(UV_BINARY),
        "tool",
        "run",
        "--from",
        str(HEADROOM_WHEEL),
        "--with",
        "mcp",
        "--with",
        "fastapi",
        "--with",
        "uvicorn<1.0",
        "--with",
        "httpx[http2]",
        "--with",
        "openai",
        "--with",
        "zstandard",
        "--with",
        "websockets",
        "headroom",
        "wrap",
        "opencode",
        "--port",
        str(port),
        "--verbose",
        "--",
        *native_command[1:],
    ]


def _decode_jwt_payload(token: str) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Codex access token is not a JWT")
    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    try:
        value = json.loads(base64.urlsafe_b64decode(payload).decode())
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Codex access token JWT payload is invalid") from exc
    if not isinstance(value, dict):
        raise ValueError("Codex access token JWT payload is not an object")
    return value


def ensure_opencode_auth(codex_auth_path: Path, xdg_data_home: Path) -> dict[str, object]:
    """Create lane-private OpenCode OAuth once; preserve any rotated credentials."""
    target = xdg_data_home / "opencode" / "auth.json"
    if target.is_file():
        return {"provider": "openai", "auth_type": "oauth", "created": False}
    source = json.loads(codex_auth_path.read_text())
    tokens = source.get("tokens", source)
    if not isinstance(tokens, dict):
        raise ValueError("Codex auth tokens are missing")
    access = tokens.get("access_token")
    refresh = tokens.get("refresh_token")
    if not isinstance(access, str) or not access or not isinstance(refresh, str) or not refresh:
        raise ValueError("Codex OAuth access/refresh tokens are missing")
    claims = _decode_jwt_payload(access)
    expires = claims.get("exp")
    if isinstance(expires, bool) or not isinstance(expires, int) or expires <= 0:
        raise ValueError("Codex OAuth access token expiration is missing")
    auth_claims = claims.get("https://api.openai.com/auth")
    nested_account = auth_claims.get("chatgpt_account_id") if isinstance(auth_claims, dict) else None
    account = (
        tokens.get("account_id")
        or source.get("account_id")
        or claims.get("chatgpt_account_id")
        or nested_account
    )
    record: dict[str, object] = {
        "type": "oauth",
        "refresh": refresh,
        "access": access,
        "expires": expires * 1000,
    }
    if isinstance(account, str) and account:
        record["accountId"] = account
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="auth.", dir=target.parent)
    try:
        with os.fdopen(fd, "w") as out:
            json.dump({"openai": record}, out, separators=(",", ":"))
        os.chmod(temporary, 0o600)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {"provider": "openai", "auth_type": "oauth", "created": True}


def _token(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"OpenCode usage {field} must be a non-negative integer")
    return value


def _empty_usage() -> dict[str, int]:
    return {
        "fresh_input_tokens": 0,
        "cached_input_tokens": 0,
        "cache_write_tokens": 0,
        "output_tokens": 0,
        "reasoning_tokens": 0,
        "total_provider_tokens": 0,
    }


def step_usage(part: dict[str, Any]) -> dict[str, int]:
    tokens = part.get("tokens")
    if not isinstance(tokens, dict):
        raise ValueError("OpenCode step_finish part is missing usage tokens")
    cache = tokens.get("cache")
    if not isinstance(cache, dict):
        raise ValueError("OpenCode step_finish part is missing cache usage")
    fresh = _token(tokens.get("input"), "input")
    output = _token(tokens.get("output"), "output")
    reasoning = _token(tokens.get("reasoning"), "reasoning")
    cached = _token(cache.get("read"), "cache.read")
    cache_write = _token(cache.get("write"), "cache.write")
    total = fresh + cached + cache_write + output + reasoning
    declared_total = tokens.get("total")
    if declared_total is not None and _token(declared_total, "total") != total:
        raise ValueError(
            f"OpenCode usage total does not match components: {declared_total} != {total}"
        )
    return {
        "fresh_input_tokens": fresh,
        "cached_input_tokens": cached,
        "cache_write_tokens": cache_write,
        "output_tokens": output + reasoning,
        "reasoning_tokens": reasoning,
        "total_provider_tokens": total,
    }


def _add_usage(target: dict[str, int], increment: dict[str, int]) -> None:
    for key in target:
        target[key] += increment[key]


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "sessions": {}}
    value = json.loads(path.read_text())
    if not isinstance(value, dict) or value.get("schema_version") != 1 or not isinstance(value.get("sessions"), dict):
        raise ValueError("OpenCode cumulative usage state is invalid")
    return value


def _write_state(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="usage.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as out:
            json.dump(value, out, indent=2)
            out.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def normalize_events(
    events: list[dict[str, Any]],
    *,
    requested_session_id: str | None,
    state_path: Path,
) -> NormalizedRun:
    session_ids = {
        str(event["sessionID"])
        for event in events
        if isinstance(event.get("sessionID"), str) and event.get("sessionID")
    }
    if requested_session_id is not None:
        if session_ids and session_ids != {requested_session_id}:
            raise ValueError(
                f"OpenCode session continuity mismatch: requested {requested_session_id}, observed {sorted(session_ids)}"
            )
        session_id = requested_session_id
    else:
        if len(session_ids) != 1:
            raise ValueError(f"OpenCode event stream did not identify exactly one session: {sorted(session_ids)}")
        session_id = next(iter(session_ids))

    state = _load_state(state_path)
    sessions = state["sessions"]
    existing = sessions.get(session_id, {})
    cumulative = existing.get("usage", _empty_usage())
    if not isinstance(cumulative, dict) or set(cumulative) != set(_empty_usage()):
        raise ValueError("OpenCode cumulative session usage shape is invalid")
    cumulative = {key: _token(cumulative[key], key) for key in _empty_usage()}
    seen = set(existing.get("seen_step_part_ids", []))
    invocation_ids: set[str] = set()
    usage_events = 0
    last_text = ""

    normalized: list[dict[str, Any]] = [{"type": "thread.started", "thread_id": session_id}]
    for event in events:
        normalized.append({"type": "opencode.event", "event": event})
        if event.get("type") == "text":
            part = event.get("part")
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                last_text = str(part["text"])
        if event.get("type") != "step_finish":
            continue
        part = event.get("part")
        if not isinstance(part, dict) or part.get("type") != "step-finish":
            raise ValueError("OpenCode step_finish event has an invalid part")
        part_id = part.get("id")
        if not isinstance(part_id, str) or not part_id:
            raise ValueError("OpenCode step_finish event is missing part identity")
        if part_id in seen or part_id in invocation_ids:
            continue
        increment = step_usage(part)
        _add_usage(cumulative, increment)
        invocation_ids.add(part_id)
        usage_events += 1

    if usage_events == 0:
        raise ValueError("OpenCode event stream contains no new provider usage")
    seen.update(invocation_ids)
    sessions[session_id] = {
        "usage": cumulative,
        "seen_step_part_ids": sorted(seen),
    }
    _write_state(state_path, state)
    normalized.append(
        {
            "type": "turn.completed",
            "usage": {
                "input_tokens": cumulative["fresh_input_tokens"]
                + cumulative["cached_input_tokens"]
                + cumulative["cache_write_tokens"],
                "cached_input_tokens": cumulative["cached_input_tokens"],
                "cache_write_tokens": cumulative["cache_write_tokens"],
                "output_tokens": cumulative["output_tokens"],
                "reasoning_output_tokens": cumulative["reasoning_tokens"],
                "total_tokens": cumulative["total_provider_tokens"],
            },
        }
    )
    return NormalizedRun(
        session_id=session_id,
        usage=cumulative,
        last_text=last_text,
        normalized_events=normalized,
    )


def _read_prompt(parsed: CompatArgs) -> str:
    if parsed.prompt_from_stdin:
        prompt = sys.stdin.read()
    else:
        prompt = parsed.prompt or ""
    if not prompt.strip():
        raise ValueError("OpenCode prompt is empty")
    return prompt


def _runtime_env(
    codex_home: Path,
    *,
    treatment: str = "bare",
    directory: Path | None = None,
) -> tuple[dict[str, str], Path]:
    if treatment not in TREATMENT_PROFILES:
        raise ValueError(f"unsupported OpenCode treatment profile: {treatment}")
    env = os.environ.copy()
    xdg_data = Path(env.get("XDG_DATA_HOME", codex_home / "xdg-data"))
    xdg_config = Path(env.get("XDG_CONFIG_HOME", codex_home / "xdg-config"))
    xdg_cache = Path(env.get("XDG_CACHE_HOME", codex_home / "xdg-cache"))
    xdg_state = Path(env.get("XDG_STATE_HOME", codex_home / "xdg-state"))
    for path in (xdg_data, xdg_config, xdg_cache, xdg_state):
        path.mkdir(parents=True, exist_ok=True)
    config: dict[str, Any] = {
        "share": "disabled",
        "autoupdate": False,
        "shell": "/usr/local/bin/eval-network-denied-shell",
        "permission": {
            "webfetch": "deny",
            "websearch": "deny",
            "task": "deny",
            "skill": "deny",
            "lsp": "deny",
            "question": "deny",
            "external_directory": "deny",
        },
    }
    if treatment == "snip":
        config["plugin"] = [
            "file:///opt/data/tool-candidates/opencode-snip-v1.6.1/.opencode/plugins/index.ts"
        ]
    elif treatment == "serena":
        config["mcp"] = {
            "serena": {
                "type": "local",
                "command": [
                    str(UV_BINARY),
                    "tool",
                    "run",
                    "--from",
                    str(SERENA_ROOT),
                    "serena",
                    "start-mcp-server",
                    "--project-from-cwd",
                    "--context=ide",
                    "--enable-web-dashboard",
                    "false",
                    "--open-web-dashboard",
                    "false",
                ],
                "environment": {"SERENA_HOME": str(xdg_state / "serena")},
                "enabled": True,
            }
        }
    elif treatment == "cartog":
        config["mcp"] = {
            "cartog": {
                "type": "local",
                "command": [str(CARTOG_BINARY), "serve", "--watch"],
                "environment": {
                    "CARTOG_MCP_COMPACT": "1",
                    "CARTOG_NO_UPDATE_CHECK": "1",
                },
                "enabled": True,
            }
        }
    env.update(
        {
            "XDG_DATA_HOME": str(xdg_data),
            "XDG_CONFIG_HOME": str(xdg_config),
            "XDG_CACHE_HOME": str(xdg_cache),
            "XDG_STATE_HOME": str(xdg_state),
            "OPENCODE_DISABLE_AUTOUPDATE": "1",
            "OPENCODE_DISABLE_MODELS_FETCH": "1",
            "OPENCODE_DISABLE_PROJECT_CONFIG": "1",
            "OPENCODE_DISABLE_EXTERNAL_SKILLS": "1",
            "OPENCODE_DISABLE_LSP_DOWNLOAD": "1",
            "OPENCODE_DISABLE_CLAUDE_CODE": "1",
            "OPENCODE_TREATMENT_PROFILE": treatment,
            "OPENCODE_CONFIG_CONTENT": json.dumps(config, separators=(",", ":")),
        }
    )
    if directory is not None:
        env["OPENCODE_EVALUATION_DIRECTORY"] = str(directory)
    return env, xdg_data


def probe(
    binary: Path,
    codex_home: Path,
    binary_sha256: str,
    *,
    treatment: str = "bare",
) -> int:
    env, xdg_data = _runtime_env(codex_home, treatment=treatment)
    ensure_opencode_auth(codex_home / "auth.json", xdg_data)
    version = subprocess.run([str(binary), "--version"], env=env, text=True, capture_output=True, timeout=60)
    if version.returncode != 0:
        sys.stderr.write(version.stderr)
        return version.returncode
    models = subprocess.run([str(binary), "models", "openai"], env=env, text=True, capture_output=True, timeout=120)
    available = {line.strip() for line in models.stdout.splitlines() if line.strip()}
    plugin_proof: dict[str, Any] | None = None
    if treatment in PLUGIN_TREATMENTS:
        plugin_info = subprocess.run(
            [str(binary), "debug", "info"],
            env=env,
            text=True,
            capture_output=True,
            timeout=120,
        )
        if plugin_info.returncode != 0:
            raise RuntimeError(f"OpenCode plugin probe failed: {plugin_info.stderr.strip()}")
        expected_plugin = "tokenjuice.js" if treatment == "tokenjuice" else "opencode-snip-v1.6.1"
        if expected_plugin not in plugin_info.stdout:
            raise RuntimeError(
                f"OpenCode {treatment} plugin was not visible in debug info: {plugin_info.stdout.strip()}"
            )
        plugin_proof = {"expected": expected_plugin, "loaded": True}
    result = {
        "runtime": "opencode-cli",
        "version": version.stdout.strip(),
        "binary": str(binary),
        "binary_sha256": binary_sha256,
        "treatment": treatment,
        "model_available": "openai/gpt-5.6-sol" in available,
        "project_config_disabled": True,
        "external_plugins_disabled_by_pure_flag": treatment not in PLUGIN_TREATMENTS,
        "external_skills_disabled": True,
        "web_tools_permission": "deny",
        "subagents_permission": "deny",
        "plugin_assignment": plugin_proof,
        "auth": {"provider": "openai", "auth_type": "oauth"},
    }
    print(json.dumps(result, indent=2))
    return 0 if models.returncode == 0 and result["model_available"] else 1


def validate_non_json_stdout(treatment: str, lines: list[str]) -> None:
    if lines and treatment != "headroom":
        raise ValueError(f"OpenCode emitted non-JSON stdout in JSON mode: {lines[:3]}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--opencode-binary", type=Path, default=DEFAULT_OPENCODE_BINARY)
    parser.add_argument("--expected-opencode-sha256", required=True)
    parser.add_argument("--treatment", choices=sorted(TREATMENT_PROFILES), default="bare")
    parser.add_argument("--probe", action="store_true")
    known, remaining = parser.parse_known_args(argv)
    codex_home = Path(os.environ.get("CODEX_HOME", ""))
    if not str(codex_home):
        raise ValueError("CODEX_HOME is required for isolated OpenCode execution")
    try:
        binary_sha256 = verify_binary_sha256(
            known.opencode_binary,
            str(known.expected_opencode_sha256),
        )
    except ValueError as exc:
        parser.error(str(exc))
    if known.probe:
        if remaining:
            raise ValueError("--probe does not accept Codex compatibility arguments")
        return probe(
            known.opencode_binary,
            codex_home,
            binary_sha256,
            treatment=known.treatment,
        )

    parsed = parse_codex_exec_args(remaining)
    prompt = _read_prompt(parsed)
    directory = parsed.directory or Path.cwd()
    env, xdg_data = _runtime_env(
        codex_home,
        treatment=known.treatment,
        directory=directory,
    )
    ensure_opencode_auth(codex_home / "auth.json", xdg_data)
    native_command = build_opencode_command(
        known.opencode_binary,
        parsed,
        prompt,
        pure=known.treatment not in PLUGIN_TREATMENTS,
    )
    command = native_command
    if known.treatment == "headroom":
        runtime_bin = xdg_data / "opencode" / "runtime-bin"
        runtime_bin.mkdir(parents=True, exist_ok=True)
        opencode_link = runtime_bin / "opencode"
        if opencode_link.exists() or opencode_link.is_symlink():
            opencode_link.unlink()
        opencode_link.symlink_to(known.opencode_binary)
        env["PATH"] = f"{runtime_bin}:{env.get('PATH', '')}"
        port = 18000 + int(hashlib.sha256(str(directory).encode()).hexdigest()[:4], 16) % 2000
        command = build_headroom_command(native_command, port=port)
    proc = subprocess.run(
        command,
        cwd=directory,
        env=env,
        text=True,
        capture_output=True,
    )
    events: list[dict[str, Any]] = []
    non_json: list[str] = []
    for line in proc.stdout.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            if line.strip():
                non_json.append(line[:500])
            continue
        if isinstance(value, dict):
            events.append(value)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        for event in events:
            print(json.dumps({"type": "opencode.event", "event": event}, ensure_ascii=False))
        return proc.returncode
    validate_non_json_stdout(known.treatment, non_json)
    result = normalize_events(
        events,
        requested_session_id=parsed.session_id,
        state_path=xdg_data / "opencode" / "workflow-usage-state.json",
    )
    parsed.last_message_path.parent.mkdir(parents=True, exist_ok=True)
    parsed.last_message_path.write_text(result.last_text + ("\n" if result.last_text else ""))
    for event in result.normalized_events:
        print(json.dumps(event, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
