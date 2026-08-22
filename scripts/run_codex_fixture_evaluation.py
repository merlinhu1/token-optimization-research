#!/usr/bin/env python3
"""Run a Codex fixture evaluation with deterministic per-lane tool isolation.

This runner is intentionally stricter than prompt-only isolation. It creates a
fresh CODEX_HOME for the active profile, writes only the allowed Codex config for
that lane, preflights MCP visibility, captures raw Codex artifacts, and audits
for forbidden tool surfaces before a run can be accepted.
"""
from __future__ import annotations

import argparse
import copy
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
CLAUDE_HOST_EXECUTABLE = Path(os.environ.get("TOKEN_EVAL_CLAUDE_EXECUTABLE", "/opt/data/.local/bin/claude"))
CLAUDE_CONTAINER_BIN = Path("/opt/data/claude-entry/claude")
CLAUDE_OPENROUTER_ENV_FILE = Path(os.environ.get("TOKEN_EVAL_CLAUDE_OPENROUTER_ENV", "/opt/data/home/.config/claude-code/openrouter.env"))
CLAUDE_ACCOUNT_HOME_ENV = "TOKEN_EVAL_CLAUDE_ACCOUNT_HOME"
OPENCODE_BIN = Path(os.environ.get("TOKEN_EVAL_OPENCODE_EXECUTABLE", "/opt/data/.local/bin/opencode"))
OPENCODE_BIN_V2 = Path("/opt/data/tool-candidates/opencode-runtime-v2/opencode.exe")
OPENCODE_BIN_SHA256 = "7c4d91c84d2bfdeabb59257e3490c5e5acb08f2aacb3e42f3ddc296a1c3f1aca"
OPENCODE_ADAPTER = "{repository_root}/scripts/opencode_workflow_adapter.py"
OPENCODE_ADAPTER_V2 = Path("/opt/data/tool-candidates/opencode-adapter-v2/opencode_workflow_adapter.py")
OPENCODE_ADAPTER_V3 = Path("/opt/data/tool-candidates/opencode-adapter-v3/opencode_workflow_adapter.py")
OPENCODE_ADAPTER_V4 = Path("/opt/data/tool-candidates/opencode-adapter-v4/opencode_workflow_adapter.py")
OPENCODE_ADAPTER_V5 = Path("/opt/data/tool-candidates/opencode-adapter-v5/opencode_workflow_adapter.py")
OPENCODE_ADAPTER_V6 = Path("/opt/data/tool-candidates/opencode-adapter-v6/opencode_workflow_adapter.py")
OPENCODE_ADAPTER_V7 = Path("/opt/data/tool-candidates/opencode-adapter-v7/opencode_workflow_adapter.py")
OPENCODE_ADAPTER_V8 = Path("/opt/data/tool-candidates/opencode-adapter-v8/opencode_workflow_adapter.py")
OPENCODE_ADAPTER_V9 = Path("/opt/data/tool-candidates/opencode-adapter-v9/opencode_workflow_adapter.py")
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
    "dcp",
    "sdl-mcp",
    "repowise",
]
BASELINE_CODEX_NO_MCP_PROFILES = {"baseline-codex-no-mcp"}
PROFILE_TOOL_CONFIG_OVERRIDES = {
    "retrieval-sdl-mcp-codex-product-v1": "sdl-mcp-codex-product-v1",
    "retrieval-sdl-mcp-opencode-product-v1": "sdl-mcp-opencode-product-v1",
    "headroom-default-codex": "headroom",
    "terminal-headroom": "headroom-proxy-only",
    "terminal-tokenjuice-codex-hook-v1": "tokenjuice-codex-hook-v1",
    "terminal-rtk-codex-instructions-v1": "rtk-codex-instructions-v1",
    "terminal-rtk-claude-code-hook-v1": "rtk-claude-code-hook-v1",
    "retrieval-cartog-claude-code-product-v1": "cartog-claude-code-product-v1",
    "behavior-caveman-claude-code-skill-v1": "caveman",
    "retrieval-codegraph-claude-code-mcp-v1": "codegraph-claude-code-mcp-v1",
    "codescope-claude-code-mcp-v1": "codescope-claude-code-mcp-v1",
    "retrieval-graphify-claude-code-skill-v1": "graphify-claude-code-skill-v1",
    "integrated-leanctx-claude-code-hybrid-v1": "leanctx-claude-code-hybrid-v1",
    "terminal-lowfat-claude-code-hook-v1": "lowfat-claude-code-hook-v1",
    "artifact-ponytail-claude-code-plugin-v1": "ponytail",
    "retrieval-serena-claude-code-mcp-v1": "serena-claude-code-mcp-v1",
    "retrieval-sigmap-claude-code-mcp-v1": "sigmap-claude-code-mcp-v1",
    "terminal-snip-claude-code-hook-v1": "snip-claude-code-hook-v1",
    "integrated-token-savior-claude-code-product-v1": "token-savior-claude-code-product-v1",
    "terminal-tokenjuice-claude-code-hook-v1": "tokenjuice-claude-code-hook-v1",
    "retrieval-jcodemunch-claude-code-mcp-v1": "jcodemunch-claude-code-mcp-v1",
    "retrieval-sdl-mcp-claude-code-product-v1": "sdl-mcp-codex-product-v1",
    "terminal-snip-codex-hook-v1": "snip-codex-hook-v1",
    "retrieval-graphify-codex-skill-v1": "graphify-codex-skill-v1",
    "retrieval-codegraph-codex-mcp-v1": "codegraph-codex-mcp-v1",
    "integrated-leanctx-codex-hybrid-v1": "leanctx-codex-hybrid-v1",
    "retrieval-jcodemunch-opencode-product-v1": "jcodemunch-opencode-product-v1",
    "integrated-leanctx-opencode-hybrid-v1": "leanctx-opencode-hybrid-v1",
    "integrated-leanctx-opencode-hybrid-v2": "leanctx-opencode-hybrid-v1",
    "retrieval-sigmap-opencode-product-v1": "sigmap-opencode-product-v1",
    "artifact-ponytail-opencode-plugin-v1": "ponytail-opencode-plugin-v1",
    "behavior-caveman-opencode-plugin-v1": "caveman-opencode-plugin-v1",
    "terminal-lowfat-opencode-plugin-v1": "lowfat-opencode-plugin-v1",
    "context-dcp-opencode-plugin-v1": "dcp-opencode-plugin-v1",
    "retrieval-cartog-codex-product-v2": "cartog-codex-product-v2",
    "codescope-codex-product-v1": "codescope-codex-product-v1",
    "swarmvault-codex-product-v1": "swarmvault-codex-product-v1",
    "retrieval-serena-codex-mcp-v1": "serena-codex-mcp-v1",
    "retrieval-sigmap-codex-live-v1": "sigmap-codex-live-v1",
    "integrated-token-savior-mcp-v1": "token-savior-mcp-v1",
    "integrated-token-savior-codex-product-v2": "token-savior-codex-product-v2",
    "retrieval-jcodemunch-codex-mcp-v2": "jcodemunch-codex-mcp-v2",
    "stack-tokenjuice-jcodemunch-mcp": "tokenjuice-jcodemunch-mcp-stack",
    "artifact-ponytail-codex-plugin-v1": "ponytail-codex-plugin-v1",
    "behavior-caveman-codex-skill-v1": "caveman-codex-skill-v1",
    "runtime-opencode-codex-product-v1": "opencode-codex-product-v1",
    "baseline-opencode-openrouter-no-mcp": "opencode-openrouter-product-v1",
    "terminal-tokenjuice-opencode-plugin-v2": "tokenjuice-opencode-plugin-v2",
    "retrieval-serena-opencode-mcp-v1": "serena-opencode-mcp-v1",
    "terminal-snip-opencode-plugin-v2": "snip-opencode-plugin-v2",
    "retrieval-cartog-opencode-product-v2": "cartog-opencode-product-v2",
    "integrated-headroom-opencode-product-v3": "headroom-opencode-product-v3",
    "codescope-opencode-product-v1": "codescope-opencode-product-v1",
    "swarmvault-opencode-product-v1": "swarmvault-opencode-product-v1",
    "retrieval-graphify-opencode-product-v1": "graphify-opencode-product-v1",
    "terminal-rtk-opencode-plugin-v1": "rtk-opencode-plugin-v1",
    "retrieval-codegraph-opencode-mcp-v1": "codegraph-opencode-mcp-v1",
    "retrieval-repowise-codex-product-v2": "repowise-codex-product-v2",
    "retrieval-repowise-opencode-product-v2": "repowise-opencode-product-v2",
}
CODEGRAPH_BIN = Path("/opt/data/tool-candidates/codegraph/dist/bin/codegraph.js")
CARTOG_ROOT = Path("/opt/data/tool-candidates/cartog")
CARTOG_BIN = CARTOG_ROOT / "target" / "release" / "cartog"
CARTOG_COMMIT = "890d15b66b523841290a63e431a31b6f6438fc4b"
CARTOG_PRODUCT_INSTALLER = "{repository_root}/scripts/install_cartog_codex_product.py"
CODESCOPE_RELEASE_ROOT = Path("/opt/data/tool-candidates/codescope-release-v0.8.12")
CODESCOPE_BIN = CODESCOPE_RELEASE_ROOT / "codescope"
CODESCOPE_SURREAL_BIN = CODESCOPE_RELEASE_ROOT / "surreal"
CODESCOPE_NEUTRAL_MCP_SOURCE = ROOT / "scripts" / "run_codescope_neutral_mcp.py"
CODESCOPE_NEUTRAL_MCP = "{repository_root}/scripts/run_codescope_neutral_mcp.py"
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
LEANCTX_BINARY = Path("/opt/data/bin/lean-ctx")
LEANCTX_ROOT = Path("/opt/data/tool-candidates/lean-ctx")
PONYTAIL_ROOT = Path("/opt/data/tool-candidates/ponytail")
DCP_ROOT = Path("/opt/data/tool-candidates/opencode-dcp")
HEADROOM_ROOT = Path("/opt/data/tool-candidates/headroom")
HEADROOM_WHEEL = HEADROOM_ROOT / "dist" / "headroom_ai-0.28.0-cp310-abi3-linux_x86_64.whl"
HEADROOM_OPENCODE_PLUGIN = HEADROOM_ROOT / "plugins" / "opencode" / "dist" / "entry.opencode.js"
HEADROOM_OPENCODE_PLUGIN_CHUNK = HEADROOM_ROOT / "plugins" / "opencode" / "dist" / "chunk-2K2XKBFN.js"
UVX_SHIM = Path("/opt/data/tool-candidates/uv-shims/uvx")
TOKEN_SAVIOR_WHEEL = TOKEN_SAVIOR_ROOT / "dist" / "token_savior_recall-4.4.1-py3-none-any.whl"
GRAPHIFY_WHEEL = GRAPHIFY_ROOT / "dist" / "graphifyy-0.9.1-py3-none-any.whl"
JCODEMUNCH_WHEEL = JCODEMUNCH_ROOT / "dist" / "jcodemunch_mcp-1.108.114-py3-none-any.whl"
JCODEMUNCH_COMMIT = "fbc14e40c7057ebc6d718fb48083d30522afe15f"
JCODEMUNCH_GUIDANCE_INSTALLER = "{repository_root}/scripts/install_jcodemunch_codex_guidance.py"
REPOWISE_ROOT = Path("/opt/data/tool-candidates/repowise")
REPOWISE_WHEEL = Path("/opt/data/tool-candidates/repowise-wheel/repowise-0.39.0-py3-none-any.whl")
SNIP_BIN = SNIP_ROOT / "snip"
UV_BIN = Path("/opt/data/opt/uv/uv")
RTK_BIN = Path("/opt/data/tool-candidates/rtk/target/release/rtk")
PONYTAIL_ROOT = Path("/opt/data/tool-candidates/ponytail")
NODE_TOOLCHAIN_ROOT = Path("/opt/data/opt/node-v24.18.0-linux-x64")
NODE_BIN = NODE_TOOLCHAIN_ROOT / "bin" / "node"
NPX_BIN = NODE_TOOLCHAIN_ROOT / "bin" / "npx"
SDL_MCP_ROOT = Path("/opt/data/tool-candidates/sdl-mcp")
SDL_MCP_INSTALL_HOME = Path("/opt/data/tool-candidates/sdl-mcp-install-home")
SDL_MCP_MAIN = SDL_MCP_ROOT / "dist" / "main.js"
SDL_MCP_CLI = SDL_MCP_ROOT / "dist" / "cli" / "index.js"
SDL_MCP_NATIVE = SDL_MCP_ROOT / "node_modules/sdl-mcp-native-linux-x64-gnu/sdl-mcp-native.linux-x64-gnu.node"
SDL_MCP_LADYBUG = SDL_MCP_ROOT / "node_modules/@ladybugdb/core-linux-x64/lbugjs.node"
PONYTAIL_COMMIT = "40e50d9e03242aa5dd53ac771950f9127362b25f"
CAVEMAN_COMMIT = "0d95a81d35a9f2d123a5e9430d1cfc43d55f1bb0"
PONYTAIL_MARKETPLACE_PREPARER = "{repository_root}/scripts/prepare_pinned_codex_marketplace.py"
CLAUDE_MARKETPLACE_PREPARER = "{repository_root}/scripts/prepare_pinned_claude_marketplace.py"
CODEX_PLUGIN_HOOK_TRUSTER = "{repository_root}/scripts/trust_codex_plugin_hooks.py"
CLAUDE_README_HOOK_INSTALLER = "{repository_root}/scripts/install_claude_readme_hooks.py"
SERENA_CODEX_HOOK_INSTALLER = "{repository_root}/scripts/install_serena_codex_hooks.py"
PINNED_UVX_RUNNER = "{repository_root}/scripts/run_pinned_uvx.py"

# Exact releases selected for the 2026-08-22 treatment batch. Tuple fields are:
# directory, release artifact, artifact sha256, official guide, guide sha256, commit.
BATCH_RELEASE_ROOT = Path("/opt/data/tool-candidates/releases")
BATCH_RELEASES = {
    "headroom": ("headroom-0.36.3", "artifacts/headroom_ai-0.36.3-cp310-abi3-manylinux_2_28_x86_64.whl", "a3fb71716b62da07f0900b0a2d82c1141063da8727fcbc91b3a9fd7c3baba1e8", "source/README.md", "fee6ad17c8df5d697c3b153193d6655a18c450e48d9fedb7ba9c1d4765884893", "87e71dd10057ff3cbe826bde617682971339e4f8"),
    "tokenjuice": ("tokenjuice-0.8.1", "artifacts/tokenjuice-0.8.1.tgz", "73ab34ce0d5c0bf3abf1e3b0d2702d762811806bdd573623fdfd26e3d4830c81", "source/README.md", "e5c9807e8b6ac3cc2a6e864c89af468dd9b28ea4096d641a5a223d1b0daf798d", "49bdcf1755833ff1e02e44e6e7fe91c0fb44c16e"),
    "rtk": ("rtk-0.45.0", "artifacts/rtk-x86_64-unknown-linux-musl.tar.gz", "c4c036fbf181fc55ef329786c8c17e0d427972b053b825944d968a6aafef1ba4", "source/README.md", "413b3c684d00c36d6517b5f45fa02dc10c83a2a5c22f0e18dea6288e3aa9490a", "b34be37caf3796b69a50952a28e60e32b5daad43"),
    "snip": ("snip-0.24.1", "artifacts/snip_0.24.1_linux_amd64.tar.gz", "6f230ab6d66885b73f7de4fd32399cb6a60f64de92133dc25532cccbfb930985", "source/README.md", "710e49a20580910a7d0e0123b389f64c1f4ceaec574df1e6870386fc4101a087", "18a57bc9dc4499f1a00b9c8ff799e982ba25ceba"),
    "graphify": ("graphify-0.9.48", "artifacts/graphifyy-0.9.48-py3-none-any.whl", "4f745d72d6c5165ef7132bf8b2819ef59707aa70cd99efd3a4fbc8c4ba43b4b9", "source/README.md", "49db070139e8ffcdf78efcf2fe5b213cc6a9c5c91e37e33960cf2d22df1b76a4", "b2cd36267456c166788c95be6e68574064a92a42"),
    "leanctx": ("lean-ctx-3.9.19", "artifacts/lean-ctx-x86_64-unknown-linux-gnu.tar.gz", "f2fce32af52c2b7b2681ce8b14de9e67f55e1daf08e1513f47ff8dbb01eb0e58", "source/README.md", "0e53184df357ed64b789301c27e718b3494cc15bd2b3fc8c81eba709cacb02e4", "8a3d23b317c98b39704543c9acb8b7cc8992c63d"),
    "cartog": ("cartog-0.32.2", "artifacts/cartog-x86_64-unknown-linux-gnu.tar.gz", "c6f330b51488cd8fb87dffa4e561b2b90b00f8fb07d53373310a09c1940c45e9", "source/README.md", "e2155e82d421dc1cedbfb7ce4c268218b2c70a3e708cfa0f0612f052010bcccf", "2eeb61a3eb57f8011573bb3117aa02c5b6906b08"),
    "codescope": ("codescope-0.8.12", "artifacts/codescope-v0.8.12-x86_64-unknown-linux-gnu.tar.gz", "ee353ad91cd23c089545dba0e1277e4f0fc6d21ca78fae1d7e639677f33fd8bc", "source/README.md", "3540e5e7c23735b5fb273d2f369a2fe73d5df86715e819f2d79f920886a95e1b", "d8e58d83e920c46a27e8b2e72c1e85a16c6af3fd"),
    "swarmvault": ("swarmvault-3.20.0", "artifacts/swarmvaultai-cli-3.20.0.tgz", "aa1ba3fe8b8d61ea5b76c33a25290b361ed31a589cf67cbe3251166258b5546f", "source/README.md", "b7085a208f7d62cbb044d5f7d38cc57205a4a13406957700759bc8646be50989", "4ce0c7cb545c669f3cd35fc6d0300c6b088a52ea"),
    "serena": ("serena-1.7.0", "artifacts/serena_agent-1.7.0-py3-none-any.whl", "6dbf1459670d96fb0595f84932adef34260a6fe14ba5135b901fdb3c8c76e891", "source/docs/02-usage/030_clients.md", "62b271277e5ba7783695646da04cab1cc9618e63d066b35e31b731a280f8481e", "949a27ef1e5fda1a6e7b561e777bcece345c6ffd"),
    "sigmap": ("sigmap-8.28.0", "artifacts/sigmap-8.28.0.tgz", "9cd40a02c852ea76cd24575561a416d6b965bf737d8af1af4f20030e7f8e719d", "source/README.md", "5c6d0392b5dcbaddf9b2b5d5717c6ed218237aff8c837ba60bab0e7d54c3fe82", "3313c3a4e88722e134e5747663c02d5db5ad3032"),
    "token-savior": ("token-savior-4.21.0", "artifacts/token_savior_recall-4.21.0-py3-none-any.whl", "36529b132d658225ad6df7c9ec4ca0cbcf0fb48ebb0054099a0284c793fc9363", "source/README.md", "e78f621c63cf9795537cd8e76f7ea155af1752c7d0b408621e411e848f141f30", "1e5984b452c5b98e6376a7250b3213f5c3500626"),
    "ponytail": ("ponytail-4.9.0", "artifacts/ponytail-v4.9.0-source.tar.gz", "7f45b3fab0b92ae5ff95c4608acda9f6ee2f0374b0122cba046289167d0cd256", "source/README.md", "743044a29ec74de597baa1ac492f874c08d749bf0510bd81663a7637681516cf", "0a4dd63ad4541f4f655c4108a295916f3c1d8fda"),
    "caveman": ("caveman-2.2.0", "artifacts/caveman-v2.2.0-source.tar.gz", "3081846d48315a6b864eb0c6d578b516c2c47cf8ca0cd927d9e0d7875f5d89aa", "source/INSTALL.md", "3eac1c3f79c09a8424669aca1b44211350b2567fd2504957081dfe55893bd9ce", "9aa63945a349bef17206540650db48c30fafbdf2"),
    "codegraph": ("codegraph-1.5.0", "artifacts/codegraph-linux-x64.tar.gz", "2ba65e87a1210b706bb1e67d5e48b5fc4a1935e43dbb3fb5f31c5597840d2e58", "source/README.md", "ef12f20aa127d8a508a41433f47a67c9efebaff18ac645acc6d851a8fe3809fa", "ea72e1b190921232aa7bd02e96bef5bbe4fe0ab6"),
    "jcodemunch": ("jcodemunch-mcp-1.108.290", "artifacts/jcodemunch_mcp-1.108.290-py3-none-any.whl", "9408996309f127bd3f14c8c9c19c73e9b069ed845561512c3cdda92406fa700c", "source/CLIENTS.md", "19e87ba818c8efadb3f26d728bfb33ecdd5e262eac48cade9cccea221d73335d", "9e76d6320c017b774d54bb31d79dd4b8a5876aff"),
    "repowise": ("repowise-0.45.0", "artifacts/repowise-0.45.0-py3-none-any.whl", "c86ec4a505b16dfe0a6df5366aae9908a0a3ef6fabb204c883a6faf94a62492a", "source/docs/agent/CODEX.md", "09829e1ebfe734235296f633a44b59a235bee2c75bdafd9b50dab67671ecf416", "e2bb8a2e4eff3d00005a602ac65a8e4be7daa4a3"),
}


def _batch_path(name: str, field: int) -> Path:
    return BATCH_RELEASE_ROOT / BATCH_RELEASES[name][0] / BATCH_RELEASES[name][field]


def _pin_batch_release(tool_id: str, release_name: str, *runtime_paths: Path) -> None:
    cfg = TOOL_CONFIGS[tool_id]
    source = BATCH_RELEASE_ROOT / BATCH_RELEASES[release_name][0] / "source"
    artifact = _batch_path(release_name, 1)
    guide = _batch_path(release_name, 3)
    local_helpers = [path for path in cfg.get("mounts", []) if "{repository_root}" in str(path)]
    # A batch runtime directory holds the tool's own executable, so it has to be on the lane
    # PATH; before the batch move these binaries lived in /opt/data/bin and were found there.
    runtime_dirs: list[str] = []
    for path in runtime_paths:
        if not path.is_dir():
            continue
        # npm puts launchers in node_modules/.bin; the runtime root holds only the tree.
        npm_bin = path / "node_modules" / ".bin"
        runtime_dirs.append(str(npm_bin if npm_bin.is_dir() else path))
    # A helper passed as a runtime path is usually also named in the profile's own mounts, and
    # Docker rejects a run outright when the same target is bound twice, so the assembled list
    # has to be unique. dict.fromkeys keeps first-seen order.
    def _unique(*groups: list[str]) -> list[str]:
        return list(dict.fromkeys(value for group in groups for value in group))

    runtime_texts = [str(path) for path in runtime_paths]
    cfg.update({
        "path_entries": _unique(cfg.get("path_entries", []), runtime_dirs),
        "mounts": _unique([str(source), str(artifact)], runtime_texts, local_helpers),
        "required_source_artifacts": _unique([str(source), str(artifact), str(guide)], runtime_texts, local_helpers),
        "clean_source_roots": [str(source)],
        "artifact_identities": [
            {"path": str(artifact), "sha256": BATCH_RELEASES[release_name][2], "kind": "official-release-artifact"},
            {"path": str(guide), "sha256": BATCH_RELEASES[release_name][4], "kind": "official-install-guide"},
        ],
        "tool_manifest_identity": "current-file-v1",
    })

TOOL_CONFIGS: dict[str, dict[str, Any]] = {
    "sdl-mcp-codex-product-v1": {
        "display_name": "SDL-MCP 0.13.2 official Codex setup",
        "lane_name": "retrieval-sdl-mcp-codex-product-v1",
        "surface": "retrieval/context+mcp+codex-guidance+codex-hooks",
        "mcp_server": "sdl-mcp",
        "allowed_terms": ["sdl-mcp", "sdl", "runtimeExecute", "sdl.context", "sdl.retrieve", "sdl.workflow"],
        "data_dir_name": "sdl-mcp-codex-product-v1",
        "mcp_command": str(NODE_BIN),
        "mcp_args": [str(SDL_MCP_MAIN), "serve", "--stdio"],
        "env": {
            "SDL_CONFIG": "{tool_data_dir}/sdlmcp.config.json",
            "SDL_CONFIG_HOME": "{tool_data_dir}",
            "SDL_GRAPH_DB_PATH": "{tool_data_dir}/sdl-mcp-graph.lbug",
            "SDL_MCP_SKIP_SETUP_WIZARD": "1",
        },
        "mounts": [str(SDL_MCP_ROOT), str(SDL_MCP_INSTALL_HOME)],
        "diff_exclude_paths": [
            "AGENTS.md", "CODEX.md", "SDL.md", "codex-mcp-config.json", ".codex",
        ],
        "codex_features": {"hooks": True},
        "host_integration": {
            "install_commands": [
                ["/bin/bash", "-lc", "set -euo pipefail; mkdir -p {codex_home}/home/.cache/sdl-mcp; cp -a /opt/data/tool-candidates/sdl-mcp-install-home/.cache/sdl-mcp/models {codex_home}/home/.cache/sdl-mcp/"],
                [str(NODE_BIN), str(SDL_MCP_CLI), "init", "-y", "--repo-path", "{repo}", "--client", "codex", "--enforce-agent-tools", "--auto-index", "--config", "{tool_data_dir}/sdlmcp.config.json"],
            ],
            "verify_commands": [
                [str(NODE_BIN), str(SDL_MCP_CLI), "version", "--config", "{tool_data_dir}/sdlmcp.config.json"],
                [str(NODE_BIN), str(SDL_MCP_CLI), "doctor", "--config", "{tool_data_dir}/sdlmcp.config.json"],
            ],
            "required_files": [
                str(SDL_MCP_ROOT / "package.json"), str(SDL_MCP_ROOT / "package-lock.json"),
                str(SDL_MCP_CLI), str(SDL_MCP_MAIN), str(SDL_MCP_NATIVE), str(SDL_MCP_LADYBUG),
                "{tool_data_dir}/sdlmcp.config.json", "{codex_home}/config.toml",
                "{repo}/AGENTS.md", "{repo}/CODEX.md", "{repo}/SDL.md",
                "{repo}/.codex/config.toml", "{repo}/.codex/hooks.json",
                "{repo}/.codex/hooks/load-sdl-skill.mjs", "{repo}/.codex/hooks/force-sdl-mcp.mjs",
            ],
            "timeout_seconds": 1800,
        },
        "artifact_identities": [
            {"path": str(SDL_MCP_ROOT / "package.json"), "sha256": "610be2ef31f79c66c330b3605aa2ceb8bce94fe9cb1e1fada1ee70f6dfd78cd1", "kind": "source-manifest"},
            {"path": str(SDL_MCP_ROOT / "package-lock.json"), "sha256": "c74182a87adc5b7d14a9981a392410cee6eb4b782fa802e77c2e7a055dd55465", "kind": "lockfile"},
            {"path": str(SDL_MCP_MAIN), "sha256": "ce884fc3e1f3191c9a5c8adfaa03d9dab9ea73013b893db6f8ede8355408a4c7", "kind": "compiled-server"},
            {"path": str(SDL_MCP_CLI), "sha256": "b9e33355f5673c730c0e530de2ff7edd8d5dafbe41ea628e072a6446f35fe681", "kind": "compiled-cli"},
            {"path": str(SDL_MCP_NATIVE), "sha256": "b1929acef9c7e2755e5f991265dc64e034b6c200034f422e309a8590bc55869e", "kind": "native-addon"},
            {"path": str(SDL_MCP_LADYBUG), "sha256": "28a59bb37cd9c55d78bf106f8765c6122c27a3308493fc49bc7897cae8eef826", "kind": "ladybug-addon"},
        ],
        "mcp_handshake": {"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 90},
        "default_tool_state": "warm-index",
    },
    "sdl-mcp-opencode-product-v1": {
        "display_name": "SDL-MCP 0.13.2 official OpenCode setup",
        "lane_name": "retrieval-sdl-mcp-opencode-product-v1",
        "surface": "retrieval/context+mcp+opencode-guidance+opencode-plugin",
        "mcp_server": "sdl-mcp",
        "allowed_terms": ["sdl-mcp", "sdl", "runtimeExecute", "sdl.context", "sdl.retrieve", "sdl.workflow"],
        "data_dir_name": "sdl-mcp-opencode-product-v1",
        "mcp_command": str(NODE_BIN),
        "mcp_args": [str(SDL_MCP_MAIN), "serve", "--stdio"],
        "env": {
            "SDL_CONFIG": "{tool_data_dir}/sdlmcp.config.json",
            "SDL_CONFIG_HOME": "{tool_data_dir}",
            "SDL_GRAPH_DB_PATH": "{tool_data_dir}/sdl-mcp-graph.lbug",
            "SDL_MCP_SKIP_SETUP_WIZARD": "1",
        },
        "mounts": [str(SDL_MCP_ROOT), str(SDL_MCP_INSTALL_HOME)],
        "diff_exclude_paths": [
            "AGENTS.md", "OPENCODE.md", "SDL.md", "opencode.json", ".opencode",
        ],
        "host_integration": {
            "install_commands": [
                ["/bin/bash", "-lc", "set -euo pipefail; mkdir -p {codex_home}/home/.cache/sdl-mcp; cp -a /opt/data/tool-candidates/sdl-mcp-install-home/.cache/sdl-mcp/models {codex_home}/home/.cache/sdl-mcp/"],
                [str(NODE_BIN), str(SDL_MCP_CLI), "init", "-y", "--repo-path", "{repo}", "--client", "opencode", "--enforce-agent-tools", "--auto-index", "--config", "{tool_data_dir}/sdlmcp.config.json"],
            ],
            "verify_commands": [
                [str(NODE_BIN), str(SDL_MCP_CLI), "version", "--config", "{tool_data_dir}/sdlmcp.config.json"],
                [str(NODE_BIN), str(SDL_MCP_CLI), "doctor", "--config", "{tool_data_dir}/sdlmcp.config.json"],
            ],
            "required_files": [
                str(SDL_MCP_ROOT / "package.json"), str(SDL_MCP_ROOT / "package-lock.json"),
                str(SDL_MCP_CLI), str(SDL_MCP_MAIN), str(SDL_MCP_NATIVE), str(SDL_MCP_LADYBUG),
                "{tool_data_dir}/sdlmcp.config.json", "{repo}/AGENTS.md", "{repo}/OPENCODE.md",
                "{repo}/SDL.md", "{repo}/opencode.json", "{repo}/.opencode/plugins/enforce-sdl.ts",
            ],
            "timeout_seconds": 1800,
        },
        "artifact_identities": [
            {"path": str(SDL_MCP_ROOT / "package.json"), "sha256": "610be2ef31f79c66c330b3605aa2ceb8bce94fe9cb1e1fada1ee70f6dfd78cd1", "kind": "source-manifest"},
            {"path": str(SDL_MCP_ROOT / "package-lock.json"), "sha256": "c74182a87adc5b7d14a9981a392410cee6eb4b782fa802e77c2e7a055dd55465", "kind": "lockfile"},
            {"path": str(SDL_MCP_MAIN), "sha256": "ce884fc3e1f3191c9a5c8adfaa03d9dab9ea73013b893db6f8ede8355408a4c7", "kind": "compiled-server"},
            {"path": str(SDL_MCP_CLI), "sha256": "b9e33355f5673c730c0e530de2ff7edd8d5dafbe41ea628e072a6446f35fe681", "kind": "compiled-cli"},
            {"path": str(SDL_MCP_NATIVE), "sha256": "b1929acef9c7e2755e5f991265dc64e034b6c200034f422e309a8590bc55869e", "kind": "native-addon"},
            {"path": str(SDL_MCP_LADYBUG), "sha256": "28a59bb37cd9c55d78bf106f8765c6122c27a3308493fc49bc7897cae8eef826", "kind": "ladybug-addon"},
        ],
        "mcp_handshake": {"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 90},
        "default_tool_state": "warm-index",
    },
    "opencode-codex-product-v1": {
        "display_name": "OpenCode CLI 1.18.9",
        "lane_name": "runtime-opencode-codex-product-v1",
        "surface": "replacement-agent-runtime",
        "allowed_terms": ["opencode"],
        "data_dir_name": "opencode-runtime",
        "mounts": [str(OPENCODE_ADAPTER)],
        "executable": str(OPENCODE_BIN),
        "expected_executable_sha256": OPENCODE_BIN_SHA256,
        "binary_mount_target": str(OPENCODE_BIN),
        "codex_wrapper": {
            "command": "/usr/bin/python3",
            "args": [
                str(OPENCODE_ADAPTER),
                "--opencode-binary",
                str(OPENCODE_BIN),
                "--expected-opencode-sha256",
                OPENCODE_BIN_SHA256,
            ],
        },
        "preflight_command": [
            "/usr/bin/python3",
            str(OPENCODE_ADAPTER),
            "--opencode-binary",
            str(OPENCODE_BIN),
            "--expected-opencode-sha256",
            OPENCODE_BIN_SHA256,
            "--probe",
        ],
        "default_tool_state": "native-runtime",
        "tool_manifest_identity": "current-file-v1",
    },
    "lean-ctx": {
        "display_name": "LeanCTX (historical MCP-only partial profile)",
        "lane_name": "retrieval-leanctx",
        "surface": "retrieval/context-mcp-only",
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
    "leanctx-codex-hybrid-v1": {
        "display_name": "LeanCTX official Codex hybrid integration v1",
        "lane_name": "integrated-leanctx-codex-hybrid-v1",
        "surface": "retrieval/context-mcp+shell-output-compression+instructions",
        "mcp_server": "lean-ctx",
        "allowed_terms": ["lean-ctx", "mcp_lean_ctx", "ctx_read", "ctx_search", "ctx_shell", "ctx_graph"],
        "data_dir_name": "leanctx-codex-hybrid-v1",
        "mcp_command": "/opt/data/bin/lean-ctx",
        "mcp_args": [],
        # BASH_ENV is how the shell-hook half reaches a non-interactive shell; lean-ctx doctor
        # names it as the container remedy verbatim. Without it this "hybrid" profile installs
        # only the MCP half and the command-compression it is half-named for never engages.
        "env": {"LEAN_CTX_DATA_DIR": "{tool_data_dir}", "BASH_ENV": "{tool_data_dir}/env.sh"},
        "mounts": ["/opt/data/bin"],
        "diff_exclude_paths": ["AGENTS.md", "LEAN-CTX.md"],
        "host_integration": {
            "install_commands": [
                ["/opt/data/bin/lean-ctx", "init", "--agent", "codex"],
                # `init` registers Codex but writes no shell hook and no env.sh. `setup` is the
                # vendor's own "shell hook, agent hooks/rules, MCP registrations" step, and is
                # the non-proxy way to get the hybrid surface: `wrap` would route the agent
                # through lean-ctx's local proxy and sit between it and the provider, which
                # would compromise the token telemetry this study measures.
                ["/opt/data/bin/lean-ctx", "setup", "--non-interactive", "--yes"],
            ],
            "verify_commands": [["/opt/data/bin/lean-ctx", "--version"]],
            "required_files": [
                "{codex_home}/config.toml",
                "{codex_home}/hooks.json",
                "{codex_home}/instructions.md",
                "{codex_home}/skills/lean-ctx/SKILL.md",
                "{repo}/AGENTS.md",
                "{repo}/LEAN-CTX.md",
            ],
            "timeout_seconds": 300,
        },
        "mcp_handshake": {"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 60},
        "default_tool_state": "warm-index",
        "warmup": {
            "kind": "index",
            "command": ["/opt/data/bin/lean-ctx", "index", "build", "{repo}"],
            "output_name": "lean-ctx-warmup-output.txt",
            "metadata_name": "lean-ctx-warmup-metadata.json",
            "timeout_seconds": 1200,
        },
    },
    "codegraph": {
        "display_name": "CodeGraph (historical no-watch manual profile)",
        "lane_name": "retrieval-codegraph",
        "surface": "retrieval/context-manual-no-watch",
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
    "codegraph-codex-mcp-v1": {
        "display_name": "CodeGraph official Codex MCP with model-runtime PATH",
        "lane_name": "retrieval-codegraph-codex-mcp-v1",
        "surface": "retrieval/context+mcp-live-index",
        "mcp_server": "codegraph",
        "allowed_terms": ["codegraph"],
        "data_dir_name": "codegraph-codex-mcp-v1",
        "mcp_command": "{tool_data_dir}/bin/codegraph",
        "mcp_args": ["serve", "--mcp"],
        "path_entries": ["{tool_data_dir}/bin"],
        "env": {"CODEGRAPH_TELEMETRY": "0"},
        "mounts": ["/opt/data/tool-candidates/codegraph"],
        "diff_exclude_paths": [".codegraph"],
        "host_integration": {
            "home_dot_codex_alias": True,
            "install_commands": [
                ["mkdir", "-p", "{tool_data_dir}/bin"],
                [
                    "/bin/bash",
                    "-lc",
                    (
                        f"printf '%s\\n' '#!/bin/sh' 'exec {CODEGRAPH_BIN} \"$@\"' "
                        "> {tool_data_dir}/bin/codegraph && chmod 755 {tool_data_dir}/bin/codegraph"
                    ),
                ],
                ["{tool_data_dir}/bin/codegraph", "install", "--target", "codex", "--location", "global", "--yes"],
            ],
            "verify_commands": [["{tool_data_dir}/bin/codegraph", "--version"]],
            "required_files": [
                "{tool_data_dir}/bin/codegraph",
                "{codex_home}/config.toml",
                "{codex_home}/AGENTS.md",
            ],
        },
        "preflight_command": ["/bin/bash", "-lc", "command -v codegraph && codegraph --version"],
        "mcp_handshake": {"required": True, "method": "initialize-and-tools-list"},
        "default_tool_state": "warm-index",
        "warmup": {
            "kind": "index",
            "command": ["{tool_data_dir}/bin/codegraph", "init", "{repo}"],
            "cleanup_paths": [".codegraph"],
            "output_name": "codegraph-warmup-output.txt",
            "metadata_name": "codegraph-warmup-metadata.json",
            "timeout_seconds": 1200,
        },
    },
    "repowise-codex-product-v2": {
        "display_name": "RepoWise 0.39.0 provider-backed Codex MCP, hooks, and guidance",
        "lane_name": "retrieval-repowise-codex-product-v2",
        "surface": "retrieval-context+mcp+codex-hooks+product-guidance+provider-backed-index",
        "mcp_server": "repowise",
        "allowed_terms": ["repowise"],
        "data_dir_name": "repowise-codex-product-v2",
        "mcp_command": "{tool_data_dir}/venv/bin/repowise",
        "mcp_args": ["mcp"],
        "path_entries": ["{tool_data_dir}/venv/bin"],
        "env": {"REPOWISE_PROVIDER": "codex_cli"},
        "mounts": [str(REPOWISE_ROOT), str(REPOWISE_WHEEL)],
        "diff_exclude_paths": [".repowise", ".mcp.json", ".codex", ".vscode", ".claude", "AGENTS.md"],
        "codex_features": {"hooks": True},
        "host_integration": {
            # repowise detects Codex by probing ~/.codex, so the lane-private CODEX_HOME has to
            # be aliased there or the Codex half of `init` silently does nothing.
            "home_dot_codex_alias": True,
            "install_commands": [
                [str(UV_BIN), "venv", "{tool_data_dir}/venv", "--python", "python3"],
                [str(UV_BIN), "pip", "install", "--python", "{tool_data_dir}/venv/bin/python", str(REPOWISE_WHEEL)],
                ["{tool_data_dir}/venv/bin/repowise", "init", "--yes", "--provider", "codex_cli", "--no-prose", "--no-claude-md", "--codex", "--agents", "--no-workspace", "{repo}"],
            ],
            "verify_commands": [["{tool_data_dir}/venv/bin/repowise", "--version"]],
            "required_files": [
                "{tool_data_dir}/venv/bin/repowise",
                "{repo}/.repowise/wiki.db",
                "{repo}/.repowise/config.yaml",
                "{repo}/.mcp.json",
                "{repo}/.codex/config.toml",
                "{repo}/.codex/hooks.json",
                "{repo}/AGENTS.md",
            ],
            "timeout_seconds": 3600,
        },
        "preflight_command": ["{tool_data_dir}/venv/bin/repowise", "--version"],
        "mcp_handshake": {"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 180},
        "artifact_identities": [
            {"path": str(REPOWISE_WHEEL), "sha256": "e7d3068856a45a3d0501b84e6f52db24521512803a07881cdf145da546d932b4", "kind": "python-wheel"},
            {"path": str(REPOWISE_ROOT / "README.md"), "sha256": "44ed3725616544a8d4eb4695c99e33c8bd28ce2bfde4c12134d1fde0e1d65a3a", "kind": "product-guidance-source"},
        ],
        "tool_manifest_identity": "current-file-v1",
        "default_tool_state": "warm-index+official-codex-hooks+product-guidance",
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
        "diff_exclude_paths": [".fastembed_cache", ".codescope"],
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
        "display_name": "Graphify (historical optional MCP-only ablation)",
        "lane_name": "retrieval-graphify",
        "surface": "retrieval/context-optional-mcp",
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
        "diff_exclude_paths": ["graphify-out"],
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
    "graphify-codex-skill-v1": {
        "display_name": "Graphify official Codex skill and always-on graph policy v1",
        "lane_name": "retrieval-graphify-codex-skill-v1",
        "surface": "retrieval/context+codex-skill+instructions+pretooluse-hook",
        "allowed_terms": ["graphify"],
        "data_dir_name": "graphify-codex-skill-v1",
        "executable": "{tool_data_dir}/bin/graphify",
        "path_entries": ["{tool_data_dir}/bin"],
        "env": {"GRAPHIFY_OUT": "graphify-out"},
        "mounts": [str(GRAPHIFY_ROOT), str(GRAPHIFY_WHEEL)],
        "diff_exclude_paths": ["graphify-out", "AGENTS.md", ".codex"],
        "codex_features": {"hooks": True, "multi_agent": True},
        "host_integration": {
            "home_dot_codex_alias": True,
            "install_commands": [
                [str(UV_BIN), "venv", "{tool_data_dir}/venv", "--python", "python3"],
                [str(UV_BIN), "pip", "install", "--python", "{tool_data_dir}/venv/bin/python", str(GRAPHIFY_WHEEL)],
                ["/bin/mkdir", "-p", "{tool_data_dir}/bin"],
                ["/bin/ln", "-s", "{tool_data_dir}/venv/bin/graphify", "{tool_data_dir}/bin/graphify"],
                ["{tool_data_dir}/venv/bin/graphify", "install", "--platform", "codex"],
            ],
            "verify_commands": [["{tool_data_dir}/venv/bin/graphify", "--help"]],
            "required_files": [
                "{tool_data_dir}/venv/bin/graphify",
                "{tool_data_dir}/bin/graphify",
                "{codex_home}/skills/graphify/SKILL.md",
            ],
            "timeout_seconds": 600,
        },
        "default_tool_state": "warm-index",
        "warmup": {
            "kind": "official-full-graph-and-codex-policy",
            "command": [
                "/bin/bash",
                "-lc",
                "set -euo pipefail; graphify update {repo} --force; cd {repo}; graphify codex install; test -f AGENTS.md; test -f .codex/hooks.json",
            ],
            "cleanup_paths": ["graphify-out", "AGENTS.md", ".codex"],
            "output_name": "graphify-warmup-output.txt",
            "metadata_name": "graphify-warmup-metadata.json",
            "timeout_seconds": 3600,
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
        "display_name": "jcodemunch MCP (historical uv-launcher profile)",
        "lane_name": "retrieval-jcodemunch-mcp",
        "surface": "retrieval/context-neutral-availability",
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
        "display_name": "Snip (historical PATH-only profile)",
        "lane_name": "terminal-snip",
        "surface": "terminal/tool-output-compaction-cli-only",
        "allowed_terms": ["snip"],
        "data_dir_name": "snip",
        "executable": str(SNIP_BIN),
        "path_entries": [str(SNIP_BIN.parent)],
        "mounts": [str(SNIP_ROOT)],
        "env": {"SNIP_TELEMETRY": "0"},
        "preflight_command": ["snip", "--version"],
        "default_tool_state": "cold-cli",
    },
    "snip-codex-hook-v1": {
        "display_name": "Snip Codex PreToolUse hook v1",
        "lane_name": "terminal-snip-codex-hook-v1",
        "surface": "codex-pre-tool-use-hook/terminal-output-compaction",
        "allowed_terms": ["snip"],
        "data_dir_name": "snip-codex-hook-v1",
        "executable": str(SNIP_BIN),
        "path_entries": [str(SNIP_BIN.parent)],
        "mounts": [str(SNIP_ROOT)],
        "env": {"SNIP_TELEMETRY": "0"},
        "codex_features": {"hooks": True},
        "host_integration": {
            "home_dot_codex_alias": True,
            "install_commands": [["snip", "init", "--agent", "codex"]],
            "verify_commands": [["snip", "hook-audit"]],
            "required_files": ["{codex_home}/hooks.json", "{codex_home}/config.toml"],
        },
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
        "display_name": "TokenJuice (historical CLI-only profile)",
        "lane_name": "terminal-tokenjuice",
        "surface": "terminal/tool-output-compaction-cli-only",
        "allowed_terms": ["tokenjuice"],
        "data_dir_name": "tokenjuice",
        "executable": str(TOKENJUICE_BIN),
        "path_entries": [str(TOKENJUICE_BIN.parent)],
        "mounts": [str(TOKENJUICE_ROOT)],
        "env": {"TOKENJUICE_TELEMETRY": "0"},
        "preflight_command": ["tokenjuice", "--version"],
        "default_tool_state": "cold-cli",
    },
    "tokenjuice-codex-hook-v1": {
        "display_name": "TokenJuice Codex hook v1",
        "lane_name": "terminal-tokenjuice-codex-hook-v1",
        "surface": "codex-post-tool-use-hook/terminal-output-compaction",
        "allowed_terms": ["tokenjuice"],
        "data_dir_name": "tokenjuice-codex-hook-v1",
        "executable": str(TOKENJUICE_BIN),
        "path_entries": [str(TOKENJUICE_BIN.parent)],
        "mounts": [str(TOKENJUICE_ROOT)],
        "env": {"TOKENJUICE_TELEMETRY": "0"},
        "codex_features": {"hooks": True},
        "host_integration": {
            "install_commands": [["tokenjuice", "install", "codex"]],
            "verify_commands": [["tokenjuice", "doctor", "codex"]],
            "required_files": ["{codex_home}/hooks.json"],
        },
        "preflight_command": ["tokenjuice", "--version"],
        "default_tool_state": "cold-cli",
    },
    "tokenjuice-jcodemunch-mcp-stack": {
        "display_name": "TokenJuice + jcodemunch MCP",
        "lane_name": "stack-tokenjuice-jcodemunch-mcp",
        "surface": "terminal/tool-output-compaction + retrieval/context",
        "component_tool_ids": ["tokenjuice", "jcodemunch-mcp"],
        "allowed_terms": ["tokenjuice", "jcodemunch", "jcodemunch-mcp"],
        "data_dir_name": "tokenjuice-jcodemunch-mcp-stack",
        "executable": str(TOKENJUICE_BIN),
        "path_entries": [str(TOKENJUICE_BIN.parent)],
        "mcp_server": "jcodemunch",
        "mcp_command": "/bin/bash",
        "mcp_args": [
            "-lc",
            "cd {repo} && exec /opt/data/opt/uv/uv tool run --from /opt/data/tool-candidates/jcodemunch-mcp/dist/jcodemunch_mcp-1.108.114-py3-none-any.whl jcodemunch-mcp serve --transport stdio --log-level ERROR",
        ],
        "mounts": [str(TOKENJUICE_ROOT), str(JCODEMUNCH_ROOT), str(JCODEMUNCH_WHEEL)],
        "env": {
            "TOKENJUICE_TELEMETRY": "0",
            "JCODEMUNCH_LOG_LEVEL": "ERROR",
        },
        "preflight_command": ["tokenjuice", "--version"],
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
            "output_name": "tokenjuice-jcodemunch-warmup-output.txt",
            "metadata_name": "tokenjuice-jcodemunch-warmup-metadata.json",
            "timeout_seconds": 1200,
        },
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
            "mcp>=1.25,<2",
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
        "display_name": "RTK (historical PATH-only profile)",
        "lane_name": "terminal-rtk",
        "surface": "terminal/tool-output-compaction-cli-only",
        "allowed_terms": ["rtk"],
        "data_dir_name": "rtk",
        "executable": str(RTK_BIN),
        "path_entries": [str(RTK_BIN.parent), "/opt"],
        "mounts": [str(RTK_BIN.parent)],
        "env": {"RTK_TELEMETRY": "0"},
        "preflight_command": ["rtk", "--version"],
    },
    "rtk-codex-instructions-v1": {
        "display_name": "RTK Codex global instruction policy v1",
        "lane_name": "terminal-rtk-codex-instructions-v1",
        "surface": "codex-global-instructions/terminal-output-compaction",
        "allowed_terms": ["rtk"],
        "data_dir_name": "rtk-codex-instructions-v1",
        "executable": str(RTK_BIN),
        "path_entries": [str(RTK_BIN.parent), "/opt"],
        "mounts": [str(RTK_BIN.parent)],
        "env": {"RTK_TELEMETRY": "0"},
        "host_integration": {
            "install_commands": [["rtk", "init", "--global", "--codex"]],
            "verify_commands": [["rtk", "init", "--global", "--codex", "--dry-run"]],
            "required_files": ["{codex_home}/AGENTS.md", "{codex_home}/RTK.md"],
        },
        "preflight_command": ["rtk", "--version"],
        "default_tool_state": "active-instruction-layer",
    },
    "rtk-claude-code-hook-v1": {
        "display_name": "RTK Claude Code native hook and instruction policy v1",
        "lane_name": "terminal-rtk-claude-code-hook-v1",
        "surface": "claude-code-pre-tool-use-hook/terminal-output-compaction",
        "allowed_terms": ["rtk"],
        "data_dir_name": "rtk-claude-code-hook-v1",
        "executable": str(RTK_BIN),
        "path_entries": ["{codex_home}/runtime-bin", str(RTK_BIN.parent)],
        "mounts": [str(RTK_BIN.parent)],
        "env": {"RTK_TELEMETRY": "0"},
        "claude_features": {"hooks": True},
        "host_integration_backend": "host",
        "host_integration": {
            "install_commands": [
                [
                    "/bin/sh",
                    "-lc",
                    f"mkdir -p {{codex_home}}/runtime-bin && cp {RTK_BIN} {{codex_home}}/runtime-bin/rtk && chmod 755 {{codex_home}}/runtime-bin/rtk && {{codex_home}}/runtime-bin/rtk init --global --auto-patch",
                ],
            ],
            "verify_commands": [["{codex_home}/runtime-bin/rtk", "init", "--show"]],
            "required_files": [
                "{codex_home}/claude-config/settings.json",
                "{codex_home}/claude-config/CLAUDE.md",
                "{codex_home}/claude-config/RTK.md",
            ],
            "timeout_seconds": 120,
        },
        "preflight_command": ["rtk", "--version"],
        "default_tool_state": "active-hook-and-instruction-layer",
    },
    "caveman": {
        "display_name": "Caveman Claude Code native plugin",
        "lane_name": "behavior-caveman",
        "surface": "claude-code-native-plugin/sessionstart+userpromptsubmit-hooks+skills",
        "allowed_terms": ["caveman"],
        "data_dir_name": "caveman",
        "mounts": [str(CAVEMAN_ROOT), CLAUDE_MARKETPLACE_PREPARER],
        "claude_features": {"hooks": True, "plugin": "caveman"},
        "host_integration_backend": "docker",
        "host_integration": {
            "controller_install_commands": [[
                "python3", CLAUDE_MARKETPLACE_PREPARER,
                "--source", str(CAVEMAN_ROOT),
                "--expected-commit", CAVEMAN_COMMIT,
                "--marketplace-root", "{tool_data_dir}/marketplace",
                "--marketplace-name", "caveman",
                "--plugin-name", "caveman",
            ]],
            "install_commands": [
                ["claude", "plugin", "marketplace", "add", "{tool_data_dir}/marketplace"],
                ["claude", "plugin", "install", "caveman@caveman"],
            ],
            "verify_commands": [[
                "bash", "-lc",
                "set -o pipefail; claude plugin list --json | python3 -c 'import sys; assert \"caveman\" in sys.stdin.read()'",
            ]],
            "required_files": [
                "{tool_data_dir}/marketplace/source-pin-receipt.json",
                "{tool_data_dir}/marketplace/.claude-plugin/marketplace.json",
                "{tool_data_dir}/marketplace/plugins/caveman/.claude-plugin/plugin.json",
            ],
            "timeout_seconds": 300,
        },
        "preflight_command": ["claude", "plugin", "list", "--json"],
        "default_tool_state": "active-native-plugin-hooks-and-skills",
    },
    "ponytail": {
        "display_name": "Ponytail Claude Code native plugin",
        "lane_name": "artifact-ponytail",
        "surface": "claude-code-native-plugin/sessionstart+userpromptsubmit+subagentstart-hooks+skills+commands",
        "allowed_terms": ["ponytail"],
        "data_dir_name": "ponytail",
        "mounts": [str(PONYTAIL_ROOT), CLAUDE_MARKETPLACE_PREPARER],
        "claude_features": {"hooks": True, "plugin": "ponytail"},
        "host_integration_backend": "docker",
        "host_integration": {
            "controller_install_commands": [[
                "python3", CLAUDE_MARKETPLACE_PREPARER,
                "--source", str(PONYTAIL_ROOT),
                "--expected-commit", PONYTAIL_COMMIT,
                "--marketplace-root", "{tool_data_dir}/marketplace",
                "--marketplace-name", "ponytail",
                "--plugin-name", "ponytail",
            ]],
            "install_commands": [
                ["claude", "plugin", "marketplace", "add", "{tool_data_dir}/marketplace"],
                ["claude", "plugin", "install", "ponytail@ponytail"],
            ],
            "verify_commands": [[
                "bash", "-lc",
                "set -o pipefail; claude plugin list --json | python3 -c 'import sys; assert \"ponytail\" in sys.stdin.read()'",
            ]],
            "required_files": [
                "{tool_data_dir}/marketplace/source-pin-receipt.json",
                "{tool_data_dir}/marketplace/.claude-plugin/marketplace.json",
                "{tool_data_dir}/marketplace/plugins/ponytail/.claude-plugin/plugin.json",
            ],
            "timeout_seconds": 300,
        },
        "preflight_command": ["claude", "plugin", "list", "--json"],
        "default_tool_state": "active-native-plugin-hooks-and-skills",
    },
}

TOOL_CONFIGS.update({
    "jcodemunch-codex-mcp-v2": {
        "display_name": "jcodemunch guide-faithful Codex MCP v2",
        "lane_name": "retrieval-jcodemunch-codex-mcp-v2",
        "surface": "retrieval/context-mcp+product-authored-codex-guidance",
        "mcp_server": "jcodemunch",
        "allowed_terms": ["jcodemunch", "jcodemunch-mcp"],
        "data_dir_name": "jcodemunch-codex-mcp-v2",
        "mcp_command": "{tool_data_dir}/venv/bin/jcodemunch-mcp",
        "mcp_args": [],
        "env": {
            "CODE_INDEX_PATH": "{tool_data_dir}/index",
            "JCODEMUNCH_LOG_LEVEL": "ERROR",
        },
        "mounts": [str(JCODEMUNCH_ROOT), str(JCODEMUNCH_WHEEL), str(JCODEMUNCH_GUIDANCE_INSTALLER)],
        "host_integration": {
            "install_commands": [
                [str(UV_BIN), "venv", "{tool_data_dir}/venv", "--python", "python3"],
                [str(UV_BIN), "pip", "install", "--python", "{tool_data_dir}/venv/bin/python", str(JCODEMUNCH_WHEEL)],
                [
                    "python3",
                    str(JCODEMUNCH_GUIDANCE_INSTALLER),
                    "--source-root",
                    str(JCODEMUNCH_ROOT),
                    "--expected-commit",
                    JCODEMUNCH_COMMIT,
                    "--codex-home",
                    "{codex_home}",
                    "--receipt",
                    "{tool_data_dir}/jcodemunch-guidance-install.json",
                ],
            ],
            "verify_commands": [["{tool_data_dir}/venv/bin/jcodemunch-mcp", "--version"]],
            "required_files": [
                "{tool_data_dir}/venv/bin/jcodemunch-mcp",
                "{codex_home}/AGENTS.md",
                "{tool_data_dir}/jcodemunch-guidance-install.json",
            ],
            "timeout_seconds": 600,
        },
        "mcp_handshake": {"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 60},
        "default_tool_state": "warm-index",
        "warmup": {
            "kind": "product-native-code-index-build",
            "command": ["{tool_data_dir}/venv/bin/jcodemunch-mcp", "index", "{repo}"],
            "output_name": "jcodemunch-warmup-output.txt",
            "metadata_name": "jcodemunch-warmup-metadata.json",
            "timeout_seconds": 1200,
        },
    },
    "ponytail-codex-plugin-v1": {
        "display_name": "Ponytail official Codex plugin v1",
        "lane_name": "artifact-ponytail-codex-plugin-v1",
        "surface": "codex-plugin/skills+commands+sessionstart+userpromptsubmit+subagentstart-hooks",
        "allowed_terms": ["ponytail"],
        "data_dir_name": "ponytail-codex-plugin-v1",
        "mounts": [str(PONYTAIL_ROOT), str(PONYTAIL_MARKETPLACE_PREPARER), str(CODEX_PLUGIN_HOOK_TRUSTER)],
        "codex_features": {"hooks": True},
        "host_integration": {
            "home_dot_codex_alias": True,
            "install_commands": [
                ["python3", str(PONYTAIL_MARKETPLACE_PREPARER), "--source", str(PONYTAIL_ROOT), "--expected-commit", PONYTAIL_COMMIT, "--marketplace-root", "{tool_data_dir}/marketplace", "--marketplace-name", "ponytail", "--plugin-name", "ponytail"],
                ["codex", "plugin", "marketplace", "add", "{tool_data_dir}/marketplace", "--json"],
                ["codex", "plugin", "add", "ponytail@ponytail", "--json"],
                ["python3", str(CODEX_PLUGIN_HOOK_TRUSTER), "--codex", "codex", "--cwd", "{repo}", "--plugin-id", "ponytail@ponytail", "--expected-events", "sessionStart,userPromptSubmit,subagentStart", "--receipt", "{tool_data_dir}/ponytail-hook-trust.json"],
            ],
            "verify_commands": [["codex", "plugin", "list", "--json"]],
            "required_files": [
                "{codex_home}/config.toml",
                "{codex_home}/plugins/cache/ponytail/ponytail/4.8.4/.codex-plugin/plugin.json",
                "{tool_data_dir}/marketplace/source-pin-receipt.json",
                "{tool_data_dir}/ponytail-hook-trust.json",
            ],
            "timeout_seconds": 300,
        },
        "preflight_command": ["codex", "plugin", "list", "--json"],
        "default_tool_state": "active-plugin-hooks-and-skills",
    },
    "caveman-codex-skill-v1": {
        "display_name": "Caveman official Codex skill v1",
        "lane_name": "behavior-caveman-codex-skill-v1",
        "surface": "codex-project-skills+documented-per-session-activation",
        "allowed_terms": ["caveman", "cavecrew"],
        "data_dir_name": "caveman-codex-skill-v1",
        "path_entries": [str(NODE_TOOLCHAIN_ROOT / "bin")],
        "mounts": [str(CAVEMAN_ROOT)],
        "diff_exclude_paths": [".agents"],
        "host_integration": {
            "home_dot_codex_alias": True,
            "install_commands": [[str(NPX_BIN), "--yes", "skills", "add", str(CAVEMAN_ROOT), "-a", "codex", "-y"]],
            "verify_commands": [["python3", "-c", "from pathlib import Path; assert Path('.agents/skills/caveman/SKILL.md').is_file()"]],
            "required_files": [
                "{repo}/.agents/skills/cavecrew/SKILL.md",
                "{repo}/.agents/skills/caveman/SKILL.md",
                "{repo}/.agents/skills/caveman-commit/SKILL.md",
                "{repo}/.agents/skills/caveman-compress/SKILL.md",
                "{repo}/.agents/skills/caveman-help/SKILL.md",
                "{repo}/.agents/skills/caveman-review/SKILL.md",
                "{repo}/.agents/skills/caveman-stats/SKILL.md",
            ],
            "timeout_seconds": 300,
        },
        "preflight_command": ["python3", "-c", "from pathlib import Path; print(Path('.agents/skills/caveman/SKILL.md').resolve())"],
        "session_activation": "/caveman",
        "default_tool_state": "active-native-skill",
    },
    "cartog-codex-product-v2": {
        "display_name": "Cartog product-guided Codex integration v2",
        "lane_name": "retrieval-cartog-codex-product-v2",
        "surface": "retrieval/context+mcp-live-watch+model-runtime-cli+product-authored-agents-guidance",
        "mcp_server": "cartog",
        "mcp_config_via_host_integration": True,
        "allowed_terms": ["cartog"],
        "data_dir_name": "cartog-codex-product-v2",
        "mcp_command": "{tool_data_dir}/bin/cartog",
        "mcp_args": ["serve", "--watch"],
        "path_entries": ["{tool_data_dir}/bin"],
        "env": {"CARTOG_MCP_COMPACT": "1", "CARTOG_NO_UPDATE_CHECK": "1"},
        "mounts": [str(CARTOG_ROOT), CARTOG_PRODUCT_INSTALLER],
        "diff_exclude_paths": [".cartog", ".cartog.toml", "AGENTS.md"],
        "host_integration": {
            "home_dot_codex_alias": True,
            "controller_install_commands": [[
                "python3",
                CARTOG_PRODUCT_INSTALLER,
                "--source-root",
                str(CARTOG_ROOT),
                "--expected-commit",
                CARTOG_COMMIT,
                "--repo",
                "{repo}",
                "--binary-source",
                str(CARTOG_BIN),
                "--binary-destination",
                "{tool_data_dir}/bin/cartog",
                "--receipt",
                "{tool_data_dir}/cartog-codex-product-installation.json",
            ]],
            "install_commands": [
                ["{tool_data_dir}/bin/cartog", "ide", "--client", "codex", "--yes"],
            ],
            "verify_commands": [[
                "python3",
                "-c",
                "from pathlib import Path; a=Path('AGENTS.md').read_text(); c=Path('{codex_home}/config.toml').read_text(); assert 'CARTOG_PRODUCT_GUIDANCE_BEGIN' in a; assert 'prefer cartog over grep' in a; assert 'args = [\\\"serve\\\", \\\"--watch\\\"]' in c",
            ]],
            "required_files": [
                "{tool_data_dir}/bin/cartog",
                "{tool_data_dir}/cartog-codex-product-installation.json",
                "{repo}/AGENTS.md",
                "{codex_home}/config.toml",
            ],
            "timeout_seconds": 300,
        },
        "preflight_command": ["/bin/bash", "-lc", "command -v cartog && cartog --version"],
        "mcp_handshake": {"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 60},
        "default_tool_state": "warm-structural-index+active-guidance+live-watch",
        "warmup": {
            "kind": "official-init-and-structural-index",
            "command": [
                "/bin/bash",
                "-lc",
                "set -euo pipefail; cartog init; cartog index .",
            ],
            "cleanup_paths": [".cartog", ".cartog.toml"],
            "output_name": "cartog-warmup-output.txt",
            "metadata_name": "cartog-warmup-metadata.json",
            "timeout_seconds": 1200,
        },
        "canonical_scope": "The product-authored Codex MCP installer, live watcher, model-runtime CLI, and documented AGENTS routing snippet are active. The optional local vector/reranker tier is not prepared; documented structural and FTS5 retrieval remain available.",
    },
    "token-savior-mcp-v1": {
        **TOOL_CONFIGS["token-savior"],
        "display_name": "Token Savior bounded Codex MCP v1",
        "lane_name": "integrated-token-savior-mcp-v1",
        "env": {**TOOL_CONFIGS["token-savior"]["env"], "TOKEN_SAVIOR_CLIENT": "codex"},
        "mcp_handshake": {"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 60},
    },
    "token-savior-codex-product-v2": {
        **TOOL_CONFIGS["token-savior"],
        "display_name": "Token Savior product-guided Codex integration v2",
        "lane_name": "integrated-token-savior-codex-product-v2",
        "surface": "integrated-mcp+product-authored-guidance+codex-pre-post-tool-hooks",
        "tool_manifest_identity": "current-file-v1",
        "data_dir_name": "token-savior-codex-product-v2",
        "env": {
            **TOOL_CONFIGS["token-savior"]["env"],
            "TOKEN_SAVIOR_CLIENT": "codex",
            "TS_CAPTURE_DISABLED": "0",
            "TS_BASH_COMPACT": "1",
            "TS_BASH_REWRITE": "1",
            "TS_BASH_REWRITE_LOG": "{tool_data_dir}/bash-rewrites.jsonl",
        },
        "diff_exclude_paths": ["AGENTS.md"],
        "codex_features": {"hooks": True},
        "codex_hook_bypass_trust": True,
        "host_integration": {
            "controller_install_commands": [
                [
                    "python3",
                    "{repository_root}/scripts/install_token_savior_codex_product.py",
                    "--source-root",
                    str(TOKEN_SAVIOR_ROOT),
                    "--expected-commit",
                    "ff42ef14cc972dad5470e0ca8101e4501e00600f",
                    "--codex-home",
                    "{codex_home}",
                    "--repo",
                    "{repo}",
                    "--receipt",
                    "{tool_data_dir}/codex-product-installation.json",
                ],
                [
                    "python3",
                    "{repository_root}/scripts/probe_token_savior_codex_hooks.py",
                    "--source-root",
                    str(TOKEN_SAVIOR_ROOT),
                    "--repo",
                    "{repo}",
                    "--state-dir",
                    "{tool_data_dir}/hook-probe-state",
                    "--receipt",
                    "{tool_data_dir}/codex-hook-probe.json",
                ],
            ],
            "install_commands": [],
            "verify_commands": [[
                "python3",
                "-c",
                "import json; from pathlib import Path; r=Path('AGENTS.md').read_text(); h=json.loads(Path('{codex_home}/hooks.json').read_text()); assert 'TOKEN_SAVIOR_PRODUCT_GUIDANCE_BEGIN' in r; assert set(('PreToolUse','PostToolUse')).issubset(h['hooks'])",
            ]],
            "required_files": [
                "{repo}/AGENTS.md",
                "{codex_home}/hooks.json",
                "{tool_data_dir}/codex-product-installation.json",
                "{tool_data_dir}/codex-hook-probe.json",
            ],
            "timeout_seconds": 120,
        },
        "mcp_handshake": {"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 60},
        "default_tool_state": "cold-auto-index+active-guidance-and-hooks",
        "compatibility_deviation": "The pinned product's Codex descriptor targets obsolete .codex/settings.json tool_complete hooks. This versioned host adapter maps the unchanged product hook scripts to Codex 0.144 hooks.json PreToolUse/PostToolUse while preserving product-authored guidance verbatim in AGENTS.md.",
    },
    "serena-codex-mcp-v1": {
        "display_name": "Serena official Codex MCP v1",
        "lane_name": "retrieval-serena-codex-mcp-v1",
        "surface": "retrieval/context+official-codex-mcp",
        "mcp_server": "serena",
        "allowed_terms": ["serena"],
        "data_dir_name": "serena-codex-mcp-v1",
        "mcp_command": str(UV_BIN),
        "mcp_args": ["tool", "run", "--from", str(SERENA_ROOT), "serena", "start-mcp-server", "--project-from-cwd", "--context=codex", "--enable-web-dashboard", "false", "--open-web-dashboard", "false"],
        "env": {"SERENA_HOME": "{tool_data_dir}"},
        "mounts": [str(SERENA_ROOT)],
        "host_integration": {
            "install_commands": [[str(UV_BIN), "tool", "run", "--from", str(SERENA_ROOT), "serena", "setup", "codex"]],
            "verify_commands": [[str(UV_BIN), "tool", "run", "--from", str(SERENA_ROOT), "serena", "--version"]],
            "required_files": ["{codex_home}/config.toml"],
            "timeout_seconds": 600,
        },
        "mcp_handshake": {"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 120},
        "default_tool_state": "cold-auto-index",
    },
    "sigmap-codex-live-v1": {
        "display_name": "SigMap Codex MCP with live watcher v1",
        "lane_name": "retrieval-sigmap-codex-live-v1",
        "surface": "retrieval/context+codex-agents+mcp-live-watch",
        "mcp_server": "sigmap",
        "allowed_terms": ["sigmap", "gen-context"],
        "data_dir_name": "sigmap-codex-live-v1",
        "mcp_command": "/bin/bash",
        "mcp_args": ["-lc", f"cd {{repo}}; {NODE_BIN} {SIGMAP_ROOT / 'gen-context.js'} --watch >/dev/null 2>&1 & watcher=$!; trap 'kill $watcher 2>/dev/null || true; wait $watcher 2>/dev/null || true' EXIT; {NODE_BIN} {SIGMAP_ROOT / 'gen-context.js'} --mcp"],
        "env": {"SIGMAP_TELEMETRY": "0"},
        "mounts": [str(SIGMAP_ROOT)],
        "diff_exclude_paths": [".context", "AGENTS.md"],
        "default_tool_state": "warm-index",
        "warmup": {"kind": "signature-map-and-codex-guidance", "command": [str(NODE_BIN), str(SIGMAP_ROOT / "gen-context.js"), "--adapter", "codex", "--no-track"], "cleanup_paths": [".context", "AGENTS.md"], "output_name": "sigmap-warmup-output.txt", "metadata_name": "sigmap-warmup-metadata.json", "timeout_seconds": 900},
        "mcp_handshake": {"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 60},
        "compatibility_deviation": "Manual Codex TOML registration is retained because the pinned targeted installer writes obsolete YAML; product AGENTS guidance and live watcher are present.",
    },
    "swarmvault-codex-product-v1": {
        "display_name": "SwarmVault official Codex rules, hook, and MCP v1",
        "lane_name": "swarmvault-codex-product-v1",
        "surface": "broad-context-owner/mcp+codex-rules+hook",
        "mcp_server": "swarmvault",
        "allowed_terms": ["swarmvault"],
        "data_dir_name": "swarmvault-codex-product-v1",
        "mcp_command": "/bin/bash",
        "mcp_args": ["-lc", f"cd {{repo}} && exec {NODE_BIN} {SWARMVAULT_CLI} mcp"],
        "env": {"SWARMVAULT_OUT": "{tool_data_dir}/vault", "SWARMVAULT_NO_NOTICES": "1"},
        "mounts": [str(SWARMVAULT_ROOT)],
        "diff_exclude_paths": ["AGENTS.md", ".codex", "swarmvault.config.json", "swarmvault.schema.md"],
        "codex_features": {"hooks": True},
        "default_tool_state": "warm-index",
        "warmup": {"kind": "official-vault-compile-and-codex-install", "command": ["/bin/bash", "-lc", f"set -euo pipefail; cd {{repo}}; {NODE_BIN} {SWARMVAULT_CLI} init --lite; {NODE_BIN} {SWARMVAULT_CLI} ingest {{repo}} --max-files 500; {NODE_BIN} {SWARMVAULT_CLI} compile; {NODE_BIN} {SWARMVAULT_CLI} install --agent codex --hook; test -f AGENTS.md"], "cleanup_paths": ["AGENTS.md", ".codex", "swarmvault.config.json", "swarmvault.schema.md"], "output_name": "swarmvault-warmup-output.txt", "metadata_name": "swarmvault-warmup-metadata.json", "timeout_seconds": 3600},
        "mcp_handshake": {"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 120},
    },
    "codescope-codex-product-v1": {
        "display_name": "CodeScope official Codex product v1",
        "lane_name": "codescope-codex-product-v1",
        "surface": "broad-context-owner/mcp+official-initialize-instructions",
        "mcp_server": "codescope",
        "allowed_terms": ["codescope"],
        "data_dir_name": "codescope-codex-product-v1",
        "mcp_command": "/bin/bash",
        "mcp_args": ["-lc", "set -euo pipefail; codescope start >/dev/null; trap 'codescope stop >/dev/null 2>&1 || true' EXIT; i=0; until codescope status | grep -q '^running'; do i=$((i+1)); [ \"$i\" -lt 50 ]; sleep 0.2; done; codescope mcp {repo}"],
        "path_entries": [str(CODESCOPE_RELEASE_ROOT)],
        "mounts": [str(CODESCOPE_BIN), str(CODESCOPE_SURREAL_BIN)],
        "diff_exclude_paths": [".codescope"],
        "host_integration": {"home_dot_codex_alias": True, "verify_commands": [[str(CODESCOPE_BIN), "--version"]]},
        "default_tool_state": "warm-index",
        "warmup": {"kind": "official-surreal-start-index-and-codex-install", "command": ["/bin/bash", "-lc", "set -euo pipefail; codescope start; trap 'codescope stop >/dev/null 2>&1 || true' EXIT; i=0; until codescope status | grep -q '^running'; do i=$((i+1)); [ \"$i\" -lt 50 ]; sleep 0.2; done; codescope init --agent codex {repo}; test -f {codex_home}/config.toml"], "cleanup_paths": [".codescope"], "output_name": "codescope-warmup-output.txt", "metadata_name": "codescope-warmup-metadata.json", "timeout_seconds": 3600},
        "mcp_handshake": {"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 120},
    },
})


def _replace_batch_paths(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        for old, new in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [_replace_batch_paths(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: _replace_batch_paths(item, replacements) for key, item in value.items()}
    return value


_BATCH_SOURCE = lambda name: BATCH_RELEASE_ROOT / BATCH_RELEASES[name][0] / "source"
_BATCH_ARTIFACT = lambda name: _batch_path(name, 1)
_BATCH_RUNTIME = lambda name: BATCH_RELEASE_ROOT / BATCH_RELEASES[name][0] / "runtime"

_BATCH_REWRITES = {
    "headroom": {str(HEADROOM_WHEEL): str(_BATCH_ARTIFACT("headroom")), str(HEADROOM_ROOT): str(_BATCH_SOURCE("headroom"))},
    "tokenjuice-codex-hook-v1": {str(TOKENJUICE_BIN): str(_BATCH_RUNTIME("tokenjuice") / "node_modules/.bin/tokenjuice"), str(TOKENJUICE_ROOT): str(_BATCH_SOURCE("tokenjuice"))},
    "rtk-codex-instructions-v1": {str(RTK_BIN): str(_BATCH_RUNTIME("rtk") / "rtk")},
    "rtk-claude-code-hook-v1": {str(RTK_BIN): str(_BATCH_RUNTIME("rtk") / "rtk")},
    "snip-codex-hook-v1": {str(SNIP_BIN): str(_BATCH_RUNTIME("snip") / "snip"), str(SNIP_ROOT): str(_BATCH_SOURCE("snip"))},
    "graphify-codex-skill-v1": {str(GRAPHIFY_WHEEL): str(_BATCH_ARTIFACT("graphify")), str(GRAPHIFY_ROOT): str(_BATCH_SOURCE("graphify"))},
    "leanctx-codex-hybrid-v1": {str(LEANCTX_BINARY): str(_BATCH_RUNTIME("leanctx") / "lean-ctx"), str(LEANCTX_ROOT): str(_BATCH_SOURCE("leanctx"))},
    "cartog-codex-product-v2": {str(CARTOG_BIN): str(_BATCH_RUNTIME("cartog") / "cartog"), str(CARTOG_ROOT): str(_BATCH_SOURCE("cartog")), CARTOG_COMMIT: BATCH_RELEASES["cartog"][5]},
    "codescope-codex-product-v1": {str(CODESCOPE_RELEASE_ROOT): str(_BATCH_RUNTIME("codescope"))},
    "swarmvault-codex-product-v1": {str(SWARMVAULT_CLI): str(_BATCH_RUNTIME("swarmvault") / "node_modules/.bin/swarmvault"), str(SWARMVAULT_ROOT): str(_BATCH_SOURCE("swarmvault"))},
    "serena-codex-mcp-v1": {str(SERENA_ROOT): str(_BATCH_ARTIFACT("serena"))},
    "sigmap-codex-live-v1": {str(SIGMAP_ROOT): str(_BATCH_RUNTIME("sigmap") / "node_modules/sigmap")},
    "token-savior-codex-product-v2": {str(TOKEN_SAVIOR_WHEEL): str(_BATCH_ARTIFACT("token-savior")), str(TOKEN_SAVIOR_ROOT): str(_BATCH_SOURCE("token-savior")), "ff42ef14cc972dad5470e0ca8101e4501e00600f": BATCH_RELEASES["token-savior"][5]},
    "ponytail-codex-plugin-v1": {str(PONYTAIL_ROOT): str(_BATCH_SOURCE("ponytail")), PONYTAIL_COMMIT: BATCH_RELEASES["ponytail"][5], "/4.8.4/": "/4.9.0/"},
    "caveman-codex-skill-v1": {str(CAVEMAN_ROOT): str(_BATCH_SOURCE("caveman")), CAVEMAN_COMMIT: BATCH_RELEASES["caveman"][5]},
    "codegraph-codex-mcp-v1": {str(CODEGRAPH_BIN): str(_BATCH_RUNTIME("codegraph") / "codegraph-linux-x64/bin/codegraph"), "/opt/data/tool-candidates/codegraph": str(_BATCH_SOURCE("codegraph"))},
    "jcodemunch-codex-mcp-v2": {str(JCODEMUNCH_WHEEL): str(_BATCH_ARTIFACT("jcodemunch")), str(JCODEMUNCH_ROOT): str(_BATCH_SOURCE("jcodemunch")), JCODEMUNCH_COMMIT: BATCH_RELEASES["jcodemunch"][5]},
    "repowise-codex-product-v2": {str(REPOWISE_WHEEL): str(_BATCH_ARTIFACT("repowise")), str(REPOWISE_ROOT): str(_BATCH_SOURCE("repowise"))},
}
for _tool_id, _replacements in _BATCH_REWRITES.items():
    TOOL_CONFIGS[_tool_id] = _replace_batch_paths(TOOL_CONFIGS[_tool_id], _replacements)

for _tool_id, _release, _runtime in (
    ("headroom", "headroom", (PINNED_UVX_RUNNER,)),
    ("tokenjuice-codex-hook-v1", "tokenjuice", (str(_BATCH_RUNTIME("tokenjuice")),)),
    ("rtk-codex-instructions-v1", "rtk", (str(_BATCH_RUNTIME("rtk")),)),
    ("rtk-claude-code-hook-v1", "rtk", (str(_BATCH_RUNTIME("rtk")),)),
    ("snip-codex-hook-v1", "snip", (str(_BATCH_RUNTIME("snip")),)),
    ("graphify-codex-skill-v1", "graphify", ()),
    ("leanctx-codex-hybrid-v1", "leanctx", (str(_BATCH_RUNTIME("leanctx")),)),
    ("cartog-codex-product-v2", "cartog", (str(_BATCH_RUNTIME("cartog")),)),
    ("codescope-codex-product-v1", "codescope", (str(_BATCH_RUNTIME("codescope")),)),
    ("swarmvault-codex-product-v1", "swarmvault", (str(_BATCH_RUNTIME("swarmvault")),)),
    ("serena-codex-mcp-v1", "serena", (SERENA_CODEX_HOOK_INSTALLER,)),
    ("sigmap-codex-live-v1", "sigmap", (str(_BATCH_RUNTIME("sigmap")),)),
    ("token-savior-codex-product-v2", "token-savior", ()),
    ("ponytail-codex-plugin-v1", "ponytail", (PONYTAIL_MARKETPLACE_PREPARER, CODEX_PLUGIN_HOOK_TRUSTER)),
    ("caveman-codex-skill-v1", "caveman", ()),
    ("codegraph-codex-mcp-v1", "codegraph", (str(_BATCH_RUNTIME("codegraph")),)),
    ("jcodemunch-codex-mcp-v2", "jcodemunch", (JCODEMUNCH_GUIDANCE_INSTALLER,)),
    ("repowise-codex-product-v2", "repowise", ()),
):
    _pin_batch_release(_tool_id, _release, *(Path(path) for path in _runtime))

_headroom_wheel = str(_BATCH_ARTIFACT("headroom")) + "[all]"
TOOL_CONFIGS["headroom"].update({
    "display_name": "Headroom 0.36.3 official Codex wrapper",
    "allowed_terms": ["headroom", "headroom_retrieve", "serena"],
    "path_entries": ["{tool_data_dir}/bin", "{codex_home}/home/.headroom/bin", "{codex_home}/home/.local/bin"],
    "env": {**TOOL_CONFIGS["headroom"]["env"], "PINNED_SERENA_WHEEL": str(_BATCH_ARTIFACT("serena"))},
    "host_integration": {
        "install_commands": [["mkdir", "-p", "{tool_data_dir}/bin"], ["ln", "-sf", PINNED_UVX_RUNNER, "{tool_data_dir}/bin/uvx"]],
        "required_files": ["{tool_data_dir}/bin/uvx"],
    },
    "codex_wrapper": {"command": str(UV_BIN), "args": ["tool", "run", "--from", _headroom_wheel, "headroom", "wrap", "codex", "--port", "{tool_port}", "--verbose", "--"]},
    "preflight_command": [str(UV_BIN), "tool", "run", "--from", _headroom_wheel, "headroom", "--version"],
})
TOOL_CONFIGS["headroom"]["mounts"].extend([str(_BATCH_SOURCE("serena")), str(_BATCH_ARTIFACT("serena"))])
TOOL_CONFIGS["headroom"]["clean_source_roots"].append(str(_BATCH_SOURCE("serena")))

TOOL_CONFIGS["graphify-codex-skill-v1"]["host_integration"].update({
    "install_commands": [
        [str(UV_BIN), "venv", "{tool_data_dir}/venv", "--python", "python3"],
        [str(UV_BIN), "pip", "install", "--python", "{tool_data_dir}/venv/bin/python", str(_BATCH_ARTIFACT("graphify"))],
        ["{tool_data_dir}/venv/bin/graphify", "codex", "install", "--project"],
    ],
    "required_files": ["{tool_data_dir}/venv/bin/graphify", "{repo}/.codex/hooks.json", "{repo}/.codex/skills/graphify/SKILL.md", "{repo}/AGENTS.md"],
})
TOOL_CONFIGS["graphify-codex-skill-v1"]["warmup"]["command"] = ["{tool_data_dir}/venv/bin/graphify", "update", "{repo}", "--force"]

TOOL_CONFIGS["leanctx-codex-hybrid-v1"]["host_integration"]["verify_commands"] = [[str(_BATCH_RUNTIME("leanctx") / "lean-ctx"), "--version"]]
TOOL_CONFIGS["leanctx-codex-hybrid-v1"]["host_integration"]["diagnostic_commands"] = [[str(_BATCH_RUNTIME("leanctx") / "lean-ctx"), "doctor"]]

_serena = TOOL_CONFIGS["serena-codex-mcp-v1"]
_serena.update({
    "display_name": "Serena 1.7.0 official Codex MCP and lifecycle hooks",
    "mcp_config_via_host_integration": True,
    "mcp_command": "{tool_data_dir}/venv/bin/serena",
    "mcp_args": ["start-mcp-server", "--project-from-cwd", "--context=codex", "--enable-web-dashboard", "false", "--open-web-dashboard", "false"],
    "path_entries": ["{tool_data_dir}/venv/bin"],
    "codex_features": {"hooks": True},
    "host_integration": {
        "install_commands": [
            [str(UV_BIN), "venv", "{tool_data_dir}/venv", "--python", "python3"],
            [str(UV_BIN), "pip", "install", "--python", "{tool_data_dir}/venv/bin/python", str(_BATCH_ARTIFACT("serena"))],
            ["{tool_data_dir}/venv/bin/serena", "setup", "codex"],
            ["python3", SERENA_CODEX_HOOK_INSTALLER, "--codex-home", "{codex_home}"],
        ],
        "verify_commands": [["{tool_data_dir}/venv/bin/serena", "--version"]],
        "required_files": ["{tool_data_dir}/venv/bin/serena", "{tool_data_dir}/venv/bin/serena-hooks", "{codex_home}/config.toml", "{codex_home}/hooks.json"],
        "timeout_seconds": 600,
    },
})

_sigmap = TOOL_CONFIGS["sigmap-codex-live-v1"]
_sigmap["host_integration"] = {
    # sigmap registers its MCP server in ~/.codex/config.yaml, so without the alias it
    # writes into the lane HOME and Codex never reads it: an installed silent no-op.
    "home_dot_codex_alias": True,
    "install_commands": [[str(_BATCH_RUNTIME("sigmap") / "node_modules/.bin/sigmap"), "mcp", "install", "codex"]],
    "required_files": ["{codex_home}/config.yaml"],
}
_sigmap["compatibility_deviation"] = "SigMap 8.28.0's official Codex installer is run and retained, but it still writes obsolete config.yaml; the controller also writes the equivalent current config.toml registration."

_token_savior = TOOL_CONFIGS["token-savior-codex-product-v2"]
_token_savior.update({
    "display_name": "Token Savior 4.21.0 native Codex product integration",
    "mcp_command": "{tool_data_dir}/venv/bin/token-savior",
    "mcp_args": [],
    "path_entries": ["{tool_data_dir}/venv/bin"],
    "host_integration": {
        "install_commands": [
            [str(UV_BIN), "venv", "{tool_data_dir}/venv", "--python", "python3"],
            [str(UV_BIN), "pip", "install", "--python", "{tool_data_dir}/venv/bin/python", str(_BATCH_ARTIFACT("token-savior")) + "[mcp]"],
            ["{tool_data_dir}/venv/bin/ts", "init", "--agent", "codex", "--global", "--yes"],
        ],
        "verify_commands": [["{tool_data_dir}/venv/bin/ts", "init", "--agent", "codex", "--global", "--dry-run"]],
        "required_files": ["{tool_data_dir}/venv/bin/token-savior", "{tool_data_dir}/venv/bin/ts", "{codex_home}/hooks.json"],
        "timeout_seconds": 600,
    },
    "compatibility_deviation": None,
})

_jcodemunch = TOOL_CONFIGS["jcodemunch-codex-mcp-v2"]
_jcodemunch["mcp_config_via_host_integration"] = True
# init resolves the server command with shutil.which and refuses to register Codex at all
# unless it finds a real binary, because uvx's cold-start chatter poisons Codex's first
# JSON-RPC frame -- a silent multi-hour hang rather than an error. Putting the venv on PATH
# is what turns that refusal into a registration.
_jcodemunch.setdefault("path_entries", []).append("{tool_data_dir}/venv/bin")
# init appends its server block to ~/.codex/config.toml, so without the alias the entry
# lands in the lane HOME and `codex mcp list` never sees the server.
_jcodemunch["host_integration"]["home_dot_codex_alias"] = True
_jcodemunch["host_integration"]["install_commands"].insert(2, ["{tool_data_dir}/venv/bin/jcodemunch-mcp", "init", "--client", "codex", "--yes", "--minimal", "--no-backup", "--no-share-savings"])
_jcodemunch["host_integration"]["required_files"].append("{codex_home}/config.toml")

_caveman_skills = ("cavecrew", "caveman", "caveman-commit", "caveman-compress", "caveman-discover", "caveman-evidence-review", "caveman-explore", "caveman-help", "caveman-learn", "caveman-manage", "caveman-optimize", "caveman-review", "caveman-setup", "caveman-stats", "investigate-first", "lean-build", "migration", "safe-refactor", "surgical-patch", "verify-and-stop")
TOOL_CONFIGS["caveman-codex-skill-v1"]["host_integration"]["required_files"] = [f"{{repo}}/.agents/skills/{name}/SKILL.md" for name in _caveman_skills]


def _opencode_treatment_config(
    treatment: str,
    *,
    display_name: str,
    lane_name: str,
    surface: str,
    allowed_terms: list[str],
    mounts: list[str],
    adapter_path: Path = OPENCODE_ADAPTER,
    **extra: Any,
) -> dict[str, Any]:
    adapter_args = [
        str(adapter_path),
        "--opencode-binary",
        str(OPENCODE_BIN),
        "--expected-opencode-sha256",
        OPENCODE_BIN_SHA256,
        "--treatment",
        treatment,
    ]
    config: dict[str, Any] = {
        "display_name": display_name,
        "lane_name": lane_name,
        "surface": surface,
        "allowed_terms": ["opencode", *allowed_terms],
        "data_dir_name": lane_name,
        "mounts": [str(adapter_path), *mounts],
        "executable": str(OPENCODE_BIN),
        "expected_executable_sha256": OPENCODE_BIN_SHA256,
        "binary_mount_target": str(OPENCODE_BIN),
        "codex_wrapper": {"command": "/usr/bin/python3", "args": adapter_args},
        "preflight_command": ["/usr/bin/python3", *adapter_args, "--probe"],
        "tool_manifest_identity": "current-file-v1",
    }
    config.update(extra)
    return config


TOOL_CONFIGS.update(
    {
        "tokenjuice-opencode-plugin-v1": _opencode_treatment_config(
            "tokenjuice",
            display_name="TokenJuice official OpenCode plugin v1",
            lane_name="terminal-tokenjuice-opencode-plugin-v1",
            surface="opencode-tool-execute-after/terminal-output-compaction",
            allowed_terms=["tokenjuice"],
            mounts=["/opt/data/tool-candidates/tokenjuice"],
            path_entries=["/opt/data/tool-candidates/tokenjuice/bin"],
            env={"TOKENJUICE_TELEMETRY": "0"},
            host_integration={
                "install_commands": [["tokenjuice", "install", "opencode"]],
                "verify_commands": [["tokenjuice", "doctor", "opencode"]],
                "required_files": ["{codex_home}/xdg-config/opencode/plugins/tokenjuice.js"],
            },
            default_tool_state="active-native-plugin",
        ),
        "serena-opencode-mcp-v1": _opencode_treatment_config(
            "serena",
            display_name="Serena official OpenCode MCP v1",
            lane_name="retrieval-serena-opencode-mcp-v1",
            surface="opencode-mcp/symbolic-retrieval",
            allowed_terms=["serena"],
            mounts=["/opt/data/tool-candidates/serena"],
            mcp_server="serena",
            mcp_command=str(UV_BIN),
            mcp_args=[
                "tool",
                "run",
                "--from",
                "/opt/data/tool-candidates/serena",
                "serena",
                "start-mcp-server",
                "--project-from-cwd",
                "--context=ide",
                "--enable-web-dashboard",
                "false",
                "--open-web-dashboard",
                "false",
            ],
            env={"SERENA_HOME": "{tool_data_dir}"},
            mcp_handshake={"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 120},
            default_tool_state="cold-auto-index",
        ),
        "snip-opencode-plugin-v1": _opencode_treatment_config(
            "snip",
            display_name="Snip official community OpenCode plugin v1.6.1",
            lane_name="terminal-snip-opencode-plugin-v1",
            surface="opencode-tool-execute-before/shell-command-rewriting",
            allowed_terms=["snip", "opencode-snip"],
            mounts=[
                "/opt/data/tool-candidates/snip",
                "/opt/data/tool-candidates/opencode-snip-v1.6.1",
            ],
            path_entries=["/opt/data/tool-candidates/snip"],
            env={"SNIP_TELEMETRY": "0"},
            host_integration={
                "verify_commands": [
                    ["snip", "--version"],
                    [
                        "python3",
                        "-c",
                        "from pathlib import Path; p=Path('/opt/data/tool-candidates/opencode-snip-v1.6.1/.opencode/plugins/index.ts'); assert p.is_file(); assert 'SnipPlugin' in p.read_text()",
                    ],
                ],
                "required_files": [
                    "/opt/data/tool-candidates/opencode-snip-v1.6.1/.opencode/plugins/index.ts"
                ],
            },
            default_tool_state="active-native-plugin",
        ),
        "cartog-opencode-product-v1": _opencode_treatment_config(
            "cartog",
            display_name="Cartog official OpenCode MCP product v1",
            lane_name="retrieval-cartog-opencode-product-v1",
            surface="opencode-mcp/structural-retrieval+live-watch",
            allowed_terms=["cartog"],
            mounts=["/opt/data/tool-candidates/cartog"],
            path_entries=["/opt/data/tool-candidates/cartog/target/release"],
            env={"CARTOG_MCP_COMPACT": "1", "CARTOG_NO_UPDATE_CHECK": "1"},
            mcp_server="cartog",
            mcp_command=str(CARTOG_BIN),
            mcp_args=["serve", "--watch"],
            host_integration={
                "install_commands": [[str(CARTOG_BIN), "ide", "--client", "opencode", "--yes"]],
                "verify_commands": [
                    [
                        "python3",
                        "-c",
                        "from pathlib import Path; p=Path('{codex_home}/xdg-config/opencode/opencode.json'); assert p.is_file(); assert '\"cartog\"' in p.read_text()",
                    ]
                ],
                "required_files": ["{codex_home}/xdg-config/opencode/opencode.json"],
            },
            mcp_handshake={"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 120},
            warmup={
                "kind": "official-init-and-structural-index",
                "command": ["/bin/bash", "-lc", "set -euo pipefail; cartog init; cartog index ."],
                "cleanup_paths": [".cartog", ".cartog.toml"],
                "output_name": "cartog-warmup-output.txt",
                "metadata_name": "cartog-warmup-metadata.json",
                "timeout_seconds": 1200,
            },
            diff_exclude_paths=[".cartog", ".cartog.toml"],
            default_tool_state="warm-structural-index+live-watch",
        ),
        "headroom-opencode-product-v1": _opencode_treatment_config(
            "headroom",
            display_name="Headroom official OpenCode integrated product v1",
            lane_name="integrated-headroom-opencode-product-v1",
            surface="opencode-proxy/context-compression+rtk+mcp+serena",
            allowed_terms=["headroom", "headroom_retrieve", "rtk", "serena"],
            mounts=[
                "/opt/data/tool-candidates/headroom",
                "/opt/data/tool-candidates/rtk",
                "/opt/data/tool-candidates/serena",
            ],
            path_entries=["{codex_home}/home/.headroom/bin", "{codex_home}/home/.local/bin"],
            env={
                "HEADROOM_HOME": "{tool_data_dir}",
                "HEADROOM_CACHE_DIR": "{tool_data_dir}/cache",
                "HEADROOM_DISABLE_DASHBOARD": "1",
                "HEADROOM_TELEMETRY": "0",
                "HEADROOM_PROJECT": "{repo_slug}",
                "OPENCODE_HOME": "{codex_home}/xdg-config/opencode",
            },
            host_integration={
                "install_commands": [
                    [
                        str(UV_BIN),
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
                        "{tool_port}",
                        "--verbose",
                        "--prepare-only",
                    ]
                ],
                "verify_commands": [
                    [
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
                    [
                        "python3",
                        "-c",
                        "from pathlib import Path; p=Path('{codex_home}/xdg-config/opencode/opencode.json'); assert p.is_file(); text=p.read_text(); assert 'headroom' in text and 'mcp' in text",
                    ],
                ],
                "required_files": ["{codex_home}/xdg-config/opencode/opencode.json"],
                "timeout_seconds": 600,
            },
            diff_exclude_paths=["AGENTS.md", ".headroom"],
            default_tool_state="active-official-integrated-wrapper",
        ),
    }
)

TOOL_CONFIGS["headroom-opencode-product-v2"] = {
    **TOOL_CONFIGS["headroom-opencode-product-v1"],
    "display_name": "Headroom official OpenCode integrated product v2",
    "lane_name": "integrated-headroom-opencode-product-v2",
    "data_dir_name": "integrated-headroom-opencode-product-v2",
    "executable": str(OPENCODE_BIN_V2),
    "binary_mount_target": str(OPENCODE_BIN_V2),
    "mounts": [
        str(OPENCODE_ADAPTER_V2) if value == str(OPENCODE_ADAPTER) else value
        for value in TOOL_CONFIGS["headroom-opencode-product-v1"]["mounts"]
    ],
    "codex_wrapper": {
        **TOOL_CONFIGS["headroom-opencode-product-v1"]["codex_wrapper"],
        "args": [
            (
                str(OPENCODE_ADAPTER_V2)
                if value == str(OPENCODE_ADAPTER)
                else str(OPENCODE_BIN_V2)
                if value == str(OPENCODE_BIN)
                else value
            )
            for value in TOOL_CONFIGS["headroom-opencode-product-v1"]["codex_wrapper"]["args"]
        ],
    },
    "preflight_command": [
        (
            str(OPENCODE_ADAPTER_V2)
            if value == str(OPENCODE_ADAPTER)
            else str(OPENCODE_BIN_V2)
            if value == str(OPENCODE_BIN)
            else value
        )
        for value in TOOL_CONFIGS["headroom-opencode-product-v1"]["preflight_command"]
    ],
}

# Repaired OpenCode treatment generations. These use fresh profile identities so
# deleted protocol/replicate identities can never be reopened.
TOOL_CONFIGS["serena-opencode-mcp-v1"].update(
    {
        "artifact_identities": [
            {
                "path": str(SERENA_ROOT / "pyproject.toml"),
                "sha256": "984623c307233179a641fa238593eb4b7bcf27ad7f1a38881b593ef20ae07cd8",
                "kind": "pinned-source-manifest",
            },
            {
                "path": str(UV_BIN),
                "sha256": "dc407e8ebb7903e94580217e564e544b231f16ce2a697c247b71632bffe35b35",
                "kind": "launcher-runtime",
            },
        ],
        "effective_host_config": {"required": True, "source": "adapter-probe"},
    }
)

TOOL_CONFIGS.update(
    {
        "tokenjuice-opencode-plugin-v2": _opencode_treatment_config(
            "tokenjuice",
            display_name="TokenJuice official OpenCode plugin v2 repaired",
            lane_name="terminal-tokenjuice-opencode-plugin-v2",
            surface="opencode-tool-execute-after/terminal-output-compaction",
            allowed_terms=["tokenjuice"],
            mounts=[str(TOKENJUICE_ROOT)],
            adapter_path=OPENCODE_ADAPTER_V3,
            path_entries=[str(TOKENJUICE_BIN.parent)],
            env={"TOKENJUICE_TELEMETRY": "0"},
            host_integration={
                "install_commands": [["tokenjuice", "install", "opencode"]],
                "verify_commands": [["tokenjuice", "doctor", "opencode"]],
                "required_files": ["{codex_home}/xdg-config/opencode/plugins/tokenjuice.js"],
            },
            artifact_identities=[
                {"path": str(TOKENJUICE_BIN), "sha256": "d3939a3f76f8ae5489add74453edee5e11870d25a4bd92972111f664f33bc690", "kind": "launcher"},
                {"path": str(TOKENJUICE_ROOT / "dist/cli/main.js"), "sha256": "d588ce6332a2ac973e966806f0be66893c7606a315793c9c99862be19d02b32c", "kind": "compiled-cli"},
            ],
            post_install_artifacts=[
                {
                    "path": "{codex_home}/xdg-config/opencode/plugins/tokenjuice.js",
                    "sha256": "331630af9834afc61f3e73d93b72343ca54ef719a46bced367fe746cb7110f7d",
                    "retain_as": "tokenjuice-installed-plugin.js",
                }
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            default_tool_state="active-native-plugin-exact-artifact",
        ),
        "snip-opencode-plugin-v2": _opencode_treatment_config(
            "snip",
            display_name="Snip official community OpenCode plugin v1.6.1 repaired",
            lane_name="terminal-snip-opencode-plugin-v2",
            surface="opencode-tool-execute-before/shell-command-rewriting",
            allowed_terms=["snip", "opencode-snip"],
            mounts=[str(SNIP_ROOT), "/opt/data/tool-candidates/opencode-snip-v1.6.1"],
            adapter_path=OPENCODE_ADAPTER_V3,
            path_entries=[str(SNIP_ROOT)],
            env={"SNIP_TELEMETRY": "0"},
            host_integration={
                "verify_commands": [["snip", "--version"]],
                "required_files": ["/opt/data/tool-candidates/opencode-snip-v1.6.1/.opencode/plugins/index.ts"],
            },
            artifact_identities=[
                {"path": str(SNIP_BIN), "sha256": "546b4e735818637f42aabcc79b357d529223385b84b28a19f28002d15d99ea5b", "kind": "compiled-cli"},
                {"path": "/opt/data/tool-candidates/opencode-snip-v1.6.1/.opencode/plugins/index.ts", "sha256": "e7b04e51dccbbeb088ebe49b34abef2d7847b0f9e2b1a933e88d59853ca2b9d0", "kind": "plugin-entry"},
                {"path": "/opt/data/tool-candidates/opencode-snip-v1.6.1/src/index.ts", "sha256": "0f4e69958c753d36ed42810c439bb1c9716d702f53213677acef7728d6463973", "kind": "plugin-source"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            default_tool_state="active-native-plugin-exact-artifact",
        ),
        "cartog-opencode-product-v2": _opencode_treatment_config(
            "cartog",
            display_name="Cartog official OpenCode MCP product v2 repaired",
            lane_name="retrieval-cartog-opencode-product-v2",
            surface="opencode-mcp/structural-retrieval+live-watch+product-guidance",
            allowed_terms=["cartog"],
            mounts=[str(CARTOG_ROOT)],
            adapter_path=OPENCODE_ADAPTER_V3,
            path_entries=[str(CARTOG_BIN.parent)],
            env={"CARTOG_MCP_COMPACT": "1", "CARTOG_NO_UPDATE_CHECK": "1"},
            mcp_server="cartog",
            mcp_command=str(CARTOG_BIN),
            mcp_args=["serve", "--watch"],
            host_integration={
                "install_commands": [
                    [str(CARTOG_BIN), "ide", "--client", "opencode", "--yes"],
                    [
                        "python3",
                        "-c",
                        "from pathlib import Path; src=Path('/opt/data/tool-candidates/cartog/docs/agent-snippet.md'); dst=Path('{repo}/AGENTS.md'); text=src.read_text(); snippet=text.split('```markdown',1)[1].split('```',1)[0].strip(); old=dst.read_text() if dst.exists() else ''; dst.write_text(old.rstrip()+'\\n\\n'+snippet+'\\n')",
                    ],
                ],
                "verify_commands": [
                    [
                        "python3",
                        "-c",
                        "from pathlib import Path; c=Path('{codex_home}/xdg-config/opencode/opencode.json'); a=Path('{repo}/AGENTS.md'); assert c.is_file() and '\"cartog\"' in c.read_text().lower(); assert a.is_file() and 'prefer cartog over grep' in a.read_text().lower() and 'mcp__cartog__cartog_search' in a.read_text()",
                    ]
                ],
                "required_files": ["{codex_home}/xdg-config/opencode/opencode.json", "{repo}/AGENTS.md"],
            },
            mcp_handshake={"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 120},
            warmup={
                "kind": "official-init-and-structural-index",
                "command": ["/bin/bash", "-lc", "set -euo pipefail; cartog init; cartog index ."],
                "cleanup_paths": [".cartog", ".cartog.toml"],
                "required_state_paths": [".cartog.toml", ".cartog/db.sqlite"],
                "output_name": "cartog-warmup-output.txt",
                "metadata_name": "cartog-warmup-metadata.json",
                "timeout_seconds": 1200,
            },
            artifact_identities=[
                {"path": str(CARTOG_BIN), "sha256": "f2f0f44841827fe05645f908d30e732bfd555013c57f5fc7768658aa1f9db8a7", "kind": "compiled-cli-mcp"},
                {"path": str(CARTOG_ROOT / "docs/agent-snippet.md"), "sha256": "09e694f5953ae45a431e31a9c4121700c487a366c031a547258486e5abf49501", "kind": "product-guidance"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            diff_exclude_paths=[".cartog", ".cartog.toml", "AGENTS.md"],
            default_tool_state="warm-structural-index+live-watch",
        ),
        "headroom-opencode-product-v3": _opencode_treatment_config(
            "headroom",
            display_name="Headroom official OpenCode integrated product v3 repaired",
            lane_name="integrated-headroom-opencode-product-v3",
            surface="opencode-proxy/context-compression+native-plugin+headroom-mcp+rtk+serena",
            allowed_terms=["headroom", "headroom_retrieve", "rtk", "serena"],
            mounts=[str(HEADROOM_ROOT), str(RTK_BIN.parent), str(SERENA_ROOT), str(UVX_SHIM.parent)],
            adapter_path=OPENCODE_ADAPTER_V3,
            path_entries=[str(UVX_SHIM.parent), "{codex_home}/home/.headroom/bin", "{codex_home}/home/.local/bin"],
            env={
                "HEADROOM_HOME": "{tool_data_dir}",
                "HEADROOM_CACHE_DIR": "{tool_data_dir}/cache",
                "HEADROOM_DISABLE_DASHBOARD": "1",
                "HEADROOM_TELEMETRY": "0",
                "HEADROOM_PROJECT": "{repo_slug}",
                "HEADROOM_OPENCODE_PLUGIN_PATH": str(HEADROOM_OPENCODE_PLUGIN),
                "OPENCODE_HOME": "{codex_home}/xdg-config/opencode",
            },
            host_integration=TOOL_CONFIGS["headroom-opencode-product-v1"]["host_integration"],
            mcp_server="headroom",
            mcp_command=str(UV_BIN),
            mcp_args=["tool", "run", "--from", str(HEADROOM_WHEEL), "--with", "mcp", "headroom", "mcp", "serve"],
            mcp_handshake={
                "attempt_required": True,
                "required": False,
                "failure_counts_as_degradation": True,
                "known_failure": "headroom 0.28.0 mcp serve is incompatible with its declared mcp>=1.0.0 dependency (Server.list_tools missing)",
                "method": "initialize-and-tools-list",
                "timeout_seconds": 120,
            },
            secondary_mcp_handshakes=[
                {
                    "server": "serena",
                    "command": str(UV_BIN),
                    "args": ["tool", "run", "--from", str(SERENA_ROOT), "serena", "start-mcp-server", "--project-from-cwd", "--context=ide", "--enable-web-dashboard", "false", "--open-web-dashboard", "false"],
                    "timeout_seconds": 120,
                }
            ],
            artifact_identities=[
                {"path": str(HEADROOM_WHEEL), "sha256": "7d4b753d8a0a33aa3222178a92aede5f43c9bc7d3642397c190854d6abbfb560", "kind": "python-wheel"},
                {"path": str(HEADROOM_OPENCODE_PLUGIN), "sha256": "957164fc98be5c7b543a249769d926b87bb0b96367ec9aaf2aee909f7d5e6d5e", "kind": "native-plugin-entry"},
                {"path": str(HEADROOM_OPENCODE_PLUGIN_CHUNK), "sha256": "ffa23c1c62a7ddfad1e71f00afb9aac7c8a249e05ff979e930c61de2650a053f", "kind": "native-plugin-bundle"},
                {"path": str(UVX_SHIM), "sha256": "dc407e8ebb7903e94580217e564e544b231f16ce2a697c247b71632bffe35b35", "kind": "uvx-runtime"},
            ],
            effective_host_config={"required": True, "source": "adapter-runtime-merged-receipt"},
            proxy_runtime_receipt={"required": True, "provider": "openai", "model": "gpt-5.6-sol"},
            native_plugin={"required": True, "path": str(HEADROOM_OPENCODE_PLUGIN)},
            diff_exclude_paths=["AGENTS.md", ".headroom", ".serena"],
            default_tool_state="active-official-integrated-wrapper-exact-artifacts",
        ),
    }
)

# Successive native OpenCode treatment batch. The selection follows the live
# compatible-screen ordering after excluding Token Savior because the pinned
# product has no OpenCode integration surface; CodeGraph is the next eligible
# product with an official OpenCode installer.
TOOL_CONFIGS.update(
    {
        "codescope-opencode-product-v1": _opencode_treatment_config(
            "codescope",
            display_name="CodeScope host-agnostic MCP on OpenCode v1",
            lane_name="codescope-opencode-product-v1",
            surface="opencode-mcp/official-initialize-instructions+warm-index",
            allowed_terms=["codescope"],
            mounts=[str(CODESCOPE_BIN), str(CODESCOPE_SURREAL_BIN)],
            adapter_path=OPENCODE_ADAPTER_V4,
            path_entries=[str(CODESCOPE_RELEASE_ROOT)],
            env={
                "CODESCOPE_DB_PATH": "{tool_data_dir}/db",
                "OPENCODE_EVALUATION_DIRECTORY": "{repo}",
            },
            host_integration={
                "verify_commands": [[str(CODESCOPE_BIN), "--version"]],
            },
            mcp_server="codescope",
            mcp_command="/bin/bash",
            mcp_args=[
                "-lc",
                (
                    f"set -euo pipefail; {CODESCOPE_BIN} start >/dev/null; "
                    f"trap '{CODESCOPE_BIN} stop >/dev/null 2>&1 || true' EXIT; "
                    f"i=0; until {CODESCOPE_BIN} status | grep -q '^running'; "
                    "do i=$((i+1)); [ \"$i\" -lt 50 ]; sleep 0.2; done; "
                    f"exec {CODESCOPE_BIN} mcp {{repo}}"
                ),
            ],
            mcp_handshake={"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 180},
            warmup={
                "kind": "official-surreal-start-and-index",
                "command": [
                    "/bin/bash",
                    "-lc",
                    (
                        f"set -euo pipefail; {CODESCOPE_BIN} start >/dev/null; "
                        f"trap '{CODESCOPE_BIN} stop >/dev/null 2>&1 || true' EXIT; "
                        f"i=0; until {CODESCOPE_BIN} status | grep -q '^running'; "
                        "do i=$((i+1)); [ \"$i\" -lt 50 ]; sleep 0.2; done; "
                        f"{CODESCOPE_BIN} index {{repo}}"
                    ),
                ],
                "output_name": "codescope-warmup-output.txt",
                "metadata_name": "codescope-warmup-metadata.json",
                "timeout_seconds": 3600,
            },
            artifact_identities=[
                {"path": str(CODESCOPE_BIN), "sha256": "d6f64f7bc7bf1ab65115fdede85d794f58151c6f1414421825959eb2101165c1", "kind": "compiled-cli-mcp"},
                {"path": str(CODESCOPE_SURREAL_BIN), "sha256": "a9a5e9e36e4f6fe922e1991a4fb0ea1ee4fe90819c5e3a8dce238a56666e8cec", "kind": "bundled-database"},
                {"path": str(OPENCODE_ADAPTER_V4), "sha256": "e3c6e77fc22ae12a6548ee3ad92836d58c2db411ceae7c3743c370c469e6bbf7", "kind": "runtime-adapter"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            default_tool_state="warm-index+official-mcp-instructions",
        ),
        "swarmvault-opencode-product-v1": _opencode_treatment_config(
            "swarmvault",
            display_name="SwarmVault official OpenCode rules, skill, hook, and MCP v1",
            lane_name="swarmvault-opencode-product-v1",
            surface="opencode-mcp+project-rules+native-plugin+skill",
            allowed_terms=["swarmvault"],
            mounts=[str(SWARMVAULT_ROOT)],
            adapter_path=OPENCODE_ADAPTER_V5,
            path_entries=[str(NODE_TOOLCHAIN_ROOT / "bin")],
            env={
                "SWARMVAULT_OUT": "{tool_data_dir}/vault",
                "SWARMVAULT_NO_NOTICES": "1",
                "OPENCODE_EVALUATION_DIRECTORY": "{repo}",
            },
            host_integration={
                "install_commands": [[
                    "/bin/bash",
                    "-lc",
                    f"set -euo pipefail; {NODE_BIN} {SWARMVAULT_CLI} init --lite; {NODE_BIN} {SWARMVAULT_CLI} install --agent opencode --hook",
                ]],
                "verify_commands": [[str(NODE_BIN), str(SWARMVAULT_CLI), "--version"]],
                "required_files": [
                    "{repo}/AGENTS.md",
                    "{repo}/.opencode/opencode.json",
                    "{repo}/.opencode/plugins/swarmvault-graph-first.js",
                    "{repo}/.opencode/skills/swarmvault/SKILL.md",
                ],
            },
            mcp_server="swarmvault",
            mcp_command=str(NODE_BIN),
            mcp_args=[str(SWARMVAULT_CLI), "mcp"],
            mcp_handshake={"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 180},
            warmup={
                "kind": "official-vault-ingest-and-compile",
                "command": [
                    "/bin/bash",
                    "-lc",
                    f"set -euo pipefail; {NODE_BIN} {SWARMVAULT_CLI} ingest {{repo}} --max-files 500; {NODE_BIN} {SWARMVAULT_CLI} compile",
                ],
                "output_name": "swarmvault-warmup-output.txt",
                "metadata_name": "swarmvault-warmup-metadata.json",
                "timeout_seconds": 3600,
            },
            artifact_identities=[
                {"path": str(SWARMVAULT_CLI), "sha256": "a61088ae9ceba5af3e0c0c5be12a214d5ab23ed2d5292d662723f84f72d7818c", "kind": "compiled-cli-mcp"},
                {"path": str(SWARMVAULT_ROOT / "packages/engine/dist/hooks/opencode.js"), "sha256": "492ee1ff509698aac8c76dc9736f11aaf35da1b3134cb5d5f743856aa1bb7416", "kind": "native-plugin-source"},
                {"path": str(OPENCODE_ADAPTER_V5), "sha256": "4fe90a1a85dfe47db5f5637c4cfdb07c89384b598d2c274ed0af080f3ae42352", "kind": "runtime-adapter"},
            ],
            post_install_artifacts=[
                {"path": "{repo}/.opencode/plugins/swarmvault-graph-first.js", "sha256": "492ee1ff509698aac8c76dc9736f11aaf35da1b3134cb5d5f743856aa1bb7416", "retain_as": "swarmvault-installed-plugin.js"},
                {"path": "{repo}/.opencode/skills/swarmvault/SKILL.md", "sha256": "c0a8cf9c84a8bb9c00bfeb2ba9a1c61e33b2b650fde999788bafa5f4161dedac", "retain_as": "swarmvault-installed-skill.md"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            preflight_requires_project=True,
            diff_exclude_paths=["AGENTS.md", ".opencode", "swarmvault.config.json", "swarmvault.schema.md"],
            default_tool_state="warm-index+active-native-plugin-and-skill",
        ),
        "graphify-opencode-product-v1": _opencode_treatment_config(
            "graphify",
            display_name="Graphify official OpenCode skill, rules, and plugin v1",
            lane_name="retrieval-graphify-opencode-product-v1",
            surface="opencode-project-skill+rules+native-pretool-plugin+warm-graph",
            allowed_terms=["graphify", "graphify-mcp"],
            mounts=[str(GRAPHIFY_ROOT), str(GRAPHIFY_WHEEL)],
            adapter_path=OPENCODE_ADAPTER_V5,
            path_entries=["{tool_data_dir}/venv/bin"],
            env={"OPENCODE_EVALUATION_DIRECTORY": "{repo}"},
            host_integration={
                "install_commands": [
                    [str(UV_BIN), "venv", "{tool_data_dir}/venv", "--python", "python3"],
                    [str(UV_BIN), "pip", "install", "--python", "{tool_data_dir}/venv/bin/python", str(GRAPHIFY_WHEEL)],
                    ["{tool_data_dir}/venv/bin/graphify", "install", "--platform", "opencode", "--project"],
                ],
                "verify_commands": [["{tool_data_dir}/venv/bin/graphify", "--version"]],
                "required_files": [
                    "{repo}/AGENTS.md",
                    "{repo}/.opencode/opencode.json",
                    "{repo}/.opencode/plugins/graphify.js",
                    "{repo}/.opencode/skills/graphify/SKILL.md",
                ],
                "timeout_seconds": 600,
            },
            warmup={
                "kind": "official-code-graph-build",
                "command": ["{tool_data_dir}/venv/bin/graphify", "update", "{repo}", "--no-cluster", "--force"],
                "cleanup_paths": ["graphify-out"],
                "required_state_paths": ["graphify-out/graph.json"],
                "output_name": "graphify-warmup-output.txt",
                "metadata_name": "graphify-warmup-metadata.json",
                "timeout_seconds": 1200,
            },
            artifact_identities=[
                {"path": str(GRAPHIFY_WHEEL), "sha256": "9c3b01b3e7745ee67149fab54af91e4dbe4743ee9632fc3ab29de62830ca1802", "kind": "python-wheel"},
                {"path": str(OPENCODE_ADAPTER_V5), "sha256": "4fe90a1a85dfe47db5f5637c4cfdb07c89384b598d2c274ed0af080f3ae42352", "kind": "runtime-adapter"},
            ],
            post_install_artifacts=[
                {"path": "{repo}/.opencode/plugins/graphify.js", "sha256": "b025b1d64b905d48cf6188392d003be971f9933e8f893d22f671c5f2428ecddb", "retain_as": "graphify-installed-plugin.js"},
                {"path": "{repo}/.opencode/skills/graphify/SKILL.md", "sha256": "f404e0adab83af433af2c807ffe27966231b0bdbb7a7ab9d6e15efadf5cd3314", "retain_as": "graphify-installed-skill.md"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            preflight_requires_project=True,
            diff_exclude_paths=["AGENTS.md", ".opencode", "graphify-out"],
            default_tool_state="warm-graph+active-native-plugin-and-skill",
        ),
        "rtk-opencode-plugin-v1": _opencode_treatment_config(
            "rtk",
            display_name="RTK official OpenCode plugin v1",
            lane_name="terminal-rtk-opencode-plugin-v1",
            surface="opencode-native-tool-execute-before/terminal-command-rewriting",
            allowed_terms=["rtk"],
            mounts=[str(RTK_BIN.parent), str(RTK_BIN.parents[2] / "hooks/opencode/rtk.ts")],
            adapter_path=OPENCODE_ADAPTER_V4,
            path_entries=[str(RTK_BIN.parent)],
            env={"RTK_TELEMETRY": "0"},
            host_integration={
                "install_commands": [[str(RTK_BIN), "init", "--global", "--opencode"]],
                "verify_commands": [[str(RTK_BIN), "init", "--global", "--opencode", "--dry-run"]],
                "required_files": ["{codex_home}/home/.config/opencode/plugins/rtk.ts"],
            },
            artifact_identities=[
                {"path": str(RTK_BIN), "sha256": "6a5f761863fc184217e6c1ae5336dd969868ad79f24e701a3efbd090a435f2ae", "kind": "compiled-cli"},
                {"path": str(RTK_BIN.parents[2] / "hooks/opencode/rtk.ts"), "sha256": "6530c131946c84892f9522abd68d4e513e1e658d8ddbad1f59388c86ebbcb6bb", "kind": "native-plugin-source"},
                {"path": str(OPENCODE_ADAPTER_V4), "sha256": "e3c6e77fc22ae12a6548ee3ad92836d58c2db411ceae7c3743c370c469e6bbf7", "kind": "runtime-adapter"},
            ],
            post_install_artifacts=[
                {"path": "{codex_home}/home/.config/opencode/plugins/rtk.ts", "sha256": "6530c131946c84892f9522abd68d4e513e1e658d8ddbad1f59388c86ebbcb6bb", "retain_as": "rtk-installed-plugin.ts"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            default_tool_state="active-native-plugin-exact-artifact",
        ),
        "codegraph-opencode-mcp-v1": _opencode_treatment_config(
            "codegraph",
            display_name="CodeGraph official OpenCode MCP product v1",
            lane_name="retrieval-codegraph-opencode-mcp-v1",
            surface="opencode-mcp+official-installer+warm-live-index",
            allowed_terms=["codegraph"],
            mounts=[str(CODEGRAPH_BIN.parent.parent.parent)],
            adapter_path=OPENCODE_ADAPTER_V4,
            path_entries=["{tool_data_dir}/bin"],
            env={"CODEGRAPH_TELEMETRY": "0", "OPENCODE_EVALUATION_DIRECTORY": "{repo}"},
            host_integration={
                "install_commands": [
                    ["mkdir", "-p", "{tool_data_dir}/bin"],
                    [
                        "/bin/bash",
                        "-lc",
                        f"printf '%s\\n' '#!/bin/sh' 'exec {CODEGRAPH_BIN} \"$@\"' > {{tool_data_dir}}/bin/codegraph && chmod 755 {{tool_data_dir}}/bin/codegraph",
                    ],
                    ["{tool_data_dir}/bin/codegraph", "install", "--target", "opencode", "--location", "local", "--yes"],
                ],
                "verify_commands": [["{tool_data_dir}/bin/codegraph", "--version"]],
                "required_files": ["{tool_data_dir}/bin/codegraph", "{repo}/opencode.jsonc", "{repo}/AGENTS.md"],
            },
            mcp_server="codegraph",
            mcp_command=str(NODE_BIN),
            mcp_args=[str(CODEGRAPH_BIN), "serve", "--mcp"],
            mcp_handshake={"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 180},
            warmup={
                "kind": "official-codegraph-index",
                "command": ["{tool_data_dir}/bin/codegraph", "init", "{repo}"],
                "cleanup_paths": [".codegraph"],
                "required_state_paths": [".codegraph"],
                "output_name": "codegraph-warmup-output.txt",
                "metadata_name": "codegraph-warmup-metadata.json",
                "timeout_seconds": 1200,
            },
            artifact_identities=[
                {"path": str(CODEGRAPH_BIN), "sha256": "7cb7ae2a31d1c30a11d2b3190f89a7f9c2db3886ad5903affdc080bd7922755e", "kind": "compiled-cli-mcp"},
                {"path": str(OPENCODE_ADAPTER_V4), "sha256": "e3c6e77fc22ae12a6548ee3ad92836d58c2db411ceae7c3743c370c469e6bbf7", "kind": "runtime-adapter"},
            ],
            post_install_artifacts=[
                {"path": "{repo}/opencode.jsonc", "sha256": "578c6965fb0902811aeb1e9607bcf4c41aa0de3e25a0fdfbe0b7a838a31496a1", "retain_as": "codegraph-installed-opencode.jsonc"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            diff_exclude_paths=["AGENTS.md", "opencode.jsonc", ".codegraph"],
            default_tool_state="warm-live-index+official-mcp-instructions",
        ),
    }
)

# Successive native OpenCode treatment batch 2. These profiles are carried
# forward from the next compatible Codex screen because the first OpenCode
# screen already consumed the five earlier eligible products.
TOOL_CONFIGS.update(
    {
        "jcodemunch-opencode-product-v1": _opencode_treatment_config(
            "jcodemunch",
            display_name="jCodemunch guide-faithful OpenCode MCP v1",
            lane_name="retrieval-jcodemunch-opencode-product-v1",
            surface="opencode-mcp+product-authored-guidance+warm-index",
            allowed_terms=["jcodemunch", "jcodemunch-mcp"],
            mounts=[str(JCODEMUNCH_ROOT), str(JCODEMUNCH_WHEEL), "{repository_root}/scripts/install_jcodemunch_opencode_guidance.py"],
            adapter_path=OPENCODE_ADAPTER_V6,
            env={"OPENCODE_TOOL_DATA_DIR": "{tool_data_dir}", "JCODEMUNCH_LOG_LEVEL": "ERROR"},
            path_entries=["{tool_data_dir}/venv/bin"],
            host_integration={
                "install_commands": [
                    [str(UV_BIN), "venv", "{tool_data_dir}/venv", "--python", "python3"],
                    [str(UV_BIN), "pip", "install", "--python", "{tool_data_dir}/venv/bin/python", str(JCODEMUNCH_WHEEL)],
                    ["python3", "{repository_root}/scripts/install_jcodemunch_opencode_guidance.py", "--source-root", str(JCODEMUNCH_ROOT), "--expected-commit", JCODEMUNCH_COMMIT, "--repo", "{repo}", "--receipt", "{tool_data_dir}/guidance-install.json"],
                ],
                "verify_commands": [["{tool_data_dir}/venv/bin/jcodemunch-mcp", "--version"]],
                "required_files": ["{tool_data_dir}/venv/bin/jcodemunch-mcp", "{tool_data_dir}/guidance-install.json", "{repo}/AGENTS.md"],
                "timeout_seconds": 900,
            },
            mcp_server="jcodemunch",
            mcp_command="{tool_data_dir}/venv/bin/jcodemunch-mcp",
            mcp_args=[],
            mcp_handshake={"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 120},
            warmup={"kind": "product-native-code-index-build", "command": ["{tool_data_dir}/venv/bin/jcodemunch-mcp", "index", "{repo}"], "output_name": "jcodemunch-warmup-output.txt", "metadata_name": "jcodemunch-warmup-metadata.json", "timeout_seconds": 1200},
            artifact_identities=[
                {"path": str(JCODEMUNCH_WHEEL), "sha256": "9ae3a44c2be5709d33fa2b56c9e569906ed63906a907f89b4762a370d397ed54", "kind": "python-wheel"},
                {"path": str(JCODEMUNCH_ROOT / "AGENT_INSTALL_UNIVERSAL.md"), "sha256": "2026d09f4af85e972a5c4a9874d91bd8a8675ab7fbb44a283911fd06afd0abb2", "kind": "product-guidance"},
                {"path": str(OPENCODE_ADAPTER_V6), "sha256": "1b98aaec34711b3a7bb09ce269c12bb06421ab08913d06593fb6d2c6641a34a3", "kind": "runtime-adapter"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            diff_exclude_paths=["AGENTS.md"],
            default_tool_state="warm-index+product-guidance",
        ),
        "repowise-opencode-product-v2": _opencode_treatment_config(
            "repowise",
            display_name="RepoWise 0.39.0 provider-backed OpenCode MCP with product guidance",
            lane_name="retrieval-repowise-opencode-product-v2",
            surface="opencode-mcp+product-guidance+provider-backed-index",
            allowed_terms=["repowise"],
            mounts=[str(REPOWISE_ROOT), str(REPOWISE_WHEEL)],
            adapter_path=OPENCODE_ADAPTER_V9,
            path_entries=["{tool_data_dir}/venv/bin"],
            env={"OPENCODE_TOOL_DATA_DIR": "{tool_data_dir}", "REPOWISE_PROVIDER": "opencode"},
            host_integration={
                "install_commands": [
                    [str(UV_BIN), "venv", "{tool_data_dir}/venv", "--python", "python3"],
                    [str(UV_BIN), "pip", "install", "--python", "{tool_data_dir}/venv/bin/python", str(REPOWISE_WHEEL)],
                    ["{tool_data_dir}/venv/bin/repowise", "init", "--yes", "--provider", "opencode", "--no-prose", "--no-claude-md", "--no-codex", "--agents", "--no-workspace", "{repo}"],
                ],
                "verify_commands": [["{tool_data_dir}/venv/bin/repowise", "--version"]],
                "required_files": [
                    "{tool_data_dir}/venv/bin/repowise",
                    "{repo}/.repowise/wiki.db",
                    "{repo}/.repowise/config.yaml",
                    "{repo}/.mcp.json",
                    "{repo}/AGENTS.md",
                ],
                "timeout_seconds": 3600,
            },
            mcp_server="repowise",
            mcp_command="{tool_data_dir}/venv/bin/repowise",
            mcp_args=["mcp"],
            mcp_handshake={"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 180},
            artifact_identities=[
                {"path": str(REPOWISE_WHEEL), "sha256": "e7d3068856a45a3d0501b84e6f52db24521512803a07881cdf145da546d932b4", "kind": "python-wheel"},
                {"path": str(REPOWISE_ROOT / "README.md"), "sha256": "44ed3725616544a8d4eb4695c99e33c8bd28ce2bfde4c12134d1fde0e1d65a3a", "kind": "product-guidance-source"},
                {"path": str(OPENCODE_ADAPTER_V9), "sha256": "6cabc28420901ec9fea5997bd63559311d73d2c7fb9c86e54d64ba42c67b822e", "kind": "runtime-adapter"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            diff_exclude_paths=[".repowise", ".mcp.json", "AGENTS.md"],
            default_tool_state="warm-index+product-guidance",
        ),
        "leanctx-opencode-hybrid-v1": _opencode_treatment_config(
            "leanctx",
            display_name="LeanCTX official OpenCode hybrid integration v1",
            lane_name="integrated-leanctx-opencode-hybrid-v1",
            surface="opencode-mcp+instructions+shell-output-compression+warm-index",
            allowed_terms=["lean-ctx", "mcp_lean_ctx", "ctx_read", "ctx_search", "ctx_shell", "ctx_graph"],
            mounts=[str(LEANCTX_BINARY), str(LEANCTX_ROOT)],
            adapter_path=OPENCODE_ADAPTER_V7,
            env={"OPENCODE_TOOL_DATA_DIR": "{tool_data_dir}", "LEAN_CTX_DATA_DIR": "{tool_data_dir}/leanctx"},
            host_integration={
                "install_commands": [
                    [str(LEANCTX_BINARY), "init", "--agent", "opencode"],
                    ["/bin/bash", "-lc", "set -e; mkdir -p {codex_home}/xdg-config/opencode; cp {codex_home}/home/.config/opencode/AGENTS.md {codex_home}/xdg-config/opencode/AGENTS.md; cp {codex_home}/home/.config/opencode/opencode.json {codex_home}/xdg-config/opencode/opencode.json"],
                ],
                "verify_commands": [[str(LEANCTX_BINARY), "--version"]],
                "required_files": ["{codex_home}/xdg-config/opencode/AGENTS.md", "{codex_home}/xdg-config/opencode/opencode.json"],
                "timeout_seconds": 600,
            },
            mcp_server="lean-ctx",
            mcp_command=str(LEANCTX_BINARY),
            mcp_args=[],
            mcp_handshake={"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 120},
            warmup={"kind": "product-native-index-build", "command": [str(LEANCTX_BINARY), "index", "build", "{repo}"], "output_name": "leanctx-warmup-output.txt", "metadata_name": "leanctx-warmup-metadata.json", "timeout_seconds": 1800},
            artifact_identities=[
                {"path": str(LEANCTX_BINARY), "sha256": "475e89e495c31824ef324f92e695706ddbd890dff2c3b55b807cd1f8526c6db9", "kind": "compiled-cli-mcp"},
                {"path": str(LEANCTX_ROOT / "README.md"), "sha256": "3511c0d1e04eda53f9e66f7528b5179138b4e3963891c07c8749fa0c3b98f5cb", "kind": "product-guidance-source"},
                {"path": str(OPENCODE_ADAPTER_V7), "sha256": "e559c52ef4ef8a7e6b02cd03bfc2b86c2da039da493969d21f1ebbeb116c1f15", "kind": "runtime-adapter"},
            ],
            post_install_artifacts=[
                {"path": "{codex_home}/xdg-config/opencode/AGENTS.md", "sha256": "8d52b53942d6ab1178ddaeafc8df555e74925659565bcf4bddfbba44e94d11b7", "retain_as": "leanctx-opencode-AGENTS.md"},
                {"path": "{codex_home}/xdg-config/opencode/opencode.json", "sha256": "c429860c056e9469335ef48d4f66cb54886b8e45db8486dabcb1afa433de9d5c", "retain_as": "leanctx-opencode-config.json"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            diff_exclude_paths=["AGENTS.md", "LEAN-CTX.md", ".lean-ctx"],
            default_tool_state="warm-index+active-guidance",
        ),
        "sigmap-opencode-product-v1": _opencode_treatment_config(
            "sigmap",
            display_name="SigMap official OpenCode MCP and context setup v1",
            lane_name="retrieval-sigmap-opencode-product-v1",
            surface="opencode-mcp+product-setup+warm-context-map",
            allowed_terms=["sigmap", "gen-context"],
            mounts=[str(SIGMAP_ROOT)],
            adapter_path=OPENCODE_ADAPTER_V6,
            env={"OPENCODE_TOOL_DATA_DIR": "{tool_data_dir}", "SIGMAP_TELEMETRY": "0"},
            host_integration={
                "install_commands": [
                    ["/bin/bash", "-lc", "cd {repo} && exec " + str(NODE_BIN) + " " + str(SIGMAP_ROOT / "gen-context.js") + " mcp install opencode"],
                ],
                "verify_commands": [[str(NODE_BIN), str(SIGMAP_ROOT / "gen-context.js"), "--version"]],
                "required_files": ["{repo}/opencode.json"],
                "timeout_seconds": 600,
            },
            mcp_server="sigmap",
            mcp_command=str(NODE_BIN),
            mcp_args=[str(SIGMAP_ROOT / "gen-context.js"), "--mcp"],
            mcp_handshake={"required": True, "method": "initialize-and-tools-list", "timeout_seconds": 120},
            warmup={"kind": "signature-map-build", "command": [str(NODE_BIN), str(SIGMAP_ROOT / "gen-context.js"), "--adapter", "copilot", "--no-track"], "cleanup_paths": [".context"], "output_name": "sigmap-warmup-output.txt", "metadata_name": "sigmap-warmup-metadata.json", "timeout_seconds": 1200},
            artifact_identities=[
                {"path": str(SIGMAP_ROOT / "gen-context.js"), "sha256": "1a920ef5dfb50f9f1a23baa7d26ab2f9329616242713a7d8734928970ad4fb59", "kind": "standalone-mcp-bundle"},
                {"path": str(SIGMAP_ROOT / "package.json"), "sha256": "f8478ca025747dada0b86288f696e1ae39ea8701a5081c60f54c70eafa034963", "kind": "source-package"},
                {"path": str(OPENCODE_ADAPTER_V6), "sha256": "1b98aaec34711b3a7bb09ce269c12bb06421ab08913d06593fb6d2c6641a34a3", "kind": "runtime-adapter"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            diff_exclude_paths=[".context", "opencode.json"],
            default_tool_state="warm-context-map+active-mcp",
        ),
        "ponytail-opencode-plugin-v1": _opencode_treatment_config(
            "ponytail",
            display_name="Ponytail official OpenCode plugin v1",
            lane_name="artifact-ponytail-opencode-plugin-v1",
            surface="opencode-plugin+per-turn-rules+skills+commands",
            allowed_terms=["ponytail"],
            mounts=[str(PONYTAIL_ROOT)],
            adapter_path=OPENCODE_ADAPTER_V6,
            env={"OPENCODE_TOOL_DATA_DIR": "{tool_data_dir}"},
            host_integration={
                "install_commands": [["/bin/bash", "-lc", "set -e; mkdir -p {repo}/.opencode/plugins; cp /opt/data/tool-candidates/ponytail/.opencode/plugins/ponytail.mjs {repo}/.opencode/plugins/ponytail.mjs; printf '\\n\\n# Ponytail product guidance (verbatim)\\n' >> {repo}/AGENTS.md; cat /opt/data/tool-candidates/ponytail/AGENTS.md >> {repo}/AGENTS.md"]],
                "verify_commands": [["python3", "-c", "from pathlib import Path; assert Path('{repo}/.opencode/plugins/ponytail.mjs').is_file(); assert Path('{repo}/AGENTS.md').is_file()"]],
                "required_files": ["{repo}/.opencode/plugins/ponytail.mjs", "{repo}/AGENTS.md"],
                "timeout_seconds": 300,
            },
            native_plugin={"required": True, "path": "{repo}/.opencode/plugins/ponytail.mjs"},
            artifact_identities=[
                {"path": str(PONYTAIL_ROOT / ".opencode/plugins/ponytail.mjs"), "sha256": "e2443648e1864724f56e2a073fdf2f29199772606d9ea1c175fe06eaa3b75853", "kind": "native-plugin"},
                {"path": str(PONYTAIL_ROOT / "AGENTS.md"), "sha256": "1cd148db944eff33bf8bb878c41a290fe85b86de3e65ac311d5d501e71a0cdbf", "kind": "product-guidance"},
                {"path": str(OPENCODE_ADAPTER_V6), "sha256": "1b98aaec34711b3a7bb09ce269c12bb06421ab08913d06593fb6d2c6641a34a3", "kind": "runtime-adapter"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            diff_exclude_paths=["AGENTS.md", ".opencode"],
            default_tool_state="active-native-plugin+per-turn-guidance",
        ),
        "caveman-opencode-plugin-v1": _opencode_treatment_config(
            "caveman",
            display_name="Caveman official OpenCode plugin and guidance v1",
            lane_name="behavior-caveman-opencode-plugin-v1",
            surface="opencode-plugin+prompt-reinforcement+skills+commands",
            allowed_terms=["caveman", "cavecrew"],
            mounts=[str(CAVEMAN_ROOT)],
            adapter_path=OPENCODE_ADAPTER_V6,
            env={"OPENCODE_TOOL_DATA_DIR": "{tool_data_dir}"},
            host_integration={
                "install_commands": [[str(NODE_BIN), str(CAVEMAN_ROOT / "bin/install.js"), "--only", "opencode", "--with-init"]],
                "verify_commands": [[str(NODE_BIN), str(CAVEMAN_ROOT / "bin/install.js"), "--list"]],
                "required_files": ["{codex_home}/xdg-config/opencode/plugins/caveman/plugin.js", "{repo}/AGENTS.md"],
                "timeout_seconds": 600,
            },
            native_plugin={"required": True, "path": "{codex_home}/xdg-config/opencode/plugins/caveman/plugin.js"},
            artifact_identities=[
                {"path": str(CAVEMAN_ROOT / "src/plugins/opencode/plugin.js"), "sha256": "6d68e8dfe205354718729a5f5c9ca9d555a045af6b2cbbc3b6a84caad1076df7", "kind": "native-plugin-source"},
                {"path": str(CAVEMAN_ROOT / "src/plugins/opencode/package.json"), "sha256": "b603811ba72eb71581db5b02045fb5f8903e3c46dcf7b40f36eeb81fbba23274", "kind": "native-plugin-package"},
                {"path": str(OPENCODE_ADAPTER_V6), "sha256": "1b98aaec34711b3a7bb09ce269c12bb06421ab08913d06593fb6d2c6641a34a3", "kind": "runtime-adapter"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            diff_exclude_paths=["AGENTS.md", ".opencode"],
            default_tool_state="active-native-plugin+per-session-guidance",
        ),
        "lowfat-opencode-plugin-v1": _opencode_treatment_config(
            "lowfat",
            display_name="LowFat official OpenCode plugin v1",
            lane_name="terminal-lowfat-opencode-plugin-v1",
            surface="opencode-native-tool-execute-before/terminal-command-rewriting",
            allowed_terms=["opencode", "lowfat"],
            mounts=[str(LOWFAT_ROOT), str(LOWFAT_BIN)],
            adapter_path=OPENCODE_ADAPTER_V7,
            path_entries=[str(LOWFAT_BIN.parent)],
            env={"LOWFAT_TELEMETRY": "0"},
            host_integration={
                "install_commands": [[str(LOWFAT_BIN), "opencode", "install"]],
                "verify_commands": [[str(LOWFAT_BIN), "--version"]],
                "required_files": ["{codex_home}/xdg-config/opencode/plugins/lowfat.ts"],
                "timeout_seconds": 300,
            },
            native_plugin={"required": True, "path": "{codex_home}/xdg-config/opencode/plugins/lowfat.ts"},
            artifact_identities=[
                {"path": str(LOWFAT_BIN), "sha256": "609e9e42d9f01b9b1c4203dc00197498c65a629453d07927cbd68cea83980558", "kind": "official-release-binary"},
                {"path": str(LOWFAT_ROOT / "crates/lowfat/embedded/opencode/lowfat.ts"), "sha256": "49a6d53d34f40a00a1d8ebdccffee5d73572db22319ee5a99959429b634bf6ed", "kind": "native-plugin-source"},
                {"path": str(OPENCODE_ADAPTER_V7), "sha256": "e7dbe311ae1ac75ebcc0838512e84efe80282f15b7a69c2db13d7f8e92fc3a3c", "kind": "runtime-adapter"},
            ],
            post_install_artifacts=[
                {"path": "{codex_home}/xdg-config/opencode/plugins/lowfat.ts", "sha256": "49a6d53d34f40a00a1d8ebdccffee5d73572db22319ee5a99959429b634bf6ed", "retain_as": "lowfat-installed-plugin.ts"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            default_tool_state="active-native-plugin-exact-artifact",
        ),
        "dcp-opencode-plugin-v1": _opencode_treatment_config(
            "dcp",
            display_name="Dynamic Context Pruning official OpenCode plugin v3.1.14",
            lane_name="context-dcp-opencode-plugin-v1",
            surface="opencode-native-context-pruning+compress-tool+automatic-cleanup",
            allowed_terms=["opencode", "dcp", "compress"],
            mounts=[str(DCP_ROOT)],
            adapter_path=OPENCODE_ADAPTER_V8,
            env={"OPENCODE_TOOL_DATA_DIR": "{tool_data_dir}"},
            host_integration={
                "controller_install_commands": [[str(OPENCODE_BIN), "plugin", "@tarquinen/opencode-dcp@3.1.14", "--global"]],
                "required_files": [
                    "{codex_home}/xdg-config/opencode/opencode.jsonc",
                    "{codex_home}/xdg-config/opencode/tui.json",
                    "{codex_home}/xdg-cache/opencode/packages/@tarquinen/opencode-dcp@3.1.14/node_modules/@tarquinen/opencode-dcp/dist/index.js",
                ],
                "timeout_seconds": 600,
            },
            native_plugin={"required": True, "path": "{codex_home}/xdg-cache/opencode/packages/@tarquinen/opencode-dcp@3.1.14/node_modules/@tarquinen/opencode-dcp/dist/index.js"},
            artifact_identities=[
                {"path": str(DCP_ROOT / "package.json"), "sha256": "9b7f126d0f5bbe06f1b17b583e0cbc7b2e66d556a58d646574319dc65d3d410e", "kind": "source-package"},
                {"path": str(DCP_ROOT / "package-lock.json"), "sha256": "cae2ac00ee6abc966e7132732fb975fe0c1d5e5494c2ac48c7cf566718aa5a98", "kind": "source-lock"},
                {"path": str(DCP_ROOT / "README.md"), "sha256": "1905a791ba86ea0f8cd8771364f7c5a8e6a3634ecb636df4eeede1614530b882", "kind": "product-guidance"},
                {"path": str(OPENCODE_ADAPTER_V8), "sha256": "d5fcd88e033767659da3acf17486273059cd566c29475c274349d2214428545c", "kind": "runtime-adapter"},
            ],
            post_install_artifacts=[
                {"path": "{codex_home}/xdg-config/opencode/opencode.jsonc", "sha256": "9b8a141b67efdf6fbcb1123f859cdc5acc41e35ab795fb8385029ff508221dd9", "retain_as": "dcp-opencode-config.jsonc"},
                {"path": "{codex_home}/xdg-config/opencode/tui.json", "sha256": "0149ceca7dfcbed690669efd026606124f175fed423b2067dd1a8f0c0a1262c0", "retain_as": "dcp-opencode-tui.json"},
                {"path": "{codex_home}/xdg-cache/opencode/packages/@tarquinen/opencode-dcp@3.1.14/node_modules/@tarquinen/opencode-dcp/dist/index.js", "sha256": "1e70b38527d6c604d9437bb447a67c857cd6f0cfe02f4fa69b69729e2ef57432", "retain_as": "dcp-installed-plugin.js"},
            ],
            effective_host_config={"required": True, "source": "adapter-probe"},
            default_tool_state="active-native-plugin+automatic-cleanup+model-visible-compress",
        ),
    }
)

# A standalone provider control: shares the pinned OpenCode binary and narrow
# compatibility adapter but must take OpenRouter's explicit model namespace.
TOOL_CONFIGS["opencode-openrouter-product-v1"] = {
    **TOOL_CONFIGS["opencode-codex-product-v1"],
    "display_name": "OpenCode CLI 1.18.9 via OpenRouter",
    "lane_name": "baseline-opencode-openrouter-no-mcp",
    "surface": "replacement-agent-runtime/openrouter-provider-control",
    "data_dir_name": "baseline-opencode-openrouter-no-mcp",
    "auth_provider": "openrouter",
    "codex_wrapper": {
        **TOOL_CONFIGS["opencode-codex-product-v1"]["codex_wrapper"],
        "args": [
            *TOOL_CONFIGS["opencode-codex-product-v1"]["codex_wrapper"]["args"],
            "--provider", "openrouter",
            "--provider-model", "openrouter/openai/gpt-5.6-sol",
        ],
    },
    "preflight_command": [
        *TOOL_CONFIGS["opencode-codex-product-v1"]["preflight_command"][:-1],
        "--provider", "openrouter",
        "--provider-model", "openrouter/openai/gpt-5.6-sol",
        "--probe",
    ],
    "tool_manifest_identity": "current-file-v1",
}


def _claude_readme_config(
    base_name: str,
    *,
    lane_name: str,
    surface: str,
    install_commands: list[list[str]],
    verify_commands: list[list[str]],
    required_files: list[str],
    diff_exclude_paths: list[str],
    timeout_seconds: int = 900,
    mcp_args: list[str] | None = None,
    env: dict[str, str] | None = None,
    warmup: dict[str, Any] | None = None,
    claude_features: dict[str, Any] | None = None,
    mounts: list[str | Path] | None = None,
    backend: str = "docker",
) -> dict[str, Any]:
    """Clone a historical adapter and bind the pinned README's Claude surface."""
    config = copy.deepcopy(TOOL_CONFIGS[base_name])
    config.update(
        {
            "lane_name": lane_name,
            "surface": surface,
            "diff_exclude_paths": diff_exclude_paths,
            "host_integration_backend": backend,
            "mounts": list(mounts) if mounts is not None else config.get("mounts", []),
            "host_integration": {
                "install_commands": install_commands,
                "verify_commands": verify_commands,
                "required_files": required_files,
                "timeout_seconds": timeout_seconds,
            },
        }
    )
    if (claude_features or {}).get("mcp"):
        config["mcp_handshake"] = {
            "required": True,
            "method": "initialize-and-tools-list",
            "timeout_seconds": 120,
        }
    if mcp_args is not None:
        config["mcp_args"] = mcp_args
    if env is not None:
        config["env"] = env
    if warmup is not None:
        config["warmup"] = warmup
    if claude_features is not None:
        config["claude_features"] = claude_features
    return config


TOOL_CONFIGS.update(
    {
        "cartog-claude-code-product-v1": _claude_readme_config(
            "cartog",
            lane_name="retrieval-cartog-claude-code-product-v1",
            surface="claude-code-readme-product-init+index+ide+mcp",
            install_commands=[
                [str(CARTOG_BIN), "init"],
                [str(CARTOG_BIN), "ide", "--client", "claude-code", "--scope", "all", "--no-watch"],
                [str(CARTOG_BIN), "index"],
            ],
            verify_commands=[[str(CARTOG_BIN), "--version"]],
            required_files=[
                "{repo}/.cartog.toml",
                "{repo}/.mcp.json",
                "{repo}/.cartog/db.sqlite",
                "{codex_home}/claude-config/settings.json",
            ],
            diff_exclude_paths=[".cartog", ".cartog.toml", ".mcp.json", ".claude", "CLAUDE.md"],
            timeout_seconds=1200,
            mcp_args=["serve"],
            claude_features={"mcp": True},
        ),
        "codegraph-claude-code-mcp-v1": _claude_readme_config(
            "codegraph",
            lane_name="retrieval-codegraph-claude-code-mcp-v1",
            surface="claude-code-readme-install+init+mcp",
            install_commands=[
                [str(CODEGRAPH_BIN), "install", "--target", "claude", "--yes"],
                [str(CODEGRAPH_BIN), "init", "{repo}"],
            ],
            verify_commands=[[str(CODEGRAPH_BIN), "--version"]],
            required_files=[
                "{codex_home}/home/.claude.json",
                "{codex_home}/claude-config/settings.json",
                "{codex_home}/claude-config/CLAUDE.md",
            ],
            diff_exclude_paths=[".codegraph", ".claude", ".mcp.json", "CLAUDE.md"],
            mcp_args=["serve", "--mcp"],
            claude_features={"mcp": True},
        ),
        "codescope-claude-code-mcp-v1": _claude_readme_config(
            "codescope",
            lane_name="codescope-claude-code-mcp-v1",
            surface="claude-code-readme-init+bundled-surreal+mcp",
            install_commands=[
                [
                    "/bin/bash",
                    "-lc",
                    "set -euo pipefail; mkdir -p {codex_home}/home/.codescope/bin; cp "
                    + str(CODESCOPE_SURREAL_BIN)
                    + " {codex_home}/home/.codescope/bin/surreal; chmod 755 {codex_home}/home/.codescope/bin/surreal",
                ],
                [str(CODESCOPE_BIN), "init", "--agent", "claude-code", "{repo}"],
            ],
            verify_commands=[[str(CODESCOPE_BIN), "--version"]],
            required_files=[
                "{codex_home}/home/.codescope/bin/surreal",
                "{repo}/.mcp.json",
            ],
            diff_exclude_paths=[".codescope", ".mcp.json", ".claude", "CLAUDE.md"],
            timeout_seconds=1200,
            claude_features={"mcp": True},
        ),
        "graphify-claude-code-skill-v1": _claude_readme_config(
            "graphify",
            lane_name="retrieval-graphify-claude-code-skill-v1",
            surface="claude-code-readme-claude-install+pretooluse-hook+mcp",
            install_commands=[[str(UV_BIN), "tool", "run", "--from", str(GRAPHIFY_WHEEL), "graphify", "claude", "install"]],
            verify_commands=[[str(UV_BIN), "tool", "run", "--from", str(GRAPHIFY_WHEEL), "graphify", "--help"]],
            required_files=[
                "{repo}/CLAUDE.md",
                "{repo}/.claude/settings.json",
            ],
            diff_exclude_paths=["graphify-out", ".claude", "CLAUDE.md", ".mcp.json"],
            claude_features={"mcp": True, "hooks": True, "guidance_append": "graphify"},
        ),
        "leanctx-claude-code-hybrid-v1": _claude_readme_config(
            "leanctx-codex-hybrid-v1",
            lane_name="integrated-leanctx-claude-code-hybrid-v1",
            surface="claude-code-readme-init+hybrid-hooks+skill+mcp",
            install_commands=[[str(LEANCTX_BINARY), "init", "--agent", "claude"]],
            verify_commands=[[str(LEANCTX_BINARY), "--version"]],
            required_files=[
                "{codex_home}/claude-config/.claude.json",
                "{codex_home}/claude-config/settings.json",
                "{codex_home}/claude-config/CLAUDE.md",
                "{codex_home}/claude-config/hooks/lean-ctx-redirect-native",
                "{codex_home}/claude-config/skills/lean-ctx/SKILL.md",
                "{repo}/AGENTS.md",
                "{repo}/LEAN-CTX.md",
                "{repo}/.claude/settings.local.json",
            ],
            diff_exclude_paths=[".lean-ctx", ".claude", "AGENTS.md", "LEAN-CTX.md", ".mcp.json"],
            claude_features={"hooks": True, "mcp": True, "skill": "lean-ctx"},
        ),
        "lowfat-claude-code-hook-v1": _claude_readme_config(
            "lowfat",
            lane_name="terminal-lowfat-claude-code-hook-v1",
            surface="claude-code-readme-pretooluse+posttooluse-hooks",
            install_commands=[
                [
                    "python3",
                    CLAUDE_README_HOOK_INSTALLER,
                    "--tool",
                    "lowfat",
                    "--settings",
                    "{codex_home}/claude-config/settings.json",
                ],
            ],
            verify_commands=[[str(LOWFAT_BIN), "--version"]],
            required_files=["{codex_home}/claude-config/settings.json"],
            diff_exclude_paths=[".claude", "CLAUDE.md", ".mcp.json"],
            claude_features={"hooks": True},
            backend="host",
        ),
        "serena-claude-code-mcp-v1": _claude_readme_config(
            "serena",
            lane_name="retrieval-serena-claude-code-mcp-v1",
            surface="claude-code-readme-setup+mcp",
            install_commands=[
                [str(UV_BIN), "tool", "run", "--from", str(SERENA_ROOT), "serena", "init"],
                [
                    "claude", "mcp", "add", "--scope", "user", "serena", "--",
                    str(UV_BIN), "tool", "run", "--from", str(SERENA_ROOT), "serena",
                    "start-mcp-server", "--transport", "stdio", "--context", "claude-code",
                    "--mode", "no-onboarding", "--mode", "no-memories", "--project-from-cwd",
                ],
            ],
            verify_commands=[
                [str(UV_BIN), "tool", "run", "--from", str(SERENA_ROOT), "serena", "--help"],
                ["claude", "mcp", "get", "serena"],
            ],
            required_files=["{codex_home}/claude-config/.claude.json"],
            diff_exclude_paths=[".serena", ".mcp.json", ".claude", "CLAUDE.md"],
            mcp_args=[
                "tool", "run", "--from", str(SERENA_ROOT), "serena", "start-mcp-server",
                "--transport", "stdio", "--context", "claude-code", "--mode", "no-onboarding",
                "--mode", "no-memories", "--project-from-cwd",
            ],
            claude_features={"mcp": True},
        ),
        "sigmap-claude-code-mcp-v1": _claude_readme_config(
            "sigmap",
            lane_name="retrieval-sigmap-claude-code-mcp-v1",
            surface="claude-code-readme-mcp-install+context-map",
            install_commands=[[str(NODE_BIN), str(SIGMAP_ROOT / "gen-context.js"), "mcp", "install", "claude", "--global"]],
            verify_commands=[[str(NODE_BIN), str(SIGMAP_ROOT / "gen-context.js"), "mcp", "list", "--json"]],
            required_files=["{repo}/.claude/settings.json"],
            diff_exclude_paths=[".context", ".mcp.json", ".claude", "CLAUDE.md"],
            warmup={
                "cleanup_paths": [".context"],
                "command": [str(NODE_BIN), str(SIGMAP_ROOT / "gen-context.js"), "--adapter", "claude", "--no-track"],
                "kind": "signature-map-build",
                "metadata_name": "sigmap-warmup-metadata.json",
                "output_name": "sigmap-warmup-output.txt",
                "timeout_seconds": 900,
            },
            claude_features={"mcp": True},
        ),
        "snip-claude-code-hook-v1": _claude_readme_config(
            "snip",
            lane_name="terminal-snip-claude-code-hook-v1",
            surface="claude-code-readme-init+pretooluse-hook",
            install_commands=[[str(SNIP_BIN), "init", "--agent", "claude-code"]],
            verify_commands=[[str(SNIP_BIN), "hook-audit"]],
            required_files=["{codex_home}/claude-config/settings.json"],
            diff_exclude_paths=[".snip", ".claude", "CLAUDE.md", ".mcp.json"],
            claude_features={"hooks": True},
        ),
        "token-savior-claude-code-product-v1": _claude_readme_config(
            "token-savior",
            lane_name="integrated-token-savior-claude-code-product-v1",
            surface="claude-code-readme-init+hooks+mcp",
            install_commands=[[str(UV_BIN), "tool", "run", "--from", str(TOKEN_SAVIOR_WHEEL), "ts", "init", "--agent", "claude", "--yes"]],
            verify_commands=[[str(UV_BIN), "tool", "run", "--from", str(TOKEN_SAVIOR_WHEEL), "ts", "init", "--agent", "claude", "--dry-run", "--yes"]],
            required_files=["{codex_home}/claude-config/settings.json"],
            diff_exclude_paths=[".token-savior", ".claude", "CLAUDE.md", ".mcp.json"],
            claude_features={"hooks": True, "mcp": True},
        ),
        "tokenjuice-claude-code-hook-v1": _claude_readme_config(
            "tokenjuice",
            lane_name="terminal-tokenjuice-claude-code-hook-v1",
            surface="claude-code-readme-install+pretooluse-hook",
            install_commands=[[str(TOKENJUICE_BIN), "install", "claude-code"]],
            verify_commands=[[str(TOKENJUICE_BIN), "doctor", "claude-code"]],
            required_files=["{codex_home}/claude-config/settings.json"],
            diff_exclude_paths=[".tokenjuice", ".claude", "CLAUDE.md", ".mcp.json"],
            claude_features={"hooks": True},
        ),
        "jcodemunch-claude-code-mcp-v1": _claude_readme_config(
            "jcodemunch-mcp",
            lane_name="retrieval-jcodemunch-claude-code-mcp-v1",
            surface="claude-code-readme-init+mcp+policy+hooks+index",
            install_commands=[
                [
                    str(UV_BIN), "tool", "run", "--from", str(JCODEMUNCH_WHEEL), "jcodemunch-mcp", "init",
                    "--client", "claude-code", "--claude-md", "project", "--hooks", "--index", "--audit",
                    "--yes", "--no-share-savings",
                ],
                [
                    "/bin/bash", "-lc",
                    "set -euo pipefail; "
                    "claude mcp remove --scope local jcodemunch >/dev/null 2>&1 || true; "
                    "claude mcp remove --scope user jcodemunch >/dev/null 2>&1 || true; "
                    "claude mcp remove --scope project jcodemunch >/dev/null 2>&1 || true; "
                    f"exec claude mcp add --scope user jcodemunch -- {UV_BIN} tool run --from {JCODEMUNCH_WHEEL} "
                    "jcodemunch-mcp serve --transport stdio --log-level ERROR",
                ],
            ],
            verify_commands=[
                [str(UV_BIN), "tool", "run", "--from", str(JCODEMUNCH_WHEEL), "jcodemunch-mcp", "--help"],
                ["claude", "mcp", "get", "jcodemunch"],
            ],
            required_files=[
                "{codex_home}/claude-config/.claude.json",
                "{codex_home}/claude-config/settings.json",
                "{repo}/CLAUDE.md",
                "{repo}/AGENTS.md",
                "{codex_home}/home/.code-index/config.jsonc",
            ],
            diff_exclude_paths=[".code-index", ".jcodemunch", ".mcp.json", "CLAUDE.md", "AGENTS.md", ".claude"],
            claude_features={"hooks": True, "mcp": True, "guidance_append": "Code Exploration Policy"},
        ),
    }
)


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


def require_repowise_provider_contract(profile_id: str) -> None:
    """Fail closed if a RepoWise profile could silently fall back to retrieval-only."""
    expected = {
        "repowise-codex-product-v2": "codex_cli",
        "repowise-opencode-product-v2": "opencode",
    }.get(str(PROFILE_TOOL_CONFIG_OVERRIDES.get(profile_id, "")))
    if expected is None:
        return
    cfg = TOOL_CONFIGS[str(PROFILE_TOOL_CONFIG_OVERRIDES[profile_id])]
    if (cfg.get("env") or {}).get("REPOWISE_PROVIDER") != expected:
        raise ValueError(f"{profile_id} must set REPOWISE_PROVIDER={expected}")
    commands = (cfg.get("host_integration") or {}).get("install_commands") or []
    init = commands[-1] if commands else []
    if "--provider" not in init or expected not in init:
        raise ValueError(f"{profile_id} init must explicitly select provider {expected}")


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


def render_tool_value(value: Any, record: dict[str, Any], codex_home: Path, cfg: dict[str, Any]) -> str:
    repo_path = rel_or_abs(record["target"]["repository_path"]) if record.get("target") else ROOT
    tool_port = 18000 + int(hashlib.sha256(str(repo_path.resolve()).encode()).hexdigest()[:8], 16) % 20000
    return str(value).format(
        repo=repo_path,
        codex_home=codex_home,
        tool_data_dir=tool_data_dir(codex_home, cfg),
        repo_slug=repo_path.name.replace("-", "_"),
        tool_port=tool_port,
        repository_root=ROOT,
    )


def render_mcp_args(record: dict[str, Any], codex_home: Path, cfg: dict[str, Any]) -> list[str]:
    return [render_tool_value(arg, record, codex_home, cfg) for arg in cfg.get("mcp_args", [])]


def prepare_claude_mcp_config(
    record: dict[str, Any],
    pid: str,
    claude_home: Path,
) -> Path | None:
    """Materialize one lane-private Claude MCP file from the pinned tool config."""
    cfg = active_tool_config(record, pid)
    server = str((cfg or {}).get("mcp_server") or "")
    if not cfg or not server:
        return None
    command = render_tool_value(str(cfg.get("mcp_command", "")), record, claude_home, cfg)
    if not command:
        raise ValueError(f"Claude MCP profile {pid} has no server command")
    config_path = claude_home / "claude-config" / "mcp.json"
    config_path.write_text(json.dumps({
        "mcpServers": {
            server: {
                "type": "stdio",
                "command": command,
                "args": render_mcp_args(record, claude_home, cfg),
                "env": render_tool_env(
                    claude_home,
                    cfg,
                    rel_or_abs(record["target"]["repository_path"])
                    if record.get("target")
                    else ROOT,
                ),
            }
        }
    }, indent=2) + "\n")
    return config_path


def write_codex_config(codex_home: Path, record: dict[str, Any], pid: str) -> None:
    cfg = active_tool_config(record, pid)
    declared_features = dict((cfg or {}).get("codex_features", {}))
    declared_features.setdefault("hooks", False)
    lines = [
        'sandbox_mode = "danger-full-access"',
        'approval_policy = "never"',
        "",
        "[features]",
        *[
            f"{key} = {'true' if value else 'false'}"
            for key, value in sorted(declared_features.items())
            if isinstance(value, bool)
        ],
        "",
    ]
    if cfg:
        executable = cfg.get("executable") or cfg.get("mcp_command")
        rendered_executable = render_tool_value(executable, record, codex_home, cfg) if executable else ""
        if rendered_executable:
            command = Path(rendered_executable)
            generated_by_install = bool(cfg.get("host_integration")) and "{" in str(executable)
            if command.is_absolute() and not command.exists() and not generated_by_install:
                raise FileNotFoundError(f"{cfg['display_name']} command not found: {command}")
        server = cfg.get("mcp_server")
        if server and not cfg.get("mcp_config_via_host_integration"):
            lines.extend(
                [
                    f"[mcp_servers.{server}]",
                    f"command = {json.dumps(rendered_executable)}",
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

    cfg = active_tool_config(record, pid)
    auth_provider = str((cfg or {}).get("auth_provider", "codex"))
    auths: list[Path] = []
    auth_link_name: str | None = None
    if auth_provider == "openrouter":
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise FileNotFoundError(
                "OPENROUTER_API_KEY is required for the isolated OpenCode/OpenRouter evaluation setup"
            )
        auth_materialization = "inherited-environment-api-key"
    else:
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
        auth_link_name = auths[0].name

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
        "auth_provider": auth_provider,
        "source_auth_home": str(source_home) if auth_provider != "openrouter" else None,
        "auth_link_name": auth_link_name,
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


def _claude_account_credential(source_home: Path) -> Path | None:
    """Resolve the Claude OAuth file without copying unrelated account state."""
    candidates = [
        source_home / ".credentials.json",
        source_home / ".claude" / ".credentials.json",
    ]
    return next((path for path in candidates if path.is_file()), None)


def prepare_claude_home(
    pid: str,
    run_dir: Path,
    home_root: Path,
    *,
    provider: str = "openrouter",
) -> Path:
    """Create isolated Claude state and copy only an explicitly supplied OAuth file."""
    claude_home = home_root / pid
    if claude_home.exists():
        make_tree_writable(claude_home)
        shutil.rmtree(claude_home, onexc=make_writable_for_removal)
    claude_home.mkdir(parents=True)
    for subdir in ["home", "python-userbase", "xdg-cache", "xdg-config", "xdg-data", "tmp", "claude-config"]:
        (claude_home / subdir).mkdir(parents=True, exist_ok=True)
    auth_materialization = "none"
    auth_source_home: str | None = None
    auth_file: str | None = None
    if provider == "anthropic":
        source_value = os.environ.get(CLAUDE_ACCOUNT_HOME_ENV)
        credential = _claude_account_credential(Path(source_value).expanduser()) if source_value else None
        if credential is not None:
            destination = claude_home / "claude-config" / ".credentials.json"
            shutil.copy2(credential, destination)
            os.chmod(destination, 0o600)
            auth_materialization = "copy-ephemeral-oauth-file"
            auth_source_home = str(Path(source_value).expanduser())
            auth_file = credential.name
        elif not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
            raise FileNotFoundError(
                f"{CLAUDE_ACCOUNT_HOME_ENV} must point to a Claude account home containing .credentials.json "
                "for the direct Anthropic condition (or provide ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN)."
            )
        else:
            auth_materialization = "inherited-anthropic-environment-credential"
    manifest = {
        "created_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "profile_id": pid,
        "runtime_id": "claude-code",
        "provider": provider,
        "claude_home": str(claude_home),
        "normal_mode": True,
        "copied_global_instructions": False,
        "copied_skills_or_plugins": False,
        "hooks_enabled": False,
        "mcp_servers": [],
        "auth_materialization": auth_materialization,
        "auth_source_home": auth_source_home,
        "auth_file": auth_file,
    }
    (run_dir / "claude-code-home-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return claude_home


def prepare_claude_project_instructions(
    repo: Path,
    run_dir: Path,
    instruction_source: Path | None = None,
) -> dict[str, Any]:
    """Expose the existing project guidance through Claude Code discovery."""
    project_source = repo / "AGENTS.md"
    source = instruction_source or (project_source if project_source.is_file() else ROOT / "AGENTS.md")
    destination = repo / "CLAUDE.md"
    if not source.is_file():
        raise RuntimeError(f"Claude normal-mode setup requires project instructions: {source}")
    source_bytes = source.read_bytes()
    if destination.exists() and destination.read_bytes() != source_bytes:
        raise RuntimeError(f"existing project CLAUDE.md does not match instruction source: {destination}")
    destination.write_bytes(source_bytes)

    exclude_path = repo / ".git" / "info" / "exclude"
    exclude_path.parent.mkdir(parents=True, exist_ok=True)
    existing_exclude = exclude_path.read_text(errors="replace") if exclude_path.exists() else ""
    marker = "# workflow-eval Claude project instructions"
    if marker not in existing_exclude:
        suffix = "" if not existing_exclude or existing_exclude.endswith("\n") else "\n"
        exclude_path.write_text(
            existing_exclude + suffix + f"{marker}\n/CLAUDE.md\n"
        )

    source_hash = hashlib.sha256(source_bytes).hexdigest()
    destination_hash = hashlib.sha256(destination.read_bytes()).hexdigest()
    source_scope = "project-repo" if source == project_source else "evaluation-root"
    source_path = str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else source.name
    manifest = {
        "runtime_id": "claude-code",
        "materialization": "exact-copy-of-existing-AGENTS.md-guidance",
        "source_scope": source_scope,
        "source_path": source_path,
        "destination_path": "CLAUDE.md",
        "source_sha256": source_hash,
        "destination_sha256": destination_hash,
        "byte_identical": source_hash == destination_hash,
        "claude_auto_discovery_expected": True,
        "evaluator_authored_guidance": False,
        "git_status_policy": "lane-local-git-info-exclude",
    }
    (run_dir / "claude-code-instruction-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    return manifest


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
            rendered_entry = str(entry).format(
                codex_home=codex_home,
                home=codex_home / "home",
                tool_data_dir=tool_data_dir(codex_home, cfg),
            )
            if rendered_entry not in path_entries:
                path_entries.insert(1, rendered_entry)
    if containerized:
        path_entries.extend(["/usr/local/sbin", "/usr/local/bin", "/usr/sbin", "/usr/bin", "/sbin", "/bin"])
    else:
        path_entries.append(env.get("PATH", ""))
    env["PATH"] = ":".join(path_entries)
    return env


def claude_env(
    agent_home: Path,
    *,
    containerized: bool = False,
    cfg: dict[str, Any] | None = None,
    provider: str = "openrouter",
) -> dict[str, str]:
    """Create isolated Claude Code HOME/XDG/config state for one lane."""
    env = codex_env(agent_home, containerized=containerized, cfg=cfg)
    if provider == "openrouter" and CLAUDE_OPENROUTER_ENV_FILE.is_file():
        for line in CLAUDE_OPENROUTER_ENV_FILE.read_text(errors="replace").splitlines():
            match = re.match(r"^\s*export\s+([A-Za-z_][A-Za-z0-9_]*)=(.*)\s*$", line)
            if not match:
                continue
            key, raw = match.groups()
            value = raw.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            value = re.sub(r"\$([A-Za-z_][A-Za-z0-9_]*)", lambda m: env.get(m.group(1), ""), value)
            env[key] = value
    elif provider == "anthropic":
        # Do not let an inherited OpenRouter key or endpoint silently change the
        # direct-account transport. API credentials may still be supplied by the
        # owner through ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN; the CLI uses its
        # first-party endpoint by default.
        env.pop("OPENROUTER_API_KEY", None)
        env.pop("ANTHROPIC_BASE_URL", None)
    config_dir = agent_home / "claude-config"
    config_dir.mkdir(parents=True, exist_ok=True)
    claude_config = agent_home / "claude-config"
    claude_config.mkdir(parents=True, exist_ok=True)
    claude_dir = agent_home / "home" / ".claude"
    claude_dir.parent.mkdir(parents=True, exist_ok=True)
    if claude_dir.exists() or claude_dir.is_symlink():
        if not claude_dir.is_symlink() or claude_dir.resolve() != claude_config.resolve():
            raise RuntimeError(f"unexpected lane-private Claude config path: {claude_dir}")
    else:
        claude_dir.symlink_to(claude_config, target_is_directory=True)
    env["CLAUDE_CONFIG_DIR"] = str(claude_config)
    env.pop("CLAUDE_CODE_SIMPLE", None)
    env.setdefault("CLAUDE_CODE_MAX_OUTPUT_TOKENS", "8000")
    env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"
    isolated_bin = agent_home / "runtime-bin"
    isolated_bin.mkdir(parents=True, exist_ok=True)
    if not containerized:
        link = isolated_bin / "claude"
        if not link.exists():
            link.symlink_to(CLAUDE_HOST_EXECUTABLE)
        env["PATH"] = f"{isolated_bin}:{env['PATH']}"
    else:
        env["PATH"] = f"{CLAUDE_CONTAINER_BIN.parent}:{env['PATH']}"
    return env


def apply_model_network_isolation(env: dict[str, str], *, prepend_denied_shell_to_path: bool = True) -> None:
    """Route model shell commands through the image's seccomp wrapper.

    Claude Code uses PATH for part of its own runtime initialization and provider
    path. Keep its explicit SHELL bound to the denied wrapper, but allow callers
    to avoid shadowing every `bash` lookup for the parent process.
    """
    env["SHELL"] = MODEL_NETWORK_DENIED_SHELL
    if not prepend_denied_shell_to_path:
        return
    path_entries = env.get("PATH", "").split(":")
    if MODEL_NETWORK_DENIED_BIN not in path_entries:
        env["PATH"] = ":".join([MODEL_NETWORK_DENIED_BIN, *path_entries])


def codex_hook_args(cfg: dict[str, Any] | None) -> list[str]:
    if bool((cfg or {}).get("codex_features", {}).get("hooks", False)):
        if bool((cfg or {}).get("codex_hook_bypass_trust", False)):
            return ["--dangerously-bypass-hook-trust"]
        return []
    return ["--disable", "hooks"]


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
    "CLAUDE_CONFIG_DIR",
    "CLAUDE_CODE_SIMPLE",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS",
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "OPENROUTER_API_KEY",
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
    if CLAUDE_HOST_EXECUTABLE.is_file():
        mounts.append((CLAUDE_HOST_EXECUTABLE, CLAUDE_CONTAINER_BIN, "ro"))
    path_texts = [
        "/opt/data/dotnet",
        "/opt/data/opt/go",
        "/opt/data/opt/uv",
        str(NODE_TOOLCHAIN_ROOT),
    ]
    if cfg:
        path_texts.extend(
            str(path).format(repository_root=ROOT)
            for path in cfg.get("mounts", [])
        )
    # Docker refuses a run outright when the same target is bound twice, so a profile that
    # names a helper in its own mounts and picks it up again as a batch local helper takes the
    # whole lane down with exit 125 before anything installs. Dedupe by target, keeping order.
    seen_targets = {target for _, target, _ in mounts}
    for path_text in path_texts:
        path = Path(path_text)
        if path.exists() and path not in seen_targets:
            seen_targets.add(path)
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
    for binary in [CODEX_HOST_EXECUTABLE, *codex_root.glob("@openai/codex-*/vendor/*/bin/codex")]:
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
    if cmd and cmd[0] == "claude":
        # The controller-side Claude binary is bind-mounted read-only. Docker
        # may mark that bind noexec, so copy it into the container filesystem
        # before invoking it; the bytes and pinned identity remain unchanged.
        args = shlex.join(cmd[1:])
        cmd = [
            "bash",
            "-lc",
            f"cp {shlex.quote(str(CLAUDE_CONTAINER_BIN))} /tmp/claude-workflow-bin && chmod 755 /tmp/claude-workflow-bin && exec /tmp/claude-workflow-bin {args}",
        ]
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
    agent_runtime: str = "codex-cli",
    provider: str = "openrouter",
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
        smoke_env = (claude_env(codex_home, containerized=True, provider=provider) if agent_runtime == "claude-code" else codex_env(codex_home, containerized=True, cfg=cfg)) if codex_home else os.environ.copy()
        smoke_mounts = docker_tool_mounts(cfg)
        if codex_home:
            add_mount(smoke_mounts, codex_home, mode="rw")
        smoke_output = run_dir / "docker-smoke-output.txt"
        smoke_program = "claude" if agent_runtime == "claude-code" else "codex"
        smoke_script = (
            f"set -euo pipefail; id; python3 --version; git --version; cp {shlex.quote(str(CLAUDE_CONTAINER_BIN))} /tmp/claude-workflow-bin; chmod 755 /tmp/claude-workflow-bin; command -v /tmp/claude-workflow-bin; /tmp/claude-workflow-bin --version"
            if agent_runtime == "claude-code"
            else f"set -euo pipefail; id; python3 --version; git --version; command -v {smoke_program}; {smoke_program} --version"
        )
        smoke_cmd = docker_command(
            [
                "bash",
                "-lc",
                smoke_script,
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


def prepare_home_dot_codex_alias(codex_home: Path) -> Path:
    """Expose lane-private CODEX_HOME to installers hard-coded to ~/.codex."""
    home = codex_home / "home"
    home.mkdir(parents=True, exist_ok=True)
    alias = home / ".codex"
    if alias.is_symlink():
        if alias.resolve() != codex_home.resolve():
            raise RuntimeError(f"unexpected ~/.codex alias target: {alias} -> {alias.resolve()}")
        return alias
    if alias.exists():
        raise RuntimeError(f"refusing to replace existing ~/.codex path: {alias}")
    alias.symlink_to(codex_home, target_is_directory=True)
    return alias


def verify_artifact_identities(
    cfg: dict[str, Any], record: dict[str, Any], codex_home: Path
) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for identity in cfg.get("artifact_identities", []):
        path = Path(render_tool_value(str(identity["path"]), record, codex_home, cfg))
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        expected = str(identity["sha256"])
        receipts.append(
            {
                "path": str(path),
                "kind": identity.get("kind"),
                "expected_sha256": expected,
                "actual_sha256": actual,
                "passed": actual == expected,
            }
        )
    return receipts


def retain_post_install_artifacts(
    cfg: dict[str, Any], record: dict[str, Any], codex_home: Path, run_dir: Path
) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for item in cfg.get("post_install_artifacts", []):
        source = Path(render_tool_value(str(item["path"]), record, codex_home, cfg))
        actual = hashlib.sha256(source.read_bytes()).hexdigest() if source.is_file() else None
        expected = str(item["sha256"])
        retained = run_dir / str(item["retain_as"])
        if actual == expected:
            shutil.copy2(source, retained)
        receipts.append(
            {
                "source": str(source),
                "expected_sha256": expected,
                "actual_sha256": actual,
                "retained_path": str(retained.relative_to(ROOT)) if retained.exists() and retained.is_relative_to(ROOT) else str(retained),
                "passed": actual == expected and retained.is_file(),
            }
        )
    return receipts


def prepare_profile_integration(
    record: dict[str, Any],
    pid: str,
    codex_home: Path,
    run_dir: Path,
    *,
    backend: str,
    docker_image: str,
) -> dict[str, Any]:
    cfg = active_tool_config(record, pid)
    runtime_id = str((record.get("agent") or {}).get("runtime_id") or "codex-cli")
    claude_mcp_config = (
        prepare_claude_mcp_config(record, pid, codex_home)
        if runtime_id == "claude-code"
        else None
    )
    integration = (cfg or {}).get("host_integration") or {}
    artifact_identities = verify_artifact_identities(cfg, record, codex_home) if cfg else []
    identities_passed = all(item["passed"] for item in artifact_identities)
    native_claude_treatment = runtime_id == "claude-code" and not pid.startswith("baseline-")
    if not integration:
        result = {
            "profile_id": pid,
            "passed": identities_passed and not native_claude_treatment,
            "skipped": True,
            "install_exit_codes": [],
            "verify_exit_codes": [],
            "missing_required_files": [],
            "artifact_identities": artifact_identities,
            "post_install_artifacts": [],
            "artifacts": [],
            "claude_mcp_config": str(claude_mcp_config) if claude_mcp_config else None,
            "failure_reasons": (
                ["Claude native treatment has no host_integration contract"]
                if native_claude_treatment else []
            ),
        }
        (run_dir / "tool-host-integration.json").write_text(json.dumps(result, indent=2) + "\n")
        return result

    assert cfg is not None
    integration_backend = str(cfg.get("host_integration_backend") or backend)
    # Native Claude installers run in the lane's declared backend. The
    # jCodeMunch adapter uses the mounted Claude entrypoint and lane-private
    # config, so forcing it onto the controller host would bypass the lane.
    if integration.get("home_dot_codex_alias"):
        prepare_home_dot_codex_alias(codex_home)
    env = (
        claude_env(
            codex_home,
            containerized=integration_backend == "docker",
            cfg=cfg,
            provider=str((record.get("agent") or {}).get("provider") or "openrouter"),
        )
        if runtime_id == "claude-code"
        else codex_env(codex_home, containerized=backend == "docker", cfg=cfg)
    )
    env.update(tool_env_for_record(record, pid, codex_home))
    mounts = container_mounts_for_record(record, codex_home, include_repo=True, cfg=cfg)
    artifacts: list[str] = []
    install_exit_codes: list[int] = []
    controller_install_exit_codes: list[int] = []
    verify_exit_codes: list[int] = []
    diagnostic_exit_codes: list[int] = []
    host_integration_retry_exit_codes: list[int] = []

    for index, raw_command in enumerate(integration.get("controller_install_commands", []), start=1):
        command = [render_tool_value(part, record, codex_home, cfg) for part in raw_command]
        artifact = run_dir / f"tool-host-controller-install-{index}.txt"
        proc = run_backend(
            command,
            backend="host",
            docker_image=docker_image,
            cwd=rel_or_abs(record["target"]["repository_path"]) if record.get("target") else codex_home / "home",
            env=env,
            stdout_path=artifact,
            timeout=int(integration.get("timeout_seconds", 300)),
        )
        controller_install_exit_codes.append(proc.returncode)
        install_exit_codes.append(proc.returncode)
        artifacts.append(str(artifact.relative_to(ROOT)) if artifact.is_relative_to(ROOT) else str(artifact))
        if proc.returncode != 0:
            break

    backend_phases = () if any(code != 0 for code in controller_install_exit_codes) else (
        ("install", integration.get("install_commands", []), install_exit_codes),
        ("verify", integration.get("verify_commands", []), verify_exit_codes),
        # Diagnostics run and are retained, but never gate. A vendor doctor reports on every
        # agent and every optional extra it knows about, so its exit code answers "is this
        # machine perfect" rather than "did this profile install" -- lean-ctx's, for one,
        # fails a Codex lane over an unset CLAUDE_ENV_FILE.
        ("diagnostic", integration.get("diagnostic_commands", []), diagnostic_exit_codes),
    )
    for phase, commands, exits in backend_phases:
        for index, raw_command in enumerate(commands, start=1):
            command = [render_tool_value(part, record, codex_home, cfg) for part in raw_command]
            artifact = run_dir / f"tool-host-{phase}-{index}.txt"
            proc = run_backend(
                command,
                backend=integration_backend,
                docker_image=docker_image,
                cwd=rel_or_abs(record["target"]["repository_path"]) if record.get("target") else codex_home / "home",
                env=env,
                stdout_path=artifact,
                timeout=int(integration.get("timeout_seconds", 300)),
                mounts=mounts,
            )
            exits.append(proc.returncode)
            artifacts.append(str(artifact.relative_to(ROOT)) if artifact.is_relative_to(ROOT) else str(artifact))
            if proc.returncode == 126 and integration_backend == "host":
                retry_artifact = run_dir / f"tool-host-{phase}-{index}-retry.txt"
                retry_proc = run_backend(
                    command,
                    backend=integration_backend,
                    docker_image=docker_image,
                    cwd=rel_or_abs(record["target"]["repository_path"]) if record.get("target") else codex_home / "home",
                    env=env,
                    stdout_path=retry_artifact,
                    timeout=int(integration.get("timeout_seconds", 300)),
                    mounts=mounts,
                )
                host_integration_retry_exit_codes.append(retry_proc.returncode)
                exits[-1] = retry_proc.returncode
                artifacts.append(
                    str(retry_artifact.relative_to(ROOT))
                    if retry_artifact.is_relative_to(ROOT)
                    else str(retry_artifact)
                )
            if exits[-1] != 0:
                break
        if exits and exits[-1] != 0:
            break

    required_files = [Path(render_tool_value(value, record, codex_home, cfg)) for value in integration.get("required_files", [])]
    missing_required_files = [str(path) for path in required_files if not path.is_file()]
    post_install_artifacts = retain_post_install_artifacts(cfg, record, codex_home, run_dir)
    passed = (
        identities_passed
        and all(item["passed"] for item in post_install_artifacts)
        and all(code == 0 for code in [*install_exit_codes, *verify_exit_codes])
        and not missing_required_files
    )
    result = {
        "profile_id": pid,
        "passed": passed,
        "skipped": False,
        "controller_install_exit_codes": controller_install_exit_codes,
        "install_exit_codes": install_exit_codes,
        "verify_exit_codes": verify_exit_codes,
        "diagnostic_exit_codes": diagnostic_exit_codes,
        "host_integration_retry_exit_codes": host_integration_retry_exit_codes,
        "missing_required_files": missing_required_files,
        "required_files": [str(path) for path in required_files],
        "artifact_identities": artifact_identities,
        "post_install_artifacts": post_install_artifacts,
        "artifacts": artifacts,
        "claude_mcp_config": str(claude_mcp_config) if claude_mcp_config else None,
    }
    (run_dir / "tool-host-integration.json").write_text(json.dumps(result, indent=2) + "\n")

    for manifest_name in ("codex-home-manifest.json", "claude-code-home-manifest.json"):
        manifest_path = run_dir / manifest_name
        if manifest_path.is_file():
            manifest = json.loads(manifest_path.read_text())
            claude_features = cfg.get("claude_features", {})
            native_plugin = claude_features.get("plugin")
            native_skills = claude_features.get("skills", [])
            manifest["copied_skills_or_plugins"] = bool(
                passed and (native_plugin or native_skills)
            )
            manifest["native_plugins"] = [native_plugin] if passed and native_plugin else []
            manifest["native_skills"] = list(native_skills) if passed else []
            manifest["hooks_enabled"] = bool(
                cfg.get("codex_features", {}).get("hooks", False)
                or claude_features.get("hooks", False)
            ) and passed
            manifest["host_integration_prepared"] = passed
            manifest["host_integration_receipt"] = str((run_dir / "tool-host-integration.json").relative_to(ROOT))
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return result


def probe_mcp_handshake(
    record: dict[str, Any],
    pid: str,
    codex_home: Path,
    run_dir: Path,
    *,
    backend: str,
    docker_image: str,
) -> dict[str, Any]:
    cfg = active_tool_config(record, pid)
    handshake = (cfg or {}).get("mcp_handshake") or {}
    receipt_path = run_dir / "mcp-handshake.json"
    if cfg and cfg.get("mcp_server") and not handshake:
        result = {
            "profile_id": pid,
            "passed": False,
            "required": True,
            "attempted": False,
            "skipped": False,
            "errors": ["MCP profile is missing a required handshake contract"],
        }
        receipt_path.write_text(json.dumps(result, indent=2) + "\n")
        return result
    required = bool(handshake.get("required"))
    attempt_required = bool(handshake.get("attempt_required", required))
    if not attempt_required:
        result = {"profile_id": pid, "passed": True, "required": required, "attempted": False, "skipped": True}
        receipt_path.write_text(json.dumps(result, indent=2) + "\n")
        return result

    assert cfg is not None
    runtime_id = str((record.get("agent") or {}).get("runtime_id") or "codex-cli")
    env = (
        claude_env(
            codex_home,
            containerized=backend == "docker",
            cfg=cfg,
            provider=str((record.get("agent") or {}).get("provider") or "openrouter"),
        )
        if runtime_id == "claude-code"
        else codex_env(codex_home, containerized=backend == "docker", cfg=cfg)
    )
    env.update(tool_env_for_record(record, pid, codex_home))
    mounts = container_mounts_for_record(record, codex_home, include_repo=True, cfg=cfg)
    probe_script = ROOT / "scripts" / "probe_mcp_stdio.py"
    add_mount(mounts, probe_script, mode="ro")
    command = [
        "python3",
        str(probe_script),
        "--command",
        render_tool_value(cfg["mcp_command"], record, codex_home, cfg),
        "--cwd",
        str(rel_or_abs(record["target"]["repository_path"])),
        "--timeout",
        str(handshake.get("timeout_seconds", 30)),
    ]
    for arg in render_mcp_args(record, codex_home, cfg):
        command.append(f"--arg={arg}")
    proc = run_backend(
        command,
        backend=backend,
        docker_image=docker_image,
        cwd=rel_or_abs(record["target"]["repository_path"]),
        env=env,
        stdout_path=receipt_path,
        timeout=int(handshake.get("timeout_seconds", 30)) + 10,
        mounts=mounts,
    )
    try:
        result = json.loads(receipt_path.read_text())
    except (OSError, json.JSONDecodeError):
        result = {"passed": False, "errors": ["MCP handshake probe did not emit a valid JSON receipt"]}
    activation_passed = bool(result.get("passed")) and proc.returncode == 0
    result["profile_id"] = pid
    result["required"] = required
    result["attempted"] = True
    result["attempt_required"] = attempt_required
    result["probe_exit_code"] = proc.returncode
    result["activation_passed"] = activation_passed
    result["treatment_degradation"] = not activation_passed and bool(handshake.get("failure_counts_as_degradation"))
    result["known_failure"] = handshake.get("known_failure") if not activation_passed else None
    result["passed"] = activation_passed if required else True
    secondary_results: list[dict[str, Any]] = []
    for secondary in cfg.get("secondary_mcp_handshakes", []):
        server = str(secondary["server"])
        secondary_path = run_dir / f"mcp-handshake-{server}.json"
        secondary_command = [
            "python3",
            str(probe_script),
            "--command",
            render_tool_value(str(secondary["command"]), record, codex_home, cfg),
            "--cwd",
            str(rel_or_abs(record["target"]["repository_path"])),
            "--timeout",
            str(secondary.get("timeout_seconds", 30)),
        ]
        for arg in secondary.get("args", []):
            secondary_command.append(
                f"--arg={render_tool_value(str(arg), record, codex_home, cfg)}"
            )
        secondary_proc = run_backend(
            secondary_command,
            backend=backend,
            docker_image=docker_image,
            cwd=rel_or_abs(record["target"]["repository_path"]),
            env=env,
            stdout_path=secondary_path,
            timeout=int(secondary.get("timeout_seconds", 30)) + 10,
            mounts=mounts,
        )
        try:
            secondary_result = json.loads(secondary_path.read_text())
        except (OSError, json.JSONDecodeError):
            secondary_result = {"passed": False, "errors": ["secondary MCP handshake did not emit valid JSON"]}
        secondary_result.update(
            {
                "server": server,
                "required": True,
                "probe_exit_code": secondary_proc.returncode,
                "passed": bool(secondary_result.get("passed")) and secondary_proc.returncode == 0,
            }
        )
        secondary_path.write_text(json.dumps(secondary_result, indent=2, sort_keys=True) + "\n")
        secondary_results.append(secondary_result)
    result["secondary_handshakes"] = secondary_results
    result["passed"] = bool(result["passed"]) and all(
        item["passed"] for item in secondary_results
    )
    receipt_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def preflight_claude_code(
    record: dict[str, Any],
    claude_home: Path,
    pid: str,
    run_dir: Path,
    *,
    backend: str,
    docker_image: str,
    cfg: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prove the normal Claude Code control surface without making a provider request."""
    provider = str((record.get("agent") or {}).get("provider") or "openrouter")
    env = claude_env(claude_home, containerized=backend == "docker", cfg=cfg, provider=provider)
    apply_model_network_isolation(env)
    mounts = container_mounts_for_record(record, claude_home, include_repo=True, cfg=cfg)
    repo = Path(rel_or_abs(record["target"]["repository_path"]))
    instruction_destination = repo / "CLAUDE.md"
    instruction_manifest_path = run_dir / "claude-code-instruction-manifest.json"
    instruction_manifest: dict[str, Any] = {}
    if instruction_manifest_path.is_file():
        instruction_manifest = json.loads(instruction_manifest_path.read_text())
    source_scope = instruction_manifest.get("source_scope")
    source_path = instruction_manifest.get("source_path")
    if source_scope == "project-repo" and isinstance(source_path, str):
        instruction_source = repo / source_path
    elif source_scope == "evaluation-root" and isinstance(source_path, str):
        instruction_source = ROOT / source_path
    else:
        instruction_source = Path()
    source_bytes = instruction_source.read_bytes() if instruction_source.is_file() else b""
    destination_bytes = instruction_destination.read_bytes() if instruction_destination.is_file() else b""
    source_hash = hashlib.sha256(source_bytes).hexdigest() if source_bytes else ""
    destination_hash = hashlib.sha256(destination_bytes).hexdigest() if destination_bytes else ""
    instruction_passed = (
        instruction_source.is_file()
        and instruction_destination.is_file()
        and source_hash == destination_hash
        and instruction_manifest.get("source_sha256") == source_hash
        and instruction_manifest.get("destination_sha256") == destination_hash
        and instruction_manifest.get("byte_identical") is True
        and instruction_manifest.get("claude_auto_discovery_expected") is True
    )
    native_guidance_append = str((cfg or {}).get("claude_features", {}).get("guidance_append") or "")
    if not instruction_passed and native_guidance_append:
        instruction_passed = (
            instruction_source.is_file()
            and instruction_destination.is_file()
            and destination_bytes.startswith(source_bytes.rstrip())
            and f"## {native_guidance_append}".encode() in destination_bytes
            and instruction_manifest.get("byte_identical") is True
            and instruction_manifest.get("claude_auto_discovery_expected") is True
        )
    version_path = run_dir / "claude-code-version.txt"
    help_path = run_dir / "claude-code-help.txt"
    version = run_backend(
        ["claude", "--version"], backend=backend, docker_image=docker_image,
        cwd=rel_or_abs(record["target"]["repository_path"]), env=env,
        stdout_path=version_path, timeout=120, mounts=mounts,
    )
    help_result = run_backend(
        ["claude", "--help"], backend=backend, docker_image=docker_image,
        cwd=rel_or_abs(record["target"]["repository_path"]), env=env,
        stdout_path=help_path, timeout=120, mounts=mounts,
    )
    version_text = version_path.read_text(errors="replace") if version_path.exists() else ""
    help_text = help_path.read_text(errors="replace") if help_path.exists() else ""
    required = ["--output-format", "stream-json", "--model", "--effort", "--tools", "--resume"]
    claude_features = (cfg or {}).get("claude_features", {})
    hooks_enabled = bool(claude_features.get("hooks", False))
    plugin_name = str(claude_features.get("plugin") or "")
    plugin_probe_path = run_dir / "claude-code-plugin-list.json"
    plugin_probe_exit_code: int | None = None
    plugin_probe_passed = True
    plugin_probe_text = ""
    if plugin_name:
        plugin_probe = run_backend(
            ["claude", "plugin", "list", "--json"],
            backend=backend,
            docker_image=docker_image,
            cwd=rel_or_abs(record["target"]["repository_path"]),
            env=env,
            stdout_path=plugin_probe_path,
            timeout=120,
            mounts=mounts,
        )
        plugin_probe_exit_code = plugin_probe.returncode
        plugin_probe_text = plugin_probe_path.read_text(errors="replace") if plugin_probe_path.exists() else ""
        plugin_probe_passed = plugin_probe.returncode == 0 and plugin_name in plugin_probe_text
    auth_status: dict[str, Any] = {"checked": False, "passed": True}
    if provider == "anthropic":
        auth_raw = claude_home / "tmp" / "claude-auth-status.json"
        auth_probe = run_backend(
            ["claude", "auth", "status", "--json"],
            backend=backend,
            docker_image=docker_image,
            cwd=rel_or_abs(record["target"]["repository_path"]),
            env=env,
            stdout_path=auth_raw,
            timeout=120,
            mounts=mounts,
        )
        try:
            raw_status = json.loads(auth_raw.read_text()) if auth_raw.is_file() else {}
        except json.JSONDecodeError:
            raw_status = {}
        finally:
            auth_raw.unlink(missing_ok=True)
        auth_status = {
            "checked": True,
            "passed": (
                auth_probe.returncode == 0
                and raw_status.get("loggedIn") is True
                and str(raw_status.get("apiProvider") or "").lower()
                not in {"openrouter", "openrouter-compatible"}
            ),
            "exit_code": auth_probe.returncode,
            "logged_in": raw_status.get("loggedIn") is True,
            "auth_method": raw_status.get("authMethod"),
            "api_provider": raw_status.get("apiProvider"),
            "subscription_type": raw_status.get("subscriptionType"),
        }
    passed = (
        instruction_passed
        and version.returncode == 0
        and help_result.returncode == 0
        and all(item in help_text for item in required)
        and plugin_probe_passed
        and bool(auth_status.get("passed"))
    )
    result = {
        "runtime_id": "claude-code",
        "profile_id": pid,
        "passed": passed,
        "provider_request_made": False,
        "version": version_text.strip(),
        "version_exit_code": version.returncode,
        "help_exit_code": help_result.returncode,
        "required_cli_surfaces": required,
        "missing_cli_surfaces": [item for item in required if item not in help_text],
        "provider": provider,
        "authentication": auth_status,
        "normal_mode": True,
        "hooks_enabled": hooks_enabled,
        "native_plugin": {
            "name": plugin_name or None,
            "probe_path": str(plugin_probe_path.relative_to(ROOT)) if plugin_name else None,
            "probe_exit_code": plugin_probe_exit_code,
            "passed": plugin_probe_passed,
        },
        "project_instruction_files": {
            "passed": instruction_passed,
            "source": "AGENTS.md",
            "discovered_as": "CLAUDE.md",
            "byte_identical": source_bytes == destination_bytes,
            "manifest": instruction_manifest,
        },
        "mcp_servers": [],
        "model": record.get("agent", {}).get("model"),
    }
    (run_dir / "claude-code-preflight.json").write_text(json.dumps(result, indent=2) + "\n")
    (run_dir / "claude-code-effective-settings.json").write_text(json.dumps({
        "bare": False,
        "normal_mode": True,
        "provider": provider,
        "model": record.get("agent", {}).get("model"),
        "effort": record.get("agent", {}).get("reasoning_effort"),
        "hooks_enabled": hooks_enabled,
        "permission_mode": "bypassPermissions",
        "tools": ["Bash", "Edit", "Read", "Grep", "Glob"],
        "mcp_config": [
            str(claude_home / "claude-config" / "mcp.json")
        ] if (claude_home / "claude-config" / "mcp.json").is_file() else [],
        "plugins": [plugin_name] if plugin_name and plugin_probe_passed else [],
        "skills": list(claude_features.get("skills", [])) if plugin_probe_passed else [],
    }, indent=2) + "\n")
    return result


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
    preflight_cwd = codex_home / "home"
    if cfg and cfg.get("preflight_requires_project"):
        preflight_cwd = rel_or_abs(record["target"]["repository_path"])
        add_mount(mounts, preflight_cwd, mode="rw")
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
        tool_preflight = run_backend(
            [render_tool_value(x, record, codex_home, cfg) for x in cfg["preflight_command"]],
            backend=backend,
            docker_image=docker_image,
            cwd=preflight_cwd,
            env=env,
            stdout_path=tool_preflight_path,
            timeout=120,
            mounts=mounts,
        )
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
    session_activation = str(cfg.get("session_activation", "")).strip()
    activation_block = (
        f"\n# Product-required session activation\n\n{session_activation}\n\n---\n\n"
        if session_activation
        else ""
    )
    return (
        "# Evaluation isolation contract\n\n"
        "This is a treatment lane. Its profile was installed and configured before the task using every tool-author-recommended normal integration surface. "
        "The product's own installed guidance remains authoritative. The evaluator adds no invocation requirement, preference, quota, or forced call. "
        "Use the exposed environment naturally, and do not invoke a tool merely because this is a treatment lane. "
        "If no treatment tool is invoked after faithful installation, zero use is a valid observed outcome. "
        "Do not use unconfigured retrieval, compression, memory, or token-saving tools. "
        "Codex web search is disabled and model-launched shell commands have no network access; do not attempt curl, wget, browsers, package downloads, or any other external retrieval. "
        "Work only inside the target repository. The controller owns concealed verification; do not inspect or modify evaluation harness files.\n\n"
        "---\n\n"
        f"{activation_block}"
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
    if not cfg:
        return 0
    warmup = cfg.get("warmup")
    if not warmup:
        return 0

    repo = rel_or_abs(record["target"]["repository_path"])
    for relative in warmup.get("cleanup_paths", []):
        cleanup = repo / str(relative)
        if cleanup.exists():
            shutil.rmtree(cleanup) if cleanup.is_dir() else cleanup.unlink()

    env = codex_env(codex_home, containerized=backend == "docker", cfg=cfg)
    env.update(tool_env_for_record(record, pid, codex_home))
    mounts = container_mounts_for_record(record, codex_home, include_repo=True, cfg=cfg)
    command = [render_tool_value(part, record, codex_home, cfg) for part in warmup["command"]]
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
    required_state_paths = [repo / str(relative) for relative in warmup.get("required_state_paths", [])]
    missing_state_paths = [str(path) for path in required_state_paths if not path.exists()]
    effective_exit_code = proc.returncode if proc.returncode != 0 or not missing_state_paths else 1
    metadata = {
        "profile_id": pid,
        "active_tool": cfg.get("display_name"),
        "tool_state": protocol.get("tool_state"),
        "warmup_kind": warmup.get("kind"),
        "command": command,
        "exit_code": effective_exit_code,
        "process_exit_code": proc.returncode,
        "required_state_paths": [str(path) for path in required_state_paths],
        "missing_state_paths": missing_state_paths,
        "started_at_utc": started.isoformat(),
        "ended_at_utc": ended.isoformat(),
        "wall_time_seconds": (ended - started).total_seconds(),
        "provider_tokens_counted": bool(protocol.get("warmup_provider_tokens_counted", False)),
        "output_artifact": output_name,
    }
    (run_dir / metadata_name).write_text(json.dumps(metadata, indent=2) + "\n")
    if metadata_name != "tool-warmup-metadata.json":
        (run_dir / "tool-warmup-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return effective_exit_code


def run_codex(record: dict[str, Any], pid: str, codex_home: Path, run_dir: Path, timeout: int, protocol: dict[str, Any], *, backend: str, docker_image: str) -> int:
    ensure_codex_native_binary_executable()
    repo = rel_or_abs(record["target"]["repository_path"])
    prompt = write_prompt(record, run_dir, pid, protocol)
    events = run_dir / "codex-events.jsonl"
    last = run_dir / "codex-last-message.txt"
    cfg = active_tool_config(record, pid)
    codex_cmd = [
        "codex",
        "exec",
        *codex_isolation_args(codex_home),
        "--json",
        "--color",
        "never",
        *codex_hook_args(cfg),
        "--ignore-rules",
        "--cd",
        str(repo),
        "--output-last-message",
        str(last),
        "-",
    ]
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
    integration = prepare_profile_integration(
        record,
        pid,
        codex_home,
        run_dir,
        backend=args.execution_backend,
        docker_image=args.docker_image,
    )
    if not integration["passed"]:
        print(json.dumps(integration, indent=2))
        return 7
    preflight = preflight_codex(record, codex_home, pid, run_dir, backend=args.execution_backend, docker_image=args.docker_image)
    if not preflight["passed"]:
        print(json.dumps(preflight, indent=2))
        return 3
    if args.prepare_only:
        workspace_code = prepare_profile_workspace(
            record,
            pid,
            codex_home,
            run_dir,
            protocol,
            backend=args.execution_backend,
            docker_image=args.docker_image,
        )
        if workspace_code != 0:
            print(f"profile workspace preparation failed with exit {workspace_code}")
            return 5
        handshake = probe_mcp_handshake(
            record,
            pid,
            codex_home,
            run_dir,
            backend=args.execution_backend,
            docker_image=args.docker_image,
        )
        if not handshake["passed"]:
            print(json.dumps(handshake, indent=2))
            return 8
        print(json.dumps({"prepared": True, "profile_id": pid, "codex_home": str(codex_home), "run_dir": str(run_dir), "host_integration": integration, "mcp_handshake": handshake, "tool_warmup_exit_code": workspace_code}, indent=2))
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
    handshake = probe_mcp_handshake(
        record,
        pid,
        codex_home,
        run_dir,
        backend=args.execution_backend,
        docker_image=args.docker_image,
    )
    if not handshake["passed"]:
        print(json.dumps(handshake, indent=2))
        return 8

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
            "weighted_token_cost": provider_usage.get("weighted_token_cost"),
            "weighted_token_cost_formula": provider_usage.get("weighted_token_cost_formula"),
        },
        "run_dir": str(run_dir),
    }
    (run_dir / "runner-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if summary["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
