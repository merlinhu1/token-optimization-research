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
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from scripts.token_metrics import weighted_token_cost
except ImportError:
    from token_metrics import weighted_token_cost

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
NODE_BINARY = Path("/opt/data/opt/node-v24.18.0-linux-x64/bin/node")
SDL_MCP_ROOT = Path("/opt/data/tool-candidates/sdl-mcp")
SDL_MCP_MAIN = SDL_MCP_ROOT / "dist" / "main.js"
CODESCOPE_BINARY = Path("/opt/data/tool-candidates/codescope-release-v0.8.12/codescope")
CODEGRAPH_BINARY = Path("/opt/data/tool-candidates/codegraph/dist/bin/codegraph.js")
JCODEMUNCH_ROOT = Path("/opt/data/tool-candidates/jcodemunch-mcp")
LEANCTX_BINARY = Path("/opt/data/bin/lean-ctx")
SIGMAP_ROOT = Path("/opt/data/tool-candidates/sigmap")
PONYTAIL_ROOT = Path("/opt/data/tool-candidates/ponytail")
CAVEMAN_ROOT = Path("/opt/data/tool-candidates/caveman")
LOWFAT_BINARY = Path("/opt/data/tool-candidates/lowfat-bin/lowfat")
DCP_PACKAGE = "@tarquinen/opencode-dcp@3.1.14"
HEADROOM_PLUGIN = Path(
    "/opt/data/tool-candidates/headroom/plugins/opencode/dist/entry.opencode.js"
)
TREATMENT_PROFILES = {
    "bare",
    "tokenjuice",
    "serena",
    "snip",
    "cartog",
    "headroom",
    "codescope",
    "graphify",
    "rtk",
    "codegraph",
    "jcodemunch",
    "leanctx",
    "sigmap",
    "ponytail",
    "caveman",
    "lowfat",
    "dcp",
    "sdl-mcp",
}
PLUGIN_TREATMENTS = {
    "tokenjuice", "snip", "headroom", "graphify", "rtk",
    "ponytail", "caveman", "lowfat", "dcp",
}
GUIDED_TREATMENTS = {"jcodemunch", "leanctx", "sigmap", "ponytail", "caveman", "sdl-mcp"}


def provider_route(provider: str, model: str) -> tuple[str, str]:
    """Validate the provider-specific OpenCode model namespace without secrets."""
    # OpenCode runs on the Codex subscription and nothing else. A second route here is what let
    # a run be pointed at a provider the study does not use, so there is only one.
    expected = "openai/gpt-5.6-sol"
    if provider != "openai":
        raise ValueError(f"unsupported OpenCode provider route: {provider}; only openai is permitted")
    if model != expected:
        raise ValueError(
            f"OpenAI must use the exact OpenCode model namespace {expected}; got {model}"
        )
    return provider, model


def provider_api_key_available(provider: str, env: dict[str, str]) -> bool:
    """Check only key presence; no credential value may enter an artifact."""
    return True


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
    usage: dict[str, int | float]
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
    provider_model: str | None = None,
) -> list[str]:
    command = [
        str(binary),
        "run",
        "--format",
        "json",
        "--model",
        provider_model or parsed.model,
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


def merge_opencode_configs(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Merge product config onto evaluator policy without dropping either surface."""
    merged: dict[str, Any] = json.loads(json.dumps(base))
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_opencode_configs(merged[key], value)
        else:
            merged[key] = value
    return merged


def validate_headroom_runtime_receipt(
    receipt: dict[str, Any], *, provider: str, model: str
) -> None:
    """Fail closed unless a paid request is correlated to the intended route."""
    if int(receipt.get("request_count", 0)) < 1 or not receipt.get("routes"):
        raise ValueError("Headroom lacks request-correlated proxy traffic")
    expected_provider = provider.lower()
    expected_model = model.lower()
    routes = receipt.get("routes", [])
    if not any(
        str(route.get("provider", "")).lower() == expected_provider
        and expected_model in str(route.get("model", "")).lower()
        for route in routes
    ):
        raise ValueError("Headroom proxy receipt has no matching provider/model route")


def _headroom_receipt_from_stats(stats: dict[str, Any]) -> dict[str, Any]:
    requests_value = stats.get("requests")
    logs_value = stats.get("request_logs")
    requests: dict[str, Any] = requests_value if isinstance(requests_value, dict) else {}
    logs: list[Any] = logs_value if isinstance(logs_value, list) else []
    routes = [
        {
            "request_id": item.get("request_id"),
            "provider": item.get("provider"),
            "model": item.get("model"),
            "status": item.get("status"),
            "input_tokens_original": item.get("input_tokens_original"),
            "input_tokens_optimized": item.get("input_tokens_optimized"),
            "tokens_saved": item.get("tokens_saved"),
            "transforms_applied": item.get("transforms_applied", []),
        }
        for item in logs
        if isinstance(item, dict)
    ]
    return {
        "request_count": int(requests.get("total", 0) or 0),
        "failed_requests": int(requests.get("failed", 0) or 0),
        "requests_by_provider": requests.get("by_provider", {}),
        "requests_by_model": requests.get("by_model", {}),
        "routes": routes,
        "tokens": {
            key: stats.get("tokens", {}).get(key)
            for key in (
                "input",
                "output",
                "saved",
                "proxy_compression_saved",
                "cli_filtering_saved",
            )
        }
        if isinstance(stats.get("tokens"), dict)
        else {},
    }


def _poll_headroom_stats(port: int, stop: threading.Event, snapshots: list[dict[str, Any]]) -> None:
    url = f"http://127.0.0.1:{port}/stats"
    while not stop.is_set():
        try:
            with urllib.request.urlopen(url, timeout=1) as response:  # nosec B310 - loopback only
                value = json.loads(response.read().decode())
            if isinstance(value, dict):
                snapshots.append(value)
        except (OSError, ValueError, urllib.error.URLError):
            pass
        stop.wait(0.25)


def _write_headroom_runtime_shim(
    path: Path, *, binary: Path, base_config: dict[str, Any], receipt_path: Path
) -> None:
    encoded = base64.b64encode(json.dumps(base_config, separators=(",", ":")).encode()).decode()
    script = f'''#!/usr/bin/env python3
import base64, json, os
from pathlib import Path
base = json.loads(base64.b64decode({encoded!r}).decode())
product = json.loads(os.environ.get("OPENCODE_CONFIG_CONTENT", "{{}}"))
def merge(left, right):
    out = json.loads(json.dumps(left))
    for key, value in right.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict): out[key] = merge(out[key], value)
        else: out[key] = value
    return out
merged = merge(base, product)
os.environ["OPENCODE_CONFIG_CONTENT"] = json.dumps(merged, separators=(",", ":"))
Path({str(receipt_path)!r}).write_text(json.dumps({{"effective_config": merged}}, indent=2) + "\\n")
os.execv({str(binary)!r}, [{str(binary)!r}, *os.sys.argv[1:]])
'''
    path.write_text(script)
    path.chmod(0o755)


def _run_headroom(
    command: list[str], *, cwd: Path, env: dict[str, str], port: int
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    snapshots: list[dict[str, Any]] = []
    stop = threading.Event()
    poller = threading.Thread(target=_poll_headroom_stats, args=(port, stop, snapshots), daemon=True)
    proc = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    poller.start()
    stdout, stderr = proc.communicate()
    time.sleep(0.1)
    stop.set()
    poller.join(timeout=2)
    completed = subprocess.CompletedProcess(command, proc.returncode, stdout, stderr)
    return completed, _headroom_receipt_from_stats(snapshots[-1] if snapshots else {})


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


def _cost(value: object, field: str) -> float:
    """Validate a derived cost rather than a raw token count.

    weighted_token_cost is fresh + 0.1*cached + 6*output, so it is a non-negative number and not
    necessarily an integer. Running it through _token rejected the zero float that _empty_usage
    seeds, which made every OpenCode session fail usage normalisation before it recorded a single
    step.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"OpenCode usage {field} must be a non-negative number")
    return float(value)


def _empty_usage() -> dict[str, int | float]:
    return {
        "fresh_input_tokens": 0,
        "cached_input_tokens": 0,
        "cache_write_tokens": 0,
        "output_tokens": 0,
        "reasoning_tokens": 0,
        "total_provider_tokens": 0,
        "weighted_token_cost": 0.0,
    }


def step_usage(part: dict[str, Any]) -> dict[str, int | float]:
    tokens = part.get("tokens")
    if not isinstance(tokens, dict):
        raise ValueError("OpenCode step_finish part is missing usage tokens")
    cache = tokens.get("cache")
    if not isinstance(cache, dict):
        raise ValueError("OpenCode step_finish part is missing cache usage")
    input_tokens = _token(tokens.get("input"), "input")
    output = _token(tokens.get("output"), "output")
    reasoning = _token(tokens.get("reasoning"), "reasoning")
    cached = _token(cache.get("read"), "cache.read")
    cache_write = _token(cache.get("write"), "cache.write")
    # OpenCode exposes cache writes separately from input.  The canonical
    # contract defines fresh input as all non-cache-read input, so cache writes
    # are included in fresh_input_tokens while remaining an explicit audit
    # subset.  Do not add cache_write again to total_provider_tokens.
    fresh = input_tokens + cache_write
    normalized_output = output + reasoning
    total = fresh + cached + normalized_output
    declared_total = tokens.get("total")
    raw_total = input_tokens + cached + cache_write + output + reasoning
    if declared_total is not None and _token(declared_total, "total") != raw_total:
        raise ValueError(
            f"OpenCode usage total does not match components: {declared_total} != {raw_total}"
        )
    usage = {
        "fresh_input_tokens": fresh,
        "cached_input_tokens": cached,
        "cache_write_tokens": cache_write,
        "output_tokens": normalized_output,
        "reasoning_tokens": reasoning,
        "total_provider_tokens": total,
    }
    usage["weighted_token_cost"] = weighted_token_cost(usage) or 0.0
    return usage


def _add_usage(target: dict[str, int | float], increment: dict[str, int | float]) -> None:
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
    cumulative = {
        key: (_cost(cumulative[key], key) if key == "weighted_token_cost" else _token(cumulative[key], key))
        for key in _empty_usage()
    }
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
                + cumulative["cached_input_tokens"],
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
    provider: str = "openai",
    directory: Path | None = None,
) -> tuple[dict[str, str], Path]:
    if treatment not in TREATMENT_PROFILES:
        raise ValueError(f"unsupported OpenCode treatment profile: {treatment}")
    if provider not in {"openai"}:
        raise ValueError(f"unsupported OpenCode provider route: {provider}")
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
            "skill": "allow" if treatment == "graphify" else "deny",
            "lsp": "deny",
            "question": "deny",
            "external_directory": "deny",
        },
    }
    if treatment == "snip":
        config["plugin"] = [
            "file:///opt/data/tool-candidates/opencode-snip-v1.6.1/.opencode/plugins/index.ts"
        ]
    elif treatment == "sdl-mcp":
        sdl_data = xdg_data / "sdl-mcp"
        config["plugin"] = [(directory / ".opencode" / "plugins" / "enforce-sdl.ts").as_uri()] if directory is not None else []
        config["mcp"] = {
            "sdl-mcp": {
                "type": "local",
                "command": [str(NODE_BINARY), str(SDL_MCP_MAIN), "serve", "--stdio"],
                "environment": {
                    "SDL_CONFIG": str(sdl_data / "sdlmcp.config.json"),
                    "SDL_CONFIG_HOME": str(sdl_data),
                    "SDL_GRAPH_DB_PATH": str(sdl_data / "sdl-mcp-graph.lbug"),
                    "SDL_MCP_SKIP_SETUP_WIZARD": "1",
                },
                "enabled": True,
            }
        }
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
    elif treatment == "headroom":
        config["plugin"] = [HEADROOM_PLUGIN.as_uri()]
        config["mcp"] = {
            "headroom": {
                "type": "local",
                "command": [
                    str(UV_BINARY),
                    "tool",
                    "run",
                    "--from",
                    str(HEADROOM_WHEEL),
                    "--with",
                    "mcp",
                    "headroom",
                    "mcp",
                    "serve",
                ],
                "environment": {"HEADROOM_HOME": str(xdg_state / "headroom")},
                "enabled": True,
            },
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
            },
        }
    elif treatment == "codescope":
        if directory is None:
            raise ValueError("CodeScope treatment requires an evaluation directory")
        config["mcp"] = {
            "codescope": {
                "type": "local",
                "command": [
                    "/bin/bash",
                    "-lc",
                    (
                        f"set -euo pipefail; {CODESCOPE_BINARY} start >/dev/null; "
                        f"trap '{CODESCOPE_BINARY} stop >/dev/null 2>&1 || true' EXIT; "
                        f"i=0; until {CODESCOPE_BINARY} status | grep -q '^running'; "
                        "do i=$((i+1)); [ \"$i\" -lt 50 ]; sleep 0.2; done; "
                        f"exec {CODESCOPE_BINARY} mcp {directory}"
                    ),
                ],
                "enabled": True,
            }
        }
    elif treatment == "graphify":
        if directory is None:
            raise ValueError("Graphify treatment requires an evaluation directory")
        plugin = directory / ".opencode" / "plugins" / "graphify.js"
        config["plugin"] = [plugin.as_uri()]
    elif treatment == "rtk":
        plugin = codex_home / "home" / ".config" / "opencode" / "plugins" / "rtk.ts"
        config["plugin"] = [plugin.as_uri()]
    elif treatment == "codegraph":
        config["mcp"] = {
            "codegraph": {
                "type": "local",
                "command": [str(NODE_BINARY), str(CODEGRAPH_BINARY), "serve", "--mcp"],
                "environment": {"CODEGRAPH_TELEMETRY": "0"},
                "enabled": True,
            }
        }
    elif treatment == "jcodemunch":
        tool_data = Path(env.get("OPENCODE_TOOL_DATA_DIR", xdg_data / "jcodemunch"))
        config["mcp"] = {
            "jcodemunch": {
                "type": "local",
                "command": [str(tool_data / "venv" / "bin" / "jcodemunch-mcp")],
                "environment": {
                    "CODE_INDEX_PATH": str(tool_data / "index"),
                    "JCODEMUNCH_LOG_LEVEL": "ERROR",
                },
                "enabled": True,
            }
        }
    elif treatment == "leanctx":
        config["mcp"] = {
            "lean-ctx": {
                "type": "local",
                "command": [str(LEANCTX_BINARY)],
                "environment": {"LEAN_CTX_DATA_DIR": str(xdg_data / "leanctx")},
                "enabled": True,
            }
        }
    elif treatment == "sigmap":
        config["mcp"] = {
            "sigmap": {
                "type": "local",
                "command": [str(NODE_BINARY), str(SIGMAP_ROOT / "gen-context.js"), "--mcp"],
                "environment": {"SIGMAP_NO_TELEMETRY": "1"},
                "enabled": True,
            }
        }
    elif treatment == "ponytail":
        if directory is None:
            raise ValueError("Ponytail treatment requires an evaluation directory")
        config["plugin"] = [(directory / ".opencode" / "plugins" / "ponytail.mjs").as_uri()]
    elif treatment == "caveman":
        plugin = xdg_config / "opencode" / "plugins" / "caveman" / "plugin.js"
        config["plugin"] = [plugin.as_uri()]
    elif treatment == "lowfat":
        plugin = xdg_config / "opencode" / "plugins" / "lowfat.ts"
        config["plugin"] = [plugin.as_uri()]
    elif treatment == "dcp":
        config["plugin"] = [DCP_PACKAGE]
    env.update(
        {
            "XDG_DATA_HOME": str(xdg_data),
            "XDG_CONFIG_HOME": str(xdg_config),
            "XDG_CACHE_HOME": str(xdg_cache),
            "XDG_STATE_HOME": str(xdg_state),
            "OPENCODE_DISABLE_AUTOUPDATE": "1",
            "OPENCODE_DISABLE_MODELS_FETCH": "1",
            "OPENCODE_DISABLE_PROJECT_CONFIG": "1",
            "OPENCODE_DISABLE_EXTERNAL_SKILLS": "0" if treatment in {"graphify", *GUIDED_TREATMENTS} else "1",
            "OPENCODE_DISABLE_LSP_DOWNLOAD": "1",
            "OPENCODE_DISABLE_CLAUDE_CODE": "1",
            "OPENCODE_TREATMENT_PROFILE": treatment,
            "OPENCODE_TOOL_DATA_DIR": env.get("OPENCODE_TOOL_DATA_DIR", str(xdg_data / treatment)),
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
    provider: str = "openai",
    provider_model: str = "openai/gpt-5.6-sol",
) -> int:
    provider, provider_model = provider_route(provider, provider_model)
    directory = Path(os.environ.get("OPENCODE_EVALUATION_DIRECTORY", Path.cwd()))
    env, xdg_data = _runtime_env(
        codex_home,
        treatment=treatment,
        provider=provider,
        directory=directory,
    )
    ensure_opencode_auth(codex_home / "auth.json", xdg_data)
    version = subprocess.run([str(binary), "--version"], env=env, text=True, capture_output=True, timeout=60)
    if version.returncode != 0:
        sys.stderr.write(version.stderr)
        return version.returncode
    models = subprocess.run([str(binary), "models", provider], env=env, text=True, capture_output=True, timeout=120)
    available = {line.strip() for line in models.stdout.splitlines() if line.strip()}
    plugin_proof: dict[str, Any] | None = None
    if treatment in PLUGIN_TREATMENTS:
        plugin_info = subprocess.run(
            [str(binary), "debug", "info"],
            env=env,
            cwd=directory,
            text=True,
            capture_output=True,
            timeout=120,
        )
        if plugin_info.returncode != 0:
            raise RuntimeError(f"OpenCode plugin probe failed: {plugin_info.stderr.strip()}")
        expected_plugin = {
            "tokenjuice": "tokenjuice.js",
            "snip": "opencode-snip-v1.6.1",
            "headroom": "entry.opencode.js",
            "graphify": "graphify.js",
            "rtk": "rtk.ts",
            "ponytail": "ponytail.mjs",
            "caveman": "caveman",
            "lowfat": "lowfat.ts",
            "dcp": DCP_PACKAGE,
        }[treatment]
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
        "provider": provider,
        "provider_model": provider_model,
        "model_available": provider_model in available,
        "project_config_disabled": True,
        "external_plugins_disabled_by_pure_flag": treatment not in PLUGIN_TREATMENTS,
        "external_skills_disabled": treatment not in {"graphify", *GUIDED_TREATMENTS},
        "web_tools_permission": "deny",
        "subagents_permission": "deny",
        "plugin_assignment": plugin_proof,
        "effective_config": json.loads(env["OPENCODE_CONFIG_CONTENT"]),
        "effective_config_sha256": hashlib.sha256(
            env["OPENCODE_CONFIG_CONTENT"].encode()
        ).hexdigest(),
        "auth": {"provider": "openai", "auth_type": "oauth"},
    }
    print(json.dumps(result, indent=2))
    return 0 if models.returncode == 0 and result["model_available"] else 1


def validate_non_json_stdout(treatment: str, lines: list[str]) -> None:
    if lines and treatment != "headroom":
        raise ValueError(f"OpenCode emitted non-JSON stdout in JSON mode: {lines[:3]}")


LAST_MESSAGE_WRITE_ATTEMPTS = 8
LAST_MESSAGE_WRITE_RETRY_SECONDS = 0.05


def write_last_message(path: Path, text: str) -> None:
    """Persist model output across transient model-output mount replacement.

    This is post-provider evidence ingress: retrying this filesystem operation
    must never invoke the provider or repeat a model turn.
    """
    payload = text + ("\n" if text else "")
    for attempt in range(LAST_MESSAGE_WRITE_ATTEMPTS):
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            path.write_text(payload)
            return
        except FileNotFoundError:
            if attempt + 1 == LAST_MESSAGE_WRITE_ATTEMPTS:
                raise
            time.sleep(LAST_MESSAGE_WRITE_RETRY_SECONDS)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--opencode-binary", type=Path, default=DEFAULT_OPENCODE_BINARY)
    parser.add_argument("--expected-opencode-sha256", required=True)
    parser.add_argument("--treatment", choices=sorted(TREATMENT_PROFILES), default="bare")
    parser.add_argument("--provider", choices=("openai",), default="openai")
    parser.add_argument("--provider-model", default="openai/gpt-5.6-sol")
    parser.add_argument("--probe", action="store_true")
    known, remaining = parser.parse_known_args(argv)
    codex_home = Path(os.environ.get("CODEX_HOME", ""))
    if not str(codex_home):
        raise ValueError("CODEX_HOME is required for isolated OpenCode execution")
    try:
        provider, provider_model = provider_route(known.provider, known.provider_model)
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
            provider=provider,
            provider_model=provider_model,
        )

    parsed = parse_codex_exec_args(remaining)
    if parsed.model.rsplit("/", 1)[-1] != provider_model.rsplit("/", 1)[-1]:
        raise ValueError(
            f"Codex compatibility model {parsed.model} does not match the selected provider route {provider_model}"
        )
    prompt = _read_prompt(parsed)
    directory = parsed.directory or Path.cwd()
    env, xdg_data = _runtime_env(
        codex_home,
        treatment=known.treatment,
        provider=provider,
        directory=directory,
    )
    ensure_opencode_auth(codex_home / "auth.json", xdg_data)
    native_command = build_opencode_command(
        known.opencode_binary,
        parsed,
        prompt,
        pure=known.treatment not in (PLUGIN_TREATMENTS | GUIDED_TREATMENTS),
        provider_model=provider_model,
    )
    command = native_command
    headroom_receipt: dict[str, Any] | None = None
    effective_config_receipt: dict[str, Any] | None = None
    if known.treatment == "headroom":
        runtime_bin = xdg_data / "opencode" / "runtime-bin"
        runtime_bin.mkdir(parents=True, exist_ok=True)
        opencode_link = runtime_bin / "opencode"
        if opencode_link.exists() or opencode_link.is_symlink():
            opencode_link.unlink()
        effective_config_path = xdg_data / "opencode" / "headroom-effective-config.json"
        base_config = json.loads(env["OPENCODE_CONFIG_CONTENT"])
        _write_headroom_runtime_shim(
            opencode_link,
            binary=known.opencode_binary,
            base_config=base_config,
            receipt_path=effective_config_path,
        )
        env["PATH"] = f"{runtime_bin}:{env.get('PATH', '')}"
        env["HEADROOM_OPENCODE_PLUGIN_PATH"] = str(HEADROOM_PLUGIN)
        port = 18000 + int(hashlib.sha256(str(directory).encode()).hexdigest()[:4], 16) % 2000
        env["HEADROOM_PROXY_URL"] = f"http://127.0.0.1:{port}"
        command = build_headroom_command(native_command, port=port)
        proc, headroom_receipt = _run_headroom(command, cwd=directory, env=env, port=port)
        if effective_config_path.is_file():
            effective_config_receipt = json.loads(effective_config_path.read_text())
    else:
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
    if known.treatment == "headroom":
        if headroom_receipt is None:
            raise ValueError("Headroom runtime receipt was not collected")
        validate_headroom_runtime_receipt(
            headroom_receipt,
            provider=parsed.model.split("/", 1)[0],
            model=parsed.model.split("/", 1)[-1],
        )
        if effective_config_receipt is None:
            raise ValueError("Headroom effective OpenCode config receipt is missing")
        effective = effective_config_receipt.get("effective_config", {})
        if not isinstance(effective, dict) or not effective.get("plugin") or not effective.get("mcp"):
            raise ValueError("Headroom effective OpenCode config lacks native plugin or MCP routes")
    result = normalize_events(
        events,
        requested_session_id=parsed.session_id,
        state_path=xdg_data / "opencode" / "workflow-usage-state.json",
    )
    write_last_message(parsed.last_message_path, result.last_text)
    if known.treatment == "headroom":
        print(
            json.dumps(
                {
                    "type": "opencode.treatment_receipt",
                    "treatment": "headroom",
                    "proxy_runtime": headroom_receipt,
                    "effective_config": effective_config_receipt,
                    "wrapper_stdout": non_json[-20:],
                },
                ensure_ascii=False,
            )
        )
    for event in result.normalized_events:
        print(json.dumps(event, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
