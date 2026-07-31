#!/usr/bin/env python3
"""Run Codex warm-state multi-task lane evaluations.

The runner evaluates one profile on one active sequence from
``data/workflow-task-sequences.json``. Every regression is pre-seeded before
provider execution; task prompts are then fed to one persistent Codex thread via
``codex exec resume``. Controller verification is deferred until every prompt
has run so hidden gates do not alter or truncate the measured workflow.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import gzip
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import extract_codex_usage  # type: ignore
import extract_opencode_usage  # type: ignore
import extract_claude_code_usage  # type: ignore
import claude_code_workflow_adapter  # type: ignore
import run_codex_fixture_evaluation as fixture  # type: ignore
import validate_repository as repository_validation  # type: ignore

DEFAULT_DOCKER_IMAGE = "token-eval-codex:latest"
DEFAULT_SOURCE_CODEX_HOME = Path(os.environ.get("CODEX_HOME", "/opt/data/home/.codex"))
DATE = dt.datetime.now(dt.UTC).date().isoformat()
COMPACT_ARTIFACT_NAMES = {"run.json", "changes.diff", "evidence.jsonl.gz", "manifest.sha256"}
PRODUCTION_LOCK_PATH = Path("/opt/data/eval-workflow-lanes/.production.lock")
PRODUCTION_LOCK_FD_ENV = "WORKFLOW_PRODUCTION_LOCK_FD"
TRUSTED_REPOSITORY_ORIGIN = "git@github.com:merlinhu1/token-optimization-research.git"
TRUSTED_REPOSITORY_UPSTREAM = "origin/phase-3"
TRUSTED_REPOSITORY_REF = "refs/heads/phase-3"
OPENCODE_STANDALONE_R2_AUTHORITY_REL = Path(
    "sources/evaluations/audits/opencode-dcp-qualification-and-r2-authorization-20260730.json"
)
OPENCODE_LIFECYCLE_V1_R1_AUTHORITY_REL = Path(
    "sources/evaluations/audits/lifecycle-v1-opencode-sol-high-r1-authorization-20260802.json"
)

PROJECT_META: dict[str, dict[str, str]] = {
    "medium-fastify-fastify": {
        "project_id": "fastify-fastify",
        "dependency_command": "npm install --ignore-scripts --no-audit --no-fund",
    },
    "large-hashicorp-terraform": {
        "project_id": "hashicorp-terraform",
        "dependency_command": "go mod download",
        "dependency_environment": {"PATH": "/opt/data/bin:/opt/data/opt/go/bin:{PATH}", "GOTOOLCHAIN": "auto"},
    },
    "medium-beetbox-beets": {
        "project_id": "beetbox-beets",
        "dependency_command": "uv sync --group test --frozen",
    },
}

SUPPORTED_WORKFLOW_TOOL_PROFILES = {
    "retrieval-leanctx": "lean-ctx",
    "integrated-leanctx-codex-hybrid-v1": "leanctx-codex-hybrid-v1",
    "retrieval-codegraph": "codegraph",
    "retrieval-codegraph-codex-mcp-v1": "codegraph-codex-mcp-v1",
    "lower-intervention-codegraph": "codegraph",
    "retrieval-cartog": "cartog",
    "retrieval-cartog-codex-product-v2": "cartog-codex-product-v2",
    "codescope-owner": "codescope",
    "codescope-codex-product-v1": "codescope-codex-product-v1",
    "swarmvault-owner": "swarmvault",
    "swarmvault-codex-product-v1": "swarmvault-codex-product-v1",
    "retrieval-serena": "serena",
    "retrieval-serena-codex-mcp-v1": "serena-codex-mcp-v1",
    "retrieval-graphify": "graphify",
    "retrieval-graphify-codex-skill-v1": "graphify-codex-skill-v1",
    "retrieval-sigmap": "sigmap",
    "retrieval-sigmap-codex-live-v1": "sigmap-codex-live-v1",
    "retrieval-jcodemunch-mcp": "jcodemunch-mcp",
    "integrated-token-savior": "token-savior",
    "integrated-token-savior-mcp-v1": "token-savior-mcp-v1",
    "integrated-token-savior-codex-product-v2": "token-savior-codex-product-v2",
    "retrieval-jcodemunch-codex-mcp-v2": "jcodemunch-codex-mcp-v2",
    "headroom-default-codex": "headroom",
    "terminal-headroom": "headroom-proxy-only",
    "terminal-rtk": "rtk",
    "terminal-rtk-codex-instructions-v1": "rtk-codex-instructions-v1",
    "terminal-rtk-claude-code-hook-v1": "rtk-claude-code-hook-v1",
    "terminal-snip": "snip",
    "terminal-snip-codex-hook-v1": "snip-codex-hook-v1",
    "terminal-lowfat": "lowfat",
    "terminal-tokenjuice": "tokenjuice",
    "terminal-tokenjuice-codex-hook-v1": "tokenjuice-codex-hook-v1",
    "stack-tokenjuice-jcodemunch-mcp": "tokenjuice-jcodemunch-mcp-stack",
    "behavior-caveman-codex-skill-v1": "caveman-codex-skill-v1",
    "artifact-ponytail-codex-plugin-v1": "ponytail-codex-plugin-v1",
    "runtime-opencode-codex-product-v1": "opencode-codex-product-v1",
    # Historical OpenCode treatment IDs remain reconstructable for immutable protocols,
    # but their profile registry status prevents rerun after deletion.
    "terminal-tokenjuice-opencode-plugin-v1": "tokenjuice-opencode-plugin-v1",
    "terminal-snip-opencode-plugin-v1": "snip-opencode-plugin-v1",
    "retrieval-cartog-opencode-product-v1": "cartog-opencode-product-v1",
    "integrated-headroom-opencode-product-v1": "headroom-opencode-product-v1",
    "integrated-headroom-opencode-product-v2": "headroom-opencode-product-v2",
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
    "retrieval-jcodemunch-opencode-product-v1": "jcodemunch-opencode-product-v1",
    "integrated-leanctx-opencode-hybrid-v1": "leanctx-opencode-hybrid-v1",
    "integrated-leanctx-opencode-hybrid-v2": "leanctx-opencode-hybrid-v1",
    "retrieval-sigmap-opencode-product-v1": "sigmap-opencode-product-v1",
    "artifact-ponytail-opencode-plugin-v1": "ponytail-opencode-plugin-v1",
    "behavior-caveman-opencode-plugin-v1": "caveman-opencode-plugin-v1",
    "terminal-lowfat-opencode-plugin-v1": "lowfat-opencode-plugin-v1",
    "context-dcp-opencode-plugin-v1": "dcp-opencode-plugin-v1",
}

# Existing profile protocols were qualified against this runner manifest. The
# Token Savior v2 controller-only host-install path does not alter those
# profiles, so preserve their semantic manifest identity instead of forcing an
# unrelated 45-lane requalification. New profiles opt into the current file
# hash explicitly through ``tool_manifest_identity``.
LEGACY_TOOL_MANIFEST_SHA256 = "6fa8271b89a577706ea0bbffcc8e4521831f41b646ed9519369efee3642fe41c"
FIXED_CURRENT_TOOL_MANIFEST_SHA256 = {
    "integrated-headroom-opencode-product-v1": "5077500216db998b089ec9bdf8f38c82023db56314cfded233105ab625c585fe",
}


def build_profile_meta() -> dict[str, dict[str, Any]]:
    catalog_path = ROOT / "data/evaluation-profiles.json"
    catalog = json.loads(catalog_path.read_text())
    canonical = {profile["id"]: profile for profile in catalog.get("profiles", [])}
    supported = {
        "baseline-bare-codex": None,
        "baseline-claude-code-no-mcp": None,
        **SUPPORTED_WORKFLOW_TOOL_PROFILES,
    }
    profiles: dict[str, dict[str, Any]] = {}
    for profile_id, tool_id in supported.items():
        source = canonical.get(profile_id)
        if source is None:
            raise KeyError(f"workflow profile {profile_id} is missing from {catalog_path}")
        cfg = fixture.TOOL_CONFIGS[str(tool_id)] if tool_id else None
        protocol = source.get("evaluation_protocol") or {}
        profile_type = str(source["profile_type"])
        profiles[profile_id] = {
            "session_role": (
                "baseline"
                if profile_type == "control"
                else "stack_treatment"
                if profile_type == "tool_stack"
                else "replacement_runtime"
                if profile_type == "replacement_runtime"
                else "individual_tool_treatment"
            ),
            "profile_type": profile_type,
            "objective_scope": str(source["objective_scope"]),
            "component_ids": [str(component["component_id"]) for component in source.get("components", [])],
            "enabled_surfaces": [str(surface) for surface in source.get("enabled_surfaces", [])],
            "disabled_overlaps": [str(surface) for surface in source.get("disabled_overlaps", [])],
            "allowed_terms": sorted({str(tool_id), *[str(term) for term in (cfg or {}).get("allowed_terms", [])]}) if tool_id else [],
            "supported_commands": sorted(str(command) for command in (cfg or {}).get("supported_commands", [])),
            "tool_state": str(protocol.get("tool_state", (cfg or {}).get("default_tool_state", "none"))),
            "tool_use_policy": str(protocol.get("tool_use_policy", "natural" if tool_id else "none")),
            "tool_id": tool_id,
            "substrate": str(source.get("substrate", "codex-cli")),
        }
    return profiles


PROFILE_META: dict[str, dict[str, Any]] = build_profile_meta()

DEFAULT_WORKFLOW_MODEL_CONDITION_ID = "codex-openai-gpt-5-6-luna-xhigh"
DEFAULT_WORKFLOW_MODEL = "gpt-5.6-luna"
DEFAULT_WORKFLOW_REASONING_EFFORT = "xhigh"
RUNNER_CONTRACT_VERSION = "workflow-runner-v10"
MAX_CODEX_OPERATIONAL_RETRIES = 1
THREAD_CONTINUITY_FAILURE_EXIT_CODE = 86
TASK_VERIFIER_RESULT_PREFIX = "__WORKFLOW_TASK_RESULT__"
PROJECT_COMPILE_RESULT_PREFIX = "WORKFLOW_PROJECT_COMPILE_RESULT"

# Preserve the active comparison pools while moving their identity away from
# whole-runner hashes. Each alias is guarded by the full causal comparison hash:
# exact rendered model-facing prompt bytes, verifier/seed bytes, fixture, model,
# runtime image, and isolation. A causal change misses the alias and mints a new
# fingerprint; reporting-only runner changes keep the existing pool and do not
# invalidate accumulated runs. The second alias per pool binds the same audited
# historical prompt bytes after rendered-prompt hashes became explicit.
COMPARISON_IDENTITY_ALIASES = {
    "fbf96dc85022c887bc5843e5bb1f6a33638c662992df5c0595b025a29e3eaf27": "b60df5d02524",
    "6bf503b180d4b0fe144ade7ec2d0ef6d67c5cd5b30368c71d2e57c4b74062b58": "e3e314f5a44e",
    "d263062d12e141cc40092602c3c74c11d8576e12a23124c90b4e78f2acc751cf": "ca2e2a06cba6",
    "d44793c6f7db74468255680444643cad47819e9a395bfe4b8c4374e46e11aec9": "b60df5d02524",
    "6d0a5299f7a8ce1cb3c041369afb6efa239a3dc7c30df1fe1247836796e3f2a6": "e3e314f5a44e",
    "b2de62fd38e071d92c2eeaa7ad03a084c6302d7336f7e3aa658ace11df00e641": "ca2e2a06cba6",
}


def validate_default_model_condition() -> None:
    """Reject launches if the registry no longer names the frozen active default."""
    conditions = json.loads((ROOT / "data/evaluation-agent-runtimes.json").read_text()).get("model_conditions", [])
    active = [item for item in conditions if item.get("status") == "active-default"]
    if active != [{
        "id": DEFAULT_WORKFLOW_MODEL_CONDITION_ID,
        "status": "active-default",
        "runtime_id": "codex-cli",
        "agent_name": "Codex CLI",
        "provider": "openai",
        "model": DEFAULT_WORKFLOW_MODEL,
        "reasoning_effort": DEFAULT_WORKFLOW_REASONING_EFFORT,
        "usage_accounting": "provider-reported Codex JSONL usage extracted by scripts/extract_codex_usage.py",
    }]:
        raise ValueError("active workflow model condition must be codex-openai-gpt-5-6-luna-xhigh")

LEAKY_PROMPT_LINE_PATTERNS = [
    re.compile(r"^Issue source:.*$", re.IGNORECASE),
    re.compile(r"^The repository has already been checked out.*$", re.IGNORECASE),
    re.compile(r"^This task follows a SWE-bench-style flow:.*$", re.IGNORECASE),
    re.compile(r".*pinned fixed upstream commit.*", re.IGNORECASE),
    re.compile(r".*seeded with a regression.*", re.IGNORECASE),
    re.compile(r".*removes? the relevant production fix.*", re.IGNORECASE),
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def run(
    cmd: list[str],
    *,
    cwd: Path,
    stdout: Path | None = None,
    timeout: int = 900,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    if stdout:
        stdout.parent.mkdir(parents=True, exist_ok=True)
        with stdout.open("w") as out:
            return subprocess.run(cmd, cwd=cwd, text=True, stdout=out, stderr=subprocess.STDOUT, timeout=timeout, env=env)
    return subprocess.run(cmd, cwd=cwd, text=True, timeout=timeout, env=env)


def chmod_tree(path: Path) -> None:
    if not path.exists():
        return
    for cur, dirs, files in os.walk(path):
        try:
            os.chmod(cur, 0o700)
        except OSError:
            pass
        for name in dirs:
            try:
                os.chmod(Path(cur) / name, 0o700)
            except OSError:
                pass
        for name in files:
            try:
                os.chmod(Path(cur) / name, 0o600)
            except OSError:
                pass


def sequence_doc() -> dict[str, Any]:
    return json.loads((ROOT / "data/workflow-task-sequences.json").read_text())


def load_sequence(sequence_id: str) -> dict[str, Any]:
    for seq in sequence_doc().get("sequences", []):
        if seq.get("id") == sequence_id:
            return seq
    raise KeyError(f"unknown workflow sequence {sequence_id}")


def active_sequence_ids() -> list[str]:
    return [seq["id"] for seq in sequence_doc().get("sequences", []) if seq.get("status") == "active"]


def warm_lane_contract(seq: dict[str, Any]) -> dict[str, Any]:
    orders = [int(task["order"]) for task in sorted(seq["tasks"], key=lambda item: int(item["order"]))]
    return {
        "seed_delivery_mode": "preseeded-composite",
        "preseeded_task_orders": orders,
        "future_seed_regressions_visible": True,
        "controller_verification": "final-only",
        "repository_state_persists_between_tasks": True,
        "tool_state_persists_between_tasks": True,
    }


def task_checkpoint_allows_continue(
    *,
    codex_exit_code: int,
    thread_id: str | None,
    verifier_integrity_passed: bool,
) -> bool:
    """Gate only operational validity between prompts; functional acceptance is final-only."""
    return codex_exit_code == 0 and thread_id is not None and verifier_integrity_passed


def safe_profile_key(profile_id: str) -> str:
    return profile_id.replace("_", "-")


BASELINE_POOL_PROTOCOL_VERSION = "baseline-pool-v1"
BASELINE_POOL_FINGERPRINT_LENGTH = 12


def _protocol_file_hash(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"baseline protocol input is missing: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _self_hash(root: Path = ROOT) -> str:
    return _protocol_file_hash(root / "scripts/run_codex_workflow_evaluation.py")


def _json_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def profile_catalog_entry(profile_id: str, root: Path = ROOT) -> dict[str, Any]:
    catalog = json.loads((root / "data/evaluation-profiles.json").read_text())
    for profile in catalog.get("profiles", []):
        if profile.get("id") == profile_id:
            return profile
    raise KeyError(f"workflow profile {profile_id} is missing from data/evaluation-profiles.json")


def profile_registry_entry(profile_id: str, root: Path = ROOT) -> dict[str, Any]:
    entry = dict(profile_catalog_entry(profile_id, root))
    # Reporting labels must not alter frozen execution/profile identity.
    entry.pop("artifact_slug", None)
    return entry


def profile_runtime_id(profile_id: str, root: Path = ROOT) -> str:
    return str(profile_registry_entry(profile_id, root).get("substrate") or "codex-cli")


def runtime_agent_name(runtime_id: str) -> str:
    return {
        "codex-cli": "Codex CLI",
        "opencode-cli": "OpenCode CLI",
        "claude-code": "Claude Code",
    }.get(runtime_id, runtime_id)


def runtime_version_from_preflight(profile_id: str, run_dir: Path) -> str:
    if profile_runtime_id(profile_id) == "opencode-cli":
        path = run_dir / "tool-preflight.txt"
        if path.is_file():
            try:
                value = json.loads(path.read_text())
            except json.JSONDecodeError:
                value = {}
            version = value.get("version") if isinstance(value, dict) else None
            return str(version) if isinstance(version, str) else ""
        return ""
    if profile_runtime_id(profile_id) == "claude-code":
        path = run_dir / "claude-code-preflight.json"
        if path.is_file():
            try:
                value = json.loads(path.read_text())
            except json.JSONDecodeError:
                value = {}
            version = value.get("version") if isinstance(value, dict) else None
            return str(version) if isinstance(version, str) else ""
        return ""
    smoke = (run_dir / "docker-smoke-output.txt").read_text(errors="replace") if (run_dir / "docker-smoke-output.txt").exists() else ""
    return next((line.strip() for line in smoke.splitlines() if "codex" in line.lower() and any(ch.isdigit() for ch in line)), "")


def assert_profile_runnable(profile_id: str, root: Path = ROOT) -> None:
    profile = profile_registry_entry(profile_id, root)
    if profile.get("status") in {"blocked-profile", "historical-profile", "deferred-profile", "invalid-profile"}:
        reason = str(
            profile.get("blocked_reason")
            or profile.get("deferred_reason")
            or "integration is not qualified"
        )
        raise ValueError(f"profile {profile_id} is {profile.get('status')}: {reason}")


PILOT_ZERO_COUNT_FIELDS = (
    "observed_unique_model_caused_incidents",
    "observed_corrected_implementation_mistakes",
    "observed_unresolved_defects",
    "observed_prohibited_operations",
    "observed_unnecessary_exploration_incidents",
    "observed_model_caused_failed_commands",
    "observed_code_rework_events",
    "observed_verifier_or_environment_failures",
)
PILOT_PROVIDER_USAGE_FIELDS = (
    "fresh_input_tokens",
    "cached_input_tokens",
    "cache_write_tokens",
    "output_tokens",
    "reasoning_tokens",
    "total_provider_tokens",
)


def canonical_protocol_id(
    seq: dict[str, Any],
    profile_id: str,
    root: Path = ROOT,
    *,
    baseline_descriptor: dict[str, Any] | None = None,
    selected_execution: dict[str, Any] | None = None,
) -> str:
    """Compute the sole canonical protocol identity from causal descriptor bytes."""
    execution = selected_execution or execution_condition_descriptor(
        seq,
        profile_id,
        timeout_seconds_per_task=3600,
        docker_image=DEFAULT_DOCKER_IMAGE,
        root=root,
    )
    baseline = baseline_descriptor or baseline_protocol_descriptor(seq, root)
    if seq.get("task_family_generation") in {"baseline-v4", "lifecycle-v1"}:
        baseline = {
            key: value
            for key, value in baseline.items()
            if key not in NON_CAUSAL_PROTOCOL_PROVENANCE_FIELDS
        }
    identity = {
        "baseline_protocol": baseline,
        "selected_execution": execution,
    }
    return "-".join(
        (
            safe_profile_key(seq["id"]),
            safe_profile_key(profile_id),
            _json_hash(identity)[:12],
        )
    )


def pilot_provider_usage_valid(usage: Any) -> bool:
    """Validate the canonical Codex provider-token evidence shape and arithmetic."""
    return repository_validation.provider_usage_valid(usage)


def condition_bound_protocol_descriptors(
    seq: dict[str, Any],
    profile_id: str,
    condition_id: str,
    model: str,
    reasoning_effort: str,
    root: Path = ROOT,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build protocol descriptors for a registered model condition without mutable globals."""
    conditions = json.loads((root / "data/evaluation-agent-runtimes.json").read_text()).get("model_conditions", [])
    matches = [
        item for item in conditions
        if item.get("id") == condition_id
        and item.get("runtime_id") == "codex-cli"
        and item.get("provider") == "openai"
        and item.get("model") == model
        and item.get("reasoning_effort") == reasoning_effort
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one registered model condition for {condition_id}/{model}/{reasoning_effort}; found {len(matches)}")
    selected = matches[0]
    launcher_path = "scripts/run_codex_workflow_model_condition.py"
    launcher_identity = {
        "path": launcher_path,
        "sha256": _protocol_file_hash(root / launcher_path),
    }

    def apply_condition(agent: dict[str, Any], condition: dict[str, Any]) -> None:
        agent.pop("codex_version_condition", None)
        agent.pop("runtime_version_condition", None)
        agent.update({
            "runtime_id": condition["runtime_id"],
            "provider": condition["provider"],
            "model": condition["model"],
            "model_condition_id": condition["id"],
            "reasoning_effort": condition["reasoning_effort"],
            "codex_version_condition": "captured-at-run-and-bound-to-record",
        })

    def condition_override(condition: dict[str, Any]) -> dict[str, Any]:
        return {
            "model_condition_id": condition["id"],
            "runtime_id": condition["runtime_id"],
            "provider": condition["provider"],
            "model": condition["model"],
            "reasoning_effort": condition["reasoning_effort"],
            "registry_status": condition.get("status"),
            "launcher": launcher_identity,
        }

    baseline_descriptor = baseline_protocol_descriptor(seq, root)
    apply_condition(baseline_descriptor["agent"], selected)
    baseline_descriptor["runtime_inputs"]["codex_runtime_condition"] = condition_id
    baseline_descriptor["runtime_inputs"]["model_condition_id"] = condition_id
    baseline_descriptor["runtime_inputs"]["model_condition_launcher"] = launcher_path
    baseline_descriptor["model_condition_override"] = condition_override(selected)
    comparison_descriptor = baseline_comparison_descriptor(seq, root)
    comparison_descriptor["agent"] = baseline_descriptor["agent"]
    comparison_descriptor["runtime_inputs"] = baseline_descriptor["runtime_inputs"]
    encoded = json.dumps(comparison_descriptor, sort_keys=True, separators=(",", ":")).encode()
    full_hash = hashlib.sha256(encoded).hexdigest()
    fingerprint = COMPARISON_IDENTITY_ALIASES.get(full_hash, full_hash[:BASELINE_POOL_FINGERPRINT_LENGTH])
    selected_execution = execution_condition_descriptor(
        seq,
        profile_id,
        timeout_seconds_per_task=3600,
        docker_image=DEFAULT_DOCKER_IMAGE,
        root=root,
    )
    apply_condition(selected_execution["agent_condition"], selected)
    selected_execution["runtime"]["agent_runtime_id"] = selected["runtime_id"]
    selected_execution["runtime"]["model_condition"] = {
        "id": selected["id"],
        "provider": selected["provider"],
        "model": selected["model"],
        "reasoning_effort": selected["reasoning_effort"],
        "launcher": launcher_path,
    }
    selected_execution["baseline_pool_reference"]["protocol_fingerprint"] = fingerprint
    selected_execution["model_condition_override"] = condition_override(selected)
    return baseline_descriptor, selected_execution


def current_baseline_v2_protocol(
    seq: dict[str, Any], gate: dict[str, Any], root: Path = ROOT
) -> tuple[dict[str, str], dict[str, Any]]:
    """Return the one frozen baseline protocol matching every current V2 input."""
    expected_descriptor, expected_execution = condition_bound_protocol_descriptors(
        seq,
        "baseline-bare-codex",
        str(gate.get("designated_model_condition", "")),
        str(gate.get("model", "")),
        str(gate.get("reasoning_effort", "")),
        root,
    )
    expected_fingerprint = baseline_protocol_fingerprint_from_descriptor(expected_descriptor)
    expected_execution_hash = _json_hash(expected_execution)
    expected_protocol_id = canonical_protocol_id(
        seq,
        "baseline-bare-codex",
        root,
        baseline_descriptor=expected_descriptor,
        selected_execution=expected_execution,
    )
    qualification_rel = seq.get("qualification_path")
    if not isinstance(qualification_rel, str):
        raise ValueError("sequence qualification_path is missing")
    qualification_path = root / qualification_rel
    qualification_sha = _protocol_file_hash(qualification_path)
    expected_condition = {
        "model_condition_id": gate.get("designated_model_condition"),
        "model": gate.get("model"),
        "reasoning_effort": gate.get("reasoning_effort"),
    }
    matches: list[tuple[Path, dict[str, Any]]] = []
    protocol_dir = root / "sources/evaluations/protocols"
    expected_protocol_path = protocol_dir / f"{expected_protocol_id}.json"
    candidate_paths = [expected_protocol_path] if expected_protocol_path.is_file() else sorted(
        protocol_dir.glob(f"{safe_profile_key(seq['id'])}-baseline-bare-codex-*.json")
    )
    for path in candidate_paths:
        document = json.loads(path.read_text())
        fixture_block = document.get("task_fixture", {})
        baseline_block = document.get("baseline", {})
        selected_execution = document.get("selected_execution", {})
        baseline_pool = document.get("baseline_pool", {})
        if (
            document.get("protocol_schema_version") == 3
            and document.get("status") == "frozen-ready-not-run"
            and document.get("protocol_id") == path.stem
            and path == protocol_dir / f"{document.get('protocol_id')}.json"
            and document.get("protocol_id") == canonical_protocol_id(
                seq,
                "baseline-bare-codex",
                root,
                baseline_descriptor=baseline_pool.get("descriptor"),
                selected_execution=selected_execution.get("descriptor"),
            )
            and fixture_block.get("sequence_id") == seq.get("id")
            and (
                seq.get("task_family_generation") not in {"baseline-v4", "lifecycle-v1"}
                or fixture_block.get("task_family_generation") == seq.get("task_family_generation")
            )
            and fixture_block.get("fixture_id") == seq.get("fixture_id")
            and fixture_block.get("snapshot") == seq.get("initial_snapshot", {}).get("commit")
            and fixture_block.get("qualification_path") == qualification_rel
            and fixture_block.get("qualification_sha256") == qualification_sha
            and baseline_block.get("profile_id") == "baseline-bare-codex"
            and {
                "model_condition_id": baseline_block.get("model_condition_id"),
                "model": baseline_block.get("model"),
                "reasoning_effort": baseline_block.get("reasoning_effort"),
            } == expected_condition
            and not document.get("treatment", {}).get("profile_id")
            and baseline_pool.get("protocol_fingerprint") == expected_fingerprint
            and baseline_protocol_descriptor_compatible(
                baseline_pool.get("descriptor"), expected_descriptor
            )
            and selected_execution.get("descriptor") == expected_execution
            and selected_execution.get("descriptor_sha256") == expected_execution_hash
        ):
            matches.append((path, document))
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one current designated baseline protocol for {seq.get('id')}; found {len(matches)}"
        )
    path, document = matches[0]
    identity = {
        "protocol_id": document["protocol_id"],
        "path": str(path.relative_to(root)),
        "sha256": _protocol_file_hash(path),
        "qualification_sha256": qualification_sha,
        "baseline_pool_fingerprint": expected_fingerprint,
        "selected_execution_sha256": expected_execution_hash,
    }
    return identity, document


def evidence_bundle_valid(path: Path, max_uncompressed_bytes: int = 64 * 1024 * 1024) -> bool:
    return repository_validation.evidence_bundle_valid(path, max_uncompressed_bytes)


def pilot_session_artifacts_valid(session: dict[str, Any], root: Path = ROOT) -> bool:
    """Require an intact compact artifact bundle bound to the audited session."""
    artifacts = session.get("artifacts")
    if not isinstance(artifacts, dict) or artifacts.get("artifact_contract") != "compact-v1-four-files":
        return False
    keys = ("run_record", "final_diff", "evidence_bundle", "manifest")
    root_resolved = root.resolve()
    paths: dict[str, Path] = {}
    try:
        for key in keys:
            value = artifacts.get(key)
            if not isinstance(value, str) or not value or Path(value).is_absolute():
                return False
            candidate = root / value
            if candidate.is_symlink():
                return False
            path = candidate.resolve()
            path.relative_to(root_resolved)
            if not path.is_file():
                return False
            paths[key] = path
    except (OSError, ValueError):
        return False
    expected_artifact_names = {
        "run_record": "run.json",
        "final_diff": "changes.diff",
        "evidence_bundle": "evidence.jsonl.gz",
        "manifest": "manifest.sha256",
    }
    if (
        len({path for path in paths.values()}) != len(keys)
        or any(paths[key].name != expected_artifact_names[key] for key in keys)
    ):
        return False
    parents = {path.parent for path in paths.values()}
    if len(parents) != 1:
        return False
    artifact_root = next(iter(parents))
    session_id = session.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return False
    expected_artifact_root = (
        root / "sources/evaluations/workflow-sessions" / session_id
    )
    expected_root_value = f"sources/evaluations/workflow-sessions/{session_id}"
    if (
        artifacts.get("root") != expected_root_value
        or expected_artifact_root.is_symlink()
        or artifact_root != expected_artifact_root.resolve()
    ):
        return False
    try:
        entries = list(artifact_root.iterdir())
    except OSError:
        return False
    if (
        len(entries) != len(COMPACT_ARTIFACT_NAMES)
        or any(entry.is_symlink() or not entry.is_file() for entry in entries)
        or {entry.name for entry in entries} != COMPACT_ARTIFACT_NAMES
    ):
        return False
    errors: list[str] = []
    repository_validation.validate_compact_manifest(
        artifact_root,
        str(session.get("session_id", "pilot-session")),
        errors,
    )
    if errors or not evidence_bundle_valid(paths["evidence_bundle"]):
        return False
    try:
        run_record = json.loads(paths["run_record"].read_text())
    except (OSError, json.JSONDecodeError):
        return False
    if not repository_validation.compact_run_record_matches_session(
        session,
        run_record,
        current_contract=True,
        require_accepted=True,
    ):
        return False
    usage = session.get("cumulative_token_usage", {})
    run_usage = run_record.get("token_usage", {}) if isinstance(run_record, dict) else {}
    accounting_invalid = (
        isinstance(session.get("interpretation"), dict)
        and session["interpretation"].get("evaluation_validity") == "invalid-accounting"
    )
    if accounting_invalid:
        for invalid_usage in (usage, run_usage):
            if not isinstance(invalid_usage, dict):
                return False
            invalid_fields = [invalid_usage.get(key) for key in PILOT_PROVIDER_USAGE_FIELDS]
            if (
                any(type(value) is not int or value < 0 for value in invalid_fields)
                or type(invalid_usage.get("cache_write_tokens")) is not int
            ):
                return False
    else:
        if not pilot_provider_usage_valid(usage) or not pilot_provider_usage_valid(run_usage):
            return False
    if any(run_usage.get(key) != usage.get(key) for key in ("measurement_source", *PILOT_PROVIDER_USAGE_FIELDS)):
        return False
    selected_descriptor = session.get("selected_execution", {}).get("descriptor", {})
    runtime = selected_descriptor.get("runtime", {}) if isinstance(selected_descriptor, dict) else {}
    expected_agent = selected_descriptor.get("agent_condition", {}) if isinstance(selected_descriptor, dict) else {}
    session_agent = session.get("agent", {})
    run_agent = run_record.get("agent_condition", {}) if isinstance(run_record, dict) else {}
    agent_keys = ("runtime_id", "provider", "model", "model_condition_id", "reasoning_effort")
    if (
        not isinstance(expected_agent, dict)
        or not isinstance(session_agent, dict)
        or not isinstance(run_agent, dict)
        or any(session_agent.get(key) != expected_agent.get(key) for key in agent_keys)
        or any(run_agent.get(key) != expected_agent.get(key) for key in agent_keys)
    ):
        return False
    profile_id = session.get("profile", {}).get("profile_id")
    selected_profile_id = selected_descriptor.get("selected_profile", {}).get("profile_id")
    expected_session_role = PROFILE_META.get(profile_id, {}).get("session_role")
    expected_execution_role = expected_session_role
    if (
        not isinstance(profile_id, str)
        or not expected_session_role
        or selected_profile_id != profile_id
        or selected_descriptor.get("execution_role") != expected_execution_role
        or session.get("session_role") != expected_session_role
    ):
        return False
    identity_errors: list[str] = []
    repository_validation.validate_docker_identity(
        session.get("docker_image_identity"), runtime.get("docker_image_identity"), str(session.get("session_id", "pilot-session")), identity_errors
    )
    repository_validation.validate_tool_adapter_identity(
        session.get("tool_adapter_identity"), selected_descriptor.get("tool_adapter"), profile_id, str(session.get("session_id", "pilot-session")), identity_errors
    )
    repository_validation.validate_docker_identity(
        run_record.get("docker_image_identity"), runtime.get("docker_image_identity"), str(session.get("session_id", "pilot-session")), identity_errors
    )
    repository_validation.validate_tool_adapter_identity(
        run_record.get("tool_adapter_identity"), selected_descriptor.get("tool_adapter"), profile_id, str(session.get("session_id", "pilot-session")), identity_errors
    )
    if identity_errors:
        return False
    return (
        isinstance(run_record, dict)
        and run_record.get("session_id") == session.get("session_id")
        and run_record.get("replicate_index") == session.get("replicate_index")
        and run_record.get("workflow_sequence_id") == session.get("task_sequence", {}).get("sequence_id")
        and run_record.get("profile_id") == session.get("profile", {}).get("profile_id")
        and run_record.get("accepted") is True
        and run_record.get("frozen_protocol") == session.get("frozen_protocol")
        and run_record.get("baseline_pool") == session.get("baseline_pool")
        and run_record.get("selected_execution") == session.get("selected_execution")
        and run_record.get("per_task_results") == session.get("per_task_results")
        and run_record.get("verifier_integrity_passed") is True
        and run_record.get("token_usage", {}).get("total_provider_tokens") == usage.get("total_provider_tokens")
    )


def repository_authority_path(root: Path, relative: str, label: str) -> Path:
    relative_path = Path(relative)
    lexical_parts = relative.split("/")
    if (
        relative_path.is_absolute()
        or "\\" in relative
        or any(part in {"", ".", ".."} for part in lexical_parts)
    ):
        raise ValueError(f"{label} must use a canonical repository-relative path without traversal")
    path = root / relative_path
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"{label} must use a canonical repository-relative path without traversal")
    return path


def baseline_pilot_attempt_receipt_path(seq: dict[str, Any], root: Path = ROOT) -> Path:
    gate = seq.get("mistake_gate")
    receipt_rel = gate.get("attempt_receipt_path") if isinstance(gate, dict) else None
    if not isinstance(receipt_rel, str) or not receipt_rel:
        raise ValueError(f"missing pilot attempt_receipt_path for {seq.get('id')}")
    return repository_authority_path(root, receipt_rel, f"pilot attempt receipt for {seq.get('id')}")


BASELINE_REPLICATION_AUTHORITY_REL = "sources/evaluations/audits/current-low-complexity-baseline-r1-r2-authorization-20260728.json"
LIFECYCLE_V1_REPLICATION_AUTHORITY_REL = "sources/evaluations/audits/lifecycle-v1-codex-sol-high-r1-authorization-20260802.json"
LIFECYCLE_V1_REPLICATION_ATTEMPT_DIR = "sources/evaluations/audits/lifecycle-v1-codex-sol-high-r1-attempts"
BEETS_R3_REPLACEMENT_AUTHORITY_REL = "sources/evaluations/audits/current-low-complexity-beets-r3-replacement-authorization-20260728.json"
BEETS_R3_REPLACEMENT_ATTEMPT_REL = "sources/evaluations/audits/current-low-complexity-beets-r3-replacement-attempt-20260728.json"
BASELINE_REPLICATION_MODEL_CONDITION = {
    "id": "codex-openai-gpt-5-6-sol-high",
    "model": "gpt-5.6-sol",
    "reasoning_effort": "high",
}
LIFECYCLE_V1_PILOT_AUTHORIZATION = {
    "authorized_by_owner_message_id": "1533263215067140148",
    "authorized_on": "2026-08-02",
    "model_condition": BASELINE_REPLICATION_MODEL_CONDITION,
    "replicate_index": 0,
    "sequence_order": [
        "fastify-lifecycle-sequence-v1",
        "beets-lifecycle-sequence-v1",
        "terraform-lifecycle-sequence-v1",
    ],
    "serialization_required": True,
    "allowed_paid_baseline_runs": 3,
    "allowed_model_turns": 9,
    "rerun_after_attempt_receipt": False,
}
BASELINE_REPLICATION_TOP_LEVEL_KEYS = {
    "schema_version", "campaign_id", "authorized_by_owner_message_id", "authorized_on",
    "paid_baseline_replication_authorized", "authorized_replicate_indexes", "sequence_order",
    "serialization_required", "allowed_paid_baseline_runs", "allowed_model_turns", "model_condition",
    "first_valid_sample_policy", "rerun_after_attempt_receipt", "provider_calls", "provider_tokens",
    "sequences", "notes",
}
BASELINE_REPLICATION_BINDING_KEYS = {
    "sequence_id", "task_family_generation", "protocol_path", "protocol_sha256", "baseline_pool_fingerprint",
}


def _json_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_current_baseline_replication_authority(root: Path = ROOT) -> dict[str, Any]:
    """Strictly validate every decision-bearing field before any campaign spend."""
    path = repository_authority_path(root, BASELINE_REPLICATION_AUTHORITY_REL, "baseline replication authorization")
    try:
        authority = json.loads(path.read_text(), object_pairs_hook=_json_without_duplicate_keys)
        sequence_doc = json.loads(
            (root / "data/workflow-task-sequences.json").read_text(),
            object_pairs_hook=_json_without_duplicate_keys,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"baseline replication authority is unreadable: {exc}") from exc
    active_sequences = [item for item in sequence_doc.get("sequences", []) if item.get("status") == "active"]
    expected_order = [item.get("id") for item in active_sequences]
    records = authority.get("sequences")
    replicate_indexes = authority.get("authorized_replicate_indexes")
    strict_header = (
        set(authority) == BASELINE_REPLICATION_TOP_LEVEL_KEYS
        and authority.get("schema_version") == 1
        and type(authority.get("schema_version")) is int
        and authority.get("campaign_id") == "current-low-complexity-baseline-r1-r2-20260728"
        and authority.get("authorized_by_owner_message_id") == "1531674305564508322"
        and authority.get("authorized_on") == "2026-07-28"
        and authority.get("paid_baseline_replication_authorized") is True
        and isinstance(replicate_indexes, list)
        and len(replicate_indexes) == 2
        and all(type(item) is int for item in replicate_indexes)
        and replicate_indexes == [1, 2]
        and authority.get("sequence_order") == expected_order
        and authority.get("serialization_required") is True
        and type(authority.get("allowed_paid_baseline_runs")) is int
        and authority.get("allowed_paid_baseline_runs") == len(active_sequences) * 2 == 6
        and type(authority.get("allowed_model_turns")) is int
        and authority.get("allowed_model_turns") == sum(len(item.get("tasks", [])) for item in active_sequences) * 2 == 18
        and authority.get("model_condition") == BASELINE_REPLICATION_MODEL_CONDITION
        and authority.get("first_valid_sample_policy") is True
        and authority.get("rerun_after_attempt_receipt") is False
        and type(authority.get("provider_calls")) is int
        and authority.get("provider_calls") == 0
        and type(authority.get("provider_tokens")) is int
        and authority.get("provider_tokens") == 0
        and isinstance(authority.get("notes"), str)
        and bool(authority.get("notes"))
    )
    strict_records = (
        isinstance(records, list)
        and len(records) == len(active_sequences)
        and all(isinstance(item, dict) and set(item) == BASELINE_REPLICATION_BINDING_KEYS for item in records)
        and [item.get("sequence_id") for item in records] == expected_order
    )
    if not strict_header or not strict_records:
        raise ValueError("baseline replication authority has invalid authorization, scope, budget, model, or policy")
    assert isinstance(records, list)
    for sequence, binding in zip(active_sequences, records, strict=True):
        identity, protocol = current_baseline_v2_protocol(sequence, sequence["mistake_gate"], root)
        expected_binding = {
            "sequence_id": sequence.get("id"),
            "task_family_generation": sequence.get("task_family_generation"),
            "protocol_path": identity["path"],
            "protocol_sha256": identity["sha256"],
            "baseline_pool_fingerprint": protocol.get("baseline_pool", {}).get("protocol_fingerprint"),
        }
        gate_model = {
            "id": sequence.get("mistake_gate", {}).get("designated_model_condition"),
            "model": sequence.get("mistake_gate", {}).get("model"),
            "reasoning_effort": sequence.get("mistake_gate", {}).get("reasoning_effort"),
        }
        if binding != expected_binding or gate_model != authority["model_condition"]:
            raise ValueError(f"baseline replication authority has stale nested binding for {sequence.get('id')}")
    return authority


def load_lifecycle_v1_replication_authority(root: Path = ROOT) -> dict[str, Any]:
    """Strictly validate the owner-authorized two-lane Lifecycle V1 r1 baseline."""
    path = repository_authority_path(
        root,
        LIFECYCLE_V1_REPLICATION_AUTHORITY_REL,
        "Lifecycle V1 r1 baseline replication authorization",
    )
    try:
        authority = json.loads(path.read_text(), object_pairs_hook=_json_without_duplicate_keys)
        sequence_doc = json.loads(
            (root / "data/workflow-task-sequences.json").read_text(),
            object_pairs_hook=_json_without_duplicate_keys,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"Lifecycle V1 r1 replication authority is unreadable: {exc}") from exc
    active_sequences = [
        item
        for item in sequence_doc.get("sequences", [])
        if item.get("status") == "active" and item.get("task_family_generation") == "lifecycle-v1"
    ]
    expected_order = ["fastify-lifecycle-sequence-v1", "beets-lifecycle-sequence-v1"]
    records = authority.get("sequences")
    strict_header = (
        set(authority) == BASELINE_REPLICATION_TOP_LEVEL_KEYS
        and type(authority.get("schema_version")) is int
        and authority.get("schema_version") == 1
        and authority.get("campaign_id") == "lifecycle-v1-codex-sol-high-r1-20260802"
        and authority.get("authorized_by_owner_message_id") == "1533297158743265280"
        and authority.get("authorized_on") == "2026-08-02"
        and authority.get("paid_baseline_replication_authorized") is True
        and authority.get("authorized_replicate_indexes") == [1]
        and all(type(item) is int for item in authority.get("authorized_replicate_indexes", []))
        and authority.get("sequence_order") == expected_order
        and [item.get("id") for item in active_sequences] == expected_order
        and authority.get("serialization_required") is True
        and type(authority.get("allowed_paid_baseline_runs")) is int
        and authority.get("allowed_paid_baseline_runs") == 2
        and type(authority.get("allowed_model_turns")) is int
        and authority.get("allowed_model_turns") == 6
        and authority.get("model_condition") == BASELINE_REPLICATION_MODEL_CONDITION
        and authority.get("first_valid_sample_policy") is True
        and authority.get("rerun_after_attempt_receipt") is False
        and type(authority.get("provider_calls")) is int
        and authority.get("provider_calls") == 0
        and type(authority.get("provider_tokens")) is int
        and authority.get("provider_tokens") == 0
        and isinstance(authority.get("notes"), str)
        and bool(authority.get("notes"))
    )
    strict_records = (
        isinstance(records, list)
        and len(records) == len(active_sequences) == 2
        and all(isinstance(item, dict) and set(item) == BASELINE_REPLICATION_BINDING_KEYS for item in records)
        and [item.get("sequence_id") for item in records] == expected_order
    )
    if not strict_header or not strict_records:
        raise ValueError("Lifecycle V1 r1 replication authority has invalid authorization, scope, budget, model, or policy")
    assert isinstance(records, list)
    for sequence, binding in zip(active_sequences, records, strict=True):
        identity, protocol = current_baseline_v2_protocol(sequence, sequence["mistake_gate"], root)
        expected_binding = {
            "sequence_id": sequence.get("id"),
            "task_family_generation": "lifecycle-v1",
            "protocol_path": identity["path"],
            "protocol_sha256": identity["sha256"],
            "baseline_pool_fingerprint": protocol.get("baseline_pool", {}).get("protocol_fingerprint"),
        }
        gate_model = {
            "id": sequence.get("mistake_gate", {}).get("designated_model_condition"),
            "model": sequence.get("mistake_gate", {}).get("model"),
            "reasoning_effort": sequence.get("mistake_gate", {}).get("reasoning_effort"),
        }
        if binding != expected_binding or gate_model != authority["model_condition"]:
            raise ValueError(f"Lifecycle V1 r1 replication authority has stale nested binding for {sequence.get('id')}")
    return authority


def load_beets_r3_replacement_authority(root: Path = ROOT) -> dict[str, Any]:
    """Strictly validate the one-run owner-authorized Beets r3 replacement."""
    path = repository_authority_path(
        root,
        BEETS_R3_REPLACEMENT_AUTHORITY_REL,
        "Beets r3 replacement authorization",
    )
    try:
        authority = json.loads(path.read_text(), object_pairs_hook=_json_without_duplicate_keys)
        sequence_doc = json.loads(
            (root / "data/workflow-task-sequences.json").read_text(),
            object_pairs_hook=_json_without_duplicate_keys,
        )
        matches = [
            item for item in sequence_doc.get("sequences", [])
            if item.get("id") == "beets-lifecycle-sequence-v0"
        ]
        if len(matches) != 1:
            raise ValueError("Beets r3 replacement sequence is absent or duplicated")
        sequence = matches[0]
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"Beets r3 replacement authority is unreadable: {exc}") from exc
    records = authority.get("sequences")
    strict_header = (
        set(authority) == BASELINE_REPLICATION_TOP_LEVEL_KEYS
        and type(authority.get("schema_version")) is int
        and authority.get("schema_version") == 1
        and authority.get("campaign_id") == "current-low-complexity-beets-r3-replacement-20260728"
        and authority.get("authorized_by_owner_message_id") == "1531806010350633101"
        and authority.get("authorized_on") == "2026-07-28"
        and authority.get("paid_baseline_replication_authorized") is True
        and authority.get("authorized_replicate_indexes") == [3]
        and all(type(item) is int for item in authority.get("authorized_replicate_indexes", []))
        and authority.get("sequence_order") == ["beets-lifecycle-sequence-v0"]
        and authority.get("serialization_required") is True
        and type(authority.get("allowed_paid_baseline_runs")) is int
        and authority.get("allowed_paid_baseline_runs") == 1
        and type(authority.get("allowed_model_turns")) is int
        and authority.get("allowed_model_turns") == 3
        and authority.get("model_condition") == BASELINE_REPLICATION_MODEL_CONDITION
        and authority.get("first_valid_sample_policy") is True
        and authority.get("rerun_after_attempt_receipt") is False
        and type(authority.get("provider_calls")) is int
        and authority.get("provider_calls") == 0
        and type(authority.get("provider_tokens")) is int
        and authority.get("provider_tokens") == 0
        and isinstance(authority.get("notes"), str)
        and bool(authority.get("notes"))
    )
    strict_records = (
        sequence.get("status") == "active"
        and isinstance(records, list)
        and len(records) == 1
        and isinstance(records[0], dict)
        and set(records[0]) == BASELINE_REPLICATION_BINDING_KEYS
        and records[0].get("sequence_id") == sequence.get("id")
    )
    if not strict_header or not strict_records:
        raise ValueError("Beets r3 replacement authority has invalid authorization, scope, budget, model, or policy")
    identity, protocol = current_baseline_v2_protocol(sequence, sequence["mistake_gate"], root)
    expected_binding = {
        "sequence_id": sequence.get("id"),
        "task_family_generation": sequence.get("task_family_generation"),
        "protocol_path": identity["path"],
        "protocol_sha256": identity["sha256"],
        "baseline_pool_fingerprint": protocol.get("baseline_pool", {}).get("protocol_fingerprint"),
    }
    gate_model = {
        "id": sequence.get("mistake_gate", {}).get("designated_model_condition"),
        "model": sequence.get("mistake_gate", {}).get("model"),
        "reasoning_effort": sequence.get("mistake_gate", {}).get("reasoning_effort"),
    }
    if records[0] != expected_binding or gate_model != authority["model_condition"]:
        raise ValueError("Beets r3 replacement authority has a stale nested binding")
    return authority


def baseline_replication_authority(
    seq: dict[str, Any],
    replicate_index: int,
    root: Path = ROOT,
) -> dict[str, Any]:
    if seq.get("task_family_generation") == "lifecycle-v1":
        if replicate_index != 1:
            raise ValueError(f"Lifecycle V1 replicate {replicate_index} requires explicit authority")
        return load_lifecycle_v1_replication_authority(root)
    if replicate_index == 3:
        if seq.get("id") != "beets-lifecycle-sequence-v0":
            raise ValueError("r3 replacement authority covers only beets-lifecycle-sequence-v0")
        return load_beets_r3_replacement_authority(root)
    return load_current_baseline_replication_authority(root)


def baseline_replication_binding(
    seq: dict[str, Any],
    replicate_index: int,
    root: Path = ROOT,
) -> tuple[dict[str, Any], Path]:
    """Validate one explicitly authorized current-panel replicate identity."""
    authority = baseline_replication_authority(seq, replicate_index, root)
    if type(replicate_index) is not int or replicate_index not in authority["authorized_replicate_indexes"]:
        raise ValueError("baseline replication is not authorized for this replicate index")
    matches = [
        item for item in authority.get("sequences", [])
        if isinstance(item, dict) and item.get("sequence_id") == seq.get("id")
    ]
    if len(matches) != 1:
        raise ValueError(f"baseline replication authority lacks one binding for {seq.get('id')}")
    binding = matches[0]
    identity, protocol = current_baseline_v2_protocol(seq, seq["mistake_gate"], root)
    expected = {
        "task_family_generation": seq.get("task_family_generation"),
        "protocol_path": identity["path"],
        "protocol_sha256": identity["sha256"],
        "baseline_pool_fingerprint": protocol.get("baseline_pool", {}).get("protocol_fingerprint"),
    }
    if any(binding.get(key) != value for key, value in expected.items()):
        raise ValueError(f"baseline replication authority binding is stale for {seq.get('id')}")
    gate_model = {
        "id": seq.get("mistake_gate", {}).get("designated_model_condition"),
        "model": seq.get("mistake_gate", {}).get("model"),
        "reasoning_effort": seq.get("mistake_gate", {}).get("reasoning_effort"),
    }
    if gate_model != authority["model_condition"]:
        raise ValueError(f"baseline replication model binding is stale for {seq.get('id')}")
    if seq.get("task_family_generation") == "lifecycle-v1":
        slug = str(seq.get("id", "")).removesuffix("-lifecycle-sequence-v1")
        receipt_rel = f"{LIFECYCLE_V1_REPLICATION_ATTEMPT_DIR}/{slug}-r{replicate_index}.json"
    elif replicate_index == 3:
        receipt_rel = BEETS_R3_REPLACEMENT_ATTEMPT_REL
    else:
        slug = str(seq.get("id", "")).removesuffix("-lifecycle-sequence-v0")
        receipt_rel = f"sources/evaluations/audits/current-low-complexity-baseline-r1-r2-attempts/{slug}-r{replicate_index}.json"
    return binding, repository_authority_path(root, receipt_rel, "baseline replication attempt receipt")


def baseline_attempt_receipt_path(
    seq: dict[str, Any],
    replicate_index: int,
    root: Path = ROOT,
) -> Path:
    if replicate_index == 0:
        return baseline_pilot_attempt_receipt_path(seq, root)
    return baseline_replication_binding(seq, replicate_index, root)[1]


def require_zero_mistake_pilot_replicate(
    seq: dict[str, Any],
    profile_id: str,
    replicate_index: int,
    *,
    prepare_only: bool,
) -> None:
    """Bind paid current-panel baselines to an explicitly authorized replicate."""
    if prepare_only or profile_id != "baseline-bare-codex":
        return
    if seq.get("task_family_generation") in {"baseline-v3", "baseline-v4", "lifecycle-v1"}:
        if type(replicate_index) is not int:
            raise ValueError("Baseline V3/V4 paid baselines require an integer replicate_index")
        if replicate_index == 0:
            return
        authority = baseline_replication_authority(seq, replicate_index, ROOT)
        baseline_replication_binding(seq, replicate_index, ROOT)
        selected_model_condition = {
            "id": DEFAULT_WORKFLOW_MODEL_CONDITION_ID,
            "model": DEFAULT_WORKFLOW_MODEL,
            "reasoning_effort": DEFAULT_WORKFLOW_REASONING_EFFORT,
        }
        if selected_model_condition != authority["model_condition"]:
            raise ValueError("baseline replication launch model does not match the strict authorization")


def reserve_baseline_pilot_attempt(
    seq: dict[str, Any],
    *,
    root: Path = ROOT,
    orchestrator: str,
    replicate_index: int,
) -> dict[str, Any]:
    """Atomically occupy one paid pilot identity before any provider task starts."""
    require_zero_mistake_pilot_replicate(
        seq,
        "baseline-bare-codex",
        replicate_index,
        prepare_only=False,
    )
    identity, protocol = current_baseline_v2_protocol(seq, seq["mistake_gate"], root)
    receipt = {
        "schema_version": 1,
        "attempt_status": "reserved-before-provider-task",
        "task_family_generation": seq.get("task_family_generation"),
        "sequence_id": seq.get("id"),
        "replicate_index": replicate_index,
        "profile_id": "baseline-bare-codex",
        "model_condition_id": seq["mistake_gate"].get("designated_model_condition"),
        "model": seq["mistake_gate"].get("model"),
        "reasoning_effort": seq["mistake_gate"].get("reasoning_effort"),
        "orchestrator": orchestrator,
        "reserved_at": dt.datetime.now(dt.UTC).isoformat(),
        "frozen_protocol": identity,
        "baseline_pool_fingerprint": protocol.get("baseline_pool", {}).get("protocol_fingerprint"),
        "provider_result": None,
        "immutable_identity_receipt": True,
    }
    atomic_create_json(baseline_attempt_receipt_path(seq, replicate_index, root), receipt)
    return receipt


def baseline_v2_pilot_run_gate(
    seq: dict[str, Any],
    root: Path = ROOT,
    replicate_index: int = 0,
) -> tuple[bool, str]:
    """Permit one provider run per declared identity; never pass-select reruns."""
    generation = seq.get("task_family_generation")
    if generation not in {"baseline-v2", "baseline-v3", "baseline-v4", "lifecycle-v1"}:
        return False, f"unsupported baseline task family generation requires explicit authority: {generation!r}"
    label = str(generation).replace("baseline-v", "Baseline V")
    gate = seq.get("mistake_gate")
    audit_rel = gate.get("pilot_audit_path") if isinstance(gate, dict) else None
    if generation in {"baseline-v3", "baseline-v4", "lifecycle-v1"} and replicate_index != 0:
        try:
            _binding, receipt_path = baseline_replication_binding(seq, replicate_index, root)
        except ValueError as exc:
            return False, str(exc)
        if receipt_path.exists():
            return False, f"paid baseline replication identity is occupied by immutable attempt receipt: {receipt_path.relative_to(root)}"
        return True, f"current-panel r{replicate_index} baseline is explicitly authorized and unoccupied"
    if generation in {"baseline-v3", "baseline-v4", "lifecycle-v1"}:
        try:
            receipt_path = baseline_pilot_attempt_receipt_path(seq, root)
        except ValueError as exc:
            return False, str(exc)
        if receipt_path.exists():
            return False, f"paid pilot identity is occupied by immutable attempt receipt: {receipt_path.relative_to(root)}"
    if generation in {"baseline-v4", "lifecycle-v1"}:
        authorization_rel = gate.get("pilot_authorization_path") if isinstance(gate, dict) else None
        if not isinstance(authorization_rel, str) or not authorization_rel:
            return False, f"{label} paid pilot is not authorized: missing pilot_authorization_path"
        try:
            authorization_path = repository_authority_path(
                root,
                authorization_rel,
                f"{label} pilot authorization",
            )
            authorization = json.loads(authorization_path.read_text())
        except (OSError, ValueError) as exc:
            return False, f"{label} paid pilot is not authorized: authorization authority is unreadable: {exc}"
        expected_authorization_schema = 2 if generation == "lifecycle-v1" else 1
        if (
            type(authorization.get("schema_version")) is not int
            or authorization.get("schema_version") != expected_authorization_schema
            or authorization.get("generation") != generation
            or authorization.get("paid_pilot_authorized") is not True
        ):
            return False, f"{label} paid pilot is not authorized by {authorization_rel}"
        if generation == "lifecycle-v1":
            if authorization.get("pilot_authorization") != LIFECYCLE_V1_PILOT_AUTHORIZATION:
                return False, f"{label} paid pilot authorization has an invalid Lifecycle V1 scope"
            pilot_attempts = authorization.get("pilot_attempts")
            if pilot_attempts is not None:
                if not isinstance(pilot_attempts, dict):
                    return False, f"{label} paid pilot attempt ledger is malformed"
                attempt = pilot_attempts.get(str(seq.get("id")))
                if attempt is not None:
                    if not isinstance(attempt, dict) or attempt.get("status") not in {"accepted", "rejected"}:
                        return False, f"{label} paid pilot attempt ledger entry is malformed"
                    return False, f"{label} paid pilot r{replicate_index} was already consumed as {attempt['status']}"

    if not isinstance(audit_rel, str) or not audit_rel:
        return False, f"missing {label} pilot_audit_path"
    try:
        audit_path = repository_authority_path(root, audit_rel, f"{label} pilot audit")
    except ValueError as exc:
        return False, str(exc)
    if not audit_path.exists():
        return True, f"no prior {label} pilot attempt is recorded"
    try:
        audit = json.loads(audit_path.read_text())
    except (OSError, ValueError) as exc:
        return False, f"existing {label} pilot audit is unreadable: {exc}"
    entries = audit.get("sequences")
    if (
        type(audit.get("schema_version")) is not int
        or audit.get("schema_version") != 1
        or audit.get("task_family_generation") != generation
        or not isinstance(entries, list)
        or not all(isinstance(entry, dict) for entry in entries)
    ):
        return False, f"existing {label} pilot audit is invalid"
    matching = [entry for entry in entries if entry.get("sequence_id") == seq.get("id")]
    if not matching:
        return True, f"no prior {label} pilot attempt is recorded for {seq.get('id')}"
    return False, (
        f"{label} pilot identity is occupied by audit status={audit.get('status', 'unknown')!r} "
        f"at {audit_rel}; preserve it and mint a simpler generation/audit identity before any new provider run"
    )


def baseline_v2_treatment_gate(seq: dict[str, Any], root: Path = ROOT) -> tuple[bool, str]:
    """Fail closed until an independently audited zero-incident baseline pilot exists."""
    generation = seq.get("task_family_generation")
    if generation not in {"baseline-v2", "baseline-v3", "baseline-v4", "lifecycle-v1"}:
        return True, "not a zero-mistake baseline sequence"
    gate = seq.get("mistake_gate")
    if not isinstance(gate, dict):
        return False, f"missing {generation} mistake gate"
    audit_rel = gate.get("pilot_audit_path")
    if not isinstance(audit_rel, str) or not audit_rel:
        return False, "missing pilot_audit_path"
    try:
        audit_path = repository_authority_path(root, audit_rel, "pilot audit")
    except ValueError as exc:
        return False, str(exc)
    if not audit_path.is_file():
        return False, f"pilot audit is absent: {audit_rel}"
    try:
        audit = json.loads(audit_path.read_text())
    except (OSError, ValueError) as exc:
        return False, f"pilot audit is unreadable: {exc}"
    if (
        type(audit.get("schema_version")) is not int
        or audit.get("schema_version") != 1
        or audit.get("task_family_generation") != generation
    ):
        return False, "pilot audit schema or task-family generation is invalid"
    entries = [
        entry for entry in audit.get("sequences", [])
        if isinstance(entry, dict) and entry.get("sequence_id") == seq.get("id")
    ]
    if len(entries) != 1:
        return False, f"pilot audit must contain exactly one entry for {seq.get('id')}"
    entry = entries[0]
    if generation == "lifecycle-v1":
        if entry.get("passed") is not True or entry.get("compile_passed") is not True:
            return False, "compile-only pilot did not pass every affected-component compile verifier"
    else:
        if entry.get("passed") is not True or entry.get("trajectory_review_complete") is not True:
            return False, "pilot trajectory review is incomplete or did not pass"
        if entry.get("independent_source_review_passed") is not True:
            return False, "independent source review did not pass"
        if entry.get("reviewer_role") != "independent":
            return False, "pilot audit reviewer is not independent"
    expected_condition = {
        "id": gate.get("designated_model_condition"),
        "model": gate.get("model"),
        "reasoning_effort": gate.get("reasoning_effort"),
    }
    if entry.get("model_condition") != expected_condition:
        return False, "pilot audit model condition does not match the designated gate tuple"
    if generation != "lifecycle-v1":
        invalid_counts = {
            field: entry.get(field)
            for field in PILOT_ZERO_COUNT_FIELDS
            if type(entry.get(field)) is not int or entry.get(field) != 0
        }
        if invalid_counts:
            return False, f"pilot audit has missing, non-integer, or nonzero incident counts: {invalid_counts}"
    session_id = entry.get("baseline_session_id")
    if not isinstance(session_id, str) or not session_id:
        return False, "pilot audit is missing baseline_session_id"
    registry_path = root / "data/workflow-sessions.json"
    try:
        registry = json.loads(registry_path.read_text())
    except (OSError, ValueError) as exc:
        return False, f"workflow session registry is unreadable: {exc}"
    registry_sessions = registry.get("sessions")
    if not isinstance(registry_sessions, list) or not all(isinstance(item, dict) for item in registry_sessions):
        return False, "workflow session registry has invalid sessions"
    sessions = [session for session in registry_sessions if session.get("session_id") == session_id]
    if len(sessions) != 1:
        return False, "pilot audit baseline session is absent or ambiguous"
    session = sessions[0]
    interpretation = session.get("interpretation", {})
    usage = session.get("cumulative_token_usage", {})
    software_quality = session.get("software_quality", {})
    selected_execution = session.get("selected_execution", {})
    selected_descriptor = selected_execution.get("descriptor", {})
    agent = session.get("agent", {})
    per_task_results = session.get("per_task_results")
    ordered_tasks = sorted(seq.get("tasks", []), key=lambda item: int(item["order"]))
    expected_task_results = [(str(task["id"]), int(task["order"])) for task in ordered_tasks]
    task_identity_complete = (
        isinstance(per_task_results, list)
        and all(isinstance(item, dict) for item in per_task_results)
        and all(type(item.get("order")) is int for item in per_task_results)
        and [(str(item.get("task_id")), item.get("order")) for item in per_task_results] == expected_task_results
    )
    if (
        type(session.get("schema_version")) is not int
        or session.get("schema_version") != 2
        or session.get("status") != "completed"
        or session.get("session_role") != "baseline"
        or type(session.get("replicate_index")) is not int
        or session.get("replicate_index") != 0
        or session.get("task_sequence", {}).get("sequence_id") != seq.get("id")
        or session.get("profile", {}).get("profile_id") != "baseline-bare-codex"
        or selected_descriptor.get("execution_role") != "baseline"
        or selected_descriptor.get("selected_profile", {}).get("profile_id") != "baseline-bare-codex"
        or not isinstance(agent, dict)
        or agent.get("runtime_id") != "codex-cli"
        or agent.get("provider") != "openai"
        or agent.get("model_condition_id") != gate.get("designated_model_condition")
        or agent.get("model") != gate.get("model")
        or agent.get("reasoning_effort") != gate.get("reasoning_effort")
        or interpretation.get("accepted_for_execution") is not True
        or interpretation.get("operationally_completed") is not True
        or interpretation.get("evaluation_validity") != "valid"
        or interpretation.get("accepted_for_objective") is not True
        or interpretation.get("primary_objective_hard_baseline") is not True
        or interpretation.get("usable_for_primary_objective_token_comparison") is not True
        or not pilot_provider_usage_valid(usage)
        or not isinstance(software_quality, dict)
        or type(software_quality.get("tasks_attempted")) is not int
        or software_quality.get("tasks_attempted") != len(ordered_tasks)
        or type(software_quality.get("tasks_passed")) is not int
        or software_quality.get("tasks_passed") != len(ordered_tasks)
        or software_quality.get("final_verifier_passed") is not True
        or software_quality.get("functional_verifier_passed") is not True
        or (generation == "lifecycle-v1" and software_quality.get("project_compile_passed") is not True)
        or not isinstance(per_task_results, list)
        or len(per_task_results) != len(ordered_tasks)
        or not task_identity_complete
        or any(
            not isinstance(item, dict)
            or item.get("agent_attempted") is not True
            or type(item.get("codex_exit_code")) is not int
            or item.get("codex_exit_code") != 0
            or item.get("controller_verification") != "passed"
            or type(item.get("verifier_exit_code")) is not int
            or item.get("verifier_exit_code") != 0
            or item.get("verifier_passed") is not True
            or item.get("accepted") is not True
            or type(item.get("operational_retry_count")) is not int
            or item.get("operational_retry_count") != 0
            for item in per_task_results
        )
        or reviewed_session_reuse_state(session, root) != "reusable"
        or not pilot_session_artifacts_valid(session, root)
    ):
        return False, "pilot audit session is not the first operationally valid provider-backed baseline for this sequence"
    protocol = entry.get("frozen_protocol")
    if not isinstance(protocol, dict) or protocol != session.get("frozen_protocol"):
        return False, "pilot audit protocol binding does not match the baseline session"
    try:
        current_protocol, protocol_document = current_baseline_v2_protocol(seq, gate, root)
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        return False, f"pilot audit protocol cannot be matched to the current baseline contract: {exc}"
    expected_binding = {
        key: current_protocol[key] for key in ("protocol_id", "path", "sha256")
    }
    if protocol != expected_binding or session.get("frozen_protocol") != expected_binding:
        return False, "pilot audit does not bind the exact current designated baseline protocol"
    if entry.get("qualification_sha256") != current_protocol["qualification_sha256"]:
        return False, "pilot audit qualification hash does not match the current protocol"
    if selected_execution != protocol_document.get("selected_execution"):
        return False, "baseline session selected execution does not match the current protocol"
    if selected_execution.get("descriptor_sha256") != current_protocol["selected_execution_sha256"]:
        return False, "baseline session selected-execution hash does not match the current protocol"
    runtime = selected_descriptor.get("runtime", {}) if isinstance(selected_descriptor, dict) else {}
    identity_errors: list[str] = []
    repository_validation.validate_docker_identity(
        session.get("docker_image_identity"), runtime.get("docker_image_identity"), session_id, identity_errors
    )
    repository_validation.validate_tool_adapter_identity(
        session.get("tool_adapter_identity"), selected_descriptor.get("tool_adapter"), "baseline-bare-codex", session_id, identity_errors
    )
    if identity_errors:
        return False, "baseline session runtime identity does not match the current selected execution"
    if (
        entry.get("baseline_pool_fingerprint") != current_protocol["baseline_pool_fingerprint"]
        or session.get("baseline_pool", {}).get("protocol_fingerprint") != current_protocol["baseline_pool_fingerprint"]
    ):
        return False, "pilot audit does not bind the current baseline-pool contract"
    agent_condition = selected_descriptor.get("agent_condition", {})
    if {
        "id": agent_condition.get("model_condition_id"),
        "model": agent_condition.get("model"),
        "reasoning_effort": agent_condition.get("reasoning_effort"),
    } != expected_condition:
        return False, "baseline session model condition does not match the designated gate tuple"
    slot_candidates = [
        item
        for item in registry_sessions
        if isinstance(item, dict)
        and item.get("task_sequence", {}).get("sequence_id") == seq.get("id")
        and item.get("profile", {}).get("profile_id") == "baseline-bare-codex"
        and item.get("frozen_protocol") == expected_binding
        and item.get("baseline_pool", {}).get("protocol_fingerprint") == current_protocol["baseline_pool_fingerprint"]
        and any(
            isinstance(result, dict) and result.get("agent_attempted") is True
            for result in item.get("per_task_results", [])
        )
    ]
    if any(type(item.get("replicate_index")) is not int for item in slot_candidates):
        return False, f"current {generation} slot registry contains malformed replicate_index evidence"
    slot_sessions = [item for item in slot_candidates if item.get("replicate_index") == 0]
    if len(slot_sessions) != 1 or slot_sessions[0].get("session_id") != session_id:
        return False, f"current {generation} r0 slot is absent, ambiguous, or was rerun"
    if generation == "lifecycle-v1":
        return True, "audited compile-passing lifecycle-v1 pilot"
    return True, f"independently audited zero-incident {generation} pilot"


def require_baseline_v2_treatment_gate(seq: dict[str, Any], root: Path = ROOT) -> None:
    passed, reason = baseline_v2_treatment_gate(seq, root)
    if not passed:
        raise ValueError(f"treatments are blocked for {seq.get('id')}: {reason}")


def default_study_id(profile_id: str) -> str:
    if PROFILE_META[profile_id]["objective_scope"] == "stack_effectiveness":
        return "phase-3-lifecycle-v0-stack-screen"
    return "phase-2-sequential-workflow-v1"


def path_identity(path_text: str) -> dict[str, Any]:
    path = Path(path_text)
    identity: dict[str, Any] = {"path": path_text, "exists": path.exists()}
    if path.is_file():
        identity.update({"kind": "file", "sha256": _protocol_file_hash(path)})
    elif path.is_dir():
        identity["kind"] = "directory"
        git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, text=True, capture_output=True, check=False)
        if git_head.returncode == 0:
            identity["git_head"] = git_head.stdout.strip()
        package = path / "package.json"
        if package.is_file():
            identity["package_json_sha256"] = _protocol_file_hash(package)
    return identity


def docker_image_identity(image: str) -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "image", "inspect", image],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"docker image inspect failed for {image}: {proc.stderr.strip() or proc.stdout.strip()}")
    inspected = json.loads(proc.stdout)
    if not inspected:
        raise RuntimeError(f"docker image inspect returned no records for {image}")
    item = inspected[0]
    image_id = str(item.get("Id") or "")
    if not image_id.startswith("sha256:"):
        raise RuntimeError(f"docker image {image} has no immutable sha256 image ID")
    return {
        "image_ref": image,
        "image_id": image_id,
        "repo_digests": sorted(str(value) for value in item.get("RepoDigests") or []),
        "repo_tags": sorted(str(value) for value in item.get("RepoTags") or []),
    }


def _tool_command_spec(cfg: dict[str, Any]) -> dict[str, Any] | None:
    if cfg.get("mcp_command"):
        return {"kind": "mcp_command", "command": [str(cfg["mcp_command"]), *[str(arg) for arg in cfg.get("mcp_args", [])]]}
    wrapper = cfg.get("codex_wrapper") or {}
    if wrapper.get("command"):
        return {"kind": "codex_wrapper", "command": [str(wrapper["command"]), *[str(arg) for arg in wrapper.get("args", [])]]}
    if cfg.get("preflight_command"):
        return {"kind": "preflight_command", "command": [str(arg) for arg in cfg["preflight_command"]]}
    if cfg.get("executable") and cfg.get("host_integration"):
        return {"kind": "executable", "command": [str(cfg["executable"])]}
    warmup = cfg.get("warmup") or {}
    if warmup.get("command"):
        return {"kind": "warmup_command", "command": [str(arg) for arg in warmup["command"]]}
    if cfg.get("executable"):
        return {"kind": "executable", "command": [str(cfg["executable"])]}
    return None


def _lane_path(cfg: dict[str, Any], root: Path = ROOT) -> str:
    path_entries = [
        "/opt/data/bin",
        str(fixture.CODEX_HOST_EXECUTABLE.parent),
        "/opt/data/opt/go/bin",
        "/opt/data/opt/uv",
        str(fixture.NODE_TOOLCHAIN_ROOT / "bin"),
    ]
    identity_home = root / ".identity-codex-home"
    for entry in cfg.get("path_entries", []):
        rendered = str(entry).format(
            codex_home=identity_home,
            home=identity_home / "home",
            tool_data_dir=fixture.tool_data_dir(identity_home, cfg),
        )
        if rendered not in path_entries:
            path_entries.insert(1, rendered)
    path_entries.extend(["/usr/local/sbin", "/usr/local/bin", "/usr/sbin", "/usr/bin", "/sbin", "/bin"])
    return os.pathsep.join(path_entries)


def _version_output(path: Path, *, environment_path: str) -> dict[str, Any]:
    env = os.environ.copy()
    env["PATH"] = environment_path
    try:
        proc = subprocess.run(
            [str(path), "--version"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except Exception as exc:
        return {
            "command": [str(path), "--version"],
            "environment_path": environment_path,
            "captured": False,
            "error": type(exc).__name__,
        }
    output = (proc.stdout + proc.stderr).strip()
    return {
        "command": [str(path), "--version"],
        "environment_path": environment_path,
        "captured": proc.returncode == 0 and bool(output),
        "exit_code": proc.returncode,
        "output": output[:2000],
        "truncated": len(output) > 2000,
    }


def executable_identity(command: list[str], cfg: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    if not command:
        raise ValueError("tool command is empty")
    token = command[0]
    if "{" in token and cfg.get("host_integration"):
        return {
            "kind": "generated-by-host-integration",
            "command_template": token,
            "install_commands": cfg["host_integration"].get("install_commands", []),
            "install_contract_sha256": _json_hash(cfg["host_integration"]),
        }
    explicit = Path(token)
    lane_path = _lane_path(cfg, root)
    resolved_text = str(explicit) if explicit.is_absolute() else shutil.which(token, path=lane_path)
    if not resolved_text and not explicit.is_absolute():
        for entry in lane_path.split(os.pathsep):
            candidate = Path(entry) / token
            if candidate.is_file():
                resolved_text = str(candidate)
                break
    if not resolved_text:
        raise FileNotFoundError(f"tool executable is not resolvable in lane PATH: {token}")
    resolved = Path(resolved_text)
    if not resolved.is_file():
        raise FileNotFoundError(f"tool executable is not a file: {resolved}")
    real = resolved.resolve()
    if not os.access(real, os.X_OK):
        try:
            real.chmod(real.stat().st_mode | 0o111)
        except OSError as exc:
            raise PermissionError(f"tool executable is not executable: {real}") from exc
    st = real.stat()
    version = _version_output(real, environment_path=_lane_path(cfg, root))
    environment_path = version.get("environment_path")
    if isinstance(environment_path, str):
        version["environment_path"] = environment_path.replace(str(root.resolve()), "{repository_root}")
    return {
        "executable_token": token,
        "resolved_path": str(resolved),
        "realpath": str(real),
        "sha256": _protocol_file_hash(real),
        "metadata": {
            "size": st.st_size,
            "mode": stat.filemode(st.st_mode),
            "uid": st.st_uid,
            "gid": st.st_gid,
            "mtime_ns": st.st_mtime_ns,
        },
        "version": version,
    }


def tool_adapter_identity(profile_id: str, root: Path = ROOT) -> dict[str, Any]:
    meta = PROFILE_META[profile_id]
    tool_id = meta.get("tool_id")
    if not tool_id:
        return {"tool_id": None, "tool_manifest": "baseline-native-codex-tools", "tool_config": None, "binary_identity": None, "source_identity": []}
    cfg = fixture.TOOL_CONFIGS[str(tool_id)]
    command_spec = _tool_command_spec(cfg)
    if command_spec is None:
        raise ValueError(f"treatment tool {tool_id} has no executable command to identify")
    source_paths = sorted({str(path) for path in cfg.get("mounts", []) if str(path)})
    source_identity = []
    for path_text in source_paths:
        rendered_path = path_text.format(repository_root=root)
        identity = path_identity(rendered_path)
        if "{repository_root}" in path_text:
            identity["path"] = path_text
        source_identity.append(identity)
    manifest_identity = str(cfg.get("tool_manifest_identity", "legacy"))
    if profile_id in FIXED_CURRENT_TOOL_MANIFEST_SHA256:
        manifest_sha256 = FIXED_CURRENT_TOOL_MANIFEST_SHA256[profile_id]
    elif manifest_identity == "current-file-v1":
        manifest_sha256 = _protocol_file_hash(root / "scripts/run_codex_fixture_evaluation.py")
    elif manifest_identity.startswith("fixed-sha256:"):
        manifest_sha256 = manifest_identity.removeprefix("fixed-sha256:")
    else:
        manifest_sha256 = LEGACY_TOOL_MANIFEST_SHA256
    return {
        "tool_id": tool_id,
        "tool_manifest": "scripts/run_codex_fixture_evaluation.py:TOOL_CONFIGS",
        "tool_manifest_sha256": manifest_sha256,
        "tool_config": cfg,
        "tool_config_sha256": _json_hash(cfg),
        "tool_state": meta["tool_state"],
        "tool_use_policy": meta["tool_use_policy"],
        "command_identity": command_spec,
        "binary_identity": executable_identity(command_spec["command"], cfg, root),
        "source_identity": source_identity,
    }


def dependency_lock_identities(seq: dict[str, Any], root: Path = ROOT) -> list[dict[str, Any]]:
    locks = []
    for item in seq.get("initial_snapshot", {}).get("dependency_lockfiles", []):
        path_text = str(item.get("path", ""))
        locks.append({
            "path": path_text,
            "snapshot_sha256": item.get("sha256"),
            "current_fixture_sha256": _protocol_file_hash(root / path_text) if (root / path_text).is_file() else None,
        })
    return locks


def execution_condition_descriptor(
    seq: dict[str, Any],
    profile_id: str,
    *,
    timeout_seconds_per_task: int = 3600,
    docker_image: str = DEFAULT_DOCKER_IMAGE,
    root: Path = ROOT,
) -> dict[str, Any]:
    meta = PROFILE_META[profile_id]
    profile_entry = profile_registry_entry(profile_id, root)
    role = meta["session_role"]
    baseline_fingerprint = baseline_protocol_fingerprint(seq, root)
    tool_adapter = tool_adapter_identity(profile_id, root)
    descriptor = {
        "version": "execution-condition-v1",
        "sequence_id": seq["id"],
        "execution_role": role,
        "selected_profile": {
            "profile_id": profile_id,
            "profile_type": meta["profile_type"],
            "component_ids": meta["component_ids"],
            "enabled_surfaces": meta["enabled_surfaces"],
            "disabled_overlaps": meta["disabled_overlaps"],
            "registry_entry_sha256": _json_hash(profile_entry),
            "registry_entry": profile_entry,
        },
        "model_facing_prompts": model_facing_prompt_descriptor(seq, profile_id, root),
        "tool_adapter": tool_adapter,
        "runtime": {
            "docker_image": docker_image,
            "docker_image_identity": docker_image_identity(docker_image),
            "dockerfile_path": str(fixture.DEFAULT_DOCKERFILE.relative_to(root)),
            "dockerfile_sha256": _protocol_file_hash(fixture.DEFAULT_DOCKERFILE),
            "fixture_runner_path": "scripts/run_codex_fixture_evaluation.py",
            "fixture_runner_sha256": tool_adapter.get("tool_manifest_sha256", LEGACY_TOOL_MANIFEST_SHA256),
            "mcp_probe_path": "scripts/probe_mcp_stdio.py",
            "mcp_probe_sha256": _protocol_file_hash(root / "scripts/probe_mcp_stdio.py"),
            "codex_entrypoint_path": "sources/evaluations/fixtures/container/codex-entrypoint.sh",
            "codex_entrypoint_sha256": _protocol_file_hash(root / "sources/evaluations/fixtures/container/codex-entrypoint.sh"),
            "timeout_seconds_per_task": timeout_seconds_per_task,
            "network_isolation": {
                "provider_access": True,
                "model_shell_network_access": False,
                "model_shell_enforcement": "seccomp denies AF_INET and AF_INET6 socket creation for the shell process and descendants",
                "codex_web_search": "disabled",
                "external_retrieval_audit": "fail-closed",
            },
            "isolation_policy": "fresh lane-specific Codex home/tool data; provider-only network with model shell and Codex web search disabled; sequential one-task prompt delivery; controller seed/verifier scripts excluded while declared model-visible acceptance tests are retained",
        },
        "dependencies": {
            "command": PROJECT_META[seq["fixture_id"]]["dependency_command"],
            "command_sha256": hashlib.sha256(PROJECT_META[seq["fixture_id"]]["dependency_command"].encode()).hexdigest(),
            "lockfiles": dependency_lock_identities(seq, root),
        },
        "agent_condition": {
            "runtime_id": "codex-cli",
            "provider": "openai",
            "model": DEFAULT_WORKFLOW_MODEL,
            "model_condition_id": DEFAULT_WORKFLOW_MODEL_CONDITION_ID,
            "reasoning_effort": DEFAULT_WORKFLOW_REASONING_EFFORT,
            "codex_version_condition": "captured-at-run-and-bound-to-record",
        },
        "isolation": {
            "prompt_delivery": "sequential-one-task-at-a-time",
            "seed_delivery_mode": "preseeded-composite",
            "future_tasks_visible": False,
            "future_seed_regressions_visible": True,
            "controller_verification": "final-only",
            "controller_verifier_scripts_and_canonical_copies_model_visible": False,
            "model_visible_acceptance_asset_paths": sequence_model_visible_acceptance_paths(seq),
            "model_concealed_paths": sequence_concealed_paths(seq),
        },
        "baseline_pool_reference": {
            "protocol_version": BASELINE_POOL_PROTOCOL_VERSION,
            "protocol_fingerprint": baseline_fingerprint,
            "comparison_policy": "paired baseline and treatment must share this baseline pool fingerprint and replicate",
        },
    }
    runtime_id = profile_runtime_id(profile_id, root)
    if runtime_id != "codex-cli":
        descriptor["agent_condition"] = {
            "runtime_id": runtime_id,
            "provider": "openai",
            "model": DEFAULT_WORKFLOW_MODEL,
            "model_condition_id": DEFAULT_WORKFLOW_MODEL_CONDITION_ID,
            "reasoning_effort": DEFAULT_WORKFLOW_REASONING_EFFORT,
            "runtime_version_condition": "captured-at-run-and-bound-to-record",
        }
        descriptor["runtime"]["network_isolation"] = {
            "provider_access": True,
            "model_shell_network_access": False,
            "model_shell_enforcement": "seccomp denies AF_INET and AF_INET6 socket creation for the shell process and descendants",
            "agent_web_tools": "disabled-by-permission",
            "external_retrieval_audit": "fail-closed",
        }
        if runtime_id == "opencode-cli":
            descriptor["runtime"].update({
                "workflow_controller_path": "scripts/run_codex_workflow_evaluation.py",
                "workflow_controller_sha256": _protocol_file_hash(root / "scripts/run_codex_workflow_evaluation.py"),
                "matrix_controller_path": "scripts/run_sequential_workflow_matrix.py",
                "matrix_controller_sha256": _protocol_file_hash(root / "scripts/run_sequential_workflow_matrix.py"),
            })
        acceptance_materialization = (
            "controller-only affected-component compile commands retained; no acceptance-test assets injected; agent prompts carry normal software objectives"
            if seq.get("task_family_generation") == "lifecycle-v1"
            else "declared model-visible acceptance tests retained"
        )
        descriptor["runtime"]["isolation_policy"] = (
            "fresh lane-specific agent home/XDG state; provider-only network with model shell and agent web tools disabled; "
            f"sequential one-task prompt delivery; controller seed/verifier scripts excluded while {acceptance_materialization}"
        )
    return descriptor


def sequence_model_visible_acceptance_paths(seq: dict[str, Any]) -> list[str]:
    paths: set[str] = set()
    for task in seq.get("tasks", []):
        for path in task.get("model_visible_acceptance_asset_paths", []):
            paths.add(str(path))
    return sorted(paths)


def sequence_concealed_paths(seq: dict[str, Any]) -> list[str]:
    paths: set[str] = set()
    for task in seq.get("tasks", []):
        for path in task.get("model_concealed_paths", []):
            paths.add(str(path))
    return sorted(paths)


def expected_task_concealed_paths(task: dict[str, Any]) -> list[str]:
    expected: set[str] = set()
    expected.update(str(path) for path in task.get("upstream_test_paths", []))
    expected.update(str(path) for path in task.get("compatibility_rebased_test_paths", []))
    return sorted(expected)


def omitted_expected_concealment(task: dict[str, Any]) -> list[str]:
    declared = {str(path) for path in task.get("model_concealed_paths", [])}
    return sorted(set(expected_task_concealed_paths(task)) - declared)


def remove_model_concealed_paths(repo: Path, seq: dict[str, Any]) -> list[str]:
    removed: list[str] = []
    for path_text in sequence_concealed_paths(seq):
        path = repo / path_text
        if path.is_dir():
            shutil.rmtree(path)
            removed.append(path_text)
        elif path.exists():
            path.unlink()
            removed.append(path_text)
    return removed


def assert_model_concealed_paths_absent(repo: Path, seq: dict[str, Any]) -> list[str]:
    return [path for path in sequence_concealed_paths(seq) if (repo / path).exists()]


def baseline_protocol_descriptor(seq: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    """Return the date-independent contract that makes a baseline reusable.

    This deliberately contains only frozen evaluation inputs: task/verifier bytes,
    fixture snapshot, baseline substrate, runtime binding, and isolation policy.
    Calendar time is execution metadata, never an identity input.
    """
    tasks = []
    for task in sorted(seq.get("tasks", []), key=lambda item: int(item["order"])):
        prompt_path = root / str(task["prompt_path"])
        verifier_path = root / str(task["verifier_command"])
        seed_path = prompt_path.parent / "seed-regression.patch"
        controller_visible = prompt_path.parent / "controller-visible"
        controller_visible_assets = [
            {
                "path": str(path.relative_to(root)),
                "sha256": _protocol_file_hash(path),
            }
            for path in sorted(controller_visible.rglob("*"))
            if path.is_file()
        ] if controller_visible.is_dir() else []
        task_descriptor = {
            "id": task["id"],
            "order": int(task["order"]),
            "task_class": task["task_class"],
            "prompt_path": str(task["prompt_path"]),
            "prompt_sha256": _protocol_file_hash(prompt_path),
            "seed_patch_sha256": _protocol_file_hash(seed_path),
            "verifier_command": str(task["verifier_command"]),
            "verifier_sha256": _protocol_file_hash(verifier_path),
            "compile_command": task.get("compile_command"),
            "acceptance_visibility": task.get("acceptance_visibility"),
            "expected_changed_paths": sorted(str(path) for path in task.get("expected_changed_paths", [])),
            "controller_visible_acceptance_assets": controller_visible_assets,
            "upstream_test_paths": sorted(str(path) for path in task.get("upstream_test_paths", [])),
            "compatibility_rebased_test_paths": sorted(str(path) for path in task.get("compatibility_rebased_test_paths", [])),
            "expected_model_concealed_paths": expected_task_concealed_paths(task),
            "model_concealed_paths": sorted(str(path) for path in task.get("model_concealed_paths", [])),
        }
        review_patch_path = task.get("review_patch_path")
        if review_patch_path:
            review_patch = prompt_path.parent / str(review_patch_path)
            task_descriptor["review_patch_path"] = str(review_patch_path)
            task_descriptor["review_patch_sha256"] = _protocol_file_hash(review_patch)
        tasks.append(task_descriptor)
    qualification_path = root / str(seq.get("qualification_path", ""))

    baseline = PROFILE_META["baseline-bare-codex"]
    return {
        "version": BASELINE_POOL_PROTOCOL_VERSION,
        "task_family_generation": seq.get("task_family_generation"),
        "runner_contract_version": RUNNER_CONTRACT_VERSION,
        "runner_sha256": _self_hash(root),
        "qualification_generator_sha256": _protocol_file_hash(root / "scripts/generate_workflow_qualification.py"),
        "validator_sha256": _protocol_file_hash(root / "scripts/validate_repository.py"),
        "sequence_id": seq["id"],
        "sequence_contract": seq["sequence_contract"],
        "fixture_id": seq["fixture_id"],
        "fixture_scale": seq.get("fixture_scale"),
        "initial_snapshot": seq.get("initial_snapshot", {}),
        "objective": seq.get("objective", "individual_tool_effectiveness"),
        "primary_metric": seq.get("primary_metric", "cumulative provider-reported workflow tokens"),
        "acceptance_design": seq.get("acceptance_design"),
        "acceptance_policy": seq.get("acceptance_policy"),
        "project_compile_command": seq.get("project_compile_command"),
        "tasks": tasks,
        "model_facing_prompts": model_facing_prompt_descriptor(seq, "baseline-bare-codex", root),
        "qualification": {
            "path": str(seq.get("qualification_path", "")),
            "sha256": _protocol_file_hash(qualification_path),
        },

        "baseline_profile": {
            "profile_id": "baseline-bare-codex",
            "profile_type": baseline["profile_type"],
            "enabled_surfaces": baseline["enabled_surfaces"],
            "disabled_overlaps": baseline["disabled_overlaps"],
        },
        "agent": {
            "runtime_id": "codex-cli",
            "provider": "openai",
            "model": DEFAULT_WORKFLOW_MODEL,
            "model_condition_id": DEFAULT_WORKFLOW_MODEL_CONDITION_ID,
            "reasoning_effort": DEFAULT_WORKFLOW_REASONING_EFFORT,
        },
        "runtime_inputs": {
            "timeout_seconds_per_task": 3600,
            "docker_image": DEFAULT_DOCKER_IMAGE,
            "docker_image_identity": docker_image_identity(DEFAULT_DOCKER_IMAGE),
            "dockerfile_path": str(fixture.DEFAULT_DOCKERFILE.relative_to(root)),
            "dockerfile_sha256": _protocol_file_hash(fixture.DEFAULT_DOCKERFILE),
            "dependency_command": PROJECT_META[seq["fixture_id"]]["dependency_command"],
            "dependency_lockfiles": seq.get("initial_snapshot", {}).get("dependency_lockfiles", []),
            "codex_runtime_condition": DEFAULT_WORKFLOW_MODEL_CONDITION_ID,
        },
        "isolation": {
            "prompt_delivery": "sequential-one-task-at-a-time",
            "seed_delivery_mode": "preseeded-composite",
            "future_tasks_visible": False,
            "future_seed_regressions_visible": True,
            "controller_verifier_scripts_and_canonical_copies_model_visible": False,
            "model_visible_acceptance_asset_paths": sequence_model_visible_acceptance_paths(seq),
            "acceptance_design": seq.get("acceptance_design"),
            "acceptance_policy": seq.get("acceptance_policy"),
            "git_baseline_true_root_at_lane_start": True,
            "controller_verification": "final-only",
            "prompt_sanitizer": "sanitize_task_prompt-v1",
            "concealment": "declared-model-concealed-paths-removed-before-root-commit",
            "model_concealed_paths": sequence_concealed_paths(seq),
        },
    }


NON_CAUSAL_PROTOCOL_PROVENANCE_FIELDS = frozenset({
    "runner_sha256",
    "qualification_generator_sha256",
    "validator_sha256",
})


def baseline_protocol_descriptor_compatible(frozen: object, current: object) -> bool:
    """Compare causal execution contracts while retaining code hashes as provenance.

    Runner/validator file hashes change for post-run classification and reporting
    fixes that are invisible to the model. `runner_contract_version` remains the
    explicit gate for causal execution-semantics changes.
    """
    if not isinstance(frozen, dict) or not isinstance(current, dict):
        return False
    frozen_causal = {
        key: value for key, value in frozen.items()
        if key not in NON_CAUSAL_PROTOCOL_PROVENANCE_FIELDS
    }
    current_causal = {
        key: value for key, value in current.items()
        if key not in NON_CAUSAL_PROTOCOL_PROVENANCE_FIELDS
    }
    if (
        "task_family_generation" not in frozen_causal
        and current_causal.get("task_family_generation") == "baseline-v3"
    ):
        current_causal.pop("task_family_generation")
    return frozen_causal == current_causal


def baseline_comparison_descriptor(seq: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    """Return only causal/model-visible inputs used to group comparable runs.

    Implementation hashes remain in the frozen protocol for provenance, but
    reporting, registry, or validator-only code changes must not split an
    otherwise identical baseline pool.
    """
    descriptor = baseline_protocol_descriptor(seq, root)
    isolation = dict(descriptor["isolation"])
    isolation["verifier_execution"] = "all-tasks-non-short-circuiting-v1"
    return {
        "version": "baseline-comparison-identity-v1",
        "sequence_id": descriptor["sequence_id"],
        "sequence_contract": descriptor["sequence_contract"],
        "fixture_id": descriptor["fixture_id"],
        "fixture_scale": descriptor["fixture_scale"],
        "initial_snapshot": descriptor["initial_snapshot"],
        "objective": descriptor["objective"],
        "tasks": descriptor["tasks"],
        "model_facing_prompts": descriptor["model_facing_prompts"],
        "baseline_profile": descriptor["baseline_profile"],
        "agent": descriptor["agent"],
        "runtime_inputs": descriptor["runtime_inputs"],
        "isolation": isolation,
    }


def baseline_protocol_fingerprint_from_descriptor(descriptor: dict[str, Any]) -> str:
    """Derive a comparison-pool fingerprint from a frozen baseline descriptor."""
    isolation = dict(descriptor["isolation"])
    isolation["verifier_execution"] = "all-tasks-non-short-circuiting-v1"
    comparison = {
        "version": "baseline-comparison-identity-v1",
        "sequence_id": descriptor["sequence_id"],
        "sequence_contract": descriptor["sequence_contract"],
        "fixture_id": descriptor["fixture_id"],
        "fixture_scale": descriptor["fixture_scale"],
        "initial_snapshot": descriptor["initial_snapshot"],
        "objective": descriptor["objective"],
        "tasks": descriptor["tasks"],
        "model_facing_prompts": descriptor["model_facing_prompts"],
        "baseline_profile": descriptor["baseline_profile"],
        "agent": descriptor["agent"],
        "runtime_inputs": descriptor["runtime_inputs"],
        "isolation": isolation,
    }
    encoded = json.dumps(comparison, sort_keys=True, separators=(",", ":")).encode()
    full_hash = hashlib.sha256(encoded).hexdigest()
    return COMPARISON_IDENTITY_ALIASES.get(
        full_hash, full_hash[:BASELINE_POOL_FINGERPRINT_LENGTH]
    )


def baseline_protocol_fingerprint(seq: dict[str, Any], root: Path = ROOT) -> str:
    return baseline_protocol_fingerprint_from_descriptor(baseline_protocol_descriptor(seq, root))


def load_protocol(path_or_id: str) -> tuple[Path, dict[str, Any]]:
    path = Path(path_or_id)
    if not path.is_absolute():
        direct = ROOT / path
        named = ROOT / "sources/evaluations/protocols" / f"{path_or_id}.json"
        path = direct if direct.is_file() else named
    if not path.is_file():
        raise FileNotFoundError(f"protocol is missing: {path_or_id}")
    return path, json.loads(path.read_text())


def validate_protocol_for_run(seq: dict[str, Any], profile_id: str, args: argparse.Namespace) -> dict[str, Any] | None:
    assert_profile_runnable(profile_id)
    if not args.prepare_only:
        readiness_errors = repository_validation.current_candidate_profile_launch_readiness_errors()
        if readiness_errors:
            raise ValueError(
                "provider launch readiness gate failed: " + "; ".join(readiness_errors)
            )
    if not args.protocol:
        raise ValueError("--protocol is required before any workflow setup")
    protocol_path, protocol = load_protocol(args.protocol)
    if protocol.get("protocol_schema_version") != 3:
        raise ValueError(f"protocol {protocol_path} must declare protocol_schema_version=3")
    if protocol.get("status") != "frozen-ready-not-run":
        raise ValueError(f"protocol {protocol_path} is not frozen-ready-not-run")
    fixture_block = protocol.get("task_fixture", {})
    baseline_block = protocol.get("baseline", {})
    treatment_block = protocol.get("treatment", {})
    expected_descriptor = baseline_protocol_descriptor(seq)
    expected_fingerprint = baseline_protocol_fingerprint(seq)
    expected_execution = execution_condition_descriptor(
        seq,
        profile_id,
        timeout_seconds_per_task=args.timeout_per_task,
        docker_image=args.docker_image,
    )
    expected_execution_hash = _json_hash(expected_execution)
    selected_execution = protocol.get("selected_execution", {})
    errors: list[str] = []
    if seq.get("task_family_generation") in {"baseline-v2", "baseline-v3", "baseline-v4", "lifecycle-v1"}:
        expected_protocol_id = canonical_protocol_id(
            seq,
            profile_id,
            baseline_descriptor=expected_descriptor,
            selected_execution=expected_execution,
        )
        accepted_protocol_ids = {expected_protocol_id}
        frozen_descriptor = protocol.get("baseline_pool", {}).get("descriptor")
        frozen_execution = selected_execution.get("descriptor")
        if (
            seq.get("task_family_generation") == "baseline-v3"
            and baseline_protocol_descriptor_compatible(frozen_descriptor, expected_descriptor)
            and frozen_execution == expected_execution
        ):
            accepted_protocol_ids.add(
                canonical_protocol_id(
                    seq,
                    profile_id,
                    baseline_descriptor=frozen_descriptor,
                    selected_execution=frozen_execution,
                )
            )
        protocol_id = protocol.get("protocol_id")
        expected_protocol_path = ROOT / "sources/evaluations/protocols" / f"{protocol_id}.json"
        if (
            protocol_id not in accepted_protocol_ids
            or protocol_path.absolute() != expected_protocol_path.absolute()
            or protocol_path.is_symlink()
            or protocol_path.name != f"{protocol_id}.json"
        ):
            errors.append("canonical_protocol_identity")
    if fixture_block.get("sequence_id") != seq["id"]:
        errors.append("sequence_id")
    if fixture_block.get("fixture_id") != seq["fixture_id"]:
        errors.append("fixture_id")
    if fixture_block.get("snapshot") != seq["initial_snapshot"]["commit"]:
        errors.append("snapshot")
    if protocol.get("baseline_pool", {}).get("protocol_fingerprint") != expected_fingerprint:
        errors.append("protocol_fingerprint")
    if not baseline_protocol_descriptor_compatible(
        protocol.get("baseline_pool", {}).get("descriptor"), expected_descriptor
    ):
        errors.append("descriptor")
    if selected_execution.get("descriptor") != expected_execution:
        errors.append("selected_execution")
    if selected_execution.get("descriptor_sha256") != expected_execution_hash:
        errors.append("selected_execution_hash")
    if int(fixture_block.get("timeout_seconds_per_task", -1)) != args.timeout_per_task:
        errors.append("timeout")
    if selected_execution.get("descriptor", {}).get("runtime", {}).get("docker_image") != args.docker_image:
        errors.append("docker_image")
    control_profile = profile_id in {"baseline-bare-codex", "baseline-claude-code-no-mcp"}
    if control_profile:
        if baseline_block.get("profile_id") != profile_id:
            errors.append("profile_id")
        if treatment_block.get("profile_id"):
            errors.append("unexpected_treatment")
    else:
        if baseline_block.get("profile_id") == profile_id:
            errors.append("baseline_only_descriptor")
        if treatment_block.get("profile_id") != profile_id:
            errors.append("treatment_profile_id")
    agent_block = baseline_block if control_profile else treatment_block
    expected_agent = expected_execution.get("agent_condition", {})
    if (
        agent_block.get("provider") != expected_agent.get("provider")
        or agent_block.get("model") != expected_agent.get("model")
        or agent_block.get("reasoning_effort") != expected_agent.get("reasoning_effort")
    ):
        errors.append("agent")
    command = str(agent_block.get("command", ""))
    for required in (
        f"--sequence-id {seq['id']}",
        f"--profile-id {profile_id}",
        f"--timeout-per-task {args.timeout_per_task}",
        f"--protocol {protocol_path.relative_to(ROOT) if protocol_path.is_relative_to(ROOT) else protocol_path}",
        f"--docker-image {args.docker_image}",
    ):
        if required not in command:
            errors.append(f"command:{required}")
    if errors:
        raise ValueError(f"protocol {protocol_path} does not match run inputs: {', '.join(errors)}")
    args.protocol_path = protocol_path
    args.protocol_doc = protocol
    return protocol


def frozen_runtime_image_ref(protocol: dict[str, Any]) -> str:
    """Return the immutable image ID bound by the selected execution descriptor."""
    image_id = (
        protocol.get("selected_execution", {})
        .get("descriptor", {})
        .get("runtime", {})
        .get("docker_image_identity", {})
        .get("image_id")
    )
    if not isinstance(image_id, str) or not image_id.startswith("sha256:"):
        raise ValueError("frozen protocol is missing an immutable Docker image ID")
    return image_id


def qualification_is_current(seq: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    return repository_validation.qualification_is_current(seq)


def artifact_lane_label(project_id: str) -> str:
    return project_id.rsplit("-", 1)[-1]


def artifact_profile_label(profile_id: str, root: Path = ROOT) -> str:
    profile = profile_catalog_entry(profile_id, root)
    slug = profile.get("artifact_slug")
    if not isinstance(slug, str) or re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) is None:
        raise ValueError(f"workflow profile {profile_id} is missing a valid explicit artifact_slug")
    return slug


def canonical_baseline_session_id(project_id: str, replicate_index: int, protocol_fingerprint: str = "unfrozen", *, run_date: str = DATE) -> str:
    return f"baseline-{artifact_lane_label(project_id)}-{run_date.replace('-', '')}-p-{protocol_fingerprint}-r{replicate_index}"


def canonical_treatment_session_id(project_id: str, profile_id: str, replicate_index: int, protocol_fingerprint: str = "unfrozen", *, run_date: str = DATE) -> str:
    return f"{artifact_profile_label(profile_id)}-{artifact_lane_label(project_id)}-{run_date.replace('-', '')}-p-{protocol_fingerprint}-r{replicate_index}"


def reviewed_session_reuse_state(session: dict[str, Any] | None, root: Path = ROOT) -> str:
    if session is None:
        return "missing"
    interpretation = session.get("interpretation", {}) if isinstance(session.get("interpretation"), dict) else {}
    execution_accepted = interpretation.get("accepted_for_execution") is True
    completed = session.get("status") == "completed"
    sequence = session.get("task_sequence", {}) if isinstance(session.get("task_sequence"), dict) else {}
    prompt_delivery = sequence.get("prompt_delivery", {}) if isinstance(sequence.get("prompt_delivery"), dict) else {}
    leakage = sequence.get("leakage_controls", {}) if isinstance(sequence.get("leakage_controls"), dict) else {}
    sequence_definition = next(
        (
            item for item in sequence_doc().get("sequences", [])
            if item.get("id") == sequence.get("sequence_id")
        ),
        {},
    )
    if sequence_definition.get("task_family_generation") in {"baseline-v2", "baseline-v3", "baseline-v4", "lifecycle-v1"}:
        verifier_visibility_valid = (
            leakage.get("controller_verifier_scripts_and_canonical_copies_model_visible") is False
            and leakage.get("model_visible_acceptance_asset_paths")
            == sequence_model_visible_acceptance_paths(sequence_definition)
        )
    else:
        verifier_visibility_valid = leakage.get("verifier_assets_model_visible") is False
    isolated = (
        prompt_delivery.get("future_tasks_visible") is False
        and prompt_delivery.get("future_prompts_materialized_lazily") is True
        and prompt_delivery.get("seed_delivery_mode") == "preseeded-composite"
        and prompt_delivery.get("future_seed_regressions_visible") is True
        and prompt_delivery.get("controller_verification") == "final-only"
        and leakage.get("task_directories_model_visible") is False
        and verifier_visibility_valid
        and leakage.get("verifier_integrity_passed") is True
        and leakage.get("seed_patches_model_visible") is False
        and leakage.get("git_baseline_true_root_at_lane_start") is True
        and leakage.get("fixed_snapshot_objects_model_visible") is False
        and leakage.get("pre_seed_reflog_entries_visible") is False
        and leakage.get("concealment_verification_passed") is True
    )
    compact_artifacts_verified = pilot_session_artifacts_valid(session, root)
    # This repository measures provider token usage, not model quality. A
    # structurally valid, operationally complete provider run is reusable even
    # when its verifier or quality review reports imperfect model output.
    execution_ready = execution_accepted and completed and isolated and compact_artifacts_verified
    return "reusable" if execution_ready else "occupied"


def canonical_baseline_group_id(project_id: str, replicate_index: int, protocol_fingerprint: str) -> str:
    return f"{project_id}-canonical-baseline-{protocol_fingerprint}-sequential-workflow-r{replicate_index}"


def treatment_experiment_group_id(project_id: str, treatment_profile_id: str, replicate_index: int, protocol_fingerprint: str = "unfrozen") -> str:
    return f"{project_id}-{safe_profile_key(treatment_profile_id)}-{protocol_fingerprint}-sequential-workflow-r{replicate_index}"


def find_pool_profile_record(registry: dict[str, Any], seq: dict[str, Any], profile_id: str, replicate_index: int) -> dict[str, Any] | None:
    fingerprint = baseline_protocol_fingerprint(seq)
    matches = [
        session for session in registry.get("sessions", [])
        if session.get("schema_version") == 2
        and session.get("baseline_pool", {}).get("protocol_fingerprint") == fingerprint
        and session.get("replicate_index") == replicate_index
        and session.get("task_sequence", {}).get("sequence_id") == seq["id"]
        and session.get("profile", {}).get("profile_id") == profile_id
    ]
    if len(matches) > 1:
        raise RuntimeError(f"ambiguous {profile_id} pool records for {seq['id']} r{replicate_index}: {[item['session_id'] for item in matches]}")
    return matches[0] if matches else None


def assert_pool_slot_available(
    registry: dict[str, Any],
    seq: dict[str, Any],
    profile_id: str,
    replicate_index: int,
) -> None:
    existing = find_pool_profile_record(registry, seq, profile_id, replicate_index)
    if existing is not None:
        raise ValueError(
            f"provider sample slot already occupied for {seq['id']} {profile_id} "
            f"r{replicate_index} by {existing['session_id']}; retain the first sample"
        )


def standalone_opencode_control_authorized(
    profile_id: str,
    replicate_index: int,
    root: Path = ROOT,
    *,
    sequence_id: str = "",
    model_condition_id: str | None = None,
) -> bool:
    selected_condition = model_condition_id or DEFAULT_WORKFLOW_MODEL_CONDITION_ID
    if (
        profile_id != "runtime-opencode-codex-product-v1"
        or selected_condition != "opencode-openai-gpt-5-6-sol-high"
    ):
        return False
    if replicate_index == 2:
        path = root / OPENCODE_STANDALONE_R2_AUTHORITY_REL
        try:
            authority = json.loads(path.read_text())
        except (OSError, ValueError):
            return False
        owner = authority.get("owner_authorization", {})
        contract = authority.get("execution_contract", {})
        return bool(
            authority.get("status") == "qualified-ready-for-provider-execution"
            and owner.get("message_id") == "1532521147327971438"
            and owner.get("authorized_new_bare_replicate_index") == 2
            and contract.get("baseline_profile_id") == profile_id
            and contract.get("model_condition_id") == selected_condition
            and contract.get("sequential_max_parallel") == 1
        )
    if replicate_index != 1 or sequence_id not in {
        "fastify-lifecycle-sequence-v1",
        "beets-lifecycle-sequence-v1",
    }:
        return False
    path = root / OPENCODE_LIFECYCLE_V1_R1_AUTHORITY_REL
    try:
        authority = json.loads(path.read_text())
    except (OSError, ValueError):
        return False
    owner = authority.get("owner_authorization", {})
    contract = authority.get("execution_contract", {})
    return bool(
        authority.get("status") == "qualified-ready-for-provider-execution"
        and owner == {
            "source": "discord",
            "message_id": "1533309463484694750",
            "request": "Run V1 lifecycle evaluation with OpenCode and GPT sol high (though codex subscription)",
            "authorized_new_runtime_replicate_index": 1,
        }
        and contract.get("task_family_generation") == "lifecycle-v1"
        and contract.get("sequence_order") == [
            "fastify-lifecycle-sequence-v1",
            "beets-lifecycle-sequence-v1",
        ]
        and contract.get("replicate_index") == 1
        and contract.get("runtime") == "opencode-cli"
        and contract.get("model_condition_id") == selected_condition
        and contract.get("model") == "gpt-5.6-sol"
        and contract.get("reasoning_effort") == "high"
        and contract.get("baseline_profile_id") == profile_id
        and contract.get("sequential_max_parallel") == 1
        and contract.get("allowed_paid_baseline_runs") == 2
        and contract.get("allowed_model_turns") == 6
        and contract.get("first_valid_sample_policy") is True
        and contract.get("rerun_after_attempt_receipt") is False
        and contract.get("provider_calls") == 0
        and contract.get("provider_tokens") == 0
    )


def require_reusable_treatment_baseline(
    registry: dict[str, Any],
    seq: dict[str, Any],
    replicate_index: int,
    root: Path = ROOT,
    *,
    profile_id: str = "",
) -> dict[str, Any]:
    baseline = (
        find_comparison_baseline_record(registry, seq, profile_id, replicate_index)
        if profile_id
        else find_canonical_baseline_record(registry, seq, replicate_index)
    )
    if baseline is None or reviewed_session_reuse_state(baseline, root) != "reusable":
        if not profile_id:
            raise ValueError(
                f"treatment execution requires a reusable canonical baseline for {seq['id']} r{replicate_index}"
            )
        expected_profile = (
            "baseline-claude-code-no-mcp"
            if PROFILE_META.get(profile_id, {}).get("substrate") == "claude-code"
            else "runtime-opencode-codex-product-v1"
            if PROFILE_META.get(profile_id, {}).get("substrate") == "opencode-cli"
            else "baseline-bare-codex"
        )
        raise ValueError(
            f"treatment execution requires reusable baseline {expected_profile} "
            f"for {seq['id']} r{replicate_index}"
        )
    return baseline


def find_comparison_baseline_record(
    registry: dict[str, Any],
    seq: dict[str, Any],
    profile_id: str,
    replicate_index: int,
) -> dict[str, Any] | None:
    meta = PROFILE_META.get(profile_id, {})
    substrate = meta.get("substrate")
    if substrate == "claude-code":
        return find_claude_baseline_record(registry, seq, replicate_index)
    if substrate != "opencode-cli" or profile_id == "runtime-opencode-codex-product-v1":
        return find_canonical_baseline_record(registry, seq, replicate_index)
    matches = []
    for session in registry.get("sessions", []):
        if session.get("schema_version") != 2:
            continue
        if session.get("profile", {}).get("profile_id") != "runtime-opencode-codex-product-v1":
            continue
        if session.get("agent", {}).get("runtime_id") != "opencode-cli":
            continue
        if session.get("replicate_index") != replicate_index:
            continue
        if session.get("task_sequence", {}).get("sequence_id") != seq["id"]:
            continue
        if session.get("status") not in (None, "completed"):
            continue
        if session.get("interpretation", {}).get("accepted_for_objective") is True:
            matches.append(session)
    if len(matches) > 1:
        raise RuntimeError(
            f"ambiguous bare OpenCode baseline for {seq['id']} r{replicate_index}: "
            f"{[item['session_id'] for item in matches]}"
        )
    return matches[0] if matches else None


def find_claude_baseline_record(
    registry: dict[str, Any],
    seq: dict[str, Any],
    replicate_index: int,
) -> dict[str, Any] | None:
    """Find the reusable Claude Code no-MCP baseline for the given sequence/replicate."""
    protocol_fingerprint = baseline_protocol_fingerprint(seq)
    matches = []
    for session in registry.get("sessions", []):
        if session.get("schema_version") != 2:
            continue
        if session.get("baseline_pool", {}).get("protocol_fingerprint") != protocol_fingerprint:
            continue
        if session.get("session_role") != "baseline":
            continue
        if session.get("profile", {}).get("profile_id") != "baseline-claude-code-no-mcp":
            continue
        selected_descriptor = session.get("selected_execution", {}).get("descriptor", {})
        if (
            selected_descriptor.get("execution_role") != "baseline"
            or selected_descriptor.get("selected_profile", {}).get("profile_id") != "baseline-claude-code-no-mcp"
        ):
            continue
        if session.get("replicate_index") != replicate_index:
            continue
        if session.get("task_sequence", {}).get("sequence_id") != seq["id"]:
            continue
        if session.get("status") not in (None, "completed"):
            continue
        interpretation = session.get("interpretation", {})
        accepted = interpretation.get("accepted_for_execution")
        if accepted is None:
            accepted = interpretation.get("accepted_for_objective")
        if accepted is True:
            matches.append(session)
    if len(matches) > 1:
        raise RuntimeError(
            f"ambiguous Claude Code baseline for {seq['id']} r{replicate_index}: "
            f"{[item['session_id'] for item in matches]}"
        )
    return matches[0] if matches else None


def find_canonical_baseline_record(registry: dict[str, Any], seq: dict[str, Any], replicate_index: int) -> dict[str, Any] | None:
    protocol_fingerprint = baseline_protocol_fingerprint(seq)
    expected_protocol_identity: dict[str, Any] | None = None
    expected_selected_execution: dict[str, Any] | None = None
    expected_identity_loaded = False
    matches = []
    for session in registry.get("sessions", []):
        if session.get("schema_version") != 2:
            continue
        if session.get("baseline_pool", {}).get("protocol_fingerprint") != protocol_fingerprint:
            continue
        if session.get("session_role") != "baseline":
            continue
        if session.get("profile", {}).get("profile_id") != "baseline-bare-codex":
            continue
        selected_descriptor = session.get("selected_execution", {}).get("descriptor", {})
        if (
            selected_descriptor.get("execution_role") != "baseline"
            or selected_descriptor.get("selected_profile", {}).get("profile_id") != "baseline-bare-codex"
        ):
            continue
        if seq.get("task_family_generation") in {"baseline-v2", "baseline-v3", "baseline-v4", "lifecycle-v1"} and not expected_identity_loaded:
            expected_protocol_identity, expected_protocol = current_baseline_v2_protocol(
                seq, seq["mistake_gate"], ROOT
            )
            expected_protocol_identity = {
                key: expected_protocol_identity[key]
                for key in ("protocol_id", "path", "sha256")
            }
            expected_selected_execution = expected_protocol["selected_execution"]
            expected_identity_loaded = True
        if expected_protocol_identity is not None and (
            session.get("frozen_protocol") != expected_protocol_identity
            or session.get("selected_execution") != expected_selected_execution
        ):
            continue
        if session.get("replicate_index") != replicate_index:
            continue
        if session.get("task_sequence", {}).get("sequence_id") != seq["id"]:
            continue
        if session.get("status") not in (None, "completed"):
            continue
        interpretation = session.get("interpretation", {})
        accepted = interpretation.get("accepted_for_execution")
        if accepted is None:
            accepted = interpretation.get("accepted_for_objective")
        if accepted is True:
            matches.append(session)
    if len(matches) > 1:
        raise RuntimeError(f"ambiguous canonical baseline pool for {seq['id']} r{replicate_index}: {[item['session_id'] for item in matches]}")
    return matches[0] if matches else None


def task_alias(order: int) -> str:
    return f"task-{order:02d}"


def task_dir(project: Path, order: int) -> Path:
    return project / "tasks" / task_alias(order)


def sanitize_task_prompt(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        if any(pattern.match(line) for pattern in LEAKY_PROMPT_LINE_PATTERNS):
            continue
        # Hide public lookup keys and upstream-fixed framing in model-facing
        # prompts. The task text still describes the bug and verifier, but not
        # the public issue/commit answer path.
        line = re.sub(r"issue\s+#?\d+", "issue", line, flags=re.IGNORECASE)
        line = re.sub(r"real issue-derived regression", "regression", line, flags=re.IGNORECASE)
        line = re.sub(r"restores? the real upstream behavior", "restores the correct behavior", line, flags=re.IGNORECASE)
        line = re.sub(r"upstream test", "acceptance test", line, flags=re.IGNORECASE)
        lines.append(line)
    text = "\n".join(lines).strip() + "\n"
    return text


def write_sanitized_prompt(src: Path, dest: Path) -> None:
    dest.write_text(sanitize_task_prompt(src.read_text()))


def controller_scratch_dir(run_dir: Path) -> Path:
    return run_dir / "controller-scratch"


def controller_git_dir(run_dir: Path) -> Path:
    return controller_scratch_dir(run_dir) / "reference.git"


def seed_delivery_path(run_dir: Path) -> Path:
    return run_dir / "seed-delivery.json"


AMBIENT_GIT_OBJECT_ENV_VARS = (
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_OBJECT_DIRECTORY",
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
)
PAID_LAUNCH_PROTECTED_FILES = (Path("scripts/test_workflow_evaluation_contract.py"),)


def clear_ambient_git_object_environment() -> None:
    """Prevent caller Git plumbing from contaminating isolation or launch gates."""
    for name in AMBIENT_GIT_OBJECT_ENV_VARS:
        os.environ.pop(name, None)


def paid_launch_checkout_errors(root: Path = ROOT) -> list[str]:
    """Require an exact clean checkout of its published upstream before spend."""
    errors: list[str] = []
    for relative in PAID_LAUNCH_PROTECTED_FILES:
        if not (root / relative).is_file():
            errors.append(f"protected control-plane file is absent: {relative}")
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if status.returncode != 0:
        errors.append("repository status is unreadable")
    elif status.stdout.strip():
        errors.append("repository checkout is not clean")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=False
    )
    upstream = subprocess.run(
        ["git", "rev-parse", "@{upstream}"], cwd=root, text=True, capture_output=True, check=False
    )
    if head.returncode != 0 or upstream.returncode != 0:
        errors.append("repository HEAD or published upstream is unreadable")
    elif head.stdout.strip() != upstream.stdout.strip():
        errors.append("repository HEAD is not the published upstream commit")
    origin = subprocess.run(
        ["git", "remote", "get-url", "origin"], cwd=root, text=True, capture_output=True, check=False
    )
    upstream_name = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if origin.returncode != 0 or origin.stdout.strip() != TRUSTED_REPOSITORY_ORIGIN:
        errors.append("repository origin is not the trusted publication remote")
    if upstream_name.returncode != 0 or upstream_name.stdout.strip() != TRUSTED_REPOSITORY_UPSTREAM:
        errors.append("repository upstream is not the trusted publication branch")
    if head.returncode == 0 and origin.returncode == 0 and origin.stdout.strip() == TRUSTED_REPOSITORY_ORIGIN:
        remote = subprocess.run(
            ["git", "ls-remote", "origin", TRUSTED_REPOSITORY_REF],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        remote_lines = [line.split() for line in remote.stdout.splitlines() if line.strip()]
        if (
            remote.returncode != 0
            or remote_lines != [[head.stdout.strip(), TRUSTED_REPOSITORY_REF]]
        ):
            errors.append("repository HEAD is not independently confirmed on the trusted publication remote")
    return errors


def certified_published_launch_commit(root: Path = ROOT) -> str:
    errors = paid_launch_checkout_errors(root)
    if errors:
        raise ValueError("paid launch checkout gate failed: " + "; ".join(errors))
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def configure_model_git(repo: Path) -> None:
    run(["git", "config", "user.email", "workflow-eval@example.invalid"], cwd=repo)
    run(["git", "config", "user.name", "Workflow Eval"], cwd=repo)
    info = repo / ".git" / "info" / "exclude"
    with info.open("a") as out:
        out.write("\n.venv/\n__pycache__/\n.pytest_cache/\nnode_modules/\n")


def verify_concealed_stage(seq: dict[str, Any], repo: Path, fixed_snapshot_oid: str, order: int) -> dict[str, Any]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    parents = subprocess.check_output(["git", "rev-list", "--parents", "-1", "HEAD"], cwd=repo, text=True).split()
    remotes = subprocess.check_output(["git", "remote"], cwd=repo, text=True).splitlines()
    status = subprocess.check_output(["git", "status", "--short"], cwd=repo, text=True).splitlines()
    reflog_oids = sorted(set(subprocess.check_output(["git", "reflog", "--all", "--format=%H"], cwd=repo, text=True).splitlines()))
    fixed_probe = subprocess.run(
        ["git", "cat-file", "-e", f"{fixed_snapshot_oid}^{{commit}}"],
        cwd=repo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    fsck = subprocess.run(
        ["git", "fsck", "--unreachable", "--no-reflogs"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    leaked_admin_paths = [
        str(path.relative_to(repo / ".git"))
        for path in [
            repo / ".git" / "FETCH_HEAD",
            repo / ".git" / "objects" / "info" / "alternates",
            repo / ".git" / "refs" / "replace",
            repo / ".git" / "refs" / "remotes",
        ]
        if path.exists()
    ]
    result = {
        "order": order,
        "head": head,
        "head_is_root": len(parents) == 1,
        "reachable_commit_count": int(subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=repo, text=True).strip()),
        "reflog_oids": reflog_oids,
        "remotes": remotes,
        "working_tree_clean": not status,
        "fixed_snapshot_object_present": fixed_probe.returncode == 0,
        "unreachable_objects": [line for line in fsck.stdout.splitlines() if line.strip()],
        "leaked_git_admin_paths": leaked_admin_paths,
        "model_concealed_paths": sequence_concealed_paths(seq),
        "model_concealed_paths_present": assert_model_concealed_paths_absent(repo, seq),
    }
    result["passed"] = (
        result["head_is_root"]
        and result["reachable_commit_count"] == 1
        and result["reflog_oids"] == [head]
        and not result["remotes"]
        and result["working_tree_clean"]
        and not result["fixed_snapshot_object_present"]
        and not result["unreachable_objects"]
        and not result["leaked_git_admin_paths"]
        and not result["model_concealed_paths_present"]
    )
    return result


def conceal_seed(seq: dict[str, Any], repo: Path, run_dir: Path, order: int, fixed_snapshot_oid: str) -> dict[str, Any]:
    """Replace Git metadata and commit the current broken state as a true root.

    Deleting the fetched repository's object database is required: committing a
    seed on top of the fixed snapshot leaves the exact answer available through
    ``HEAD^`` even after the upstream remote is removed.
    """
    git_dir = repo / ".git"
    if git_dir.exists():
        chmod_tree(git_dir)
        shutil.rmtree(git_dir)
    remove_model_concealed_paths(repo, seq)
    run(["git", "init", "-q"], cwd=repo, stdout=run_dir / f"seed-task-{order:02d}-git-init.txt")
    configure_model_git(repo)
    run(["git", "add", "-A"], cwd=repo, stdout=run_dir / f"seed-task-{order:02d}-git-add.txt")
    commit = run(
        ["git", "commit", "-q", "-m", f"workflow task {order} broken-start baseline"],
        cwd=repo,
        stdout=run_dir / f"seed-task-{order:02d}-git-commit.txt",
    )
    if commit.returncode != 0:
        raise RuntimeError(f"failed to create concealed root for task {order}")
    verification = verify_concealed_stage(seq, repo, fixed_snapshot_oid, order)
    (run_dir / f"seed-task-{order:02d}-concealment.json").write_text(json.dumps(verification, indent=2) + "\n")
    if not verification["passed"]:
        raise RuntimeError(f"concealed task {order} baseline failed structural verification")
    return verification


def apply_composite_seed_patches(repo: Path, patches: list[Path], scratch: Path, log_path: Path) -> None:
    """Merge independently-authored regressions against one fixed snapshot."""
    scratch.mkdir(parents=True, exist_ok=True)
    base_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, text=True, capture_output=True
    ).stdout.strip()
    events: list[dict[str, Any]] = []

    for index, patch_path in enumerate(patches, start=1):
        worktree = scratch / f"seed-{index:02d}"
        subprocess.run(["git", "worktree", "add", "--detach", str(worktree), base_commit], cwd=repo, check=True, capture_output=True)
        try:
            subprocess.run(["git", "apply", str(patch_path)], cwd=worktree, check=True, capture_output=True)
            tracked = subprocess.run(
                ["git", "diff", "--name-only", "--no-renames", "-z"],
                cwd=worktree,
                check=True,
                stdout=subprocess.PIPE,
            ).stdout
            untracked = subprocess.run(
                ["git", "ls-files", "--others", "-z"],
                cwd=worktree,
                check=True,
                stdout=subprocess.PIPE,
            ).stdout
            changed = sorted(
                {Path(os.fsdecode(item)) for item in (tracked + untracked).split(b"\0") if item},
                key=lambda item: item.as_posix(),
            )
            if not changed:
                raise RuntimeError(f"composite seed patch produced no changed paths: {patch_path}")
            merged_paths: list[str] = []
            for relative in changed:
                current = repo / relative
                seeded = worktree / relative
                base_exists = subprocess.run(
                    ["git", "cat-file", "-e", f"{base_commit}:{relative.as_posix()}"],
                    cwd=repo,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                ).returncode == 0
                base_path = scratch / f"base-{index:02d}" / relative
                if base_exists:
                    base_path.parent.mkdir(parents=True, exist_ok=True)
                    base_path.write_bytes(
                        subprocess.run(
                            ["git", "show", f"{base_commit}:{relative.as_posix()}"],
                            cwd=repo,
                            check=True,
                            stdout=subprocess.PIPE,
                        ).stdout
                    )

                if not base_exists:
                    if not seeded.exists():
                        raise RuntimeError(f"composite seed has unsupported add/delete state for {relative}")
                    if current.exists() and current.read_bytes() != seeded.read_bytes():
                        raise RuntimeError(f"composite seed conflict on independently-added file {relative}")
                    current.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(seeded, current)
                elif not seeded.exists():
                    if current.exists() and current.read_bytes() != base_path.read_bytes():
                        raise RuntimeError(f"composite seed conflict deleting modified file {relative}")
                    current.unlink(missing_ok=True)
                elif not current.exists():
                    raise RuntimeError(f"composite seed conflict restoring deleted file {relative}")
                elif current.read_bytes() == base_path.read_bytes():
                    shutil.copy2(seeded, current)
                elif seeded.read_bytes() != base_path.read_bytes():
                    merged = subprocess.run(
                        ["git", "merge-file", "-p", str(current), str(base_path), str(seeded)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    if merged.returncode != 0:
                        raise RuntimeError(
                            f"composite seed conflict for {relative} from {patch_path}: "
                            f"{merged.stderr.decode(errors='replace').strip()}"
                        )
                    current.write_bytes(merged.stdout)
                merged_paths.append(relative.as_posix())
            events.append({"order": index, "patch": rel(patch_path), "merged_paths": merged_paths})
        finally:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                cwd=repo,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    log_path.write_text(json.dumps({"mode": "preseeded-composite", "patches": events}, indent=2) + "\n")


def create_project(seq: dict[str, Any], project: Path, run_dir: Path, *, conceal_seed_origin: bool = True) -> None:
    if project.exists():
        chmod_tree(project)
        shutil.rmtree(project)
    project.mkdir(parents=True)
    tasks_dest = run_dir / "tasks"
    tasks_dest.mkdir()

    ordered_tasks = sorted(seq["tasks"], key=lambda item: item["order"])
    alias_manifest: list[dict[str, Any]] = []
    for task in ordered_tasks:
        order = int(task["order"])
        src = ROOT / Path(task["prompt_path"]).parent
        dest = task_dir(run_dir, order)
        shutil.copytree(src, dest)
        shared_controller_hidden = src.parents[1] / "controller-hidden"
        if shared_controller_hidden.is_dir():
            shutil.copytree(shared_controller_hidden, dest / "controller-hidden", dirs_exist_ok=True)
        write_sanitized_prompt(src / "agent-prompt.txt", dest / "agent-prompt.txt")
        alias_manifest.append({
            "order": order,
            "task_id": task["id"],
            "alias": task_alias(order),
            "model_prompt_path": rel(dest / "agent-prompt.txt"),
            "verifier_command": rel(dest / "verify.sh"),
        })
    (run_dir / "task-alias-manifest.json").write_text(json.dumps(alias_manifest, indent=2) + "\n")

    repo = project / "repo"
    repo.mkdir()
    commit = seq["initial_snapshot"]["commit"]
    upstream = seq["initial_snapshot"]["upstream"]
    run(["git", "init", "-q"], cwd=repo, stdout=run_dir / "setup-git-init.txt")
    run(["git", "remote", "add", "origin", upstream], cwd=repo)
    run(["git", "fetch", "--depth", "1", "origin", commit], cwd=repo, stdout=run_dir / "setup-fetch.txt", timeout=1200)
    fetched = subprocess.check_output(["git", "rev-parse", "FETCH_HEAD"], cwd=repo, text=True).strip()
    if fetched != commit:
        raise RuntimeError(f"fetched {fetched}, expected {commit}")
    run(["git", "checkout", "-q", "--detach", "FETCH_HEAD"], cwd=repo)
    run(["git", "reset", "--hard", commit], cwd=repo, stdout=run_dir / "setup-reset.txt")
    run(["git", "clean", "-fdx"], cwd=repo, stdout=run_dir / "setup-clean.txt")
    run(["git", "config", "user.email", "workflow-eval@example.invalid"], cwd=repo)
    run(["git", "config", "user.name", "Workflow Eval"], cwd=repo)

    # Build every regression against the same fixed commit before provider
    # execution. The model then receives one persistent composite-broken root;
    # no seed patch is applied over model-authored repairs between prompts.
    scratch = controller_scratch_dir(run_dir)
    scratch.mkdir()
    orders = [int(task["order"]) for task in ordered_tasks]
    seed_patches = [task_dir(run_dir, order) / "seed-regression.patch" for order in orders]
    apply_composite_seed_patches(
        repo,
        seed_patches,
        scratch / "composite-worktrees",
        run_dir / "composite-seed-merge.json",
    )
    composite_diff = subprocess.run(
        ["git", "diff", "--full-index", "--binary"],
        cwd=repo,
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    if not composite_diff.strip():
        raise RuntimeError("composite seed produced no source changes")
    (run_dir / "composite-seed.diff").write_text(composite_diff)

    if conceal_seed_origin:
        shutil.move(str(repo / ".git"), str(controller_git_dir(run_dir)))
        concealment = conceal_seed(seq, repo, run_dir, orders[0], commit)
    else:
        remove_model_concealed_paths(repo, seq)
        run(["git", "add", "-A"], cwd=repo)
        run(["git", "commit", "-q", "-m", "debug composite broken snapshot"], cwd=repo)
        concealment = {"order": orders[0], "passed": False, "debug_unconcealed": True}

    merge_state = json.loads((run_dir / "composite-seed-merge.json").read_text())
    merged_orders = [int(item["order"]) for item in merge_state.get("patches", [])]
    leaked_assets: list[str] = []
    explicit_forbidden_names = {"seed-regression.patch", "verify.sh", "task.md", "agent-prompt.txt"}
    for path in repo.rglob("*"):
        if ".git" not in path.parts and path.is_file() and path.name in explicit_forbidden_names:
            leaked_assets.append(str(path.relative_to(repo)))
    delivery_verification = {
        "mode": "preseeded-composite",
        "preseeded_task_orders": orders,
        "merged_task_orders": merged_orders,
        "composite_diff_sha256": hashlib.sha256(composite_diff.encode()).hexdigest(),
        "model_repo_seed_or_verifier_assets": leaked_assets,
        "model_concealed_paths": sequence_concealed_paths(seq),
        "model_concealed_paths_present": assert_model_concealed_paths_absent(repo, seq),
    }
    delivery_verification["passed"] = (
        merged_orders == orders
        and bool(composite_diff.strip())
        and not leaked_assets
        and not delivery_verification["model_concealed_paths_present"]
    )
    stage_passed = bool(concealment.get("passed")) and bool(delivery_verification["passed"])
    state = {
        "mode": "preseeded-composite",
        "future_seed_regressions_visible": True,
        "seed_patches_model_visible": False,
        "preseeded_task_orders": orders,
        "pending_seed_orders": [],
        "controller_verification": "final-only",
        "diff_basis": "ordered-task-checkpoints-plus-final-cumulative-diff",
        "fixed_snapshot_oid": commit,
        "concealment": concealment,
        "composite_seed_delivery": delivery_verification,
    }
    seed_delivery_path(run_dir).write_text(json.dumps(state, indent=2) + "\n")
    qualification_path = ROOT / seq.get("qualification_path", "")
    qualification_passed, qualification = qualification_is_current(seq)
    qualification_composite_sha256 = qualification.get("composite_seed_diff_sha256")
    runtime_composite_sha256 = delivery_verification["composite_diff_sha256"]
    composite_hash_matches_qualification = qualification_composite_sha256 == runtime_composite_sha256
    stage_passed = stage_passed and qualification_passed and composite_hash_matches_qualification
    prepare_verification = {
        "passed": stage_passed,
        **state,
        "stage_seed_delivery": delivery_verification,
        "fixed_composite_qualification": {
            "path": rel(qualification_path) if qualification_path.is_file() else "",
            "passed": qualification_passed,
            "full_fixed_cumulative_verifier_zero": qualification.get("full_fixed_cumulative_verifier_zero"),
            "composite_seed_merge_zero": qualification.get("composite_seed_merge_zero"),
            "composite_seeded_verifiers_nonzero": qualification.get("composite_seeded_verifiers_nonzero"),
            "composite_seed_diff_sha256": qualification_composite_sha256,
            "runtime_composite_seed_diff_sha256": runtime_composite_sha256,
            "composite_seed_diff_hash_matches": composite_hash_matches_qualification,
        },
    }
    (run_dir / "prepare-verification.json").write_text(json.dumps(prepare_verification, indent=2) + "\n")
    if conceal_seed_origin and not stage_passed:
        raise RuntimeError("composite seed delivery, qualification, or concealment verification failed")


def treatment_diff_exclude_paths(
    cfg: dict[str, Any] | None,
    profile_id: str | None = None,
) -> tuple[str, ...]:
    if not cfg and profile_id != "baseline-claude-code-no-mcp":
        return ()
    paths = [str(path) for path in (cfg or {}).get("diff_exclude_paths", [])]
    warmup = (cfg or {}).get("warmup") or {}
    paths.extend(str(path) for path in warmup.get("cleanup_paths", []))
    if profile_id == "baseline-claude-code-no-mcp":
        paths.append("CLAUDE.md")
    return tuple(dict.fromkeys(paths))


def capture_task_delta(
    repo: Path,
    run_dir: Path,
    order: int,
    excluded_paths: tuple[str, ...] = (),
) -> Path:
    def included(path: str) -> bool:
        return not any(path == prefix or path.startswith(prefix.rstrip("/") + "/") for prefix in excluded_paths)

    untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=repo)
    paths = [path for path in untracked.decode().split("\0") if path and included(path)]
    if paths:
        run(["git", "add", "-N", "--", *paths], cwd=repo)
    pathspec = ["."]
    for prefix in excluded_paths:
        pathspec.extend([f":(exclude){prefix}", f":(exclude){prefix.rstrip('/')}/**"])
    path = run_dir / f"task-{order:02d}-agent.diff"
    run(["git", "diff", "--binary", "HEAD", "--", *pathspec], cwd=repo, stdout=path, timeout=120)
    run(["git", "diff", "--stat", "HEAD", "--", *pathspec], cwd=repo, stdout=run_dir / f"task-{order:02d}-agent-diffstat.txt", timeout=120)
    return path


def base_record(session_id: str, seq: dict[str, Any], profile_id: str, project: Path, run_dir: Path) -> dict[str, Any]:
    pmeta = PROFILE_META[profile_id]
    project_id = PROJECT_META[seq["fixture_id"]]["project_id"]
    return {
        "schema_version": 1,
        "evaluation_id": session_id,
        "target": {
            "fixture_id": seq["fixture_id"],
            "fixture_scale": seq["fixture_scale"],
            "project_id": project_id,
            "repository_path": rel(project / "repo"),
        },
        "task": {
            "id": seq["id"],
            "prompt_path": rel(run_dir / "task-prompts"),
            "verifier_command": rel(run_dir / "verify-workflow.sh"),
        },
        "profile": {
            "profile_id": profile_id,
            "profile_type": pmeta["profile_type"],
            "component_ids": pmeta["component_ids"],
            "enabled_surfaces": pmeta["enabled_surfaces"],
        },
        "setup": {
            "tool_permissions": {
                "profile_id": profile_id,
                "allowed_token_saving_tools": pmeta["allowed_terms"],
                "allowed_prompt_mentions": pmeta["allowed_terms"],
                "allowed_tool_commands": {
                    str(pmeta["tool_id"]): pmeta["supported_commands"]
                }
                if pmeta["tool_id"] and pmeta["supported_commands"]
                else {},
                "external_retrieval_allowed": False,
                "forbidden_tools": [],
            }
        },
        "agent": {
            "runtime_id": profile_runtime_id(profile_id),
            "model_condition_id": DEFAULT_WORKFLOW_MODEL_CONDITION_ID,
            "provider": (
                "openrouter"
                if DEFAULT_WORKFLOW_MODEL_CONDITION_ID.startswith("claude-code-openrouter-")
                else "anthropic"
                if profile_runtime_id(profile_id) == "claude-code"
                else "openai"
            ),
            "model": DEFAULT_WORKFLOW_MODEL,
            "reasoning_effort": DEFAULT_WORKFLOW_REASONING_EFFORT,
        },
        "artifacts": {"root": rel(run_dir)},
    }


def profile_prompt_guidance(profile_id: str) -> str:
    pmeta = PROFILE_META[profile_id]
    if pmeta["profile_type"] == "replacement_runtime":
        return (
            "# Evaluation isolation contract\n\n"
            "You are running inside the `runtime-opencode-codex-product-v1` replacement-runtime lane. "
            "This is an OpenCode substrate condition: native shell, file, git, and repository edit operations are allowed. "
            "Do not use external retrieval, compression, memory, MCP, external skills/plugins, subagents, or token-saving tools. "
            "OpenCode web tools are disabled and model-launched shell commands have no network access; do not attempt curl, wget, browsers, package downloads, or any other external retrieval. "
            "Work only inside the target repository. The controller runs concealed verification only after the full task lane; "
            "do not inspect or modify evaluation harness files.\n\n"
            "---\n\n"
        )
    tool_id = pmeta.get("tool_id")
    if not tool_id:
        if pmeta.get("substrate") == "claude-code":
            return (
                "# Evaluation isolation contract\n\n"
                "You are running inside the `baseline-claude-code-no-mcp` control lane using normal Claude Code with no evaluator-installed tool treatment. "
                "Native shell, file, git, and repository edit operations are allowed. "
                "Do not use external retrieval, compression, memory, MCP, external skills/plugins, or token-saving tools. "
                "Claude Code web and agent tools are disabled and model-launched shell commands have no network access; do not attempt curl, wget, browsers, package downloads, or any other external retrieval. "
                "Work only inside the target repository. The controller runs concealed verification only after the full task lane; "
                "do not inspect or modify evaluation harness files.\n\n---\n\n"
            )
        return (
            "# Evaluation isolation contract\n\n"
            "You are running inside the `baseline-bare-codex` control lane. "
            "This is a Codex substrate baseline: native shell, file, git, and repository edit operations are allowed. "
            "Do not use external retrieval, compression, memory, MCP, or token-saving tools. "
            "Codex web search is disabled and model-launched shell commands have no network access; do not attempt curl, wget, browsers, package downloads, or any other external retrieval. "
            "Work only inside the target repository. The controller runs concealed verification only after the full task lane; "
            "do not inspect or modify evaluation harness files.\n\n"
            "---\n\n"
        )
    cfg = fixture.TOOL_CONFIGS[str(tool_id)]
    return fixture.treatment_lane_guidance(
        profile_id,
        cfg,
        {
            "tool_state": str(pmeta.get("tool_state", "cold")),
            "tool_use_policy": str(pmeta.get("tool_use_policy", "natural")),
        },
    )


def model_facing_profile_guidance(seq: dict[str, Any], profile_id: str) -> str:
    """Return only profile guidance that belongs in this generation's model prompt."""
    if seq.get("task_family_generation") == "lifecycle-v1":
        return ""
    return profile_prompt_guidance(profile_id)


def render_task_prompt(
    seq: dict[str, Any],
    profile_id: str,
    order: int,
    prompt_text: str,
    *,
    first_task: bool,
    review_patch_text: str = "",
) -> str:
    preface: list[str] = []
    if first_task:
        preface.append(model_facing_profile_guidance(seq, profile_id))
        preface.extend([
            f"# Sequential workflow session: {seq['id']}",
            "",
            "You are in one persistent repository checkout. Do not reset the repository.",
            "You will receive workflow prompts one at a time. Future prompts remain hidden until the current response completes.",
            "Complete only the current task. Preserve the working tree for later tasks.",
            "Preserve all previously repaired behavior and do not trade one disclosed task contract for another.",
            "Source, agent, tool, index, and cache state persist without controller resets between tasks.",
            "All latent regressions are present in the initial repository, but only the current task prompt is disclosed.",
            "The visible git baseline is the composite broken-start state; do not assume `git diff` or history reveals the intended fixes.",
            "",
        ])
    else:
        preface.extend([
            f"# Continue sequential workflow session: {seq['id']}",
            "",
            "Continue in the same source checkout and preserve earlier fixes.",
            "Preserve all previously repaired behavior and do not trade one disclosed task contract for another.",
            "The controller did not run concealed verification, inject another regression, or refresh Git state between prompts.",
            "All regressions remain present from the initial composite broken start; only later task prompts remain hidden.",
            "Complete only the current task. Repository, agent, tool, index, and cache state continue unchanged except for your own work.",
            "",
        ])
    generation = seq.get("task_family_generation")
    if generation == "lifecycle-v1":
        validation_guidance = (
            "Complete the requested software change correctly. Search and inspect the repository as needed, including related definitions and call sites. Validate the implementation with relevant existing tests and checks when practical. Preserve earlier task edits in the persistent checkout; do not stop after merely making the touched files parse or compile."
        )
    elif generation in {"baseline-v2", "baseline-v3", "baseline-v4"}:
        validation_guidance = (
            "Run only the exact command block in the current task prompt. It includes the complete focused acceptance for this task. Do not rerun earlier checks or inspect aggregate Git state; preserve earlier edits and stop when the block exits 0."
        )
    else:
        validation_guidance = (
            "Run the repository's model-visible behavioral and type checks for the current and previously disclosed work. Do not stop after syntax checks when executable validation is available. The controller runs concealed verification only after the final task prompt."
        )
    preface.extend([
        f"## Current task {order}: {task_alias(order)}",
        "",
        validation_guidance,
        "",
        prompt_text,
    ])
    if review_patch_text:
        preface.extend([
            "",
            "## Proposed change under review",
            "",
            "```diff",
            review_patch_text.rstrip(),
            "```",
        ])
    return "\n".join(preface).rstrip() + "\n"


def review_patch_text(task: dict[str, Any], task_directory: Path) -> str:
    path = task.get("review_patch_path")
    if not path:
        return ""
    return (task_directory / str(path)).read_text()


def task_prompt(seq: dict[str, Any], profile_id: str, project: Path, order: int, *, first_task: bool) -> str:
    directory = task_dir(project, order)
    prompt_path = directory / "agent-prompt.txt"
    task = next(item for item in seq["tasks"] if int(item["order"]) == order)
    return render_task_prompt(
        seq,
        profile_id,
        order,
        prompt_path.read_text(),
        first_task=first_task,
        review_patch_text=review_patch_text(task, directory),
    )


def model_facing_prompt_descriptor(
    seq: dict[str, Any], profile_id: str, root: Path = ROOT
) -> dict[str, Any]:
    """Hash the exact deterministic prompt bytes visible to the model."""
    guidance = model_facing_profile_guidance(seq, profile_id)
    prompts: list[dict[str, Any]] = []
    for index, task in enumerate(sorted(seq.get("tasks", []), key=lambda item: int(item["order"]))):
        order = int(task["order"])
        source = root / str(task["prompt_path"])
        rendered = render_task_prompt(
            seq,
            profile_id,
            order,
            sanitize_task_prompt(source.read_text()),
            first_task=index == 0,
            review_patch_text=review_patch_text(task, source.parent),
        )
        prompts.append({
            "task_id": str(task["id"]),
            "order": order,
            "rendered_prompt_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
        })
    return {
        "rendering_contract": "sequential-model-facing-prompts-v2",
        "profile_guidance_sha256": hashlib.sha256(guidance.encode()).hexdigest(),
        "tasks": prompts,
    }


def materialize_task_prompt(prompt_dir: Path, order: int, content: str) -> Path:
    prompt_path = prompt_dir / f"task-{order:02d}.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(content)
    return prompt_path


def write_verifier(seq: dict[str, Any], run_dir: Path, task_root: Path) -> Path:
    verifier = run_dir / "verify-workflow.sh"
    lines = ["#!/usr/bin/env bash", "set -uo pipefail", "status=0"]
    for task in sorted(seq["tasks"], key=lambda item: item["order"]):
        order = int(task["order"])
        task_id = str(task.get("id") or task_alias(order))
        command = f"bash {json.dumps(str(task_dir(task_root, order) / 'verify.sh'))}"
        lines.extend(
            [
                command,
                "task_status=$?",
                'if [ "$task_status" -ne 0 ]; then status=1; fi',
                (
                    "printf '%s\\t%s\\t%s\\t%s\\n' "
                    f"{json.dumps(TASK_VERIFIER_RESULT_PREFIX)} {json.dumps(str(order))} "
                    f"{json.dumps(task_id)} \"$task_status\""
                ),
            ]
        )
    project_compile_command = seq.get("project_compile_command")
    if isinstance(project_compile_command, str) and project_compile_command:
        lines.extend(
            [
                project_compile_command,
                "project_compile_status=$?",
                'if [ "$project_compile_status" -ne 0 ]; then status=1; fi',
                f"printf '%s\\t%s\\n' {json.dumps(PROJECT_COMPILE_RESULT_PREFIX)} \"$project_compile_status\"",
            ]
        )
    lines.append('exit "$status"')
    verifier.write_text("\n".join(lines) + "\n")
    verifier.chmod(0o755)
    return verifier


def parse_task_verifier_results(seq: dict[str, Any], output_path: Path) -> list[dict[str, Any]]:
    """Parse one controller-authored outcome for every concealed task verifier."""
    expected = {
        (int(task["order"]), str(task["id"]))
        for task in sorted(seq["tasks"], key=lambda item: item["order"])
    }
    parsed: dict[tuple[int, str], dict[str, Any]] = {}
    for line in output_path.read_text(errors="replace").splitlines():
        if not line.startswith(f"{TASK_VERIFIER_RESULT_PREFIX}\t"):
            continue
        parts = line.split("\t")
        if len(parts) != 4:
            raise ValueError(f"malformed structured verifier outcome: {line!r}")
        _, order_text, task_id, exit_text = parts
        try:
            order = int(order_text)
            exit_code = int(exit_text)
        except ValueError as exc:
            raise ValueError(f"malformed structured verifier outcome: {line!r}") from exc
        key = (order, task_id)
        if key not in expected:
            raise ValueError(f"unexpected structured verifier outcome: order={order} task_id={task_id}")
        if key in parsed:
            raise ValueError(f"duplicate structured verifier outcome: order={order} task_id={task_id}")
        parsed[key] = {
            "task_id": task_id,
            "order": order,
            "verifier_exit_code": exit_code,
            "verifier_passed": exit_code == 0,
        }
    missing = sorted(expected - parsed.keys())
    if missing:
        raise ValueError(f"missing structured verifier outcomes: {missing}")
    return [parsed[key] for key in sorted(expected)]


def parse_project_compile_result(seq: dict[str, Any], output_path: Path) -> bool | None:
    """Parse the single final project-wide compile outcome for compile-only generations."""
    if not seq.get("project_compile_command"):
        return None
    prefix = f"{PROJECT_COMPILE_RESULT_PREFIX}\t"
    lines = [line for line in output_path.read_text(errors="replace").splitlines() if line.startswith(prefix)]
    if len(lines) != 1:
        raise ValueError(f"expected exactly one project-wide compile outcome; found {len(lines)}")
    exit_text = lines[0].removeprefix(prefix)
    try:
        exit_code = int(exit_text)
    except ValueError as exc:
        raise ValueError(f"malformed project-wide compile outcome: {lines[0]!r}") from exc
    return exit_code == 0


def complete_task_checkpoints(
    ordered_tasks: list[dict[str, Any]],
    task_checkpoints: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Represent every expected task, including prompts not reached by the agent."""
    by_order = {int(item["order"]): dict(item) for item in task_checkpoints}
    completed: list[dict[str, Any]] = []
    for task in sorted(ordered_tasks, key=lambda item: int(item["order"])):
        order = int(task["order"])
        checkpoint = by_order.get(order)
        if checkpoint is None:
            checkpoint = {
                "task_id": str(task["id"]),
                "task_class": task["task_class"],
                "task_alias": task_alias(order),
                "order": order,
                "agent_attempted": False,
                "codex_exit_code": None,
                "controller_verification": "deferred-to-final",
                "accepted": None,
                "task_delta": None,
                "usage_events": None,
                "operational_retry_count": 0,
            }
        else:
            checkpoint.setdefault("agent_attempted", True)
        completed.append(checkpoint)
    return completed


def apply_task_verifier_results(
    task_checkpoints: list[dict[str, Any]], verifier_results: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Attach final controller-verifier outcomes to their task checkpoints."""
    by_key = {(int(item["order"]), str(item["task_id"])): item for item in verifier_results}
    updated: list[dict[str, Any]] = []
    for checkpoint in task_checkpoints:
        item = dict(checkpoint)
        result = by_key.get((int(item["order"]), str(item["task_id"])))
        if result is None:
            item["controller_verification"] = "not-run"
            item["accepted"] = None
            item["verifier_exit_code"] = None
            item["verifier_passed"] = None
        else:
            passed = bool(result["verifier_passed"])
            item["controller_verification"] = "passed" if passed else "failed"
            item["accepted"] = passed
            item["verifier_exit_code"] = int(result["verifier_exit_code"])
            item["verifier_passed"] = passed
        updated.append(item)
    return updated


def verifier_paths(seq: dict[str, Any], task_root: Path, run_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for task in sorted(seq["tasks"], key=lambda item: item["order"]):
        copied_task_dir = task_dir(task_root, int(task["order"]))
        paths.append(copied_task_dir / "verify.sh")
        controller_visible = copied_task_dir / "controller-visible"
        if controller_visible.is_dir():
            paths.extend(sorted(path for path in controller_visible.rglob("*") if path.is_file()))
    paths.append(run_dir / "verify-workflow.sh")
    return paths


def snapshot_verifier_hashes(seq: dict[str, Any], task_root: Path, run_dir: Path) -> dict[str, str]:
    return {rel(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in verifier_paths(seq, task_root, run_dir)}


def check_verifier_integrity(expected: dict[str, str]) -> dict[str, Any]:
    missing: list[str] = []
    changed: list[str] = []
    for path_text, expected_digest in expected.items():
        path = Path(path_text)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            missing.append(path_text)
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected_digest:
            changed.append(path_text)
    return {"passed": not missing and not changed, "missing": missing, "changed": changed, "expected_sha256": expected}


def model_output_directory(run_dir: Path) -> Path:
    output = run_dir / "model-output"
    output.mkdir(parents=True, exist_ok=True)
    return output


def model_mounts_for_record(
    record: dict[str, Any],
    codex_home: Path,
    run_dir: Path,
    *,
    cfg: dict[str, Any] | None,
) -> list[tuple[Path, Path, str]]:
    mounts = fixture.container_mounts_for_record(record, codex_home, include_repo=True, cfg=cfg)
    fixture.add_mount(mounts, model_output_directory(run_dir), mode="rw")
    return mounts


def final_verifier_mounts(
    seq: dict[str, Any],
    record: dict[str, Any],
    codex_home: Path,
    run_dir: Path,
) -> list[tuple[Path, Path, str]]:
    mounts = fixture.container_mounts_for_record(record, codex_home, include_repo=True)
    repo = ROOT / record["target"]["repository_path"]
    for task in sorted(seq["tasks"], key=lambda item: item["order"]):
        order = int(task["order"])
        fixture.add_mount(mounts, task_dir(run_dir, order), target=task_dir(repo.parent, order), mode="ro")
    fixture.add_mount(mounts, run_dir / "verify-workflow.sh", mode="ro")
    return mounts


def validate_run_safety_args(args: argparse.Namespace) -> None:
    if bool(getattr(args, "no_provider", False)) and not bool(getattr(args, "prepare_only", False)):
        raise ValueError("--no-provider is only valid with --prepare-only")
    bypasses = [
        name
        for name in ("skip_container_preflight", "skip_codex_preflight", "skip_dependency_install", "no_conceal_seed_origin")
        if bool(getattr(args, name, False))
    ]
    if bypasses and not bool(getattr(args, "prepare_only", False)):
        rendered = ", ".join("--" + name.replace("_", "-") for name in bypasses)
        raise ValueError(f"debug bypasses are prepare-only and cannot produce an accepted run: {rendered}")


def docker_setup_deps(seq: dict[str, Any], record: dict[str, Any], codex_home: Path, run_dir: Path, docker_image: str) -> int:
    repo = ROOT / record["target"]["repository_path"]
    env = fixture.codex_env(codex_home, containerized=True)
    env["PATH"] = "/opt/data/bin:/opt/data/opt/go/bin:" + env.get("PATH", "")
    mounts = fixture.container_mounts_for_record(record, codex_home, include_repo=True)
    cmd = ["bash", "-c", PROJECT_META[seq["fixture_id"]]["dependency_command"]]
    proc = fixture.run_backend(cmd, backend="docker", docker_image=docker_image, cwd=repo, env=env, stdout_path=run_dir / "setup-deps-output.txt", timeout=2400, mounts=mounts)
    return proc.returncode


def codex_isolation_args(codex_home: Path | None = None) -> list[str]:
    """Share the fixture runner's provider-only network contract."""
    return fixture.codex_isolation_args(codex_home)


def codex_base_cmd(
    record: dict[str, Any], codex_home: Path | None = None, cfg: dict[str, Any] | None = None
) -> list[str]:
    return [
        "codex",
        "exec",
        *fixture.codex_model_args(record),
        *codex_isolation_args(codex_home),
        "--json",
        "--color",
        "never",
        *fixture.codex_hook_args(cfg),
        "--ignore-rules",
    ]


def extract_thread_ids(events_path: Path) -> list[str]:
    thread_ids: list[str] = []
    for line in events_path.read_text(errors="replace").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("type") == "thread.started" and item.get("thread_id"):
            thread_ids.append(str(item["thread_id"]))
    return thread_ids


def extract_thread_id(events_path: Path) -> str | None:
    thread_ids = extract_thread_ids(events_path)
    return thread_ids[0] if thread_ids else None


def thread_stream_continuity(
    events_path: Path,
    requested_thread_id: str | None,
) -> tuple[str | None, dict[str, Any] | None]:
    observed = extract_thread_ids(events_path)
    unique = sorted(set(observed))
    expected = requested_thread_id
    if len(unique) != 1 or (expected is not None and unique[0] != expected):
        return expected, {
            "events": str(events_path),
            "expected_thread_id": expected,
            "observed_thread_ids": unique,
            "thread_started_event_count": len(observed),
            "message": (
                "Codex event stream did not prove exactly one persistent thread"
                if expected is None
                else "Codex resume event stream did not match the requested persistent thread"
            ),
        }
    return unique[0], None


def retryable_codex_operational_failure(events_path: Path) -> bool:
    """Recognize the narrow malformed-tool-call failure observed in Codex JSONL."""
    if not events_path.exists():
        return False
    for line in events_path.read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "turn.failed":
            continue
        error = event.get("error")
        message = error.get("message", "") if isinstance(error, dict) else str(error or "")
        if "failed to parse function arguments" in message and "EOF while parsing an object" in message:
            return True
    return False


def run_codex_task(
    record: dict[str, Any],
    profile_id: str,
    codex_home: Path,
    run_dir: Path,
    docker_image: str,
    prompt_path: Path,
    output_path: Path,
    last_message_path: Path,
    *,
    timeout: int,
    thread_id: str | None,
    operational_retries: int = MAX_CODEX_OPERATIONAL_RETRIES,
) -> tuple[int, str | None, dict[str, Any] | None]:
    if profile_runtime_id(profile_id) == "claude-code":
        return claude_code_workflow_adapter.run_task(
            record=record,
            claude_home=codex_home,
            run_dir=run_dir,
            docker_image=docker_image,
            prompt_path=prompt_path,
            events_path=output_path,
            session_id=thread_id,
            timeout=timeout,
            fixture=fixture,
        )
    cfg = fixture.active_tool_config(record, profile_id)
    repo = ROOT / record["target"]["repository_path"]
    wrapper = (cfg or {}).get("codex_wrapper") if cfg else None
    env = fixture.codex_env(codex_home, containerized=True, cfg=cfg)
    env.update(fixture.tool_env_for_record(record, profile_id, codex_home))
    fixture.apply_model_network_isolation(env)
    mounts = model_mounts_for_record(record, codex_home, run_dir, cfg=cfg)

    def execute(active_prompt: Path, events: Path, active_thread: str | None, attempt_timeout: int) -> int:
        if active_thread is None:
            codex_cmd = [*codex_base_cmd(record, codex_home, cfg), "--cd", str(repo), "--output-last-message", str(last_message_path), "-"]
        else:
            codex_cmd = ["codex", "exec", "resume", *fixture.codex_model_args(record), *codex_isolation_args(codex_home), "--json", *fixture.codex_hook_args(cfg), "--ignore-rules", "--output-last-message", str(last_message_path), active_thread, "-"]
        input_path_for_proc: Path | None = active_prompt
        if wrapper:
            assert cfg is not None
            data_dir = fixture.tool_data_dir(codex_home, cfg)
            tool_port = 18000 + int(hashlib.sha256(str(repo.resolve()).encode()).hexdigest()[:8], 16) % 20000
            wrapper_args = [
                str(part).format(
                    repository_root=ROOT,
                    repo=repo,
                    codex_home=codex_home,
                    tool_data_dir=data_dir,
                    repo_slug=repo.name.replace("-", "_"),
                    tool_port=tool_port,
                )
                for part in wrapper.get("args", [])
            ]
            if codex_cmd[-1] == "-":
                codex_cmd = [*codex_cmd[:-1], active_prompt.read_text()]
                input_path_for_proc = None
            cmd = [str(wrapper["command"]), *wrapper_args, *codex_cmd[1:]]
        else:
            cmd = codex_cmd
        proc = fixture.run_backend(cmd, backend="docker", docker_image=docker_image, cwd=repo, env=env, stdout_path=events, input_path=input_path_for_proc, timeout=attempt_timeout, mounts=mounts)
        return proc.returncode

    deadline = time.monotonic() + timeout
    code = execute(prompt_path, output_path, thread_id, timeout)
    captured_thread, continuity_error = thread_stream_continuity(output_path, thread_id)
    if continuity_error is not None:
        code = THREAD_CONTINUITY_FAILURE_EXIT_CODE
    remaining_timeout = max(0, int(deadline - time.monotonic()))
    if code != 0 and remaining_timeout > 0 and operational_retries > 0 and captured_thread and continuity_error is None and retryable_codex_operational_failure(output_path):
        retry_prompt = prompt_path.with_name(f"{prompt_path.stem}-operational-retry-01.md")
        retry_prompt.write_text(
            "The previous turn ended because Codex emitted a malformed tool call before completion. "
            "This is one operational retry of the same task, not a new task. Inspect the current repository state, "
            "preserve valid work already made, complete the currently active task, and run its available validation.\n"
        )
        retry_events = output_path.with_name(f"{output_path.stem}-retry-01{output_path.suffix}")
        retry_code = execute(retry_prompt, retry_events, captured_thread, remaining_timeout)
        _, retry_continuity_error = thread_stream_continuity(retry_events, captured_thread)
        if retry_continuity_error is not None:
            retry_code = THREAD_CONTINUITY_FAILURE_EXIT_CODE
            continuity_error = retry_continuity_error
        original_text = output_path.read_text(errors="replace")
        retry_text = retry_events.read_text(errors="replace")
        separator = "" if not original_text or original_text.endswith("\n") else "\n"
        output_path.write_text(original_text + separator + retry_text)
        code = retry_code
    return code, captured_thread, continuity_error


def run_final_verifier(seq: dict[str, Any], record: dict[str, Any], codex_home: Path, run_dir: Path, docker_image: str) -> int:
    repo = ROOT / record["target"]["repository_path"]
    env = fixture.codex_env(codex_home, containerized=True)
    mounts = final_verifier_mounts(seq, record, codex_home, run_dir)
    proc = fixture.run_backend(["bash", str(run_dir / "verify-workflow.sh")], backend="docker", docker_image=docker_image, cwd=repo, env=env, stdout_path=run_dir / "final-verifier-output.txt", timeout=3600, mounts=mounts)
    return proc.returncode


def build_provider_usage(profile_id: str, events_path: Path) -> dict[str, Any]:
    runtime_id = profile_runtime_id(profile_id)
    if runtime_id == "opencode-cli":
        return extract_opencode_usage.build_summary(events_path)
    if runtime_id == "claude-code":
        return extract_claude_code_usage.build_summary(events_path)
    return extract_codex_usage.build_summary(events_path)


def concatenate_events(run_dir: Path, task_count: int, *, runtime_id: str = "codex-cli") -> Path:
    stem = "claude-events" if runtime_id == "claude-code" else "codex-events"
    combined = run_dir / f"{stem}.jsonl"
    with combined.open("w") as out:
        for order in range(1, task_count + 1):
            path = run_dir / f"task-{order:02d}-{stem}.jsonl"
            if path.exists():
                text = path.read_text(errors="replace")
                out.write(text)
                if text and not text.endswith("\n"):
                    out.write("\n")
    return combined


def capture_diff(record: dict[str, Any], run_dir: Path) -> None:
    repo = ROOT / record["target"]["repository_path"]
    run(["git", "status", "--short"], cwd=repo, stdout=run_dir / "git-status.txt", timeout=60)
    task_deltas = sorted(run_dir.glob("task-??-agent.diff"))
    if task_deltas:
        with (run_dir / "changes.diff").open("w") as out:
            out.write("# Ordered cumulative source checkpoints. Every section is relative to the one composite broken-start root.\n")
            for path in task_deltas:
                out.write(f"\n# --- {path.stem} ---\n")
                text = path.read_text(errors="replace")
                out.write(text)
                if text and not text.endswith("\n"):
                    out.write("\n")
        with (run_dir / "final-diffstat.txt").open("w") as out:
            for path in sorted(run_dir.glob("task-??-agent-diffstat.txt")):
                out.write(f"--- {path.name} ---\n")
                text = path.read_text(errors="replace")
                out.write(text)
                if text and not text.endswith("\n"):
                    out.write("\n")
        return
    run(["git", "diff", "--stat"], cwd=repo, stdout=run_dir / "final-diffstat.txt", timeout=60)
    pathspec = ["."]
    if record.get("profile", {}).get("profile_id") == "baseline-claude-code-no-mcp":
        pathspec.append(":(exclude)CLAUDE.md")
    run(["git", "diff", "--binary", "--", *pathspec], cwd=repo, stdout=run_dir / "changes.diff", timeout=120)


def audit(record_path: Path, run_dir: Path) -> int:
    artifacts = [str(record_path)]
    artifacts.extend(str(path) for path in sorted(run_dir.glob("*events.jsonl")))
    artifacts.extend(str(path) for path in (run_dir / "codex-mcp-list.txt", run_dir / "codex-effective-config.toml") if path.exists())
    artifacts.extend(str(path) for path in sorted((run_dir / "task-prompts").glob("task-*.md")))
    return fixture.run([
        sys.executable,
        str(ROOT / "scripts/audit_tool_isolation.py"),
        "--json-output",
        str(run_dir / "tool-isolation-audit.json"),
        *artifacts,
    ], stdout_path=run_dir / "tool-isolation-audit.txt", timeout=120).returncode


def compact_artifacts(run_dir: Path) -> dict[str, str]:
    return {
        "artifact_contract": "compact-v1-four-files",
        "root": rel(run_dir),
        "run_record": rel(run_dir / "run.json"),
        "final_diff": rel(run_dir / "changes.diff"),
        "final_diff_basis": "ordered cumulative checkpoints plus final cumulative source diff from one composite root",
        "evidence_bundle": rel(run_dir / "evidence.jsonl.gz"),
        "manifest": rel(run_dir / "manifest.sha256"),
    }


def evidence_source_files(run_dir: Path) -> list[Path]:
    """Return text evidence to pack, excluding scratch checkouts/homes."""
    files: list[Path] = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(run_dir).parts
        if not rel_parts or rel_parts[0] in {"codex-homes", "controller-scratch", "tasks"}:
            continue
        if rel_parts == ("composite-seed.diff",):
            continue
        if rel_parts[0] == "project":
            continue
        if len(rel_parts) == 1 and rel_parts[0] in COMPACT_ARTIFACT_NAMES:
            continue
        files.append(path)
    return files


def write_evidence_bundle(run_dir: Path) -> Path:
    bundle = run_dir / "evidence.jsonl.gz"
    with gzip.open(bundle, "wt", encoding="utf-8") as out:
        for path in evidence_source_files(run_dir):
            entry = {
                "path": str(path.relative_to(run_dir)),
                "content": path.read_text(errors="replace"),
            }
            out.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return bundle


def write_manifest(run_dir: Path) -> Path:
    manifest = run_dir / "manifest.sha256"
    lines = []
    for name in sorted(COMPACT_ARTIFACT_NAMES - {"manifest.sha256"}):
        path = run_dir / name
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {name}\n")
    manifest.write_text("".join(lines))
    return manifest


def remove_noncompact_artifacts(run_dir: Path) -> None:
    for path in list(run_dir.iterdir()):
        if path.is_file() and path.name in COMPACT_ARTIFACT_NAMES:
            continue
        if path.is_dir():
            chmod_tree(path)
            shutil.rmtree(path)
        else:
            path.unlink()


def finalize_failed_attempt(summary: dict[str, Any], record: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    """Compact a pre-model infrastructure failure without publishing a session."""
    if not (run_dir / "changes.diff").exists():
        capture_diff(record, run_dir)
    redact_auth_sync(run_dir)
    remove_ephemeral_homes(run_dir)
    summary["artifacts"] = compact_artifacts(run_dir)
    (run_dir / "run.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_evidence_bundle(run_dir)
    remove_noncompact_artifacts(run_dir)
    write_manifest(run_dir)
    return summary


def redact_json_file(path: Path, keys: set[str]) -> None:
    if not path.exists():
        return
    data = json.loads(path.read_text())
    for key in keys:
        if key in data:
            data[key] = "[REDACTED]"
    path.write_text(json.dumps(data, indent=2) + "\n")


def redact_auth_sync(run_dir: Path) -> None:
    path = run_dir / "codex-auth-sync.jsonl"
    if path.exists():
        lines = []
        for line in path.read_text().splitlines():
            try:
                item = json.loads(line)
                if "source_home" in item:
                    item["source_home"] = "[REDACTED]"
                lines.append(json.dumps(item))
            except json.JSONDecodeError:
                lines.append(line)
        path.write_text("\n".join(lines) + ("\n" if lines else ""))
    redact_json_file(run_dir / "codex-home-manifest.json", {"source_auth_home"})


def sync_copied_codex_auth_back(codex_home: Path, source_home: Path, run_dir: Path, stage: str) -> None:
    """Persist refreshed copied Codex auth from the ephemeral Docker home.

    Docker runs copy auth into the run-local Codex home instead of mounting the
    controller account home. Codex may refresh that file during preflight or task
    execution, so copy it back and leave only a redacted sync audit event.
    """
    if os.environ.get("WORKFLOW_LANE_DISABLE_AUTH_SYNC") == "1":
        return
    auths = fixture.auth_candidates(source_home)
    if not auths:
        return
    source_auth = auths[0]
    copied_auth = codex_home / source_auth.name
    event = {
        "stage": stage,
        "source_home": str(source_auth.parent),
        "auth_link_name": source_auth.name,
        "synced": False,
    }
    if copied_auth.exists():
        shutil.copy2(copied_auth, source_auth)
        os.chmod(source_auth, 0o600)
        event["synced"] = True
    with (run_dir / "codex-auth-sync.jsonl").open("a") as out:
        out.write(json.dumps(event) + "\n")


def remove_ephemeral_homes(run_dir: Path) -> None:
    for name in ["codex-homes"]:
        path = run_dir / name
        if path.exists():
            chmod_tree(path)
            shutil.rmtree(path)


def functional_task_count(*, task_checkpoints: list[dict[str, Any]]) -> int:
    """Count final controller-verifier passes from structured per-task outcomes."""
    return sum(item.get("accepted") is True for item in task_checkpoints)


def execution_integrity_record(
    summary: dict[str, Any], audit_code: int, audit_result: dict[str, Any]
) -> dict[str, Any]:
    return {
        "verifier_integrity_passed": bool(
            summary.get("leakage_controls", {}).get("verifier_integrity_passed")
        ),
        "tool_isolation_audit_passed": audit_code == 0,
        "external_retrieval_hits": audit_result.get("external_retrieval_hits", []),
        "pass_through_tool_command_hits": audit_result.get(
            "pass_through_tool_command_hits", []
        ),
    }


def workflow_session_record(
    seq: dict[str, Any],
    summary: dict[str, Any],
    run_dir: Path,
    profile_id: str,
    codex_exit_codes: list[int],
    final_verifier_code: int,
    audit_code: int,
    usage: dict[str, Any],
    task_checkpoints: list[dict[str, Any]],
    *,
    prompt_delivery: dict[str, Any],
    leakage_controls: dict[str, Any],
    comparison_baseline_session_id: str = "",
) -> dict[str, Any]:
    pmeta = PROFILE_META[profile_id]
    runtime_id = profile_runtime_id(profile_id)
    baseline_control_profile = profile_id in {"baseline-bare-codex", "baseline-claude-code-no-mcp"}
    if baseline_control_profile and comparison_baseline_session_id:
        raise ValueError("baseline session must not carry a comparison baseline binding")
    accepted = bool(summary.get("accepted"))
    standalone_opencode_control = (
        profile_id == "runtime-opencode-codex-product-v1"
        and not comparison_baseline_session_id
    )
    if (
        not baseline_control_profile
        and accepted
        and not comparison_baseline_session_id
        and not standalone_opencode_control
    ):
        raise ValueError("accepted treatment session requires a comparison baseline binding")
    tasks_passed = functional_task_count(task_checkpoints=task_checkpoints)
    project_compile_passed = parse_project_compile_result(
        seq, run_dir / "final-verifier-output.txt"
    )
    audit_path = run_dir / "tool-isolation-audit.json"
    audit_result = json.loads(audit_path.read_text()) if audit_path.exists() else {}
    total_provider_tokens = usage.get("total_provider_tokens")
    tokens_per_accepted_task = (total_provider_tokens / tasks_passed) if tasks_passed and isinstance(total_provider_tokens, (int, float)) else None
    raw_agent_condition = summary.get("agent_condition")
    agent_condition: dict[str, Any] = dict(raw_agent_condition) if isinstance(raw_agent_condition, dict) else {}
    agent_provider = str(agent_condition.get("provider") or ("openrouter" if runtime_id == "claude-code" else "openai"))
    agent_model = str(agent_condition.get("model") or ("gpt-5.6-sol" if runtime_id == "claude-code" else DEFAULT_WORKFLOW_MODEL))
    agent_reasoning_effort = agent_condition.get("reasoning_effort") or (
        "high" if runtime_id == "claude-code" else DEFAULT_WORKFLOW_REASONING_EFFORT
    )
    return {
        "schema_version": 2,
        "session_id": summary["session_id"],
        "record_type": "workflow_session",
        "evidence_type": "workflow-simulation",
        "study_id": summary["study_id"],
        "experiment_group_id": summary["experiment_group_id"],
        "objective": (
            pmeta["objective_scope"]
            if pmeta["objective_scope"] != "control"
            else seq.get("objective", "individual_tool_effectiveness")
        ),
        "evidence_stage": "reproduction",
        "status": "completed" if accepted else "failed",
        "session_role": pmeta["session_role"],
        "replicate_index": summary["replicate_index"],
        "frozen_protocol": summary["frozen_protocol"],
        "baseline_pool": summary["baseline_pool"],
        "selected_execution": summary["selected_execution"],
        "docker_image_identity": summary["docker_image_identity"],
        "tool_adapter_identity": summary["tool_adapter_identity"],
        "date": DATE,
        "target": {
            "fixture_id": seq["fixture_id"],
            "fixture_scale": seq["fixture_scale"],
            "project_id": PROJECT_META[seq["fixture_id"]]["project_id"],
            "repository_path": summary["repository_path"],
            "initial_snapshot": {
                "commit": seq["initial_snapshot"]["commit"],
                "branch": "detached",
                "fixture_hash": "",
            },
        },
        "task_sequence": {
            "sequence_id": seq["id"],
            "sequence_contract": seq["sequence_contract"],
            "task_ids": [task["id"] for task in sorted(seq["tasks"], key=lambda item: item["order"])],
            "task_classes": [task["task_class"] for task in sorted(seq["tasks"], key=lambda item: item["order"])],
            "reset_policy": "reset source checkout, profile home, tool state, indexes, caches, generated config, and agent home before the lane; preserve repository, thread, tool, index, cache, and agent state across every sequential prompt",
            "prompt_delivery": prompt_delivery,
            "leakage_controls": leakage_controls,
        },
        "profile": {
            "profile_id": profile_id,
            "profile_type": pmeta["profile_type"],
            "enabled_surfaces": pmeta["enabled_surfaces"],
            "disabled_overlaps": pmeta["disabled_overlaps"],
            "component_ids": pmeta["component_ids"],
        },
        "agent": {
            "runtime_id": runtime_id,
            "model_condition_id": agent_condition.get("model_condition_id") or DEFAULT_WORKFLOW_MODEL_CONDITION_ID,
            "name": runtime_agent_name(runtime_id),
            "version": summary.get("agent_runtime_version", summary.get("codex_version", "")),
            "provider": agent_provider,
            "model": agent_model,
            "reasoning_effort": agent_reasoning_effort,
            "temperature": None,
            "max_turns": None,
            "time_budget_seconds": summary.get("timeout_seconds"),
        },
        "state_policy": sequence_doc().get("state_policy_defaults", {}),
        "cumulative_token_usage": {
            "measurement_source": usage.get("measurement_source"),
            "fresh_input_tokens": usage.get("fresh_input_tokens"),
            "cached_input_tokens": usage.get("cached_input_tokens"),
            "cache_write_tokens": usage.get("cache_write_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "reasoning_tokens": usage.get("reasoning_tokens"),
            "total_provider_tokens": usage.get("total_provider_tokens"),
            "provider_usage_details": usage.get("provider_usage_details"),
            "tokens_per_accepted_task": tokens_per_accepted_task,
            "accounting_basis": f"{runtime_agent_name(runtime_id)}-reported token volume; monetary cost estimation is out of scope",
        },
        "per_task_results": task_checkpoints,
        "software_quality": {
            "tasks_attempted": sum(
                item.get("agent_attempted") is True for item in task_checkpoints
            ),
            "tasks_agent_claimed_complete": sum(
                item.get("agent_attempted") is True
                and item.get("codex_exit_code") == 0
                for item in task_checkpoints
            ),
            "tasks_passed": tasks_passed,
            "final_verifier_command": rel(run_dir / "verify-workflow.sh"),
            "final_verifier_passed": final_verifier_code == 0,
            "project_compile_command": seq.get("project_compile_command"),
            "project_compile_passed": project_compile_passed,
            "functional_verifier_passed": (
                final_verifier_code == 0
                and tasks_passed == len(seq["tasks"])
                and (not seq.get("project_compile_command") or project_compile_passed is True)
            ),
            "quality_review_status": "not-reviewed",
            "quality_score": None,
            "critical_failures": [] if final_verifier_code == 0 else ["one or more workflow verifiers failed"],
        },
        "execution_integrity": execution_integrity_record(summary, audit_code, audit_result),
        "artifacts": compact_artifacts(run_dir),
        "interpretation": {
            "accepted_for_execution": accepted,
            "accepted_for_objective": accepted,
            "claim_status": "token-accounting-eligible" if accepted else "operationally-invalid",
            "comparison_baseline_session_id": comparison_baseline_session_id,
            "standalone_runtime_control": standalone_opencode_control,
            "exclusion_reason": "" if accepted else f"codex_exit_codes={codex_exit_codes}; audit_exit={audit_code}; thread_continuity_errors={summary.get('thread_continuity_errors', [])}; usage_warnings={usage.get('warnings')}",
            "notes": "Provider-backed lane completed with clean integrity; verifier and review outcomes are diagnostic model-behavior evidence and do not gate token accounting." if accepted else "Lane did not complete operationally; exclude it from token accounting.",
            "scope_note": "Full warm-state lane; all regressions are preseeded, prompts are disclosed sequentially, and controller verification runs only after the final prompt; declared acceptance assertions remain model-visible.",
            "evaluation_validity": "valid" if accepted else "operationally-invalid",
            "primary_objective_hard_baseline": accepted and baseline_control_profile,
            "usable_for_primary_objective_token_comparison": accepted,
            "operationally_completed": accepted,
            "agent_declared_task_completion_count": sum(
                item.get("agent_attempted") is True and item.get("codex_exit_code") == 0
                for item in task_checkpoints
            ),
        },
    }


def inherited_provider_production_lock_fd() -> int | None:
    """Validate the matrix-held lock capability inherited by a child lane."""
    inherited = os.environ.get(PRODUCTION_LOCK_FD_ENV)
    if inherited is None:
        return None
    try:
        fd = int(inherited)
        held = os.fstat(fd)
        expected = PRODUCTION_LOCK_PATH.stat()
    except (OSError, TypeError, ValueError) as exc:
        raise RuntimeError("invalid inherited workflow production lock") from exc
    if (held.st_dev, held.st_ino) != (expected.st_dev, expected.st_ino):
        raise RuntimeError("inherited workflow production lock points to the wrong file")
    probe_fd = os.open(PRODUCTION_LOCK_PATH, os.O_RDONLY)
    try:
        try:
            fcntl.flock(probe_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            pass
        else:
            fcntl.flock(probe_fd, fcntl.LOCK_UN)
            raise RuntimeError("inherited workflow production lock was not held before child launch")
    finally:
        os.close(probe_fd)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        raise RuntimeError("inherited workflow production lock is not held by this matrix") from exc
    return fd


def acquire_provider_production_lock() -> int:
    """Acquire, or verify inheritance of, the shared provider-production lock."""
    inherited_fd = inherited_provider_production_lock_fd()
    if inherited_fd is not None:
        return inherited_fd
    PRODUCTION_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(PRODUCTION_LOCK_PATH, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        os.close(fd)
        raise RuntimeError("another provider-capable workflow run is already active") from exc
    return fd


def same_provider_slot(existing: dict[str, Any], record: dict[str, Any]) -> bool:
    """Match the immutable provider-sample slot independently of session ID."""
    if existing.get("schema_version") != 2 or record.get("schema_version") != 2:
        return False
    same_coordinate = (
        existing.get("task_sequence", {}).get("sequence_id") == record.get("task_sequence", {}).get("sequence_id")
        and existing.get("profile", {}).get("profile_id") == record.get("profile", {}).get("profile_id")
        and existing.get("replicate_index") == record.get("replicate_index")
    )
    if not same_coordinate:
        return False
    same_pool = existing.get("baseline_pool", {}).get("protocol_fingerprint") == record.get("baseline_pool", {}).get("protocol_fingerprint")
    existing_protocol = existing.get("frozen_protocol", {})
    record_protocol = record.get("frozen_protocol", {})
    same_protocol = all(
        existing_protocol.get(key) == record_protocol.get(key)
        for key in ("protocol_id", "path", "sha256")
    )
    return same_pool or same_protocol


def update_registry(record: dict[str, Any]) -> None:
    path = ROOT / "data/workflow-sessions.json"
    doc = json.loads(path.read_text())
    sessions = doc.get("sessions", [])
    if any(session.get("session_id") == record["session_id"] for session in sessions):
        raise FileExistsError(
            f"workflow session {record['session_id']} already exists; use a new replicate/session ID and supersedes_session_id"
        )
    occupied = next((session for session in sessions if same_provider_slot(session, record)), None)
    if occupied is not None:
        raise FileExistsError(
            "provider sample slot already occupied at registry publication by "
            f"{occupied.get('session_id')}; refusing duplicate {record.get('session_id')}"
        )
    sessions.append(record)
    doc["sessions"] = sessions
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(json.dumps(doc, indent=2) + "\n")
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def publish_session_after_strict_ingress(record: dict[str, Any], run_dir: Path) -> None:
    """Publish only a compact session that passes the same strict ingress used by matrix merge."""
    if not pilot_session_artifacts_valid(record, ROOT):
        rejection_receipt = run_dir.parent / f"{record['session_id']}.strict-ingress-rejection.json"
        atomic_create_json(
            rejection_receipt,
            {
                "schema_version": 1,
                "status": "rejected-before-registry-publication",
                "session_id": record["session_id"],
                "artifact_root": record.get("artifacts", {}).get("root"),
                "pilot_attempt_receipt": str(
                    baseline_pilot_attempt_receipt_path(load_sequence(record["task_sequence"]["sequence_id"]))
                ),
                "reason": "strict compact artifact ingress validation failed",
                "source_evidence_retained": str(run_dir),
            },
        )
        raise RuntimeError(
            f"strict compact artifact ingress validation failed for {record['session_id']}; "
            f"evidence retained at {run_dir} and identity remains occupied"
        )
    update_registry(record)


def freshish_tokens(record: dict[str, Any]) -> int | float | None:
    usage = record.get("cumulative_token_usage", {})
    fresh = usage.get("fresh_input_tokens")
    output = usage.get("output_tokens")
    if isinstance(fresh, (int, float)) and isinstance(output, (int, float)):
        return fresh + output
    total = usage.get("total_provider_tokens")
    cached = usage.get("cached_input_tokens")
    if isinstance(total, (int, float)) and isinstance(cached, (int, float)):
        return total - cached
    return None


def percent_delta(delta: int | float | None, baseline: int | float | None) -> float | None:
    return (delta / baseline * 100) if delta is not None and baseline else None


def atomic_create_json(path: Path, data: Any) -> None:
    """Durably publish new JSON without exposing partial bytes or overwriting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            json.dump(data, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary_path, path)
        except FileExistsError as exc:
            raise FileExistsError(f"atomic JSON target already exists; refusing overwrite: {path}") from exc
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def write_comparison_if_ready(seq: dict[str, Any], study_id: str, replicate_index: int, treatment_profile_id: str) -> dict[str, Any] | None:
    registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
    project_id = PROJECT_META[seq["fixture_id"]]["project_id"]
    current_protocol_fingerprint = baseline_protocol_fingerprint(seq)
    comparison_key = safe_profile_key(treatment_profile_id)
    treatment_candidates = [
        session
        for session in registry.get("sessions", [])
        if session.get("task_sequence", {}).get("sequence_id") == seq["id"]
        and session.get("profile", {}).get("profile_id") == treatment_profile_id
        and session.get("replicate_index") == replicate_index
    ]
    treatment = treatment_candidates[0] if len(treatment_candidates) == 1 else None
    frozen_protocol_fingerprint = (
        treatment.get("baseline_pool", {}).get("protocol_fingerprint")
        if isinstance(treatment, dict)
        else None
    )
    protocol_fingerprint = (
        frozen_protocol_fingerprint
        if isinstance(frozen_protocol_fingerprint, str) and frozen_protocol_fingerprint
        else current_protocol_fingerprint
    )
    group_id = (
        treatment.get("experiment_group_id")
        if isinstance(treatment, dict) and isinstance(treatment.get("experiment_group_id"), str)
        else treatment_experiment_group_id(project_id, treatment_profile_id, replicate_index, protocol_fingerprint)
    )
    baseline = find_comparison_baseline_record(
        registry,
        seq,
        treatment_profile_id,
        replicate_index,
    )
    if treatment is None:
        sessions = [s for s in registry.get("sessions", []) if s.get("experiment_group_id") == group_id]
        treatment = next(
            (
                s
                for s in sessions
                if s.get("profile", {}).get("profile_id") == treatment_profile_id
                and s.get("baseline_pool", {}).get("protocol_fingerprint") == protocol_fingerprint
            ),
            None,
        )
    if not baseline or not treatment:
        return None
    if reviewed_session_reuse_state(baseline, ROOT) != "reusable" or reviewed_session_reuse_state(treatment, ROOT) != "reusable":
        return None
    b_tokens = baseline.get("cumulative_token_usage", {}).get("total_provider_tokens")
    t_tokens = treatment.get("cumulative_token_usage", {}).get("total_provider_tokens")
    delta = t_tokens - b_tokens if isinstance(b_tokens, (int, float)) and isinstance(t_tokens, (int, float)) else None
    b_freshish = freshish_tokens(baseline)
    t_freshish = freshish_tokens(treatment)
    freshish_delta = t_freshish - b_freshish if isinstance(b_freshish, (int, float)) and isinstance(t_freshish, (int, float)) else None
    baseline_profile_id = baseline.get("profile", {}).get("profile_id")
    nested_runtime_baseline = baseline_profile_id == "runtime-opencode-codex-product-v1"
    comparison = {
        "schema_version": 3,
        "comparison_id": f"baseline-{artifact_lane_label(project_id)}-{DATE.replace('-', '')}-vs-{artifact_profile_label(treatment_profile_id)}-p-{protocol_fingerprint}-r{replicate_index}",
        "study_id": study_id,
        "objective": treatment.get("objective"),
        "experiment_group_id": group_id,
        "comparison_design": (
            "protocol-bound-shared-runtime-baseline-v1"
            if nested_runtime_baseline
            else "protocol-bound-shared-baseline-v3"
        ),
        "baseline_reuse_policy": (
            "one accepted bare OpenCode runtime sample per sequence, protocol fingerprint, and replicate is shared by OpenCode-native tool treatments"
            if nested_runtime_baseline
            else "one operationally valid canonical baseline-bare-codex provider sample per causal comparison fingerprint and replicate is shared by all treatment comparisons; verifier/review outcomes and execution date do not select the sample"
        ),
        "baseline_profile_id": baseline_profile_id,
        "baseline_protocol_fingerprint": protocol_fingerprint,
        "replicate_count": 1,
        "uncertainty": None,
        "claim_status": "single-run-screening",
        "eligible_for_ranking": False,
        "sequence_id": seq["id"],
        "baseline_session_id": baseline["session_id"],
        "treatment_session_id": treatment["session_id"],
        "baseline_total_provider_tokens": b_tokens,
        "treatment_total_provider_tokens": t_tokens,
        "delta_total_provider_tokens": delta,
        "delta_percent": percent_delta(delta, b_tokens),
        "baseline_freshish_tokens": b_freshish,
        "treatment_freshish_tokens": t_freshish,
        "delta_freshish_tokens": freshish_delta,
        "delta_freshish_percent": percent_delta(freshish_delta, b_freshish),
        "baseline_accepted": baseline.get("interpretation", {}).get("accepted_for_objective"),
        "treatment_accepted": treatment.get("interpretation", {}).get("accepted_for_objective"),
        "model_behavior_diagnostics": {
            "baseline_tasks_passed": baseline.get("software_quality", {}).get("tasks_passed"),
            "treatment_tasks_passed": treatment.get("software_quality", {}).get("tasks_passed"),
            "task_count": len(seq["tasks"]),
        },
        "interpretation": f"Single-run token screening observation only; do not treat one pair as a population estimate. Negative token deltas mean {treatment_profile_id} used fewer provider-reported tokens than the compatible retained baseline. Structured verifier and review outcomes are diagnostic and do not select the pair. Freshish tokens are fresh_input_tokens + output_tokens for a cache-adjusted secondary view.",
    }
    out = ROOT / "sources/evaluations/workflow-sessions" / f"{comparison['comparison_id']}.json"
    atomic_create_json(out, comparison)
    return comparison


def run_one(args: argparse.Namespace) -> dict[str, Any]:
    """Serialize every direct provider run from slot check through publication."""
    clear_ambient_git_object_environment()
    if args.prepare_only:
        return _run_one_locked(args)
    selected_sequence = load_sequence(args.sequence_id)
    require_zero_mistake_pilot_replicate(
        selected_sequence,
        args.profile_id,
        args.replicate_index,
        prepare_only=False,
    )
    if args.profile_id == "baseline-bare-codex":
        pilot_allowed, pilot_reason = baseline_v2_pilot_run_gate(
            selected_sequence,
            replicate_index=args.replicate_index,
        )
        if not pilot_allowed:
            raise ValueError(f"baseline provider run is blocked: {pilot_reason}")
    current_baseline_replication = (
        args.profile_id == "baseline-bare-codex"
        and args.replicate_index > 0
        and selected_sequence.get("task_family_generation") in {"baseline-v3", "baseline-v4", "lifecycle-v1"}
    )
    if current_baseline_replication:
        checkout_errors = paid_launch_checkout_errors(ROOT)
        if checkout_errors:
            raise ValueError("paid launch checkout gate failed: " + "; ".join(checkout_errors))
    lock_fd = acquire_provider_production_lock()
    try:
        return _run_one_locked(args)
    finally:
        os.close(lock_fd)


def _run_one_locked(args: argparse.Namespace) -> dict[str, Any]:
    validate_default_model_condition()
    validate_run_safety_args(args)
    seq = load_sequence(args.sequence_id)
    if seq.get("status") != "active" and not args.prepare_only:
        raise ValueError(f"workflow sequence {seq['id']} is not active; only prepare-only is allowed")
    if seq["fixture_id"] not in PROJECT_META:
        raise ValueError(f"No runner metadata for fixture {seq['fixture_id']}")
    profile_id = args.profile_id
    baseline_control_profile = profile_id in {"baseline-bare-codex", "baseline-claude-code-no-mcp"}
    if profile_id not in PROFILE_META:
        raise ValueError(f"No runner metadata for profile {profile_id}")
    standalone_opencode_control = standalone_opencode_control_authorized(
        profile_id,
        args.replicate_index,
        ROOT,
        sequence_id=seq["id"],
    )
    if not baseline_control_profile and not standalone_opencode_control:
        require_baseline_v2_treatment_gate(seq, ROOT)
    validate_protocol_for_run(seq, profile_id, args)
    comparison_baseline_session_id = ""
    if not args.prepare_only:
        registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
        assert_pool_slot_available(registry, seq, profile_id, args.replicate_index)
        if not baseline_control_profile and not standalone_opencode_control:
            comparison_baseline_session_id = require_reusable_treatment_baseline(
                registry,
                seq,
                args.replicate_index,
                ROOT,
                profile_id=profile_id,
            )["session_id"]
    project_id = PROJECT_META[seq["fixture_id"]]["project_id"]
    protocol_fingerprint = baseline_protocol_fingerprint(seq)
    protocol_path = args.protocol_path
    protocol_doc = args.protocol_doc
    selected_execution = protocol_doc["selected_execution"]
    selected_descriptor = selected_execution["descriptor"]
    runtime_docker_image = frozen_runtime_image_ref(protocol_doc)
    frozen_protocol = {
        "protocol_id": protocol_doc.get("protocol_id"),
        "path": rel(protocol_path),
        "sha256": _protocol_file_hash(protocol_path),
    }
    baseline_pool = {
        "protocol_version": BASELINE_POOL_PROTOCOL_VERSION,
        "protocol_fingerprint": protocol_fingerprint,
        "identity_policy": "frozen-protocol-and-replicate; execution date is metadata only",
    }
    study_id = args.study_id or default_study_id(profile_id)
    comparison_profile_id = (
        ""
        if standalone_opencode_control
        else args.comparison_profile_id or (profile_id if profile_id != "baseline-bare-codex" else "")
    )
    if args.prepare_only and not args.session_id:
        stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%S%fZ")
        args.session_id = f"prepare-{artifact_lane_label(project_id)}-{safe_profile_key(profile_id)}-{stamp}-p{os.getpid()}"
    if profile_id == "baseline-bare-codex":
        session_id = args.session_id or canonical_baseline_session_id(project_id, args.replicate_index, protocol_fingerprint)
        experiment_group_id = args.experiment_group_id or canonical_baseline_group_id(project_id, args.replicate_index, protocol_fingerprint)
    else:
        session_id = args.session_id or canonical_treatment_session_id(project_id, profile_id, args.replicate_index, protocol_fingerprint)
        experiment_group_id = args.experiment_group_id or treatment_experiment_group_id(project_id, profile_id, args.replicate_index, protocol_fingerprint)
    run_dir = ROOT / "sources/evaluations/workflow-sessions" / session_id
    if run_dir.exists():
        raise FileExistsError(
            f"workflow session directory already exists: {run_dir}; use a new replicate/session ID instead of overwriting evidence"
        )
    if profile_id != "baseline-bare-codex" and comparison_profile_id:
        comparison_id = f"baseline-{artifact_lane_label(project_id)}-{DATE.replace('-', '')}-vs-{artifact_profile_label(comparison_profile_id)}-p-{protocol_fingerprint}-r{args.replicate_index}"
        comparison_path = ROOT / "sources/evaluations/workflow-sessions" / f"{comparison_id}.json"
        if comparison_path.exists():
            raise FileExistsError(f"workflow comparison already exists; use a new replicate index: {comparison_path}")
    run_dir.mkdir(parents=True, exist_ok=True)
    project = run_dir / "project"
    prompt_dir = run_dir / "task-prompts"
    prompt_dir.mkdir(exist_ok=True)

    create_project(seq, project, run_dir, conceal_seed_origin=not args.no_conceal_seed_origin)
    instruction_manifest = None
    if profile_runtime_id(profile_id) == "claude-code":
        instruction_manifest = fixture.prepare_claude_project_instructions(project / "repo", run_dir)
    verifier = write_verifier(seq, run_dir, project)
    expected_verifier_hashes = snapshot_verifier_hashes(seq, run_dir, run_dir)
    record = base_record(session_id, seq, profile_id, project, run_dir)
    if instruction_manifest is not None:
        record["setup"]["project_instruction_files"] = instruction_manifest
    record["task"]["verifier_command"] = rel(verifier)
    record_path = run_dir / "run-record-input.json"
    record_path.write_text(json.dumps(record, indent=2) + "\n")

    protocol = fixture.evaluation_protocol(record, profile_id, PROFILE_META[profile_id]["tool_state"], PROFILE_META[profile_id]["tool_use_policy"])
    protocol["prompt_delivery"] = "sequential-one-task-at-a-time"
    protocol["seed_origin_concealment"] = not args.no_conceal_seed_origin
    (run_dir / "evaluation-protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")

    codex_home_root = run_dir / "codex-homes"
    runtime_id = profile_runtime_id(profile_id)
    codex_home = (
        fixture.prepare_claude_home(profile_id, run_dir, codex_home_root)
        if runtime_id == "claude-code"
        else fixture.prepare_codex_home(record, profile_id, run_dir, args.source_codex_home, codex_home_root, copy_auth=True)
    )
    cfg = fixture.active_tool_config(record, profile_id)

    if not args.skip_container_preflight:
        container_preflight = fixture.check_container_runtime("docker", runtime_docker_image, run_dir, False, build_image=False, dockerfile=fixture.DEFAULT_DOCKERFILE, codex_home=codex_home, cfg=cfg, agent_runtime=runtime_id)
        if not container_preflight.get("passed"):
            return finalize_failed_attempt({"session_id": session_id, "profile_id": profile_id, "accepted": False, "stage": "container-preflight", "run_dir": rel(run_dir), "container_preflight": container_preflight}, record, run_dir)
    integration = fixture.prepare_profile_integration(
        record,
        profile_id,
        codex_home,
        run_dir,
        backend="docker",
        docker_image=runtime_docker_image,
    )
    if not integration.get("passed"):
        return finalize_failed_attempt({"session_id": session_id, "profile_id": profile_id, "accepted": False, "stage": "host-integration", "run_dir": rel(run_dir), "host_integration": integration}, record, run_dir)
    preflight: dict[str, Any] = {"passed": None, "skipped": True}
    if not args.skip_codex_preflight:
        preflight = (
            fixture.preflight_claude_code(
                record,
                codex_home,
                profile_id,
                run_dir,
                backend="docker",
                docker_image=runtime_docker_image,
                cfg=cfg,
            )
            if runtime_id == "claude-code"
            else fixture.preflight_codex(record, codex_home, profile_id, run_dir, backend="docker", docker_image=runtime_docker_image)
        )
        redact_auth_sync(run_dir)
        if not preflight.get("passed"):
            return finalize_failed_attempt({"session_id": session_id, "profile_id": profile_id, "accepted": False, "stage": "codex-preflight", "run_dir": rel(run_dir), "preflight": preflight}, record, run_dir)
    if not args.skip_dependency_install:
        deps_code = docker_setup_deps(seq, record, codex_home, run_dir, runtime_docker_image)
        if deps_code != 0:
            return finalize_failed_attempt({"session_id": session_id, "profile_id": profile_id, "accepted": False, "stage": "setup-deps", "setup_deps_exit_code": deps_code, "run_dir": rel(run_dir)}, record, run_dir)

    warmup_code = fixture.prepare_profile_workspace(
        record,
        profile_id,
        codex_home,
        run_dir,
        protocol,
        backend="docker",
        docker_image=runtime_docker_image,
    )
    if warmup_code != 0:
        return finalize_failed_attempt({"session_id": session_id, "profile_id": profile_id, "accepted": False, "stage": "tool-warmup", "tool_warmup_exit_code": warmup_code, "run_dir": rel(run_dir)}, record, run_dir)

    handshake = fixture.probe_mcp_handshake(
        record,
        profile_id,
        codex_home,
        run_dir,
        backend="docker",
        docker_image=runtime_docker_image,
    )
    if not handshake.get("passed"):
        return finalize_failed_attempt({"session_id": session_id, "profile_id": profile_id, "accepted": False, "stage": "mcp-handshake", "run_dir": rel(run_dir), "mcp_handshake": handshake}, record, run_dir)

    ordered_tasks = sorted(seq["tasks"], key=lambda item: item["order"])

    if args.prepare_only:
        first_task = ordered_tasks[0]
        first_order = int(first_task["order"])
        materialize_task_prompt(
            prompt_dir,
            first_order,
            task_prompt(seq, profile_id, run_dir, first_order, first_task=True),
        )
        prepare_verification = json.loads((run_dir / "prepare-verification.json").read_text())
        redact_auth_sync(run_dir)
        remove_ephemeral_homes(run_dir)
        result = {
            "session_id": session_id,
            "profile_id": profile_id,
            "sequence_id": seq["id"],
            "prepared": bool(prepare_verification.get("passed")),
            "prepare_verification": prepare_verification,
            "host_integration": integration,
            "mcp_handshake": handshake,
            "codex_preflight": preflight,
            "tool_warmup_exit_code": warmup_code,
        }
        chmod_tree(run_dir)
        shutil.rmtree(run_dir)
        return result

    if profile_id == "baseline-bare-codex" and seq.get("task_family_generation") in {"baseline-v3", "baseline-v4", "lifecycle-v1"}:
        reserve_baseline_pilot_attempt(
            seq,
            root=ROOT,
            orchestrator="direct-runner",
            replicate_index=args.replicate_index,
        )

    thread_id: str | None = None
    codex_exit_codes: list[int] = []
    task_checkpoints: list[dict[str, Any]] = []
    thread_continuity_errors: list[dict[str, Any]] = []
    verifier_integrity_checks: list[dict[str, Any]] = []
    model_output_dir = model_output_directory(run_dir)
    operational_retries = (
        0
        if profile_id == "baseline-bare-codex"
        and args.replicate_index > 0
        and seq.get("task_family_generation") in {"baseline-v3", "baseline-v4", "lifecycle-v1"}
        else MAX_CODEX_OPERATIONAL_RETRIES
    )
    for task in ordered_tasks:
        order = int(task["order"])
        prompt_path = materialize_task_prompt(
            prompt_dir,
            order,
            task_prompt(seq, profile_id, run_dir, order, first_task=order == 1),
        )
        event_stem = "claude-events" if runtime_id == "claude-code" else "codex-events"
        events_path = run_dir / f"task-{order:02d}-{event_stem}.jsonl"
        last_message_path = model_output_dir / f"task-{order:02d}-{event_stem.replace('events', 'last-message')}.txt"
        requested_thread_id = thread_id
        code, thread_id, continuity_error = run_codex_task(
            record,
            profile_id,
            codex_home,
            run_dir,
            runtime_docker_image,
            prompt_path,
            events_path,
            last_message_path,
            timeout=args.timeout_per_task,
            thread_id=requested_thread_id,
            operational_retries=operational_retries,
        )
        codex_exit_codes.append(code)
        redact_auth_sync(run_dir)
        cfg = fixture.active_tool_config(record, profile_id)
        excluded_paths = treatment_diff_exclude_paths(cfg, profile_id)
        capture_task_delta(project / "repo", run_dir, order, excluded_paths)
        integrity = {"stage": f"after-task-{order:02d}", **check_verifier_integrity(expected_verifier_hashes)}
        verifier_integrity_checks.append(integrity)
        if continuity_error is not None:
            continuity_error = {
                "order": order,
                "task_id": task["id"],
                "requested_thread_id": requested_thread_id,
                **continuity_error,
            }
            thread_continuity_errors.append(continuity_error)
            (run_dir / f"task-{order:02d}-thread-continuity-error.txt").write_text(
                json.dumps(continuity_error, indent=2) + "\n"
            )
        elif thread_id is None:
            message = f"Codex task {order} exited {code} but no thread_id was captured; refusing to continue because workflow continuity is unproven."
            thread_continuity_errors.append({"order": order, "task_id": task["id"], "message": message})
            (run_dir / f"task-{order:02d}-thread-continuity-error.txt").write_text(message + "\n")
        task_checkpoints.append({
            "task_id": task["id"],
            "task_class": task["task_class"],
            "task_alias": task_alias(order),
            "order": order,
            "agent_attempted": True,
            "codex_exit_code": code,
            "thread_continuity_passed": continuity_error is None and thread_id is not None,
            "thread_id": thread_id,
            "controller_verification": "deferred-to-final",
            "accepted": None,
            "task_delta": rel(run_dir / f"task-{order:02d}-agent.diff"),
            "usage_events": rel(events_path),
            "operational_retry_count": len(list(prompt_dir.glob(f"task-{order:02d}-operational-retry-*.md"))),
        })
        if not task_checkpoint_allows_continue(
            codex_exit_code=code,
            thread_id=thread_id,
            verifier_integrity_passed=bool(integrity["passed"]),
        ):
            break

    final_integrity = {"stage": "before-final-verifier", **check_verifier_integrity(expected_verifier_hashes)}
    verifier_integrity_checks.append(final_integrity)
    (run_dir / "verifier-integrity.json").write_text(json.dumps({"checks": verifier_integrity_checks}, indent=2) + "\n")
    verifier_integrity_passed = all(check["passed"] for check in verifier_integrity_checks)
    events_artifact = concatenate_events(run_dir, len(ordered_tasks), runtime_id=runtime_id)
    usage = build_provider_usage(profile_id, events_artifact)
    (run_dir / "provider-usage.json").write_text(json.dumps(usage, indent=2) + "\n")
    task_checkpoints = complete_task_checkpoints(ordered_tasks, task_checkpoints)
    verifier_results: list[dict[str, Any]] = []
    verifier_ready = verifier_integrity_passed
    if verifier_ready:
        final_verifier_code = run_final_verifier(
            seq, record, codex_home, run_dir, runtime_docker_image
        )
        try:
            verifier_results = parse_task_verifier_results(
                seq, run_dir / "final-verifier-output.txt"
            )
        except ValueError as exc:
            (run_dir / "final-verifier-results-error.txt").write_text(f"{exc}\n")
            final_verifier_code = 1
    else:
        final_verifier_code = 1
    task_checkpoints = apply_task_verifier_results(task_checkpoints, verifier_results)
    (run_dir / "final-verifier-results.json").write_text(
        json.dumps({"tasks": verifier_results}, indent=2) + "\n"
    )
    capture_diff(record, run_dir)
    audit_code = audit(record_path, run_dir)
    # Provider-backed token accounting is valid when the lane completed
    # operationally with clean integrity and complete usage. Verifier outcomes
    # describe model behavior; they do not gate the token-usage sample.
    accepted = (
        all(code == 0 for code in codex_exit_codes)
        and not thread_continuity_errors
        and len(task_checkpoints) == len(ordered_tasks)
        and audit_code == 0
        and verifier_integrity_passed
        and not usage.get("warnings")
    )
    agent_runtime_version = runtime_version_from_preflight(profile_id, run_dir)
    lane_contract = warm_lane_contract(seq)
    prepare_state = json.loads(seed_delivery_path(run_dir).read_text())
    concealment_verified = bool(prepare_state.get("concealment", {}).get("passed"))
    prompt_delivery = {
        "mode": "sequential-one-task-at-a-time",
        "future_tasks_visible": False,
        "future_prompts_materialized_lazily": True,
        "seed_delivery_mode": lane_contract["seed_delivery_mode"],
        "future_seed_regressions_visible": lane_contract["future_seed_regressions_visible"],
        "controller_verification": lane_contract["controller_verification"],
        "codex_thread_id": thread_id,
        "task_prompt_evidence": rel(run_dir / "evidence.jsonl.gz"),
    }
    generation = seq.get("task_family_generation")
    if generation == "lifecycle-v1":
        acceptance_visibility_limit = (
            "Future semantic regression code is present from lane start. Agent prompts state normal software objectives and do not disclose controller scoring. Affected-component compile commands and controller verifier scripts remain controller-only; no acceptance-test assets are injected."
        )
    elif generation in {"baseline-v2", "baseline-v3", "baseline-v4"}:
        acceptance_visibility_limit = (
            "Future regression code and declared focused acceptance tests are present from lane start; future prompts, seed patches, and controller verifier scripts remain controller-only."
        )
    else:
        acceptance_visibility_limit = (
            "Future regression code is present from lane start, while future prompts and concealed acceptance assets remain controller-only."
        )
    leakage_controls = {
        "seed_origin_concealed": not args.no_conceal_seed_origin,
        "seed_patches_model_visible": False,
        "git_baseline_true_root_at_lane_start": concealment_verified,
        "fixed_snapshot_objects_model_visible": False,
        "pre_seed_reflog_entries_visible": False,
        "concealment_verification_passed": concealment_verified,
        "task_directories_model_visible": False,
        "controller_verifier_scripts_and_canonical_copies_model_visible": False,
        "model_visible_acceptance_asset_paths": sequence_model_visible_acceptance_paths(seq),
        "model_writable_surface": "target repository plus isolated model-output directory",
        "verifier_integrity_passed": verifier_integrity_passed,
        "verifier_integrity_evidence": f"{rel(run_dir / 'evidence.jsonl.gz')}#verifier-integrity.json",
        "model_prompts_sanitized": True,
        "upstream_remote_removed_from_model_facing_repo": not args.no_conceal_seed_origin,
        "broken_start_committed_as_local_baseline": not args.no_conceal_seed_origin,
        "remaining_limitations": [
            acceptance_visibility_limit,
            "Task semantics and verifier names may still be searchable if the model intentionally uses external network access.",
        ],
    }
    summary = {
        "session_id": session_id,
        "study_id": study_id,
        "experiment_group_id": experiment_group_id,
        "replicate_index": args.replicate_index,
        "frozen_protocol": frozen_protocol,
        "baseline_pool": baseline_pool,
        "selected_execution": selected_execution,
        "agent_condition": selected_descriptor.get("agent_condition"),
        "docker_image_identity": selected_descriptor.get("runtime", {}).get("docker_image_identity"),
        "tool_adapter_identity": selected_descriptor.get("tool_adapter") if not baseline_control_profile else None,
        "profile_id": profile_id,
        "workflow_sequence_id": seq["id"],
        "fixture_id": seq["fixture_id"],
        "repository_path": rel(project / "repo"),
        "codex_exit_codes": codex_exit_codes,
        "final_verifier_exit_code": final_verifier_code,
        "tool_isolation_audit_exit_code": audit_code,
        "verifier_integrity_passed": verifier_integrity_passed,
        "thread_continuity_errors": thread_continuity_errors,
        "seed_delivery": {
            "mode": lane_contract["seed_delivery_mode"],
            "future_seed_regressions_visible": lane_contract["future_seed_regressions_visible"],
            "preseeded_task_orders": lane_contract["preseeded_task_orders"],
            "pending_seed_orders": [],
        },
        "accepted": accepted,
        "timeout_seconds": args.timeout_per_task * len(ordered_tasks),
        "codex_version": agent_runtime_version if profile_runtime_id(profile_id) == "codex-cli" else "",
        "agent_runtime_version": agent_runtime_version,
        "token_usage": {
            "measurement_source": usage.get("measurement_source"),
            **{key: usage.get(key) for key in PILOT_PROVIDER_USAGE_FIELDS},
            "provider_usage_details": usage.get("provider_usage_details"),
        },
        "usage_warnings": usage.get("warnings"),
        "per_task_results": task_checkpoints,
        "prompt_delivery": prompt_delivery,
        "leakage_controls": leakage_controls,
        "artifacts": compact_artifacts(run_dir),
        "run_dir": rel(run_dir),
    }
    session_record = workflow_session_record(
        seq,
        summary,
        run_dir,
        profile_id,
        codex_exit_codes,
        final_verifier_code,
        audit_code,
        usage,
        task_checkpoints,
        prompt_delivery=prompt_delivery,
        leakage_controls=leakage_controls,
        comparison_baseline_session_id=comparison_baseline_session_id,
    )
    remove_ephemeral_homes(run_dir)
    (run_dir / "run.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_evidence_bundle(run_dir)
    remove_noncompact_artifacts(run_dir)
    write_manifest(run_dir)
    publish_session_after_strict_ingress(session_record, run_dir)
    write_comparison_if_ready(seq, study_id, args.replicate_index, comparison_profile_id) if comparison_profile_id else None
    print(json.dumps(summary, indent=2), flush=True)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Manual rerun guide: docs/evaluations/operations/runner-reference.md. "
            "For shared-baseline and treatment orchestration use: "
            "python3 scripts/run_sequential_workflow_matrix.py [sequence-id] --treatment-profile <profile-id>."
        ),
    )
    parser.add_argument("--sequence-id")
    parser.add_argument("--profile-id", choices=sorted(PROFILE_META), default="baseline-bare-codex")
    parser.add_argument("--list-sequences", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--protocol", help="required frozen protocol path or id for provider-backed runs")
    parser.add_argument("--no-provider", action="store_true", help="prepare-only proof mode; forces provider-spend setup steps off")
    parser.add_argument("--timeout-per-task", type=int, default=3600)
    parser.add_argument("--replicate-index", type=int, default=0)
    parser.add_argument("--session-id")
    parser.add_argument("--study-id")
    parser.add_argument("--experiment-group-id")
    parser.add_argument("--comparison-profile-id", choices=sorted(PROFILE_META), help="treatment profile used to group baseline/treatment comparison records")
    parser.add_argument("--docker-image", default=DEFAULT_DOCKER_IMAGE)
    parser.add_argument("--source-codex-home", type=Path, default=DEFAULT_SOURCE_CODEX_HOME)
    parser.add_argument("--skip-container-preflight", action="store_true")
    parser.add_argument("--skip-codex-preflight", action="store_true")
    parser.add_argument("--skip-dependency-install", action="store_true")
    parser.add_argument("--no-conceal-seed-origin", action="store_true", help="debug only: leave seed patch as visible git diff; prepare-only runs only")
    args = parser.parse_args(argv)
    if args.no_provider:
        args.skip_dependency_install = True
    if args.list_sequences:
        print(json.dumps({"active_sequences": active_sequence_ids(), "profiles": sorted(PROFILE_META)}, indent=2))
        return 0
    if not args.sequence_id:
        parser.error("--sequence-id is required unless --list-sequences is used")
    try:
        selected_sequence = load_sequence(args.sequence_id)
    except KeyError:
        parser.error(f"unknown workflow sequence: {args.sequence_id}")
    if selected_sequence.get("status") != "active" and not args.prepare_only:
        parser.error(f"workflow sequence {args.sequence_id} is not active; only prepare-only is allowed")
    result = run_one(args)
    if args.prepare_only:
        print(json.dumps(result, indent=2))
        return 0 if result.get("prepared") is True else 1
    if result.get("prepared"):
        print(json.dumps(result, indent=2))
        return 0
    return 0 if result.get("accepted") else 1


if __name__ == "__main__":
    raise SystemExit(main())
