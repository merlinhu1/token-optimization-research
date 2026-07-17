#!/usr/bin/env python3
"""Run a Codex fixture evaluation with deterministic per-lane tool isolation.

This runner is intentionally stricter than prompt-only isolation. It creates a
fresh CODEX_HOME for the active profile, writes only the allowed Codex config for
that lane, preflights MCP visibility, captures raw Codex artifacts, and audits
for forbidden tool surfaces before a run can be accepted.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CODEX_HOME_ROOT = Path("/opt/data/eval-codex-homes")
DEFAULT_SOURCE_CODEX_HOME = Path("/opt/data/home/.codex")
DEFAULT_DOCKER_IMAGE = "token-eval-codex:latest"
DEFAULT_DOCKERFILE = ROOT / "sources" / "evaluations" / "fixtures" / "container" / "Dockerfile"
MODEL_NETWORK_DENIED_SHELL = "/usr/local/bin/eval-network-denied-shell"
MODEL_NETWORK_DENIED_BIN = "/opt/data/model-network-bin"
CODEX_RUNTIME_ROOT = Path(os.environ.get(
    "TOKEN_EVAL_CODEX_RUNTIME_ROOT",
    "/opt/data/.local/lib/node_modules/@openai/codex",
))
CODEX_HOST_EXECUTABLE = Path(os.environ.get("TOKEN_EVAL_CODEX_EXECUTABLE", "/opt/data/.local/bin/codex"))
CODEX_CONTAINER_RUNTIME_ROOT = Path("/opt/data/codex-runtime")
CODEX_CONTAINER_BIN_ROOT = Path("/opt/data/codex-entry")
FORBIDDEN_BASELINE_TERMS = [
    "lean-ctx",
    "mcp_lean_ctx",
    "ctx_read",
    "ctx_search",
    "ctx_shell",
    "ctx_graph",
    "codegraph",
    "serena",
    "graphify",
    "graphify-mcp",
    "headroom",
    "headroom_retrieve",
    "token-savior",
    "token_savior",
    "rtk",
    "ponytail",
    "lowfat",
    "tokenjuice",
    "repomix",
    "mex",
    "cavemem",
    "cartog",
    "codescope",
    "swarmvault",
    "sigmap",
    "jcodemunch",
    "jcodemunch-mcp",
    "snip",
    "lowfat",
    "tokenjuice",
    "caveman",
]
BASELINE_CODEX_NO_MCP_PROFILES = {"baseline-codex-no-mcp"}
PROFILE_TOOL_CONFIG_OVERRIDES = {
    "headroom-default-codex": "headroom",
    "terminal-headroom": "headroom-proxy-only",
}
CODEGRAPH_BIN = Path("/opt/data/tool-candidates/codegraph/dist/bin/codegraph.js")
CARTOG_ROOT = Path("/opt/data/tool-candidates/cartog")
CARTOG_BIN = CARTOG_ROOT / "target" / "release" / "cartog"
CODESCOPE_RELEASE_ROOT = Path("/opt/data/tool-candidates/codescope-release-v0.8.12")
CODESCOPE_BIN = CODESCOPE_RELEASE_ROOT / "codescope"
CODESCOPE_SURREAL_BIN = CODESCOPE_RELEASE_ROOT / "surreal"
CODESCOPE_NEUTRAL_MCP_SOURCE = ROOT / "scripts" / "run_codescope_neutral_mcp.py"
CODESCOPE_NEUTRAL_MCP = Path("/opt/data/tool-candidates/codescope-adapter/run_codescope_neutral_mcp.py")
SWARMVAULT_ROOT = Path("/opt/data/tool-candidates/swarmvault")
SWARMVAULT_CLI = SWARMVAULT_ROOT / "packages" / "cli" / "dist" / "index.js"
SERENA_ROOT = Path("/opt/data/tool-candidates/serena")
TOKEN_SAVIOR_ROOT = Path("/opt/data/tool-candidates/token-savior")
GRAPHIFY_ROOT = Path("/opt/data/tool-candidates/graphify")
SIGMAP_ROOT = Path("/opt/data/tool-candidates/sigmap")
JCODEMUNCH_ROOT = Path("/opt/data/tool-candidates/jcodemunch-mcp")
SNIP_ROOT = Path("/opt/data/tool-candidates/snip")
LOWFAT_ROOT = Path("/opt/data/tool-candidates/lowfat")
LOWFAT_BIN = Path("/opt/data/tool-candidates/lowfat-bin/lowfat")
TOKENJUICE_ROOT = Path("/opt/data/tool-candidates/tokenjuice")
TOKENJUICE_BIN = TOKENJUICE_ROOT / "bin" / "tokenjuice"
CAVEMAN_ROOT = Path("/opt/data/tool-candidates/caveman")
HEADROOM_ROOT = Path("/opt/data/tool-candidates/headroom")
HEADROOM_WHEEL = HEADROOM_ROOT / "dist" / "headroom_ai-0.28.0-cp310-abi3-linux_x86_64.whl"
TOKEN_SAVIOR_WHEEL = TOKEN_SAVIOR_ROOT / "dist" / "token_savior_recall-4.4.1-py3-none-any.whl"
GRAPHIFY_WHEEL = GRAPHIFY_ROOT / "dist" / "graphifyy-0.9.1-py3-none-any.whl"
JCODEMUNCH_WHEEL = JCODEMUNCH_ROOT / "dist" / "jcodemunch_mcp-1.108.114-py3-none-any.whl"
SNIP_BIN = SNIP_ROOT / "snip"
UV_BIN = Path("/opt/data/opt/uv/uv")
RTK_BIN = Path("/opt/data/tool-candidates/rtk/target/release/rtk")
PONYTAIL_ROOT = Path("/opt/data/ponytail")
NODE_TOOLCHAIN_ROOT = Path("/opt/data/opt/node-v24.18.0-linux-x64")

TOOL_CONFIGS: dict[str, dict[str, Any]] = {
    "lean-ctx": {
        "display_name": "LeanCTX",
        "lane_name": "retrieval-leanctx",
        "surface": "retrieval/context",
        "mcp_server": "lean-ctx",
        "allowed_terms": ["lean-ctx", "mcp_lean_ctx", "ctx_read", "ctx_search", "ctx_shell", "ctx_graph"],
        "data_dir_name": "lean-ctx",
        "mcp_command": "/opt/data/bin/lean-ctx",
        "mcp_args": [],
        "env": {"LEAN_CTX_DATA_DIR": "{tool_data_dir}"},
        "mounts": ["/opt/data/bin"],
        "warmup": {
            "kind": "index",
            "command": ["/opt/data/bin/lean-ctx", "index", "build", "{repo}"],
            "output_name": "lean-ctx-warmup-output.txt",
            "metadata_name": "lean-ctx-warmup-metadata.json",
        },
    },
    "codegraph": {
        "display_name": "CodeGraph",
        "lane_name": "retrieval-codegraph",
        "surface": "retrieval/context",
        "mcp_server": "codegraph",
        "allowed_terms": ["codegraph"],
        "data_dir_name": "codegraph",
        "mcp_command": str(CODEGRAPH_BIN),
        "mcp_args": ["serve", "--mcp", "--no-watch"],
        "env": {"CODEGRAPH_TELEMETRY": "0"},
        "mounts": ["/opt/data/tool-candidates/codegraph"],
        "warmup": {
            "kind": "index",
            "command": [str(CODEGRAPH_BIN), "init", "{repo}"],
            "cleanup_paths": [".codegraph"],
            "output_name": "codegraph-warmup-output.txt",
            "metadata_name": "codegraph-warmup-metadata.json",
        },
    },
    "cartog": {
        "display_name": "Cartog",
        "lane_name": "retrieval-cartog",
        "surface": "retrieval/context",
        "mcp_server": "cartog",
        "allowed_terms": ["cartog"],
        "data_dir_name": "cartog",
        "mcp_command": "/bin/bash",
        "mcp_args": [
            "-lc",
            "cd {repo} && exec /opt/data/tool-candidates/cartog/target/release/cartog serve",
        ],
        "env": {
            "CARTOG_AUTO_INIT": "1",
            "CARTOG_MCP_COMPACT": "1",
        },
        "mounts": [str(CARTOG_ROOT)],
        "diff_exclude_paths": [".cartog"],
        "preflight_command": [str(CARTOG_BIN), "--version"],
        "default_tool_state": "warm-index",
        "warmup": {
            "kind": "code-graph-build",
            "command": [str(CARTOG_BIN), "index", "{repo}"],
            "cleanup_paths": [".cartog"],
            "output_name": "cartog-warmup-output.txt",
            "metadata_name": "cartog-warmup-metadata.json",
            "timeout_seconds": 1200,
        },
    },
    "codescope": {
        "display_name": "CodeScope",
        "lane_name": "codescope-owner",
        "surface": "broad-context-owner/mcp",
        "mcp_server": "codescope",
        "allowed_terms": ["codescope"],
        "data_dir_name": "codescope",
        "mcp_command": "python3",
        "mcp_args": [
            str(CODESCOPE_NEUTRAL_MCP),
            "{repo}",
            "--codescope-bin",
            str(CODESCOPE_BIN),
        ],
        "path_entries": [str(CODESCOPE_RELEASE_ROOT)],
        "mounts": [
            str(CODESCOPE_NEUTRAL_MCP),
            str(CODESCOPE_BIN),
            str(CODESCOPE_SURREAL_BIN),
        ],
        "preflight_command": [str(CODESCOPE_BIN), "--version"],
        "default_tool_state": "cold-auto-index",
        "initialize_instructions_policy": "strip-mandatory-uptake-text",
    },
    "swarmvault": {
        "display_name": "SwarmVault",
        "lane_name": "swarmvault-owner",
        "surface": "broad-context-owner/mcp",
        "mcp_server": "swarmvault",
        "allowed_terms": ["swarmvault"],
        "data_dir_name": "swarmvault",
        "mcp_command": "/bin/bash",
        "mcp_args": [
            "-lc",
            f"cd {{tool_data_dir}}/workspace && exec {NODE_TOOLCHAIN_ROOT}/bin/node {SWARMVAULT_CLI} mcp",
        ],
        "env": {
            "SWARMVAULT_OUT": ".swarmvault",
            "SWARMVAULT_NO_NOTICES": "1",
        },
        "mounts": [str(SWARMVAULT_ROOT)],
        "preflight_command": [str(NODE_TOOLCHAIN_ROOT / "bin" / "node"), str(SWARMVAULT_CLI), "--version"],
        "default_tool_state": "warm-index",
        "warmup": {
            "kind": "knowledge-graph-build",
            "command": [
                "/bin/bash",
                "-lc",
                (
                    f"set -euo pipefail; mkdir -p {{tool_data_dir}}/workspace; cd {{tool_data_dir}}/workspace; "
                    f"{NODE_TOOLCHAIN_ROOT}/bin/node {SWARMVAULT_CLI} init --lite; "
                    f"{NODE_TOOLCHAIN_ROOT}/bin/node {SWARMVAULT_CLI} ingest {{repo}} --max-files 500; "
                    f"{NODE_TOOLCHAIN_ROOT}/bin/node {SWARMVAULT_CLI} compile"
                ),
            ],
            "output_name": "swarmvault-warmup-output.txt",
            "metadata_name": "swarmvault-warmup-metadata.json",
            "timeout_seconds": 3600,
        },
    },
    "serena": {
        "display_name": "Serena",
        "lane_name": "retrieval-serena",
        "surface": "retrieval/context",
        "mcp_server": "serena",
        "allowed_terms": ["serena"],
        "data_dir_name": "serena",
        "mcp_command": str(UV_BIN),
        "mcp_args": [
            "tool",
            "run",
            "--from",
            str(SERENA_ROOT),
            "serena",
            "start-mcp-server",
            "--transport",
            "stdio",
            "--context",
            "codex",
            "--mode",
            "no-onboarding",
            "--mode",
            "no-memories",
            "--project",
            "{repo}",
            "--enable-web-dashboard",
            "false",
            "--open-web-dashboard",
            "false",
        ],
        "env": {"SERENA_HOME": "{tool_data_dir}"},
        "mounts": [str(SERENA_ROOT)],
    },
    "graphify": {
        "display_name": "Graphify",
        "lane_name": "retrieval-graphify",
        "surface": "retrieval/context",
        "mcp_server": "graphify",
        "allowed_terms": ["graphify", "graphify-mcp"],
        "data_dir_name": "graphify",
        "mcp_command": str(UV_BIN),
        "mcp_args": [
            "tool",
            "run",
            "--from",
            str(GRAPHIFY_WHEEL),
            "--with",
            "mcp",
            "graphify-mcp",
            "--graph",
            "{repo}/graphify-out/graph.json",
            "--transport",
            "stdio",
        ],
        "env": {"GRAPHIFY_OUT": "graphify-out"},
        "mounts": [str(GRAPHIFY_ROOT)],
        "default_tool_state": "warm-index",
        "warmup": {
            "kind": "code-graph-build",
            "command": [
                str(UV_BIN),
                "tool",
                "run",
                "--from",
                str(GRAPHIFY_WHEEL),
                "--with",
                "mcp",
                "graphify",
                "update",
                "{repo}",
                "--no-cluster",
                "--force",
            ],
            "cleanup_paths": ["graphify-out"],
            "output_name": "graphify-warmup-output.txt",
            "metadata_name": "graphify-warmup-metadata.json",
            "timeout_seconds": 1200,
        },
    },

    "sigmap": {
        "display_name": "SigMap",
        "lane_name": "retrieval-sigmap",
        "surface": "retrieval/context",
        "mcp_server": "sigmap",
        "allowed_terms": ["sigmap", "gen-context"],
        "data_dir_name": "sigmap",
        "mcp_command": "/bin/bash",
        "mcp_args": [
            "-lc",
            "cd {repo} && exec /opt/data/opt/node-v24.18.0-linux-x64/bin/node /opt/data/tool-candidates/sigmap/gen-context.js --mcp",
        ],
        "env": {"SIGMAP_TELEMETRY": "0"},
        "mounts": [str(SIGMAP_ROOT)],
        "default_tool_state": "warm-index",
        "warmup": {
            "kind": "signature-map-build",
            "command": [
                str(NODE_TOOLCHAIN_ROOT / "bin" / "node"),
                str(SIGMAP_ROOT / "gen-context.js"),
                "--adapter",
                "codex",
                "--no-track",
            ],
            "cleanup_paths": [".context"],
            "output_name": "sigmap-warmup-output.txt",
            "metadata_name": "sigmap-warmup-metadata.json",
            "timeout_seconds": 900,
        },
    },
    "jcodemunch-mcp": {
        "display_name": "jcodemunch MCP",
        "lane_name": "retrieval-jcodemunch-mcp",
        "surface": "retrieval/context",
        "mcp_server": "jcodemunch",
        "allowed_terms": ["jcodemunch", "jcodemunch-mcp"],
        "data_dir_name": "jcodemunch-mcp",
        "mcp_command": "/bin/bash",
        "mcp_args": [
            "-lc",
            "cd {repo} && exec /opt/data/opt/uv/uv tool run --from /opt/data/tool-candidates/jcodemunch-mcp/dist/jcodemunch_mcp-1.108.114-py3-none-any.whl jcodemunch-mcp serve --transport stdio --log-level ERROR",
        ],
        "env": {"JCODEMUNCH_LOG_LEVEL": "ERROR"},
        "mounts": [str(JCODEMUNCH_ROOT), str(JCODEMUNCH_WHEEL)],
        "default_tool_state": "warm-index",
        "warmup": {
            "kind": "code-index-build",
            "command": [
                str(UV_BIN),
                "tool",
                "run",
                "--from",
                str(JCODEMUNCH_WHEEL),
                "jcodemunch-mcp",
                "index",
                "{repo}",
            ],
            "output_name": "jcodemunch-warmup-output.txt",
            "metadata_name": "jcodemunch-warmup-metadata.json",
            "timeout_seconds": 1200,
        },
    },
    "snip": {
        "display_name": "Snip",
        "lane_name": "terminal-snip",
        "surface": "terminal/tool-output-compaction",
        "allowed_terms": ["snip"],
        "data_dir_name": "snip",
        "executable": str(SNIP_BIN),
        "path_entries": [str(SNIP_BIN.parent)],
        "mounts": [str(SNIP_ROOT)],
        "env": {"SNIP_TELEMETRY": "0"},
        "preflight_command": ["snip", "--version"],
        "default_tool_state": "cold-cli",
    },
    "lowfat": {
        "display_name": "Lowfat",
        "lane_name": "terminal-lowfat",
        "surface": "terminal/tool-output-compaction",
        "allowed_terms": ["lowfat"],
        "data_dir_name": "lowfat",
        "executable": str(LOWFAT_BIN),
        "path_entries": [str(LOWFAT_BIN.parent)],
        "mounts": [str(LOWFAT_ROOT), str(LOWFAT_BIN.parent)],
        "binary_mount_target": "/usr/local/bin/lowfat",
        "env": {"LOWFAT_TELEMETRY": "0"},
        "preflight_command": ["lowfat", "--version"],
        "coverage_preflight_command": ["lowfat", "info"],
        "supported_commands": ["docker", "find", "git", "grep", "ls", "tree"],
        "default_tool_state": "cold-cli",
    },
    "tokenjuice": {
        "display_name": "TokenJuice",
        "lane_name": "terminal-tokenjuice",
        "surface": "terminal/tool-output-compaction",
        "allowed_terms": ["tokenjuice"],
        "data_dir_name": "tokenjuice",
        "executable": str(TOKENJUICE_BIN),
        "path_entries": [str(TOKENJUICE_BIN.parent)],
        "mounts": [str(TOKENJUICE_ROOT)],
        "env": {"TOKENJUICE_TELEMETRY": "0"},
        "preflight_command": ["tokenjuice", "--version"],
        "default_tool_state": "cold-cli",
    },

    "headroom": {
        "display_name": "Headroom",
        "lane_name": "headroom-default-codex",
        "surface": "broad-compression/proxy/codex-wrapper",
        "allowed_terms": ["headroom", "headroom_retrieve", "rtk", "tokensave", "token-savior", "token_savior", "serena"],
        "data_dir_name": "headroom",
        "mounts": [str(HEADROOM_ROOT), str(HEADROOM_WHEEL)],
        "path_entries": ["{codex_home}/home/.headroom/bin", "{codex_home}/home/.local/bin"],
        "env": {
            "HEADROOM_HOME": "{tool_data_dir}",
            "HEADROOM_CACHE_DIR": "{tool_data_dir}/cache",
            "HEADROOM_DISABLE_DASHBOARD": "1",
            "HEADROOM_TELEMETRY": "0",
            "HEADROOM_PROJECT": "{repo_slug}",
        },
        "codex_wrapper": {
            "command": str(UV_BIN),
            "args": [
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
                "codex",
                "--port",
                "{tool_port}",
                "--verbose",
                "--",
            ],
        },
        "preflight_command": [
            str(UV_BIN),
            "tool",
            "run",
            "--from",
            str(HEADROOM_WHEEL),
            "--with",
            "mcp",
            "headroom",
            "--version",
        ],
        "default_tool_state": "active-wrapper",
    },
    "headroom-proxy-only": {
        "display_name": "Headroom proxy-only ablation",
        "lane_name": "terminal-headroom",
        "surface": "api-proxy/context-compression",
        "allowed_terms": ["headroom", "headroom_retrieve", "rtk", "tokensave", "serena"],
        "data_dir_name": "headroom-proxy-only",
        "mounts": [str(HEADROOM_ROOT), str(HEADROOM_WHEEL)],
        "path_entries": ["{codex_home}/home/.headroom/bin", "{codex_home}/home/.local/bin"],
        "env": {
            "HEADROOM_HOME": "{tool_data_dir}",
            "HEADROOM_CACHE_DIR": "{tool_data_dir}/cache",
            "HEADROOM_DISABLE_DASHBOARD": "1",
            "HEADROOM_TELEMETRY": "0",
            "HEADROOM_PROJECT": "{repo_slug}",
        },
        "codex_wrapper": {
            "command": str(UV_BIN),
            "args": [
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
                "codex",
                "--port",
                "{tool_port}",
                "--no-context-tool",
                "--no-mcp",
                "--no-tokensave",
                "--no-serena",
                "--verbose",
                "--",
            ],
        },
        "preflight_command": [
            str(UV_BIN),
            "tool",
            "run",
            "--from",
            str(HEADROOM_WHEEL),
            "--with",
            "mcp",
            "headroom",
            "--version",
        ],
        "default_tool_state": "active-proxy-only-wrapper",
    },
    "token-savior": {
        "display_name": "Token Savior",
        "lane_name": "integrated-token-savior",
        "surface": "integrated-mcp/retrieval-memory-compact-ops",
        "mcp_server": "token-savior",
        "allowed_terms": ["token-savior", "token_savior", "ts"],
        "data_dir_name": "token-savior",
        "mcp_command": str(UV_BIN),
        "mcp_args": [
            "tool",
            "run",
            "--from",
            str(TOKEN_SAVIOR_WHEEL),
            "--with",
            "mcp",
            "token-savior",
        ],
        "env": {
            "PROJECT_ROOT": "{repo}",
            "WORKSPACE_ROOTS": "{repo}",
            "CLAUDE_PROJECT_ROOT": "{repo}",
            "TOKEN_SAVIOR_PROFILE": "optimized",
            "TS_THIN_SCHEMAS": "1",
            "TS_CAPTURE_DISABLED": "1",
            "TS_HOME": "{tool_data_dir}",
        },
        "mounts": [str(TOKEN_SAVIOR_ROOT)],
    },
    "rtk": {
        "display_name": "RTK",
        "lane_name": "terminal-rtk",
        "surface": "terminal/tool-output-compaction",
        "allowed_terms": ["rtk"],
        "data_dir_name": "rtk",
        "executable": str(RTK_BIN),
        "path_entries": [str(RTK_BIN.parent)],
        "mounts": [str(RTK_BIN.parent)],
        "binary_mount_target": "/usr/local/bin/rtk",
        "env": {"RTK_TELEMETRY": "0"},
        "preflight_command": ["rtk", "--version"],
    },
    "caveman": {
        "display_name": "Caveman",
        "lane_name": "behavior-caveman",
        "surface": "behavioral-output-compression/mcp-description-compression",
        "allowed_terms": ["caveman"],
        "data_dir_name": "caveman",
        "mounts": [str(CAVEMAN_ROOT)],
        "preflight_command": ["node", str(CAVEMAN_ROOT / "src" / "tools" / "caveman-init.js"), "--help"],
        "prompt_instructions_command": ["python3", "-c", f"from pathlib import Path; print(Path({str(CAVEMAN_ROOT / 'skills' / 'caveman' / 'SKILL.md')!r}).read_text())"],
        "default_tool_state": "active-instruction-layer",
    },
    "ponytail": {
        "display_name": "Ponytail",
        "lane_name": "artifact-ponytail",
        "surface": "artifact/code-minimization-policy",
        "allowed_terms": ["ponytail"],
        "data_dir_name": "ponytail",
        "mounts": [str(PONYTAIL_ROOT)],
        "preflight_command": ["node", "-e", "const {getPonytailInstructions}=require('/opt/data/ponytail/hooks/ponytail-instructions.js'); console.log(getPonytailInstructions('full').split('\\n')[0]);"],
        "prompt_instructions_command": ["node", "-e", "const {getFallbackInstructions}=require('/opt/data/ponytail/hooks/ponytail-instructions.js'); console.log(getFallbackInstructions('full'));"],
    },
}


def rel_or_abs(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
    stdout_path: Path | None = None,
    input_path: Path | None = None,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    stdin = input_path.open("r") if input_path else None
    stdout_handle = stdout_path.open("w") if stdout_path else None
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd or ROOT,
            env=env,
            timeout=timeout,
            text=True,
            stdin=stdin,
            stdout=stdout_handle if stdout_handle else subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    finally:
        if stdin:
            stdin.close()
        if stdout_handle:
            stdout_handle.close()
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed with exit {proc.returncode}: {' '.join(cmd)}")
    return proc


def load_run_record(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    if data.get("record_type") != "run":
        raise ValueError(f"not an evaluation run record: {path}")
    return data


def profile_id(record: dict[str, Any], override: str | None) -> str:
    if override:
        return override
    return record.get("profile", {}).get("profile_id") or record.get("setup", {}).get("tool_permissions", {}).get("profile_id")


def auth_candidates(source_home: Path) -> list[Path]:
    names = ["auth.json", "credentials.json"]
    homes = [source_home, Path.home() / ".codex", Path("/opt/data/home/.codex")]
    seen: set[Path] = set()
    paths: list[Path] = []
    for home in homes:
        for name in names:
            p = home / name
            if p not in seen and p.exists():
                seen.add(p)
                paths.append(p)
    return paths


def tool_ids_for_record(record: dict[str, Any], pid: str) -> list[str]:
    if pid in BASELINE_CODEX_NO_MCP_PROFILES:
        return []
    if pid in PROFILE_TOOL_CONFIG_OVERRIDES:
        return [PROFILE_TOOL_CONFIG_OVERRIDES[pid]]

    def resolve(raw_values: list[Any]) -> list[str]:
        ids: list[str] = []
        for raw in raw_values:
            term = str(raw).lower()
            if term in TOOL_CONFIGS and term not in ids:
                ids.append(term)
            elif term in {"mcp_lean_ctx", "ctx_read", "ctx_search", "ctx_shell", "ctx_graph"} and "lean-ctx" not in ids:
                ids.append("lean-ctx")
        return ids

    component_ids = resolve(record.get("profile", {}).get("component_ids") or [])
    if component_ids:
        return component_ids

    permission_ids = resolve(record.get("setup", {}).get("tool_permissions", {}).get("allowed_token_saving_tools") or [])
    if permission_ids:
        return permission_ids

    # Compatibility fallback for old planned records. New tools should be declared
    # in profile.component_ids or setup.tool_permissions.allowed_token_saving_tools.
    ids: list[str] = []
    for tool_id, cfg in TOOL_CONFIGS.items():
        if tool_id.replace("-", "") in pid.replace("-", "") or tool_id in pid:
            ids.append(tool_id)
    return ids


def active_tool_config(record: dict[str, Any], pid: str) -> dict[str, Any] | None:
    ids = tool_ids_for_record(record, pid)
    if not ids:
        return None
    if len(ids) > 1:
        raise ValueError(f"runner currently supports one token-saving tool per lane; got {ids}")
    return TOOL_CONFIGS[ids[0]]


def codex_model_args(record: dict[str, Any]) -> list[str]:
    """Return Codex CLI args that bind the recorded model condition."""
    agent = record.get("agent") or {}
    args: list[str] = []
    model = agent.get("model")
    if model:
        args.extend(["--model", str(model)])
    reasoning_effort = agent.get("reasoning_effort")
    if reasoning_effort:
        args.extend(["--config", f"model_reasoning_effort={json.dumps(str(reasoning_effort))}"])
    return args


def tool_data_dir(codex_home: Path, cfg: dict[str, Any]) -> Path:
    return codex_home / ".config" / str(cfg["data_dir_name"])


def render_tool_env(codex_home: Path, cfg: dict[str, Any], repo: Path | None = None) -> dict[str, str]:
    data_dir = tool_data_dir(codex_home, cfg)
    data_dir.mkdir(parents=True, exist_ok=True)
    rendered: dict[str, str] = {}
    repo_path = repo or ROOT
    for key, value in (cfg.get("env") or {}).items():
        rendered[key] = str(value).format(tool_data_dir=data_dir, codex_home=codex_home, repo=repo_path, repo_slug=repo_path.name.replace("-", "_"))
    return rendered


def format_toml_array(values: list[str]) -> str:
    return "[" + ", ".join(json.dumps(v) for v in values) + "]"


def render_mcp_args(record: dict[str, Any], codex_home: Path, cfg: dict[str, Any]) -> list[str]:
    repo = rel_or_abs(record["target"]["repository_path"]) if record.get("target") else ROOT
    data_dir = tool_data_dir(codex_home, cfg)
    return [str(arg).format(repo=repo, codex_home=codex_home, tool_data_dir=data_dir) for arg in cfg.get("mcp_args", [])]


def write_codex_config(codex_home: Path, record: dict[str, Any], pid: str) -> None:
    lines = [
        'sandbox_mode = "danger-full-access"',
        'approval_policy = "never"',
        "",
        "[features]",
        "hooks = false",
        "",
    ]
    cfg = active_tool_config(record, pid)
    if cfg:
        executable = cfg.get("executable") or cfg.get("mcp_command")
        if executable:
            command = Path(str(executable))
            if command.is_absolute() and not command.exists():
                raise FileNotFoundError(f"{cfg['display_name']} command not found: {command}")
        server = cfg.get("mcp_server")
        if server:
            lines.extend(
                [
                    f"[mcp_servers.{server}]",
                    f"command = {json.dumps(str(cfg['mcp_command']))}",
                    f"args = {format_toml_array(render_mcp_args(record, codex_home, cfg))}",
                    "",
                ]
            )
            env = render_tool_env(codex_home, cfg, rel_or_abs(record["target"]["repository_path"]) if record.get("target") else ROOT)
            if env:
                lines.append(f"[mcp_servers.{server}.env]")
                for key, value in sorted(env.items()):
                    lines.append(f"{key} = {json.dumps(value)}")
                lines.append("")
    (codex_home / "config.toml").write_text("\n".join(lines))


def make_writable_for_removal(func: Any, path: str, exc_info: BaseException) -> None:
    """Let rmtree remove read-only caches created inside isolated eval homes."""
    path_obj = Path(path)
    for candidate in (path_obj, path_obj.parent):
        try:
            os.chmod(candidate, 0o700)
        except OSError:
            pass
    func(path)


def make_tree_writable(path: Path) -> None:
    """Pre-chmod an isolated eval home before recursive deletion."""
    if not path.exists():
        return
    for current, dirs, files in os.walk(path):
        try:
            os.chmod(current, 0o700)
        except OSError:
            pass
        for name in dirs:
            try:
                os.chmod(Path(current) / name, 0o700)
            except OSError:
                pass
        for name in files:
            try:
                os.chmod(Path(current) / name, 0o600)
            except OSError:
                pass


def prepare_codex_home(record: dict[str, Any], pid: str, run_dir: Path, source_home: Path, codex_home_root: Path, *, copy_auth: bool = False) -> Path:
    codex_home = codex_home_root / pid
    if codex_home.exists():
        make_tree_writable(codex_home)
        shutil.rmtree(codex_home, onexc=make_writable_for_removal)
    codex_home.mkdir(parents=True)

    auths = auth_candidates(source_home)
    if not auths:
        raise FileNotFoundError(
            f"No Codex auth file found under {source_home}, ~/.codex, or /opt/data/home/.codex. "
            "Run `codex login` first, then rerun this evaluation."
        )
    # Host mode symlinks auth to avoid copying secrets. Container mode copies auth into
    # the ephemeral Codex home so the container does not need the controller
    # account home mounted. The copied file is never written into run artifacts.
    auth_materialization = "copy-ephemeral" if copy_auth else "symlink-controller-home"
    auth_dest = codex_home / auths[0].name
    if copy_auth:
        shutil.copy2(auths[0], auth_dest)
        os.chmod(auth_dest, 0o600)
    else:
        os.symlink(auths[0], auth_dest)

    for subdir in ["home", "python-userbase", "xdg-cache", "xdg-config", "xdg-data", "tmp"]:
        (codex_home / subdir).mkdir(parents=True, exist_ok=True)
    write_codex_config(codex_home, record, pid)

    # Hard guard: never copy global instructions, skills, plugins, hooks, or tool-state docs.
    cfg = active_tool_config(record, pid)
    if cfg and cfg.get("mcp_server"):
        mcp_policy = "profile exposes only the MCP server declared by its active token-saving tool"
        allowed_mcp_servers = [cfg["mcp_server"]]
    elif cfg:
        mcp_policy = "profile exposes a non-MCP token-saving tool through lane-specific PATH/env only; no MCP servers are exposed"
        allowed_mcp_servers = []
    else:
        mcp_policy = "Codex no-MCP baseline: profile exposes no MCP servers; Codex native shell/edit tools remain part of the substrate"
        allowed_mcp_servers = []

    manifest = {
        "created_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "profile_id": pid,
        "codex_home": str(codex_home),
        "source_auth_home": str(source_home),
        "auth_link_name": auths[0].name,
        "auth_materialization": auth_materialization,
        "copied_global_instructions": False,
        "copied_skills_or_plugins": False,
        "hooks_enabled": False,
        "agent_home": str(codex_home / "home"),
        "python_userbase": str(codex_home / "python-userbase"),
        "mcp_policy": mcp_policy,
        "allowed_mcp_servers": allowed_mcp_servers,
    }
    (run_dir / "codex-home-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return codex_home


def codex_env(codex_home: Path, *, containerized: bool = False, cfg: dict[str, Any] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    env["HOME"] = str(codex_home / "home")
    env["PYTHONUSERBASE"] = str(codex_home / "python-userbase")
    env["XDG_CACHE_HOME"] = str(codex_home / "xdg-cache")
    env["XDG_CONFIG_HOME"] = str(codex_home / "xdg-config")
    env["XDG_DATA_HOME"] = str(codex_home / "xdg-data")
    env["TMPDIR"] = str(codex_home / "tmp")
    env["GOPATH"] = str(codex_home / "go")
    env["GOCACHE"] = str(codex_home / "go-build-cache")
    env["GOMODCACHE"] = str(codex_home / "go" / "pkg" / "mod")
    # Let Go satisfy toolchain directives, but force downloads/caches into this run home.
    env["GOTOOLCHAIN"] = "auto"
    for key in ("GOPATH", "GOCACHE", "GOMODCACHE"):
        Path(env[key]).mkdir(parents=True, exist_ok=True)
    # Keep only the Codex wrapper and pinned language toolchains in PATH. Do not
    # expose broad host wrapper directories such as /opt/data/bin in baseline or
    # unrelated treatment lanes; they may contain other token-saving tools.
    isolated_codex_bin = codex_home / "runtime-bin"
    if not containerized:
        isolated_codex_bin.mkdir(parents=True, exist_ok=True)
        link = isolated_codex_bin / "codex"
        if not link.exists():
            link.symlink_to(CODEX_HOST_EXECUTABLE)
    path_entries = [
        str(CODEX_CONTAINER_BIN_ROOT if containerized else isolated_codex_bin),
        "/opt/data/opt/go/bin",
        "/opt/data/opt/uv",
        str(NODE_TOOLCHAIN_ROOT / "bin"),
    ]
    if cfg:
        for entry in cfg.get("path_entries", []):
            rendered_entry = str(entry).format(codex_home=codex_home, home=codex_home / "home")
            if rendered_entry not in path_entries:
                path_entries.insert(1, rendered_entry)
    if containerized:
        path_entries.extend(["/usr/local/sbin", "/usr/local/bin", "/usr/sbin", "/usr/bin", "/sbin", "/bin"])
    else:
        path_entries.append(env.get("PATH", ""))
    env["PATH"] = ":".join(path_entries)
    return env


def apply_model_network_isolation(env: dict[str, str]) -> None:
    """Route Codex shell commands through the image's seccomp wrapper."""
    env["SHELL"] = MODEL_NETWORK_DENIED_SHELL
    path_entries = env.get("PATH", "").split(":")
    if MODEL_NETWORK_DENIED_BIN not in path_entries:
        env["PATH"] = ":".join([MODEL_NETWORK_DENIED_BIN, *path_entries])


def codex_isolation_args(codex_home: Path | None = None) -> list[str]:
    """Allow Codex provider traffic but deny model-visible web and shell network."""
    args = [
        "--strict-config",
        "-c",
        'web_search="disabled"',
        "-c",
        'sandbox_mode="danger-full-access"',
        "--disable",
        "standalone_web_search",
        "--disable",
        "in_app_browser",
        "--disable",
        "browser_use",
        "--disable",
        "browser_use_external",
        "--disable",
        "computer_use",
    ]
    return args


DOCKER_ENV_KEYS = [
    "CODEX_HOME",
    "HOME",
    "PYTHONUSERBASE",
    "XDG_CACHE_HOME",
    "XDG_CONFIG_HOME",
    "XDG_DATA_HOME",
    "TMPDIR",
    "GOPATH",
    "GOCACHE",
    "GOMODCACHE",
    "GOTOOLCHAIN",
    "PATH",
    "SHELL",
    "LEAN_CTX_DATA_DIR",
    "CODEGRAPH_TELEMETRY",
]


def docker_env_keys() -> list[str]:
    keys = list(DOCKER_ENV_KEYS)
    for cfg in TOOL_CONFIGS.values():
        for key in (cfg.get("env") or {}).keys():
            if key not in keys:
                keys.append(key)
    return keys

def tool_env_for_record(record: dict[str, Any], pid: str, codex_home: Path) -> dict[str, str]:
    cfg = active_tool_config(record, pid)
    repo = rel_or_abs(record["target"]["repository_path"]) if record.get("target") else ROOT
    return render_tool_env(codex_home, cfg, repo) if cfg else {}



def docker_tool_mounts(cfg: dict[str, Any] | None = None) -> list[tuple[Path, Path, str]]:
    mounts: list[tuple[Path, Path, str]] = []
    if CODEX_RUNTIME_ROOT.exists():
        mounts.append((CODEX_RUNTIME_ROOT, CODEX_CONTAINER_RUNTIME_ROOT, "ro"))
    codex_wrapper = ROOT / "sources/evaluations/fixtures/container/codex-entrypoint.sh"
    if codex_wrapper.exists():
        mounts.append((codex_wrapper, CODEX_CONTAINER_BIN_ROOT / "codex", "ro"))
    path_texts = [
        "/opt/data/dotnet",
        "/opt/data/opt/go",
        "/opt/data/opt/uv",
        str(NODE_TOOLCHAIN_ROOT),
    ]
    if cfg:
        path_texts.extend(str(path) for path in cfg.get("mounts", []))
    for path_text in path_texts:
        path = Path(path_text)
        if path.exists():
            mounts.append((path, path, "ro"))
    if cfg and cfg.get("binary_mount_target") and cfg.get("executable"):
        executable = Path(str(cfg["executable"]))
        if executable.exists():
            mounts.append((executable, Path(str(cfg["binary_mount_target"])), "ro"))
    return mounts


def add_mount(mounts: list[tuple[Path, Path, str]], source: Path, target: Path | None = None, mode: str = "rw") -> None:
    source = source.resolve()
    target = target or source
    item = (source, target, mode)
    if item not in mounts:
        mounts.append(item)


_DOCKER_HOST_PATH_CACHE: dict[Path, Path | None] = {}


def _docker_host_root_for_container_root(container_root: Path) -> Path | None:
    """Return the Docker-daemon host path backing a path mounted in this container.

    When Hermes itself runs in Docker and controls the host daemon through
    /var/run/docker.sock, Docker bind sources are resolved on the host, not inside
    the Hermes container. Nested runs therefore translate the agent-visible data
    root to the host-side source path at runtime. Environment overrides keep
    remote-daemon setups explicit and avoid guessing when auto-detection is
    unavailable. Host paths are not written to publishable artifacts.
    """
    container_root = container_root.resolve()
    if container_root in _DOCKER_HOST_PATH_CACHE:
        return _DOCKER_HOST_PATH_CACHE[container_root]

    env_container_root = Path(os.environ.get("TOKEN_EVAL_CONTAINER_DATA_ROOT", "/opt/data")).resolve()
    env_host_root = os.environ.get("TOKEN_EVAL_DOCKER_HOST_DATA_ROOT")
    if container_root == env_container_root and env_host_root:
        value = Path(env_host_root)
        _DOCKER_HOST_PATH_CACHE[container_root] = value
        return value

    value: Path | None = None
    try:
        proc = subprocess.run(
            [
                "docker",
                "inspect",
                os.uname().nodename,
                "--format",
                "{{range .Mounts}}{{if eq .Destination \"" + str(container_root) + "\"}}{{.Source}}{{end}}{{end}}",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
        source = proc.stdout.strip()
        if proc.returncode == 0 and source:
            value = Path(source)
    except Exception:
        value = None

    if value is None:
        # Fallback for bind mounts visible in /proc/self/mountinfo. The fourth
        # field is the root within the backing filesystem; for ordinary host bind
        # mounts this is often the host path usable by the Docker daemon.
        try:
            for line in Path("/proc/self/mountinfo").read_text().splitlines():
                fields = line.split()
                if len(fields) > 4 and Path(fields[4].replace("\\040", " ")) == container_root:
                    root_field = fields[3].replace("\\040", " ")
                    if root_field and root_field != "/":
                        value = Path(root_field)
                    break
        except Exception:
            value = None

    _DOCKER_HOST_PATH_CACHE[container_root] = value
    return value


def docker_host_source_path(path: Path) -> Path:
    container_root = Path(os.environ.get("TOKEN_EVAL_CONTAINER_DATA_ROOT", "/opt/data")).resolve()
    source = path.resolve()
    try:
        relative = source.relative_to(container_root)
    except ValueError:
        return source
    host_root = _docker_host_root_for_container_root(container_root)
    return host_root / relative if host_root else source


def docker_path_mapping_metadata() -> dict[str, str | bool | None]:
    container_root = Path(os.environ.get("TOKEN_EVAL_CONTAINER_DATA_ROOT", "/opt/data")).resolve()
    host_root = _docker_host_root_for_container_root(container_root)
    return {
        "container_data_root": str(container_root),
        "docker_host_path_mapping_active": bool(host_root),
        "docker_host_data_root": "<redacted>" if host_root else None,
    }


def ensure_codex_native_binary_executable() -> None:
    """Codex may leave its packaged native binary without execute bits.

    The Docker runner bind-mounts the controller-side Codex installation. Ensure
    the native executable can be spawned by the same UID inside the eval container
    before each smoke/preflight/solve invocation.
    """
    codex_root = CODEX_RUNTIME_ROOT / "node_modules"
    if not codex_root.exists():
        return
    for binary in codex_root.glob("@openai/codex-*/vendor/*/bin/codex"):
        try:
            mode = binary.stat().st_mode
            binary.chmod(mode | 0o111)
        except OSError:
            pass


def docker_command(
    cmd: list[str],
    *,
    image: str,
    cwd: Path,
    env: dict[str, str],
    mounts: list[tuple[Path, Path, str]],
) -> list[str]:
    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "--interactive",
        "--init",
        "--user",
        f"{os.getuid()}:{os.getgid()}",
        "--workdir",
        str(cwd),
    ]
    for source, target, mode in mounts:
        access = ",readonly" if mode == "ro" else ""
        host_source = docker_host_source_path(source)
        docker_cmd.extend(["--mount", f"type=bind,source={host_source},target={target},bind-propagation=rprivate{access}"])
    for key in docker_env_keys():
        if key in env:
            docker_cmd.extend(["--env", f"{key}={env[key]}"])
    # Keep the network enabled because Codex must reach the model provider. The
    # container boundary is for filesystem/process isolation, not offline replay.
    docker_cmd.append(image)
    docker_cmd.extend(cmd)
    return docker_cmd


def run_backend(
    cmd: list[str],
    *,
    backend: str,
    docker_image: str,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
    stdout_path: Path | None = None,
    input_path: Path | None = None,
    mounts: list[tuple[Path, Path, str]] | None = None,
) -> subprocess.CompletedProcess[str]:
    if backend == "host":
        return run(cmd, cwd=cwd, env=env, timeout=timeout, stdout_path=stdout_path, input_path=input_path)
    if backend != "docker":
        raise ValueError(f"unsupported execution backend: {backend}")
    docker_mounts = mounts or []
    wrapped = docker_command(cmd, image=docker_image, cwd=cwd or ROOT, env=env or os.environ.copy(), mounts=docker_mounts)
    return run(wrapped, cwd=ROOT, env=os.environ.copy(), timeout=timeout, stdout_path=stdout_path, input_path=input_path)


def check_container_runtime(
    backend: str,
    docker_image: str,
    run_dir: Path,
    allow_host_eval: bool,
    *,
    build_image: bool = False,
    dockerfile: Path = DEFAULT_DOCKERFILE,
    codex_home: Path | None = None,
    cfg: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "execution_backend": backend,
        "container_required": True,
        "containerized_codex_solve": backend == "docker",
        "docker_image": docker_image if backend == "docker" else None,
        "dockerfile": str(dockerfile.relative_to(ROOT) if dockerfile.is_relative_to(ROOT) else dockerfile),
        "docker_path_mapping": docker_path_mapping_metadata(),
        "passed": False,
        "failure_reasons": [],
        "warnings": [],
    }
    if backend == "host":
        if allow_host_eval:
            result["passed"] = True
            result["warnings"].append("host execution explicitly allowed; this is not container-grade evidence")
        else:
            result["failure_reasons"].append("host evaluation requires --allow-host-eval")
        (run_dir / "container-preflight.json").write_text(json.dumps(result, indent=2) + "\n")
        return result

    version = run(["docker", "--version"], timeout=30)
    info = run(["docker", "info", "--format", "{{.ServerVersion}}"], timeout=30)
    docker_info_text = (info.stdout or "")
    result["docker_version_output"] = (version.stdout or "")[-500:]
    result["docker_info_output"] = docker_info_text[-1000:]
    daemon_unavailable = info.returncode != 0 or "Cannot connect to the Docker daemon" in docker_info_text or "Is the docker daemon running" in docker_info_text
    if version.returncode != 0:
        result["failure_reasons"].append("docker client is unavailable")
    if daemon_unavailable:
        result["failure_reasons"].append("docker daemon is unavailable; start Docker or point DOCKER_HOST at a reachable daemon before running container-grade experiments")
    if result["failure_reasons"]:
        (run_dir / "container-preflight.json").write_text(json.dumps(result, indent=2) + "\n")
        return result

    if build_image:
        build_output = run_dir / "docker-build-output.txt"
        if not dockerfile.exists():
            result["failure_reasons"].append(f"dockerfile not found: {dockerfile}")
        else:
            build = run(["docker", "build", "-f", str(dockerfile), "-t", docker_image, str(ROOT)], timeout=1800, stdout_path=build_output)
            result["docker_build_exit_code"] = build.returncode
            result["docker_build_output"] = str(build_output.relative_to(ROOT))
            if build.returncode != 0:
                result["failure_reasons"].append(f"docker image build failed: {docker_image}")
    image = run(["docker", "image", "inspect", docker_image], timeout=30)
    result["docker_image_inspect_exit_code"] = image.returncode
    if image.returncode != 0:
        result["failure_reasons"].append(f"docker image not found: {docker_image}; rerun with --build-docker-image or build {dockerfile}")

    if not result["failure_reasons"]:
        ensure_codex_native_binary_executable()
        smoke_env = codex_env(codex_home, containerized=True, cfg=cfg) if codex_home else os.environ.copy()
        smoke_mounts = docker_tool_mounts(cfg)
        if codex_home:
            add_mount(smoke_mounts, codex_home, mode="rw")
        smoke_output = run_dir / "docker-smoke-output.txt"
        smoke_cmd = docker_command(
            [
                "bash",
                "-lc",
                "set -euo pipefail; id; python3 --version; git --version; command -v codex; codex --version",
            ],
            image=docker_image,
            cwd=codex_home / "home" if codex_home else ROOT,
            env=smoke_env,
            mounts=smoke_mounts,
        )
        smoke = run(smoke_cmd, cwd=ROOT, env=os.environ.copy(), timeout=120, stdout_path=smoke_output)
        result["docker_smoke_exit_code"] = smoke.returncode
        result["docker_smoke_output"] = str(smoke_output.relative_to(ROOT))
        if smoke.returncode != 0:
            result["failure_reasons"].append("docker smoke test failed; inspect docker-smoke-output.txt for missing mounted tools or image dependencies")

    result["passed"] = not result["failure_reasons"]
    (run_dir / "container-preflight.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def project_root_for_record(record: dict[str, Any]) -> Path:
    repo = rel_or_abs(record["target"]["repository_path"])
    return repo.parent


def container_mounts_for_record(record: dict[str, Any], codex_home: Path, *, include_project: bool = False, include_repo: bool = True, cfg: dict[str, Any] | None = None) -> list[tuple[Path, Path, str]]:
    mounts = docker_tool_mounts(cfg)
    add_mount(mounts, codex_home, mode="rw")
    if include_project:
        add_mount(mounts, project_root_for_record(record), mode="rw")
    elif include_repo:
        add_mount(mounts, rel_or_abs(record["target"]["repository_path"]), mode="rw")
    return mounts


def profile_protocol_from_catalog(pid: str) -> dict[str, Any]:
    catalog = ROOT / "data" / "evaluation-profiles.json"
    if not catalog.exists():
        return {}
    try:
        data = json.loads(catalog.read_text())
    except json.JSONDecodeError:
        return {}
    for profile in data.get("profiles", []):
        if profile.get("id") == pid:
            return profile.get("evaluation_protocol") or {}
    return {}


def evaluation_protocol(record: dict[str, Any], pid: str, tool_state: str | None, tool_use_policy: str | None) -> dict[str, Any]:
    protocol: dict[str, Any] = {}
    protocol.update(profile_protocol_from_catalog(pid))
    protocol.update(record.get("evaluation_protocol") or record.get("protocol") or {})
    cfg = active_tool_config(record, pid)
    state = tool_state or protocol.get("tool_state")
    policy = tool_use_policy or protocol.get("tool_use_policy")
    if state is None:
        state = "cold" if cfg else "none"
    if policy is None:
        policy = "natural" if cfg else "none"
    return {
        "tool_state": state,
        "tool_use_policy": policy,
        "active_tool": cfg["display_name"] if cfg else None,
        "active_tool_id": next((tool_id for tool_id, candidate in TOOL_CONFIGS.items() if candidate is cfg), None) if cfg else None,
        "warmup_provider_tokens_counted": bool(protocol.get("warmup_provider_tokens_counted", False)),
        "warmup_accounting": protocol.get("warmup_accounting") or "pre-Codex tool-state preparation commands are recorded as wall-time/artifacts, not provider tokens, unless their output appears in codex-events.jsonl",
        "container_required": bool(protocol.get("container_required", True)),
    }


def text_contains_forbidden(path: Path, forbidden: list[str]) -> list[str]:
    text = path.read_text(errors="replace") if path.exists() else ""
    lower = text.lower()
    return sorted({term for term in forbidden if term.lower() in lower})


def forbidden_command_probe_terms(allowed_terms: set[str]) -> list[str]:
    return [
        term for term in FORBIDDEN_BASELINE_TERMS
        if term.lower() not in allowed_terms and re.fullmatch(r"[A-Za-z0-9_.-]+", term)
    ]


def forbidden_command_probe_script(terms: list[str]) -> str:
    quoted_terms = " ".join(shlex.quote(term) for term in terms)
    return (
        "set -euo pipefail\n"
        f"for term in {quoted_terms}; do\n"
        "  path=$(command -v \"$term\" 2>/dev/null || true)\n"
        "  if [ -n \"$path\" ]; then printf '%s\\t%s\\n' \"$term\" \"$path\"; fi\n"
        "done\n"
    )


def missing_declared_filter_commands(
    output: str, declared_commands: list[str]
) -> list[str]:
    """Return declared Lowfat commands absent from `lowfat info` output."""
    lines = output.splitlines()
    missing: list[str] = []
    for command in declared_commands:
        pattern = re.compile(rf"^\s*●\s+\S+\s+{re.escape(command)}\s*$")
        if not any(pattern.match(line) for line in lines):
            missing.append(command)
    return missing


def preflight_codex(record: dict[str, Any], codex_home: Path, pid: str, run_dir: Path, *, backend: str, docker_image: str) -> dict[str, Any]:
    ensure_codex_native_binary_executable()
    cfg = active_tool_config(record, pid)
    env = codex_env(codex_home, containerized=backend == "docker", cfg=cfg)
    env.update(tool_env_for_record(record, pid, codex_home))
    doctor_path = run_dir / "codex-doctor.txt"
    mcp_path = run_dir / "codex-mcp-list.txt"
    config_path = run_dir / "codex-effective-config.toml"

    mounts = docker_tool_mounts(cfg)
    add_mount(mounts, codex_home, mode="rw")
    doctor = run_backend(["codex", "doctor", "--summary"], backend=backend, docker_image=docker_image, cwd=codex_home / "home", env=env, stdout_path=doctor_path, timeout=120, mounts=mounts)
    mcp = run_backend(["codex", "mcp", "list"], backend=backend, docker_image=docker_image, cwd=codex_home / "home", env=env, stdout_path=mcp_path, timeout=120, mounts=mounts)
    shutil.copy2(codex_home / "config.toml", config_path)

    forbidden = FORBIDDEN_BASELINE_TERMS
    mcp_hits = text_contains_forbidden(mcp_path, forbidden)
    config_hits = text_contains_forbidden(config_path, forbidden)
    allowed_terms = {term.lower() for term in (cfg.get("allowed_terms", []) if cfg else [])}
    visible_hits = {h.lower() for h in (mcp_hits + config_hits)}
    disallowed_mcp_hits = [h for h in mcp_hits if h.lower() not in allowed_terms]
    disallowed_config_hits = [h for h in config_hits if h.lower() not in allowed_terms]
    command_visibility_path = run_dir / "forbidden-command-visibility.txt"
    command_terms = forbidden_command_probe_terms(allowed_terms)
    command_probe = run_backend(
        ["bash", "-lc", forbidden_command_probe_script(command_terms)],
        backend=backend,
        docker_image=docker_image,
        cwd=codex_home / "home",
        env=env,
        stdout_path=command_visibility_path,
        timeout=120,
        mounts=mounts,
    )
    visible_forbidden_commands: list[dict[str, str]] = []
    if command_visibility_path.exists():
        for line in command_visibility_path.read_text(errors="replace").splitlines():
            if not line.strip():
                continue
            term, _, path = line.partition("\t")
            visible_forbidden_commands.append({"term": term, "path": path})
    passed = mcp.returncode == 0 and command_probe.returncode == 0
    failure_reasons: list[str] = []
    warnings: list[str] = []
    if doctor.returncode != 0:
        warnings.append(
            f"codex doctor exited {doctor.returncode}; preserve the diagnostic, but use the isolated MCP/config probes and task execution as gates"
        )
    if mcp.returncode != 0:
        failure_reasons.append(f"codex mcp list exited {mcp.returncode}")
    if disallowed_mcp_hits or disallowed_config_hits:
        passed = False
        failure_reasons.append("forbidden tool surface visible in Codex MCP/config preflight")
    if visible_forbidden_commands:
        passed = False
        failure_reasons.append("forbidden token-saving command visible on PATH in Codex runtime")
    tool_preflight = None
    coverage_preflight = None
    missing_filter_commands: list[str] = []
    if cfg and cfg.get("mcp_server") and str(cfg["mcp_server"]).lower() not in visible_hits:
        passed = False
        failure_reasons.append(f"{pid} profile did not expose expected MCP server {cfg['mcp_server']} in preflight")
    if cfg and cfg.get("preflight_command"):
        tool_preflight_path = run_dir / "tool-preflight.txt"
        tool_preflight = run_backend([str(x) for x in cfg["preflight_command"]], backend=backend, docker_image=docker_image, cwd=codex_home / "home", env=env, stdout_path=tool_preflight_path, timeout=120, mounts=mounts)
        if tool_preflight.returncode != 0:
            passed = False
            failure_reasons.append(f"{cfg['display_name']} preflight exited {tool_preflight.returncode}")
    if cfg and cfg.get("coverage_preflight_command"):
        coverage_path = run_dir / "tool-coverage-preflight.txt"
        coverage_preflight = run_backend([str(x) for x in cfg["coverage_preflight_command"]], backend=backend, docker_image=docker_image, cwd=codex_home / "home", env=env, stdout_path=coverage_path, timeout=120, mounts=mounts)
        if coverage_preflight.returncode != 0:
            passed = False
            failure_reasons.append(f"{cfg['display_name']} coverage preflight exited {coverage_preflight.returncode}")
        else:
            missing_filter_commands = missing_declared_filter_commands(
                coverage_path.read_text(errors="replace"),
                [str(command) for command in cfg.get("supported_commands", [])],
            )
            if missing_filter_commands:
                passed = False
                failure_reasons.append(
                    f"{cfg['display_name']} is missing declared filters: {', '.join(missing_filter_commands)}"
                )

    result = {
        "profile_id": pid,
        "passed": passed,
        "doctor_exit_code": doctor.returncode,
        "mcp_list_exit_code": mcp.returncode,
        "tool_preflight_exit_code": tool_preflight.returncode if tool_preflight else None,
        "coverage_preflight_exit_code": coverage_preflight.returncode if coverage_preflight else None,
        "missing_declared_filter_commands": missing_filter_commands,
        "forbidden_command_probe_exit_code": command_probe.returncode,
        "forbidden_mcp_hits": disallowed_mcp_hits,
        "forbidden_config_hits": disallowed_config_hits,
        "visible_forbidden_commands": visible_forbidden_commands,
        "failure_reasons": failure_reasons,
        "warnings": warnings,
        "artifacts": {
            "doctor": str(doctor_path.relative_to(ROOT)),
            "mcp_list": str(mcp_path.relative_to(ROOT)),
            "effective_config": str(config_path.relative_to(ROOT)),
            "forbidden_command_visibility": str(command_visibility_path.relative_to(ROOT)),
            "tool_preflight": str((run_dir / "tool-preflight.txt").relative_to(ROOT)) if tool_preflight else None,
            "tool_coverage_preflight": str((run_dir / "tool-coverage-preflight.txt").relative_to(ROOT)) if coverage_preflight else None,
        },
    }
    (run_dir / "codex-preflight.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def render_prompt_instructions(cfg: dict[str, Any]) -> str:
    command = cfg.get("prompt_instructions_command")
    if not command:
        return ""
    proc = subprocess.run([str(part) for part in command], cwd=ROOT, text=True, capture_output=True, timeout=30)
    if proc.returncode != 0:
        raise RuntimeError(f"{cfg['display_name']} instruction generation failed: {proc.stderr or proc.stdout}")
    return proc.stdout.strip()


def treatment_lane_guidance(pid: str, cfg: dict[str, Any], protocol: dict[str, Any]) -> str:
    """Describe isolation without steering treatment-tool use.

    Tool-specific prompt content is included only when that content is itself the
    tool's normal installation surface (for example, an instruction-layer tool).
    """
    del pid, protocol
    prompt_instructions = render_prompt_instructions(cfg)
    prompt_block = (
        f"\n# Installed profile instructions\n\n{prompt_instructions}\n\n---\n\n"
        if prompt_instructions
        else ""
    )
    return (
        "# Evaluation isolation contract\n\n"
        "This is a treatment lane. Its profile was installed and configured before the task using the profile's normal integration surface. "
        "No tool invocation is required or preferred. Use the exposed environment naturally, and do not invoke a tool merely because this is a treatment lane. "
        "If no treatment tool is invoked, zero use is a valid observed outcome. "
        "Do not use unconfigured retrieval, compression, memory, or token-saving tools. "
        "Codex web search is disabled and model-launched shell commands have no network access; do not attempt curl, wget, browsers, package downloads, or any other external retrieval. "
        "Work only inside the target repository. The controller owns concealed verification; do not inspect or modify evaluation harness files.\n\n"
        "---\n\n"
        f"{prompt_block}"
    )


def write_prompt(record: dict[str, Any], run_dir: Path, pid: str, protocol: dict[str, Any]) -> Path:
    prompt_path = rel_or_abs(record["task"]["prompt_path"])
    prompt = prompt_path.read_text()
    cfg = active_tool_config(record, pid)
    if cfg:
        lane_guidance = treatment_lane_guidance(pid, cfg, protocol)
    else:
        lane_guidance = """# Evaluation isolation contract\n\nYou are running inside the `baseline-codex-no-mcp` control lane. This is a Codex substrate baseline, not a model-only baseline: Codex native shell, file, git, and verifier operations are allowed. Do not use external retrieval, compression, memory, MCP, or token-saving tools. Codex web search is disabled and model-launched shell commands have no network access; do not attempt `curl`, `wget`, browsers, package downloads, or any other external retrieval. Work only inside the target repository and use the verifier as the acceptance gate.\n\n---\n\n"""
    out = run_dir / "prompt.md"
    out.write_text(lane_guidance + prompt)
    return out


def run_setup(record: dict[str, Any], run_dir: Path, *, backend: str, docker_image: str, codex_home: Path) -> int:
    setup_cmd = record.get("setup", {}).get("setup_command")
    if not setup_cmd:
        return 0
    env = codex_env(codex_home, containerized=backend == "docker")
    mounts = container_mounts_for_record(record, codex_home, include_project=True, include_repo=False)
    proc = run_backend([str(rel_or_abs(setup_cmd))], backend=backend, docker_image=docker_image, cwd=project_root_for_record(record), env=env, stdout_path=run_dir / "setup-output.txt", timeout=900, mounts=mounts)
    return proc.returncode


def prepare_profile_workspace(record: dict[str, Any], pid: str, codex_home: Path, run_dir: Path, protocol: dict[str, Any], *, backend: str, docker_image: str) -> int:
    cfg = active_tool_config(record, pid)
    if not cfg or protocol.get("tool_state") != "warm-index":
        return 0
    warmup = cfg.get("warmup")
    if not warmup:
        metadata = {
            "profile_id": pid,
            "active_tool": cfg.get("display_name"),
            "tool_state": protocol.get("tool_state"),
            "skipped": True,
            "reason": "active tool has no warmup hook",
        }
        (run_dir / "tool-warmup-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        return 0

    repo = rel_or_abs(record["target"]["repository_path"])
    for relative in warmup.get("cleanup_paths", []):
        cleanup = repo / str(relative)
        if cleanup.exists():
            shutil.rmtree(cleanup) if cleanup.is_dir() else cleanup.unlink()

    env = codex_env(codex_home, containerized=backend == "docker", cfg=cfg)
    env.update(tool_env_for_record(record, pid, codex_home))
    mounts = container_mounts_for_record(record, codex_home, include_repo=True, cfg=cfg)
    command = [str(part).format(repo=repo, codex_home=codex_home, tool_data_dir=tool_data_dir(codex_home, cfg)) for part in warmup["command"]]
    output_name = warmup.get("output_name", "tool-warmup-output.txt")
    metadata_name = warmup.get("metadata_name", "tool-warmup-metadata.json")
    started = dt.datetime.now(dt.UTC)
    proc = run_backend(
        command,
        backend=backend,
        docker_image=docker_image,
        cwd=repo,
        env=env,
        stdout_path=run_dir / output_name,
        timeout=int(warmup.get("timeout_seconds", 900)),
        mounts=mounts,
    )
    ended = dt.datetime.now(dt.UTC)
    metadata = {
        "profile_id": pid,
        "active_tool": cfg.get("display_name"),
        "tool_state": protocol.get("tool_state"),
        "warmup_kind": warmup.get("kind"),
        "command": command,
        "exit_code": proc.returncode,
        "started_at_utc": started.isoformat(),
        "ended_at_utc": ended.isoformat(),
        "wall_time_seconds": (ended - started).total_seconds(),
        "provider_tokens_counted": bool(protocol.get("warmup_provider_tokens_counted", False)),
        "output_artifact": output_name,
    }
    (run_dir / metadata_name).write_text(json.dumps(metadata, indent=2) + "\n")
    if metadata_name != "tool-warmup-metadata.json":
        (run_dir / "tool-warmup-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return proc.returncode


def run_codex(record: dict[str, Any], pid: str, codex_home: Path, run_dir: Path, timeout: int, protocol: dict[str, Any], *, backend: str, docker_image: str) -> int:
    ensure_codex_native_binary_executable()
    repo = rel_or_abs(record["target"]["repository_path"])
    prompt = write_prompt(record, run_dir, pid, protocol)
    events = run_dir / "codex-events.jsonl"
    last = run_dir / "codex-last-message.txt"
    codex_cmd = [
        "codex",
        "exec",
        *codex_isolation_args(codex_home),
        "--json",
        "--color",
        "never",
        "--disable",
        "hooks",
        "--ignore-rules",
        "--cd",
        str(repo),
        "--output-last-message",
        str(last),
        "-",
    ]
    cfg = active_tool_config(record, pid)
    wrapper = (cfg or {}).get("codex_wrapper") if cfg else None
    input_path_for_proc: Path | None = prompt
    if wrapper:
        data_dir = tool_data_dir(codex_home, cfg)
        tool_port = 18000 + int(hashlib.sha256(str(repo.resolve()).encode()).hexdigest()[:8], 16) % 20000
        wrapper_args = [
            str(part).format(
                repo=repo,
                codex_home=codex_home,
                tool_data_dir=data_dir,
                repo_slug=repo.name.replace("-", "_"),
                tool_port=tool_port,
            )
            for part in wrapper.get("args", [])
        ]
        if codex_cmd and codex_cmd[-1] == "-":
            codex_cmd = [*codex_cmd[:-1], prompt.read_text()]
            input_path_for_proc = None
        cmd = [str(wrapper["command"]), *wrapper_args, *codex_cmd[1:]]
    else:
        cmd = codex_cmd
    env = codex_env(codex_home, containerized=backend == "docker", cfg=cfg)
    env.update(tool_env_for_record(record, pid, codex_home))
    if backend == "docker":
        apply_model_network_isolation(env)
    mounts = container_mounts_for_record(record, codex_home, include_repo=True, cfg=cfg)
    add_mount(mounts, run_dir, mode="rw")
    proc = run_backend(cmd, backend=backend, docker_image=docker_image, cwd=repo, env=env, stdout_path=events, input_path=input_path_for_proc, timeout=timeout, mounts=mounts)
    (run_dir / "codex-exit-code.txt").write_text(str(proc.returncode) + "\n")
    return proc.returncode


def run_verifier(record: dict[str, Any], run_dir: Path, *, backend: str, docker_image: str, codex_home: Path) -> int:
    verifier = rel_or_abs(record["task"]["verifier_command"])
    env = codex_env(codex_home, containerized=backend == "docker")
    mounts = container_mounts_for_record(record, codex_home, include_project=True, include_repo=False)
    proc = run_backend([str(verifier)], backend=backend, docker_image=docker_image, cwd=project_root_for_record(record), env=env, stdout_path=run_dir / "verifier-output.txt", timeout=900, mounts=mounts)
    return proc.returncode


def capture_diff(record: dict[str, Any], run_dir: Path) -> None:
    repo = rel_or_abs(record["target"]["repository_path"])
    git_dir = repo / ".git"
    git_base = ["git", f"--git-dir={git_dir}", f"--work-tree={repo}"]
    run(git_base + ["status", "--short"], cwd=repo, stdout_path=run_dir / "git-status.txt", timeout=60)
    run(git_base + ["diff", "--stat"], cwd=repo, stdout_path=run_dir / "final-diffstat.txt", timeout=60)
    run(git_base + ["diff"], cwd=repo, stdout_path=run_dir / "final.diff", timeout=60)


def extract_usage(run_dir: Path) -> int:
    events = run_dir / "codex-events.jsonl"
    if not events.exists():
        events.write_text("")
    proc = run(
        [
            sys.executable,
            str(ROOT / "scripts" / "extract_codex_usage.py"),
            str(events),
            "--output",
            str(run_dir / "provider-usage.json"),
        ],
        stdout_path=run_dir / "provider-usage-extract.txt",
        timeout=120,
    )
    return proc.returncode


def audit(record_path: Path, run_dir: Path) -> int:
    transcript = run_dir / "codex-events.jsonl"
    if not transcript.exists():
        transcript.write_text("")
    audit_json = run_dir / "tool-isolation-audit.json"
    proc = run(
        [
            sys.executable,
            str(ROOT / "scripts" / "audit_tool_isolation.py"),
            "--json-output",
            str(audit_json),
            str(record_path),
            str(transcript),
            str(run_dir / "codex-mcp-list.txt"),
            str(run_dir / "codex-effective-config.toml"),
            str(run_dir / "prompt.md"),
        ],
        stdout_path=run_dir / "tool-isolation-audit.txt",
        timeout=120,
    )
    return proc.returncode


def safe_clean_run_dir(run_dir: Path) -> None:
    """Remove stale artifacts for a rerun without touching source checkouts."""
    try:
        relative = run_dir.resolve().relative_to(ROOT.resolve())
    except ValueError as exc:
        raise SystemExit(f"refusing to clean run dir outside repository: {run_dir}") from exc
    parts = relative.parts
    if "runs" not in parts or not run_dir.name.startswith("planned-"):
        raise SystemExit(f"refusing to clean unexpected run artifact directory: {run_dir}")
    if run_dir.exists():
        make_tree_writable(run_dir)
        shutil.rmtree(run_dir, onexc=make_writable_for_removal)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_record", type=Path)
    parser.add_argument("--profile-id")
    parser.add_argument("--codex-home-root", type=Path, default=DEFAULT_CODEX_HOME_ROOT)
    parser.add_argument("--source-codex-home", type=Path, default=DEFAULT_SOURCE_CODEX_HOME)
    parser.add_argument("--timeout", type=int, default=2700)
    parser.add_argument("--prepare-only", action="store_true", help="prepare Codex home and preflight, but do not run setup/Codex/verifier")
    parser.add_argument("--skip-setup", action="store_true")
    parser.add_argument("--execution-backend", choices=["docker", "host"], default=os.environ.get("TOKEN_EVAL_BACKEND", "docker"))
    parser.add_argument("--allow-host-eval", action="store_true", help="permit non-containerized execution; resulting evidence is not container-grade")
    parser.add_argument("--docker-image", default=os.environ.get("TOKEN_EVAL_DOCKER_IMAGE", DEFAULT_DOCKER_IMAGE))
    parser.add_argument("--dockerfile", type=Path, default=DEFAULT_DOCKERFILE)
    parser.add_argument("--build-docker-image", action="store_true", help="build --docker-image from --dockerfile before Docker preflight")
    parser.add_argument("--tool-state", choices=["none", "cold", "warm-index"], help="override protocol tool-state condition")
    parser.add_argument("--tool-use-policy", choices=["none", "preferred", "optional"], help="override treatment guidance policy")
    args = parser.parse_args(argv)

    record_path = args.run_record if args.run_record.is_absolute() else ROOT / args.run_record
    record = load_run_record(record_path)
    pid = profile_id(record, args.profile_id)
    if not pid:
        raise SystemExit("run record does not identify a profile_id")
    permissions = record.setdefault("setup", {}).setdefault("tool_permissions", {})
    permissions["external_retrieval_allowed"] = False
    cfg = active_tool_config(record, pid)
    if cfg and cfg.get("supported_commands"):
        permissions["allowed_tool_commands"] = {
            tool_ids_for_record(record, pid)[0]: [
                str(command) for command in cfg["supported_commands"]
            ]
        }

    run_dir = rel_or_abs(record.get("artifacts", {}).get("root") or f"sources/evaluations/runs/{record['evaluation_id']}")
    safe_clean_run_dir(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run-record-input.json").write_text(json.dumps(record, indent=2) + "\n")

    protocol = evaluation_protocol(record, pid, args.tool_state, args.tool_use_policy)
    (run_dir / "evaluation-protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
    codex_home = prepare_codex_home(record, pid, run_dir, args.source_codex_home, args.codex_home_root, copy_auth=args.execution_backend == "docker")
    container_preflight = check_container_runtime(
        args.execution_backend,
        args.docker_image,
        run_dir,
        args.allow_host_eval,
        build_image=args.build_docker_image,
        dockerfile=args.dockerfile if args.dockerfile.is_absolute() else ROOT / args.dockerfile,
        codex_home=codex_home,
        cfg=active_tool_config(record, pid),
    )
    if not container_preflight["passed"]:
        print(json.dumps(container_preflight, indent=2))
        return 6
    preflight = preflight_codex(record, codex_home, pid, run_dir, backend=args.execution_backend, docker_image=args.docker_image)
    if not preflight["passed"]:
        print(json.dumps(preflight, indent=2))
        return 3
    if args.prepare_only:
        print(json.dumps({"prepared": True, "profile_id": pid, "codex_home": str(codex_home), "run_dir": str(run_dir)}, indent=2))
        return 0

    setup_code = 0 if args.skip_setup else run_setup(record, run_dir, backend=args.execution_backend, docker_image=args.docker_image, codex_home=codex_home)
    if setup_code != 0:
        capture_diff(record, run_dir)
        print(f"setup failed with exit {setup_code}")
        return 4

    workspace_code = prepare_profile_workspace(record, pid, codex_home, run_dir, protocol, backend=args.execution_backend, docker_image=args.docker_image)
    if workspace_code != 0:
        capture_diff(record, run_dir)
        print(f"profile workspace preparation failed with exit {workspace_code}")
        return 5

    codex_code = run_codex(record, pid, codex_home, run_dir, args.timeout, protocol, backend=args.execution_backend, docker_image=args.docker_image)
    usage_code = extract_usage(run_dir)
    verifier_code = run_verifier(record, run_dir, backend=args.execution_backend, docker_image=args.docker_image, codex_home=codex_home)
    capture_diff(record, run_dir)
    audit_code = audit(run_dir / "run-record-input.json", run_dir)

    provider_usage: dict[str, Any] = {}
    provider_usage_path = run_dir / "provider-usage.json"
    if provider_usage_path.exists():
        try:
            provider_usage = json.loads(provider_usage_path.read_text())
        except json.JSONDecodeError:
            provider_usage = {}

    summary = {
        "evaluation_id": record.get("evaluation_id"),
        "profile_id": pid,
        "codex_exit_code": codex_code,
        "execution_backend": args.execution_backend,
        "containerized_codex_solve": args.execution_backend == "docker",
        "evaluation_protocol": protocol,
        "provider_usage_extract_exit_code": usage_code,
        "verifier_exit_code": verifier_code,
        "tool_isolation_audit_exit_code": audit_code,
        "accepted": codex_code == 0 and usage_code == 0 and verifier_code == 0 and audit_code == 0,
        "token_usage": {
            "fresh_input_tokens": provider_usage.get("fresh_input_tokens"),
            "cached_input_tokens": provider_usage.get("cached_input_tokens"),
            "output_tokens": provider_usage.get("output_tokens"),
            "reasoning_tokens": provider_usage.get("reasoning_tokens"),
            "total_provider_tokens": provider_usage.get("total_provider_tokens"),
        },
        "run_dir": str(run_dir),
    }
    (run_dir / "runner-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if summary["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
