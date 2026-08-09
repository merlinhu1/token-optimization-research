#!/usr/bin/env python3
"""Run multiple sequential workflow shared-baseline lanes in isolated parallel checkouts.

This is the concurrency wrapper for whatever workflow sequences are currently active.
Each flow runs in its own rsync-materialized checkout so parallel runs do not race on
`data/workflow-sessions.json`, workflow-session artifact directories, Codex home
roots, tool caches, or Truthmark temporary outputs. After lanes finish, this
controller copies the lane artifacts back and merges only the produced workflow
session records into the controller checkout.
"""
from __future__ import annotations

import argparse
import atexit
import concurrent.futures as futures
from contextlib import contextmanager
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_codex_workflow_evaluation as workflow  # type: ignore
import run_codex_workflow_model_condition as model_condition_launcher  # type: ignore
import run_opencode_workflow_model_condition as opencode_condition_launcher  # type: ignore
import run_claude_code_workflow_model_condition as claude_condition_launcher  # type: ignore
import workflow_model_condition_runtime as condition_runtime  # type: ignore
DEFAULT_LANE_ROOT = Path("/opt/data/eval-workflow-lanes")
OPENCODE_BASELINE_AUTHORITY_REL = Path(
    "sources/evaluations/audits/opencode-dcp-qualification-and-r2-authorization-20260730.json"
)
OPENCODE_BASELINE_ATTEMPT_DIR = Path("sources/evaluations/audits/opencode-bare-r2-attempts")
OPENCODE_LIFECYCLE_V1_ATTEMPT_DIRS = {
    0: Path("sources/evaluations/audits/lifecycle-v1-opencode-sol-high-r0-attempts"),
    1: Path("sources/evaluations/audits/lifecycle-v1-opencode-sol-high-r1-attempts"),
    2: Path("sources/evaluations/audits/lifecycle-v1-opencode-sol-high-r2-attempts"),
}
OPENCODE_LIFECYCLE_V1_R1_ATTEMPT_DIR = OPENCODE_LIFECYCLE_V1_ATTEMPT_DIRS[1]
OPENCODE_LIFECYCLE_V1_R1_RECOVERY_AUTHORITY_REL = (
    "sources/evaluations/audits/lifecycle-v1-opencode-sol-high-r1-fastify-no-provider-recovery-authorization-20260802.json"
)
OPENCODE_LIFECYCLE_V1_R2_BEETS_RETRY_AUTHORITY_REL = (
    "sources/evaluations/audits/lifecycle-v1-opencode-sol-high-r2-beets-retry-authorization-20260802.json"
)
OPENCODE_LIFECYCLE_V1_R2_BEETS_RETRY_ATTEMPT_REL = (
    "sources/evaluations/audits/lifecycle-v1-opencode-sol-high-r2-attempts/beets-r2-retry-1.json"
)
CLAUDE_BASELINE_AUTHORITY_REL = Path(
    "sources/evaluations/audits/claude-code-sol-high-normal-baseline-authorization-20260731.json"
)
CLAUDE_LIFECYCLE_V1_AUTHORITY_REL = Path(
    "sources/evaluations/audits/claude-code-lifecycle-v1-sol-high-r0-authorization-20260802.json"
)
CLAUDE_LIFECYCLE_V1_ATTEMPT_DIR = Path(
    "sources/evaluations/audits/claude-code-lifecycle-v1-sol-high-r0-attempts"
)
CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER = (
    "fastify-lifecycle-sequence-v1",
    "beets-lifecycle-sequence-v1",
)
CLAUDE_LIFECYCLE_V1_MODEL_CONDITION = {
    "id": "claude-code-openrouter-gpt-5-6-sol-high",
    "runtime_id": "claude-code",
    "provider": "openrouter",
    "model": "gpt-5.6-sol",
    "reasoning_effort": "high",
}
CLAUDE_ANTHROPIC_SONNET_5_HIGH_CONDITION_ID = "claude-code-anthropic-sonnet-5-high"
CLAUDE_ANTHROPIC_PREPARATION_REL = Path(
    "sources/evaluations/audits/claude-code-anthropic-sonnet-5-high-lifecycle-v1-protocol-preparation-20260808.json"
)
CLAUDE_ANTHROPIC_AUTHORIZATION_REL = Path(
    "sources/evaluations/audits/claude-code-anthropic-sonnet-5-high-lifecycle-v1-baseline-authorization-20260808.json"
)
CLAUDE_ANTHROPIC_ATTEMPT_DIR = Path(
    "sources/evaluations/audits/claude-code-anthropic-sonnet-5-high-lifecycle-v1-attempts"
)
CLAUDE_ANTHROPIC_SONNET_TREATMENT_ATTEMPT_DIR = Path(
    "sources/evaluations/audits/claude-code-anthropic-sonnet-5-high-lifecycle-v1-treatment-attempts"
)
CLAUDE_ANTHROPIC_OPUS_5_HIGH_CONDITION_ID = "claude-code-anthropic-opus-5-high"
CLAUDE_ANTHROPIC_OPUS_PREPARATION_REL = Path(
    "sources/evaluations/audits/claude-code-anthropic-opus-5-high-lifecycle-v1-protocol-preparation-20260808.json"
)
CLAUDE_ANTHROPIC_OPUS_AUTHORIZATION_REL = Path(
    "sources/evaluations/audits/claude-code-anthropic-opus-5-high-lifecycle-v1-baseline-authorization-20260808.json"
)
CLAUDE_ANTHROPIC_OPUS_ATTEMPT_DIR = Path(
    "sources/evaluations/audits/claude-code-anthropic-opus-5-high-lifecycle-v1-attempts"
)
WORKFLOW_ARTIFACT_ROOT = Path("sources/evaluations/workflow-sessions")
COMPACT_ARTIFACT_NAMES = {"run.json", "changes.diff", "evidence.jsonl.gz", "manifest.sha256"}


class UnsafeLaneOutputError(ValueError):
    """The provider-capable lane changed a controller output path unsafely."""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def direct_anthropic_campaign(model_condition_id: str | None) -> dict[str, Any] | None:
    campaigns = {
        CLAUDE_ANTHROPIC_SONNET_5_HIGH_CONDITION_ID: {
            "preparation": CLAUDE_ANTHROPIC_PREPARATION_REL,
            "authorization": CLAUDE_ANTHROPIC_AUTHORIZATION_REL,
            "attempt_dir": CLAUDE_ANTHROPIC_ATTEMPT_DIR,
            "campaign_id": "claude-code-anthropic-sonnet-5-high-lifecycle-v1",
            "model_condition": {
                "id": CLAUDE_ANTHROPIC_SONNET_5_HIGH_CONDITION_ID,
                "runtime_id": "claude-code",
                "provider": "anthropic",
                "model": "claude-sonnet-5",
                "reasoning_effort": "high",
            },
        },
        CLAUDE_ANTHROPIC_OPUS_5_HIGH_CONDITION_ID: {
            "preparation": CLAUDE_ANTHROPIC_OPUS_PREPARATION_REL,
            "authorization": CLAUDE_ANTHROPIC_OPUS_AUTHORIZATION_REL,
            "attempt_dir": CLAUDE_ANTHROPIC_OPUS_ATTEMPT_DIR,
            "campaign_id": "claude-code-anthropic-opus-5-high-lifecycle-v1",
            "model_condition": {
                "id": CLAUDE_ANTHROPIC_OPUS_5_HIGH_CONDITION_ID,
                "runtime_id": "claude-code",
                "provider": "anthropic",
                "model": "claude-opus-5",
                "reasoning_effort": "high",
            },
        },
    }
    return campaigns.get(model_condition_id)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def baseline_reuse_state(session: dict[str, Any] | None, root: Path = ROOT) -> str:
    return workflow.reviewed_session_reuse_state(session, root)


def find_baseline_record(
    registry: dict[str, Any],
    seq: dict[str, Any],
    replicate_index: int,
    profile_id: str = "baseline-bare-codex",
) -> dict[str, Any] | None:
    if profile_id == "baseline-bare-codex":
        return workflow.find_canonical_baseline_record(registry, seq, replicate_index)
    return workflow.find_pool_profile_record(registry, seq, profile_id, replicate_index)


def baseline_campaign_state(
    registry: dict[str, Any],
    seq: dict[str, Any],
    replicate_index: int,
    baseline_profile_id: str = "baseline-bare-codex",
    root: Path = ROOT,
) -> str:
    """Separate reusable-baseline selection from replicate occupancy."""
    baseline = find_baseline_record(registry, seq, replicate_index, baseline_profile_id)
    if baseline is not None:
        return baseline_reuse_state(baseline, root)
    occupied = workflow.find_pool_profile_record(
        registry,
        seq,
        baseline_profile_id,
        replicate_index,
    )
    return workflow.reviewed_session_reuse_state(occupied, root)


def acquire_production_lock() -> int:
    lock_path = DEFAULT_LANE_ROOT / ".production.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        raise RuntimeError("another provider-capable workflow matrix is already running")
    return fd


def active_sequences() -> list[str]:
    doc = load_json(ROOT / "data/workflow-task-sequences.json")
    return [seq["id"] for seq in doc.get("sequences", []) if seq.get("status") == "active"]


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


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")


def workflow_lane_environment(tmp: Path, *, allow_auth_sync: bool = False) -> dict[str, str]:
    env = os.environ.copy()
    for name in workflow.AMBIENT_GIT_OBJECT_ENV_VARS:
        env.pop(name, None)
    env["TMPDIR"] = str(tmp)
    env["SKIP_PAIR_VALIDATION"] = "1"
    if allow_auth_sync:
        env.pop("WORKFLOW_LANE_DISABLE_AUTH_SYNC", None)
    else:
        env["WORKFLOW_LANE_DISABLE_AUTH_SYNC"] = "1"
    return env


def copytree_ignore(current: str, names: list[str]) -> set[str]:
    current_path = Path(current)
    ignored: set[str] = set()
    if ".git" in names:
        ignored.add(".git")
    parts = current_path.parts
    if "fixtures" in parts and "repo" in names:
        ignored.add("repo")
    if "workflow-sessions" in parts:
        ignored.update({name for name in names if name in {
            "project", "tasks", "controller-scratch", "codex-homes", "task-prompts", "model-output"
        }})
    if current_path.name == "audits":
        ignored.update({name for name in names if name.startswith("baseline-v") and "-pilot-attempt-" in name and name.endswith(".json")})
        if "current-low-complexity-baseline-r1-r2-attempts" in names:
            ignored.add("current-low-complexity-baseline-r1-r2-attempts")
    return ignored


def rsync_checkout(source: Path, destination: Path) -> None:
    if destination.exists():
        chmod_tree(destination)
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if shutil.which("rsync") is None:
        shutil.copytree(source, destination, ignore=copytree_ignore, symlinks=True)
        return
    cmd = [
        "rsync",
        "-a",
        "--delete",
        "--exclude=/.git/",
        "--exclude=/sources/evaluations/fixtures/*/*/repo/",
        "--exclude=/sources/evaluations/workflow-sessions/*/project/",
        "--exclude=/sources/evaluations/workflow-sessions/*/tasks/",
        "--exclude=/sources/evaluations/workflow-sessions/*/controller-scratch/",
        "--exclude=/sources/evaluations/workflow-sessions/*/codex-homes/",
        "--exclude=/sources/evaluations/workflow-sessions/*/task-prompts/",
        "--exclude=/sources/evaluations/workflow-sessions/*/model-output/",
        "--exclude=/sources/evaluations/audits/baseline-v*-pilot-attempt-*.json",
        "--exclude=/sources/evaluations/audits/current-low-complexity-baseline-r1-r2-attempts/",
        str(source.resolve()) + "/",
        str(destination.resolve()) + "/",
    ]
    subprocess.run(cmd, check=True)


def clone_published_checkout(destination: Path, expected_commit: str) -> None:
    """Materialize provider lanes only from the independently published trusted branch."""
    if destination.exists():
        chmod_tree(destination)
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    for name in workflow.AMBIENT_GIT_OBJECT_ENV_VARS:
        env.pop(name, None)
    upstream_name = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
        cwd=ROOT,
        text=True,
    ).strip()
    if not upstream_name.startswith("origin/"):
        raise ValueError("provider lane source must track a published origin branch")
    published_branch = upstream_name.removeprefix("origin/")
    published_ref = f"refs/heads/{published_branch}"
    branch_probe = subprocess.run(
        ["git", "ls-remote", workflow.TRUSTED_REPOSITORY_ORIGIN, published_ref],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if branch_probe.returncode != 0 or not any(
        line.split() == [line.split()[0], published_ref]
        for line in branch_probe.stdout.splitlines()
        if line.split()
    ):
        published_branch = workflow.TRUSTED_REPOSITORY_REF.removeprefix("refs/heads/")
    subprocess.run(
        [
            "git", "clone", "--no-local", "--single-branch", "--branch", published_branch,
            workflow.TRUSTED_REPOSITORY_ORIGIN, str(destination),
        ],
        env=env,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=destination, text=True).strip()
    if actual != expected_commit:
        raise RuntimeError(f"trusted publication branch advanced during launch: expected {expected_commit}, got {actual}")
    errors = workflow.paid_launch_checkout_errors(destination)
    if errors:
        raise RuntimeError("published lane checkout certification failed: " + "; ".join(errors))


def find_protocol(
    root: Path,
    sequence_id: str,
    profile_id: str,
    model_condition_override: dict[str, str] | None = None,
) -> Path:
    sequences = load_json(root / "data/workflow-task-sequences.json").get("sequences", [])
    active_sequence = next((item for item in sequences if item.get("id") == sequence_id), None)
    if not isinstance(active_sequence, dict) or active_sequence.get("status") != "active":
        raise ValueError(f"unknown or non-active workflow sequence: {sequence_id}")
    active_qualification = active_sequence.get("qualification_path")
    current_fingerprint = workflow.baseline_protocol_fingerprint(active_sequence)
    current_baseline_descriptor = workflow.baseline_protocol_descriptor(active_sequence)
    if model_condition_override:
        setattr(workflow, "DEFAULT_WORKFLOW_MODEL_CONDITION_ID", model_condition_override.get("id", model_condition_override.get("model_condition_id", "")))
        setattr(workflow, "DEFAULT_WORKFLOW_MODEL", model_condition_override.get("model", ""))
        setattr(workflow, "DEFAULT_WORKFLOW_REASONING_EFFORT", model_condition_override.get("reasoning_effort", ""))
    current_execution = workflow.execution_condition_descriptor(
        active_sequence,
        profile_id,
        timeout_seconds_per_task=3600,
        docker_image=workflow.DEFAULT_DOCKER_IMAGE,
    )
    compatible_matches: list[Path] = []
    exact_matches: list[Path] = []
    for path in (root / "sources/evaluations/protocols").glob("*.json"):
        protocol = load_json(path)
        selected_execution = protocol.get("selected_execution", {})
        selected = selected_execution.get("descriptor", {})
        if (
            protocol.get("status") == "frozen-ready-not-run"
            and protocol.get("task_fixture", {}).get("sequence_id") == sequence_id
            and protocol.get("task_fixture", {}).get("qualification_path") == active_qualification
            and protocol.get("baseline_pool", {}).get("protocol_fingerprint") == current_fingerprint
            and workflow.baseline_protocol_descriptor_compatible(
                protocol.get("baseline_pool", {}).get("descriptor"),
                current_baseline_descriptor,
            )
            and selected.get("selected_profile", {}).get("profile_id") == profile_id
            and selected == current_execution
            and selected_execution.get("descriptor_sha256") == workflow._json_hash(current_execution)
        ):
            compatible_matches.append(path)
            if protocol.get("baseline_pool", {}).get("descriptor") == current_baseline_descriptor:
                exact_matches.append(path)
    matches = exact_matches or compatible_matches
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one current frozen protocol for {sequence_id}/{profile_id}; "
            f"exact={[path.name for path in exact_matches]} compatible={[path.name for path in compatible_matches]}"
        )
    return matches[0]


def claude_lifecycle_v1_attempt_path(
    sequence_id: str,
    replicate_index: int,
    root: Path = ROOT,
    attempt_dir: Path = CLAUDE_LIFECYCLE_V1_ATTEMPT_DIR,
) -> Path:
    if sequence_id not in CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER or replicate_index != 0:
        raise ValueError("Claude Code Lifecycle V1 attempt identity is not authorized")
    lane = sequence_id.removesuffix("-lifecycle-sequence-v1")
    return root / attempt_dir / f"{lane}-r0.json"


def claude_lifecycle_v1_run_gate(
    registry: dict[str, Any],
    sequence_id: str,
    replicate_index: int,
    root: Path = ROOT,
) -> tuple[bool, str]:
    """Validate the owner-bound Claude Code Lifecycle V1 provider authority."""
    path = root / CLAUDE_LIFECYCLE_V1_AUTHORITY_REL
    if not path.is_file():
        return False, f"missing Claude Code Lifecycle V1 authority: {CLAUDE_LIFECYCLE_V1_AUTHORITY_REL}"
    try:
        authority = load_json(path)
    except (OSError, ValueError) as exc:
        return False, f"unreadable Claude Code Lifecycle V1 authority: {exc}"
    expected_keys = {
        "schema_version", "campaign_id", "authorized_by_owner_message_id", "authorized_on",
        "authorized_source_commit", "paid_baseline_execution_authorized", "authorized_replicate_index",
        "sequence_order", "max_parallel", "allowed_paid_baseline_runs", "allowed_model_turns",
        "serialization_required", "model_condition", "first_valid_sample_policy",
        "rerun_after_attempt_receipt", "provider_calls", "provider_tokens", "sequences", "notes",
    }
    records = authority.get("sequences")
    header_ok = (
        isinstance(authority, dict)
        and set(authority) == expected_keys
        and authority.get("schema_version") == 1
        and authority.get("campaign_id") == "claude-code-lifecycle-v1-sol-high-r0-20260802"
        and authority.get("authorized_by_owner_message_id") == "1533397324384964609"
        and authority.get("authorized_on") == "2026-08-02"
        and isinstance(authority.get("authorized_source_commit"), str)
        and len(authority["authorized_source_commit"]) == 40
        and authority.get("paid_baseline_execution_authorized") is True
        and authority.get("authorized_replicate_index") == 0
        and authority.get("sequence_order") == list(CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER)
        and authority.get("max_parallel") == 1
        and authority.get("allowed_paid_baseline_runs") == len(CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER)
        and authority.get("allowed_model_turns") == sum(
            len(workflow.load_sequence(item).get("tasks", []))
            for item in CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER
        )
        and authority.get("serialization_required") is True
        and authority.get("model_condition") == CLAUDE_LIFECYCLE_V1_MODEL_CONDITION
        and authority.get("first_valid_sample_policy") is True
        and authority.get("rerun_after_attempt_receipt") is False
        and type(authority.get("provider_calls")) is int
        and authority.get("provider_calls") == 0
        and type(authority.get("provider_tokens")) is int
        and authority.get("provider_tokens") == 0
        and isinstance(authority.get("notes"), str)
        and bool(authority.get("notes"))
    )
    binding_keys = {
        "sequence_id", "protocol_path", "protocol_sha256", "baseline_pool_fingerprint",
    }
    records_ok = (
        isinstance(records, list)
        and len(records) == len(CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER)
        and all(isinstance(item, dict) and set(item) == binding_keys for item in records)
        and [item.get("sequence_id") for item in records] == list(CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER)
    )
    if (
        not header_ok
        or not records_ok
        or replicate_index != 0
        or sequence_id not in CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER
    ):
        return False, "Claude Code Lifecycle V1 authority does not match the requested identity, scope, or budget"
    bindings = {item["sequence_id"]: item for item in records}
    for active_id in CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER:
        binding = bindings[active_id]
        protocol_path = root / str(binding["protocol_path"])
        try:
            protocol_raw = protocol_path.read_bytes()
            protocol = json.loads(protocol_raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return False, f"Claude Code Lifecycle V1 authority protocol is unreadable: {active_id}: {exc}"
        descriptor = protocol.get("selected_execution", {}).get("descriptor", {})
        agent = descriptor.get("agent_condition", {}) if isinstance(descriptor, dict) else {}
        if (
            hashlib.sha256(protocol_raw).hexdigest() != binding["protocol_sha256"]
            or protocol.get("status") != "frozen-ready-not-run"
            or protocol.get("task_fixture", {}).get("sequence_id") != active_id
            or protocol.get("baseline_pool", {}).get("protocol_fingerprint")
            != binding["baseline_pool_fingerprint"]
            or descriptor.get("selected_profile", {}).get("profile_id") != "baseline-claude-code-no-mcp"
            or agent != {
                "runtime_id": "claude-code",
                "provider": "openrouter",
                "model": "gpt-5.6-sol",
                "model_condition_id": "claude-code-openrouter-gpt-5-6-sol-high",
                "reasoning_effort": "high",
                "runtime_version_condition": "captured-at-run-and-bound-to-record",
            }
        ):
            return False, f"Claude Code Lifecycle V1 authority has stale protocol binding: {active_id}"
    try:
        receipt = claude_lifecycle_v1_attempt_path(sequence_id, replicate_index, root)
    except ValueError as exc:
        return False, str(exc)
    if receipt.exists():
        return False, f"Claude Code Lifecycle V1 identity is occupied by immutable attempt receipt: {receipt.relative_to(root)}"
    occupied = workflow.find_pool_profile_record(
        registry,
        workflow.load_sequence(sequence_id),
        "baseline-claude-code-no-mcp",
        replicate_index,
    )
    if occupied is not None:
        return False, f"Claude Code Lifecycle V1 identity is already occupied by session {occupied.get('session_id')}"
    return True, "owner-authorized Claude Code Lifecycle V1 Sol/high baseline is unoccupied"


def reserve_claude_lifecycle_v1_attempt(
    *,
    sequence_id: str,
    replicate_index: int,
    expected_session_binding: dict[str, Any],
    run_root: Path,
    root: Path = ROOT,
    model_condition: dict[str, str] | None = None,
    authority_rel: Path = CLAUDE_LIFECYCLE_V1_AUTHORITY_REL,
    attempt_dir: Path = CLAUDE_LIFECYCLE_V1_ATTEMPT_DIR,
    owner_authorization_message_id: str = "1533397324384964609",
) -> Path:
    """Reserve one immutable Claude Code Lifecycle V1 identity before a lane clone."""
    if (
        expected_session_binding.get("sequence_id") != sequence_id
        or expected_session_binding.get("profile_id") != "baseline-claude-code-no-mcp"
        or expected_session_binding.get("replicate_index") != replicate_index
        or not isinstance(expected_session_binding.get("frozen_protocol"), dict)
        or not isinstance(expected_session_binding.get("selected_execution"), dict)
    ):
        raise ValueError("Claude Code Lifecycle V1 receipt binding does not match the requested identity")
    condition = model_condition or CLAUDE_LIFECYCLE_V1_MODEL_CONDITION
    path = claude_lifecycle_v1_attempt_path(sequence_id, replicate_index, root, attempt_dir)
    if path.exists():
        raise FileExistsError(f"immutable Claude Code Lifecycle V1 attempt receipt already exists: {path}")
    payload = {
        "schema_version": 1,
        "attempt_status": "reserved-before-provider-task",
        "task_family_generation": "lifecycle-v1",
        "sequence_id": sequence_id,
        "replicate_index": replicate_index,
        "profile_id": "baseline-claude-code-no-mcp",
        "model_condition_id": condition["id"],
        "model": condition["model"],
        "reasoning_effort": condition["reasoning_effort"],
        "owner_authorization_message_id": owner_authorization_message_id,
        "authority_path": str(authority_rel),
        "orchestrator": str(run_root),
        "reserved_at": dt.datetime.now(dt.UTC).isoformat(),
        "expected_session_binding": expected_session_binding,
        "provider_result": None,
        "immutable_identity_receipt": True,
    }
    workflow.atomic_create_json(path, payload)
    return path


def claude_baseline_run_gate(
    registry: dict[str, Any],
    sequence_id: str,
    replicate_index: int,
    root: Path = ROOT,
    model_condition_id: str | None = None,
) -> tuple[bool, str]:
    campaign = direct_anthropic_campaign(model_condition_id)
    if campaign is not None:
        expected_model = campaign["model_condition"]
        preparation_rel = campaign["preparation"]
        authorization_rel = campaign["authorization"]
        attempt_dir = campaign["attempt_dir"]
        preparation_path = root / preparation_rel
        if not preparation_path.is_file():
            return False, f"missing direct-Anthropic Claude Code preparation authority: {preparation_rel}"
        try:
            preparation = load_json(preparation_path)
        except (OSError, ValueError) as exc:
            return False, f"unreadable direct-Anthropic Claude Code preparation authority: {exc}"
        condition = preparation.get("model_condition", {})
        if (
            preparation.get("status") != "frozen-provider-free-protocols-account-pending"
            or condition != {**expected_model, "runtime_version": "2.1.220"}
        ):
            return False, "direct-Anthropic Claude Code preparation authority does not match the frozen model identity"
        authorization_path = root / authorization_rel
        if not authorization_path.is_file():
            return False, f"missing direct-Anthropic Claude Code baseline authorization: {authorization_rel}"
        try:
            authorization = load_json(authorization_path)
        except (OSError, ValueError) as exc:
            return False, f"unreadable direct-Anthropic Claude Code baseline authorization: {exc}"
        account_home = os.environ.get("TOKEN_EVAL_CLAUDE_ACCOUNT_HOME")
        if not account_home or not Path(account_home).is_dir():
            return False, "direct-Anthropic Claude Code account home is not supplied through TOKEN_EVAL_CLAUDE_ACCOUNT_HOME"
        expected_protocols = {
            item.get("sequence_id"): item
            for item in authorization.get("protocols", [])
            if isinstance(item, dict)
        }
        expected_agent = {
            "runtime_id": expected_model["runtime_id"],
            "provider": expected_model["provider"],
            "model": expected_model["model"],
            "model_condition_id": expected_model["id"],
            "reasoning_effort": expected_model["reasoning_effort"],
            "runtime_version_condition": "captured-at-run-and-bound-to-record",
        }
        expected_order = list(CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER)
        header_ok = (
            authorization.get("schema_version") == 1
            and authorization.get("status") == "owner-authorized-provider-run"
            and authorization.get("campaign_id") == campaign["campaign_id"]
            and authorization.get("task_family_generation") == "lifecycle-v1"
            and authorization.get("authorized_replicate_index") == 0
            and authorization.get("sequence_order") == expected_order
            and authorization.get("max_parallel") == 1
            and authorization.get("allowed_paid_baseline_runs") == 2
            and authorization.get("allowed_model_turns") == 6
            and authorization.get("serialization_required") is True
            and authorization.get("model_condition") == expected_model
            and authorization.get("first_valid_sample_policy") is True
            and authorization.get("rerun_after_attempt_receipt") is False
            and type(authorization.get("provider_calls")) is int
            and 0 <= authorization.get("provider_calls") <= authorization.get("allowed_model_turns")
            and type(authorization.get("provider_tokens")) is int
            and authorization.get("provider_tokens") >= 0
            and isinstance(authorization.get("notes"), str)
            and bool(authorization.get("notes"))
            and [item.get("sequence_id") for item in authorization.get("protocols", []) if isinstance(item, dict)] == expected_order
        )
        if not header_ok or set(expected_protocols) != set(CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER):
            return False, "direct-Anthropic Claude Code baseline authorization does not match the bounded identity, scope, or budget"
        for active_id in CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER:
            binding = expected_protocols[active_id]
            protocol_path = root / str(binding.get("protocol_path", ""))
            try:
                protocol_raw = protocol_path.read_bytes()
                protocol = json.loads(protocol_raw)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                return False, f"direct-Anthropic baseline protocol is unreadable: {active_id}: {exc}"
            descriptor = protocol.get("selected_execution", {}).get("descriptor", {})
            agent = descriptor.get("agent_condition", {}) if isinstance(descriptor, dict) else {}
            if (
                hashlib.sha256(protocol_raw).hexdigest() != binding.get("protocol_sha256")
                or protocol.get("status") != "frozen-ready-not-run"
                or protocol.get("task_fixture", {}).get("sequence_id") != active_id
                or protocol.get("baseline_pool", {}).get("protocol_fingerprint") != binding.get("baseline_pool_fingerprint")
                or descriptor.get("selected_profile", {}).get("profile_id") != "baseline-claude-code-no-mcp"
                or agent != expected_agent
            ):
                return False, f"direct-Anthropic baseline authorization has stale protocol binding: {active_id}"
        try:
            receipt = claude_lifecycle_v1_attempt_path(
                sequence_id,
                replicate_index,
                root,
                attempt_dir,
            )
        except ValueError as exc:
            return False, str(exc)
        if receipt.exists():
            return False, f"direct-Anthropic Claude Code identity is occupied by immutable attempt receipt: {receipt.relative_to(root)}"
        occupied = next(
            (
                session
                for session in registry.get("sessions", [])
                if session.get("task_sequence", {}).get("sequence_id") == sequence_id
                and session.get("replicate_index") == replicate_index
                and session.get("profile", {}).get("profile_id") == "baseline-claude-code-no-mcp"
                and session.get("agent", {}).get("model_condition_id") == expected_model["id"]
            ),
            None,
        )
        if occupied is not None:
            return False, f"direct-Anthropic Claude Code identity is already occupied by session {occupied.get('session_id')}"
        return True, f"owner-authorized direct-Anthropic Claude Code {expected_model['model']}/high baseline is unoccupied"
    if sequence_id in CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER:
        return claude_lifecycle_v1_run_gate(registry, sequence_id, replicate_index, root)
    path = root / CLAUDE_BASELINE_AUTHORITY_REL
    if not path.is_file():
        return False, f"missing Claude Code baseline authority: {CLAUDE_BASELINE_AUTHORITY_REL}"
    try:
        authority = load_json(path)
    except (OSError, ValueError) as exc:
        return False, f"unreadable Claude Code baseline authority: {exc}"
    expected_sequences = [
        item["id"]
        for item in load_json(root / "data/workflow-task-sequences.json").get("sequences", [])
        if item.get("status") == "active"
    ]
    expected_keys = {
        "schema_version", "campaign_id", "authorized_by_owner_message_id", "authorized_on",
        "paid_baseline_execution_authorized", "authorized_replicate_index", "sequence_order",
        "max_parallel", "allowed_paid_baseline_runs", "allowed_model_turns", "serialization_required",
        "model_condition", "first_valid_sample_policy", "rerun_after_attempt_receipt", "provider_calls",
        "provider_tokens", "sequences", "notes",
    }
    model = authority.get("model_condition", {})
    header_ok = (
        set(authority) == expected_keys
        and authority.get("schema_version") == 1
        and authority.get("campaign_id") == "claude-code-sol-high-baseline-20260731"
        and authority.get("authorized_by_owner_message_id") == "1532773213061255369"
        and authority.get("authorized_on") == "2026-07-31"
        and authority.get("paid_baseline_execution_authorized") is True
        and authority.get("authorized_replicate_index") == 0
        and authority.get("sequence_order") == expected_sequences
        and authority.get("max_parallel") == 3
        and authority.get("allowed_paid_baseline_runs") == len(expected_sequences)
        and authority.get("allowed_model_turns") == sum(
            len(workflow.load_sequence(item).get("tasks", [])) for item in expected_sequences
        )
        and authority.get("serialization_required") is False
        and model == {
            "id": "claude-code-openrouter-gpt-5-6-sol-high",
            "runtime_id": "claude-code",
            "provider": "openrouter",
            "model": "gpt-5.6-sol",
            "reasoning_effort": "high",
        }
        and authority.get("first_valid_sample_policy") is True
        and authority.get("rerun_after_attempt_receipt") is False
        and authority.get("provider_calls") == 0
        and authority.get("provider_tokens") == 0
        and isinstance(authority.get("notes"), str)
        and bool(authority.get("notes"))
    )
    records = authority.get("sequences")
    records_ok = isinstance(records, list) and [item.get("sequence_id") for item in records] == expected_sequences
    if not header_ok or not records_ok or replicate_index != 0 or sequence_id not in expected_sequences:
        return False, "Claude Code baseline authority does not match the requested identity, scope, or budget"
    bindings = {item.get("sequence_id"): item for item in records}
    for active_id in expected_sequences:
        binding = bindings.get(active_id)
        if not isinstance(binding, dict):
            return False, f"Claude Code authority is missing sequence binding: {active_id}"
        protocol_path = root / str(binding.get("protocol_path", ""))
        if not protocol_path.is_file():
            return False, f"Claude Code authority protocol is missing: {binding.get('protocol_path')}"
        protocol_sha = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
        protocol = load_json(protocol_path)
        if (
            protocol_sha != binding.get("protocol_sha256")
            or protocol.get("status") != "frozen-ready-not-run"
            or protocol.get("baseline_pool", {}).get("protocol_fingerprint") != binding.get("baseline_pool_fingerprint")
        ):
            return False, f"Claude Code authority has stale protocol binding: {active_id}"
    occupied = workflow.find_pool_profile_record(
        registry, workflow.load_sequence(sequence_id), "baseline-claude-code-no-mcp", replicate_index
    )
    if occupied is not None:
        return False, f"Claude Code baseline identity is already occupied by session {occupied.get('session_id')}"
    return True, "owner-authorized Claude Code Sol/high baseline is unoccupied"


def plan_workflow_jobs(
    sequence_ids: list[str],
    treatment_profiles: list[str],
    *,
    baseline_state: Callable[[str], str],
    profile_state: Callable[[str, str], str],
    baseline_run_gate: Callable[[str], tuple[bool, str]],
    treatment_gate: Callable[[str], tuple[bool, str]] | None = None,
    baseline_profile_id: str = "baseline-bare-codex",
) -> list[tuple[str, str]]:
    """Plan baselines or treatments only after a reusable baseline and explicit pilot gate."""
    if len(set(sequence_ids)) != len(sequence_ids):
        raise ValueError("duplicate sequence IDs are not allowed in one matrix")
    if len(set(treatment_profiles)) != len(treatment_profiles):
        raise ValueError("duplicate treatment profiles are not allowed in one matrix")
    jobs: list[tuple[str, str]] = []
    for sequence_id in sequence_ids:
        state = baseline_state(sequence_id)
        if not treatment_profiles:
            if state == "missing":
                passed, reason = baseline_run_gate(sequence_id)
                if not passed:
                    raise ValueError(f"baseline provider run is blocked for {sequence_id}: {reason}")
                jobs.append((sequence_id, baseline_profile_id))
            else:
                raise ValueError(f"baseline for {sequence_id} is {state}; no new baseline run is needed")
        elif state == "reusable":
            if treatment_gate is None:
                raise ValueError("treatment planning requires an explicit zero-mistake baseline pilot gate")
            passed, reason = treatment_gate(sequence_id)
            if not passed:
                raise ValueError(f"treatments are blocked for {sequence_id}: {reason}")
            for profile in treatment_profiles:
                treatment_state = profile_state(sequence_id, profile)
                if treatment_state == "missing":
                    jobs.append((sequence_id, profile))
                elif treatment_state != "reusable":
                    raise ValueError(
                        f"treatment {profile} for {sequence_id} is {treatment_state}; review it or choose a new replicate"
                    )
        elif state == "missing":
            passed, reason = baseline_run_gate(sequence_id)
            if not passed:
                raise ValueError(f"baseline provider run is blocked for {sequence_id}: {reason}")
            jobs.append((sequence_id, baseline_profile_id))
        else:
            raise ValueError(
                f"baseline for {sequence_id} is {state}; review it or choose a new replicate before treatment execution"
            )
    return jobs


def opencode_baseline_attempt_path(
    sequence_id: str,
    replicate_index: int,
    root: Path = ROOT,
) -> Path:
    if sequence_id.endswith("-lifecycle-sequence-v1"):
        try:
            attempt_dir = OPENCODE_LIFECYCLE_V1_ATTEMPT_DIRS[replicate_index]
        except KeyError as exc:
            raise ValueError(f"no OpenCode Lifecycle V1 attempt identity for r{replicate_index}") from exc
        lane = sequence_id.removesuffix("-lifecycle-sequence-v1")
        return root / attempt_dir / f"{lane}-r{replicate_index}.json"
    lane = sequence_id.removesuffix("-lifecycle-sequence-v0")
    return root / OPENCODE_BASELINE_ATTEMPT_DIR / f"{lane}-r{replicate_index}.json"


def opencode_lifecycle_v1_r1_no_provider_recovery_authorized(
    sequence_id: str,
    replicate_index: int,
    root: Path = ROOT,
) -> bool:
    """Allow exactly the owner-authorized Fastify r1 retry after local no-provider proof."""
    if sequence_id != "fastify-lifecycle-sequence-v1" or replicate_index != 1:
        return False
    receipt_rel = (
        "sources/evaluations/audits/lifecycle-v1-opencode-sol-high-r1-attempts/fastify-r1.json"
    )
    receipt_path = root / receipt_rel
    authority_path = root / OPENCODE_LIFECYCLE_V1_R1_RECOVERY_AUTHORITY_REL
    try:
        receipt_raw = receipt_path.read_bytes()
        receipt = json.loads(receipt_raw)
        authority = json.loads(authority_path.read_text())
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    expected_receipt = {
        "attempt_status": "reserved-before-provider-task",
        "sequence_id": sequence_id,
        "replicate_index": 1,
        "profile_id": "runtime-opencode-codex-product-v1",
        "model_condition_id": "opencode-openai-gpt-5-6-sol-high",
        "provider_result": None,
    }
    contract = authority.get("recovery_contract")
    return bool(
        isinstance(receipt, dict)
        and all(receipt.get(key) == value for key, value in expected_receipt.items())
        and authority.get("schema_version") == 1
        and authority.get("status") == "owner-authorized-no-provider-recovery"
        and authority.get("owner_recovery_authorization") == {
            "source": "discord",
            "authorization_prompt_message_id": "1533351879592120481",
            "message_id": "1533353885559816214",
            "selection": "2",
        }
        and isinstance(contract, dict)
        and contract == {
            "sequence_id": sequence_id,
            "replicate_index": 1,
            "profile_id": "runtime-opencode-codex-product-v1",
            "model_condition_id": "opencode-openai-gpt-5-6-sol-high",
            "original_attempt_receipt_path": receipt_rel,
            "original_attempt_receipt_sha256": hashlib.sha256(receipt_raw).hexdigest(),
            "provider_execution_disposition": "locally-proven-no-provider-subprocess",
            "authorized_provider_run_count": 1,
            "same_replicate_recovery": True,
        }
    )



def opencode_lifecycle_v1_r2_beets_retry_authorized(root: Path = ROOT) -> bool:
    """Authorize one distinct r2 Beets retry without reusing its failed receipt."""
    sequence_id = "beets-lifecycle-sequence-v1"
    original_receipt_rel = (
        "sources/evaluations/audits/lifecycle-v1-opencode-sol-high-r2-attempts/beets-r2.json"
    )
    rejection_rel = (
        "sources/evaluations/audits/lifecycle-v1-opencode-sol-high-r2-beets-ingress-rejection-20260802.json"
    )
    fastify_session_id = "opencode-fastify-20260802-p-72ac148f730b-r2"
    try:
        original_receipt = (root / original_receipt_rel).read_bytes()
        rejection = (root / rejection_rel).read_bytes()
        authority = load_json(root / OPENCODE_LIFECYCLE_V1_R2_BEETS_RETRY_AUTHORITY_REL)
        registry = load_json(root / "data/workflow-sessions.json")
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    original = json.loads(original_receipt)
    fastify = next(
        (session for session in registry.get("sessions", []) if session.get("session_id") == fastify_session_id),
        None,
    )
    contract = authority.get("retry_contract")
    bindings = authority.get("frozen_protocols")
    if not (
        isinstance(original, dict)
        and original.get("attempt_status") == "reserved-before-provider-task"
        and original.get("sequence_id") == sequence_id
        and original.get("replicate_index") == 2
        and original.get("profile_id") == "runtime-opencode-codex-product-v1"
        and original.get("model_condition_id") == "opencode-openai-gpt-5-6-sol-high"
        and isinstance(fastify, dict)
        and fastify.get("interpretation", {}).get("accepted_for_objective") is True
        and workflow.pilot_session_artifacts_valid(fastify, root)
        and authority.get("schema_version") == 1
        and authority.get("status") == "qualified-ready-for-provider-execution"
        and authority.get("owner_authorization") == {
            "source": "discord",
            "message_id": "1533506744347656284",
            "request": "I want you to fix the R2 beets and not create R3. Re run the fixed R2 beets",
            "authorized_action": "one-r2-beets-retry-1-only",
        }
        and contract == {
            "sequence_id": sequence_id,
            "replicate_index": 2,
            "profile_id": "runtime-opencode-codex-product-v1",
            "model_condition_id": "opencode-openai-gpt-5-6-sol-high",
            "model": "gpt-5.6-sol",
            "reasoning_effort": "high",
            "serial_predecessor_session_id": fastify_session_id,
            "original_attempt_receipt_path": original_receipt_rel,
            "original_attempt_receipt_sha256": hashlib.sha256(original_receipt).hexdigest(),
            "original_rejection_audit_path": rejection_rel,
            "original_rejection_audit_sha256": hashlib.sha256(rejection).hexdigest(),
            "retry_attempt_receipt_path": str(OPENCODE_LIFECYCLE_V1_R2_BEETS_RETRY_ATTEMPT_REL),
            "authorized_provider_lane_runs": 1,
            "authorized_model_turns": 3,
            "same_replicate_lane_completion": True,
            "new_replicate_index": None,
            "rerun_after_attempt_receipt": False,
        }
        and isinstance(bindings, list)
        and len(bindings) == 1
        and isinstance(bindings[0], dict)
        and set(bindings[0]) == {
            "sequence_id", "protocol_path", "protocol_sha256", "baseline_pool_fingerprint"
        }
        and bindings[0].get("sequence_id") == sequence_id
    ):
        return False
    binding = bindings[0]
    try:
        protocol_raw = (root / str(binding["protocol_path"])).read_bytes()
        protocol = json.loads(protocol_raw)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    return bool(
        hashlib.sha256(protocol_raw).hexdigest() == binding.get("protocol_sha256")
        and protocol.get("baseline_pool", {}).get("protocol_fingerprint")
        == binding.get("baseline_pool_fingerprint")
    )


def opencode_lifecycle_v1_r2_beets_retry_attempt_path(root: Path = ROOT) -> Path:
    return root / OPENCODE_LIFECYCLE_V1_R2_BEETS_RETRY_ATTEMPT_REL


def opencode_baseline_run_gate(
    registry: dict[str, Any],
    sequence_id: str,
    replicate_index: int,
    root: Path = ROOT,
    *,
    r2_beets_retry: bool = False,
) -> tuple[bool, str]:
    if r2_beets_retry:
        if (
            sequence_id != "beets-lifecycle-sequence-v1"
            or replicate_index != 2
            or not opencode_lifecycle_v1_r2_beets_retry_authorized(root)
        ):
            return False, "r2 Beets retry does not match its exact owner authorization"
        authority = load_json(root / OPENCODE_LIFECYCLE_V1_R2_BEETS_RETRY_AUTHORITY_REL)
        ready_reason = "owner-authorized distinct r2 Beets retry-1 is unoccupied"
    elif sequence_id.endswith("-lifecycle-sequence-v1"):
        if not workflow.standalone_opencode_control_authorized(
            "runtime-opencode-codex-product-v1",
            replicate_index,
            root,
            sequence_id=sequence_id,
            model_condition_id="opencode-openai-gpt-5-6-sol-high",
        ):
            return False, "Lifecycle V1 OpenCode authority does not match the requested identity"
        try:
            authority = load_json(root / workflow.opencode_lifecycle_v1_authority_rel(replicate_index))
        except (OSError, ValueError) as exc:
            return False, f"unreadable Lifecycle V1 OpenCode authority: {exc}"
        ready_reason = f"owner-authorized Lifecycle V1 OpenCode r{replicate_index} baseline is unoccupied"
    else:
        authority_path = root / OPENCODE_BASELINE_AUTHORITY_REL
        if not authority_path.is_file():
            return False, f"missing OpenCode baseline authority: {OPENCODE_BASELINE_AUTHORITY_REL}"
        try:
            authority = load_json(authority_path)
        except (OSError, ValueError) as exc:
            return False, f"unreadable OpenCode baseline authority: {exc}"
        owner = authority.get("owner_authorization", {})
        contract = authority.get("execution_contract", {})
        if not (
            authority.get("status") == "qualified-ready-for-provider-execution"
            and owner.get("message_id") == "1532521147327971438"
            and owner.get("authorized_new_bare_replicate_index") == replicate_index == 2
            and contract.get("model_condition_id") == "opencode-openai-gpt-5-6-sol-high"
            and contract.get("baseline_profile_id") == "runtime-opencode-codex-product-v1"
            and contract.get("sequential_max_parallel") == 1
        ):
            return False, "OpenCode baseline authority does not match the requested identity"
        ready_reason = "owner-authorized OpenCode r2 baseline is unoccupied"

    if sequence_id.endswith("-lifecycle-sequence-v1"):
        matches = [
            item
            for item in authority.get("frozen_protocols", [])
            if isinstance(item, dict) and item.get("sequence_id") == sequence_id
        ]
        if len(matches) != 1 or set(matches[0]) != {
            "sequence_id", "protocol_path", "protocol_sha256", "baseline_pool_fingerprint"
        }:
            return False, "Lifecycle V1 OpenCode authority does not bind exactly one frozen protocol"
        frozen = matches[0]
        try:
            protocol_raw = (root / str(frozen["protocol_path"])).read_bytes()
            protocol = json.loads(protocol_raw)
        except (OSError, ValueError) as exc:
            return False, f"unreadable authorized Lifecycle V1 OpenCode protocol: {exc}"
        if (
            hashlib.sha256(protocol_raw).hexdigest() != frozen["protocol_sha256"]
            or protocol.get("baseline_pool", {}).get("protocol_fingerprint")
            != frozen["baseline_pool_fingerprint"]
        ):
            return False, "Lifecycle V1 OpenCode protocol hash or baseline pool drifted from authority"

    receipt = (
        opencode_lifecycle_v1_r2_beets_retry_attempt_path(root)
        if r2_beets_retry
        else opencode_baseline_attempt_path(sequence_id, replicate_index, root)
    )
    if receipt.exists():
        if not r2_beets_retry and opencode_lifecycle_v1_r1_no_provider_recovery_authorized(
            sequence_id, replicate_index, root
        ):
            ready_reason = "owner-authorized same-r1 recovery after locally proven no-provider subprocess boundary"
        else:
            return False, (
                "OpenCode baseline identity is occupied by immutable attempt receipt: "
                f"{receipt.relative_to(root)}"
            )
    sequence = workflow.load_sequence(sequence_id)
    occupied = workflow.find_pool_profile_record(
        registry,
        sequence,
        "runtime-opencode-codex-product-v1",
        replicate_index,
    )
    if occupied is not None:
        return False, f"OpenCode baseline identity is occupied by session {occupied.get('session_id')}"
    return True, ready_reason


def reserve_opencode_baseline_attempt(
    *,
    sequence_id: str,
    replicate_index: int,
    expected_session_binding: dict[str, Any],
    run_root: Path,
    r2_beets_retry: bool = False,
) -> Path:
    lifecycle_v1 = sequence_id.endswith("-lifecycle-sequence-v1")
    if r2_beets_retry:
        if (
            sequence_id != "beets-lifecycle-sequence-v1"
            or replicate_index != 2
            or not opencode_lifecycle_v1_r2_beets_retry_authorized(ROOT)
        ):
            raise ValueError("r2 Beets retry reservation does not match its exact authority")
        path = opencode_lifecycle_v1_r2_beets_retry_attempt_path(ROOT)
    else:
        path = opencode_baseline_attempt_path(sequence_id, replicate_index, ROOT)
    if path.exists():
        if lifecycle_v1 and opencode_lifecycle_v1_r1_no_provider_recovery_authorized(
            sequence_id, replicate_index, ROOT
        ):
            return path
        raise FileExistsError(f"immutable OpenCode baseline attempt receipt already exists: {path}")
    authority_rel: Path | None = None
    owner_authorization_message_id = "1532521147327971438"
    if lifecycle_v1:
        authority_rel = (
            Path(OPENCODE_LIFECYCLE_V1_R2_BEETS_RETRY_AUTHORITY_REL)
            if r2_beets_retry
            else workflow.opencode_lifecycle_v1_authority_rel(replicate_index)
        )
        authority = load_json(ROOT / authority_rel)
        owner = authority.get("owner_authorization", {})
        owner_authorization_message_id = owner.get("message_id") if isinstance(owner, dict) else ""
        if not isinstance(owner_authorization_message_id, str) or not owner_authorization_message_id:
            raise ValueError("Lifecycle V1 OpenCode authority lacks an owner message ID")
    payload = {
        "schema_version": 1,
        "attempt_status": "reserved-before-provider-task",
        "sequence_id": sequence_id,
        "replicate_index": replicate_index,
        "profile_id": "runtime-opencode-codex-product-v1",
        "model_condition_id": "opencode-openai-gpt-5-6-sol-high",
        "owner_authorization_message_id": owner_authorization_message_id,
        "orchestrator": str(run_root),
        "reserved_at": dt.datetime.now(dt.UTC).isoformat(),
        "expected_session_binding": expected_session_binding,
        "provider_result": None,
        "immutable_identity_receipt": True,
    }
    if lifecycle_v1:
        payload["task_family_generation"] = "lifecycle-v1"
        payload["authority_path"] = str(authority_rel)
    if r2_beets_retry:
        payload["retry_attempt_of"] = "sources/evaluations/audits/lifecycle-v1-opencode-sol-high-r2-attempts/beets-r2.json"
        payload["retry_attempt_number"] = 1
    workflow.atomic_create_json(path, payload)
    return path


def workflow_lane_command(
    *,
    sequence_id: str,
    profile_id: str,
    protocol: Path,
    replicate_index: int,
    runner_args: list[str],
    model_condition: dict[str, str] | None = None,
) -> list[str]:
    if model_condition is None:
        cmd = [sys.executable, "scripts/run_codex_workflow_evaluation.py"]
    else:
        launcher = model_condition.get(
            "launcher",
            "scripts/run_opencode_workflow_model_condition.py"
            if model_condition.get("runtime_id") == "opencode-cli"
            else "scripts/run_claude_code_workflow_model_condition.py"
            if model_condition.get("runtime_id") == "claude-code"
            else "scripts/run_codex_workflow_model_condition.py",
        )
        cmd = [
            sys.executable,
            launcher,
            "--workflow-model-condition-id", model_condition["id"],
            "--workflow-model", model_condition["model"],
            "--workflow-reasoning-effort", model_condition["reasoning_effort"],
        ]
    cmd.extend([
        "--sequence-id", sequence_id,
        "--profile-id", profile_id,
        "--protocol", str(protocol),
        "--replicate-index", str(replicate_index),
        *runner_args,
    ])
    if profile_id not in {"baseline-bare-codex", "baseline-claude-code-no-mcp", "runtime-opencode-codex-product-v1"}:
        cmd.extend(["--comparison-profile-id", profile_id])
    return cmd


def expected_session_binding_for_protocol(
    *,
    sequence_id: str,
    profile_id: str,
    replicate_index: int,
    protocol_path: Path,
    root: Path,
) -> dict[str, Any]:
    """Bind an immutable parent receipt to the exact frozen protocol bytes."""
    absolute_protocol = protocol_path if protocol_path.is_absolute() else root / protocol_path
    relative_protocol = absolute_protocol.relative_to(root)
    protocol_doc = load_json(absolute_protocol)
    return {
        "sequence_id": sequence_id,
        "profile_id": profile_id,
        "replicate_index": replicate_index,
        "frozen_protocol": {
            "protocol_id": protocol_doc["protocol_id"],
            "path": str(relative_protocol),
            "sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
        },
        "baseline_pool_fingerprint": protocol_doc["baseline_pool"]["protocol_fingerprint"],
        "selected_execution": protocol_doc["selected_execution"],
    }


def claude_anthropic_sonnet_treatment_attempt_path(
    sequence_id: str,
    profile_id: str,
    replicate_index: int,
    root: Path = ROOT,
) -> Path:
    if (
        sequence_id not in CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER
        or not profile_id
        or profile_id == "baseline-claude-code-no-mcp"
        or replicate_index != 0
    ):
        raise ValueError("direct-Anthropic Sonnet treatment identity is not authorized")
    lane = sequence_id.removesuffix("-lifecycle-sequence-v1")
    return root / CLAUDE_ANTHROPIC_SONNET_TREATMENT_ATTEMPT_DIR / (
        f"{safe_name(lane)}-{safe_name(profile_id)}-r{replicate_index}.json"
    )


def reserve_claude_anthropic_sonnet_treatment_attempt(
    *,
    sequence_id: str,
    profile_id: str,
    replicate_index: int,
    expected_session_binding: dict[str, Any],
    run_root: Path,
    root: Path = ROOT,
) -> Path:
    """Occupy a paid Sonnet treatment slot before any provider task starts."""
    path = claude_anthropic_sonnet_treatment_attempt_path(
        sequence_id, profile_id, replicate_index, root
    )
    if expected_session_binding.get("sequence_id") != sequence_id or expected_session_binding.get("profile_id") != profile_id:
        raise ValueError("Sonnet treatment receipt binding does not match the requested identity")
    if path.exists():
        raise FileExistsError(f"immutable Sonnet treatment attempt receipt already exists: {path}")
    atomic_write_json(
        path,
        {
            "schema_version": 1,
            "attempt_status": "reserved-before-provider-task",
            "task_family_generation": "lifecycle-v1",
            "sequence_id": sequence_id,
            "replicate_index": replicate_index,
            "profile_id": profile_id,
            "model_condition_id": CLAUDE_ANTHROPIC_SONNET_5_HIGH_CONDITION_ID,
            "model": "claude-sonnet-5",
            "reasoning_effort": "high",
            "orchestrator": f"workflow-matrix:{run_root.name}",
            "reserved_at": dt.datetime.now(dt.UTC).isoformat(),
            "expected_session_binding": expected_session_binding,
            "provider_result": None,
            "immutable_identity_receipt": True,
        },
    )
    return path


def run_flow_lane(
    *,
    sequence_id: str,
    treatment_profile: str,
    lane_root: Path,
    replicate_index: int,
    runner_args: list[str],
    source_codex_home: Path | None,
    model_condition: dict[str, str] | None = None,
    production_lock_fd: int | None = None,
    published_launch_commit: str | None = None,
    r2_beets_retry: bool = False,
) -> dict[str, Any]:
    lane_id = safe_name(f"{sequence_id}--{treatment_profile}")
    lane_dir = lane_root / lane_id
    checkout = lane_dir / "checkout"
    tmp = lane_dir / "tmp"
    logs = lane_dir / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)
    provider_capable = "--no-provider" not in runner_args
    if r2_beets_retry and (
        sequence_id != "beets-lifecycle-sequence-v1"
        or treatment_profile != "runtime-opencode-codex-product-v1"
        or replicate_index != 2
    ):
        raise ValueError("r2 Beets retry mode permits only bare OpenCode Beets r2")
    if provider_capable and not published_launch_commit:
        raise ValueError("provider-capable lane requires a certified published launch commit")
    parent_claude_receipt_binding: dict[str, Any] | None = None
    parent_claude_treatment_receipt: Path | None = None
    parent_opencode_receipt_binding: dict[str, Any] | None = None
    if (
        provider_capable
        and treatment_profile == "runtime-opencode-codex-product-v1"
        and sequence_id.endswith("-lifecycle-sequence-v1")
    ):
        parent_protocol = find_protocol(
            ROOT,
            sequence_id,
            treatment_profile,
            model_condition_override=model_condition,
        )
        parent_opencode_receipt_binding = expected_session_binding_for_protocol(
            sequence_id=sequence_id,
            profile_id=treatment_profile,
            replicate_index=replicate_index,
            protocol_path=parent_protocol,
            root=ROOT,
        )
        reserve_opencode_baseline_attempt(
            sequence_id=sequence_id,
            replicate_index=replicate_index,
            expected_session_binding=parent_opencode_receipt_binding,
            run_root=lane_root,
            r2_beets_retry=r2_beets_retry,
        )
    if (
        provider_capable
        and treatment_profile == "baseline-claude-code-no-mcp"
        and sequence_id in CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER
    ):
        parent_protocol = find_protocol(
            ROOT,
            sequence_id,
            treatment_profile,
            model_condition_override=model_condition,
        )
        parent_claude_receipt_binding = expected_session_binding_for_protocol(
            sequence_id=sequence_id,
            profile_id=treatment_profile,
            replicate_index=replicate_index,
            protocol_path=parent_protocol,
            root=ROOT,
        )
        direct_campaign = (
            direct_anthropic_campaign(model_condition.get("id"))
            if isinstance(model_condition, dict)
            else None
        )
        reserve_claude_lifecycle_v1_attempt(
            sequence_id=sequence_id,
            replicate_index=replicate_index,
            expected_session_binding=parent_claude_receipt_binding,
            run_root=lane_root,
            root=ROOT,
            model_condition=(
                model_condition
                if direct_campaign is not None
                else None
            ),
            authority_rel=(
                direct_campaign["authorization"]
                if direct_campaign is not None
                else CLAUDE_LIFECYCLE_V1_AUTHORITY_REL
            ),
            attempt_dir=(
                direct_campaign["attempt_dir"]
                if direct_campaign is not None
                else CLAUDE_LIFECYCLE_V1_ATTEMPT_DIR
            ),
            owner_authorization_message_id=(
                "user-request-current-session"
                if direct_campaign is not None
                else "1533397324384964609"
            ),
        )
    if (
        provider_capable
        and isinstance(model_condition, dict)
        and model_condition.get("id") == CLAUDE_ANTHROPIC_SONNET_5_HIGH_CONDITION_ID
        and treatment_profile != "baseline-claude-code-no-mcp"
        and sequence_id in CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER
    ):
        parent_protocol = find_protocol(
            ROOT,
            sequence_id,
            treatment_profile,
            model_condition_override=model_condition,
        )
        parent_binding = expected_session_binding_for_protocol(
            sequence_id=sequence_id,
            profile_id=treatment_profile,
            replicate_index=replicate_index,
            protocol_path=parent_protocol,
            root=ROOT,
        )
        parent_claude_treatment_receipt = reserve_claude_anthropic_sonnet_treatment_attempt(
            sequence_id=sequence_id,
            profile_id=treatment_profile,
            replicate_index=replicate_index,
            expected_session_binding=parent_binding,
            run_root=lane_root,
            root=ROOT,
        )
    if provider_capable:
        clone_published_checkout(checkout, published_launch_commit)
    else:
        rsync_checkout(ROOT, checkout)
    if parent_claude_treatment_receipt is not None:
        child_receipt = checkout / parent_claude_treatment_receipt.relative_to(ROOT)
        child_receipt.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(parent_claude_treatment_receipt, child_receipt)
    before_session_ids = {
        str(session.get("session_id"))
        for session in load_json(checkout / "data/workflow-sessions.json").get("sessions", [])
        if session.get("session_id")
    }
    artifact_root = checkout / WORKFLOW_ARTIFACT_ROOT
    before_artifact_entries = {path.name for path in artifact_root.iterdir()}

    protocol = find_protocol(checkout, sequence_id, treatment_profile).relative_to(checkout)
    expected_session_binding = expected_session_binding_for_protocol(
        sequence_id=sequence_id,
        profile_id=treatment_profile,
        replicate_index=replicate_index,
        protocol_path=checkout / protocol,
        root=checkout,
    )
    if (
        (parent_claude_receipt_binding is not None and expected_session_binding != parent_claude_receipt_binding)
        or (parent_opencode_receipt_binding is not None and expected_session_binding != parent_opencode_receipt_binding)
    ):
        raise UnsafeLaneOutputError(
            "Lifecycle V1 child protocol does not match the parent-reserved identity"
        )
    cmd = workflow_lane_command(
        sequence_id=sequence_id,
        profile_id=treatment_profile,
        protocol=protocol,
        replicate_index=replicate_index,
        runner_args=runner_args,
        model_condition=model_condition,
    )
    if "--prepare-only" in runner_args:
        cmd.extend(["--session-id", f"prepare-{lane_id}"])
    if source_codex_home is not None:
        cmd.extend(["--source-codex-home", str(source_codex_home)])
    env = workflow_lane_environment(
        tmp,
        allow_auth_sync=(
            isinstance(model_condition, dict)
            and direct_anthropic_campaign(model_condition.get("id")) is not None
        ),
    )
    pass_fds: tuple[int, ...] = ()
    if production_lock_fd is not None:
        env[workflow.PRODUCTION_LOCK_FD_ENV] = str(production_lock_fd)
        pass_fds = (production_lock_fd,)
    log_path = logs / "lane.log"
    failure_evidence: list[str] = []
    failure_result: dict[str, Any] = {
        "lane_id": lane_id,
        "lane_dir": str(lane_dir),
        "run_root": str(lane_root),
        "failure_evidence": failure_evidence,
    }
    if provider_capable:
        retain_lane_checkout(
            lane_dir,
            lane_id,
            "provider-capable child has started; cleanup remains prohibited until evidence is canonical or preserved",
        )
    # Lane-local scratch may be reclaimed while a long trusted clone is in progress.
    # Recreate it at the last possible point before crossing the child boundary.
    logs.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)
    try:
        with log_path.open("w") as log:
            if provider_capable and production_lock_fd is not None and treatment_profile == "baseline-bare-codex":
                parent_sequence = workflow.load_sequence(sequence_id)
                if parent_sequence.get("task_family_generation") in {"baseline-v3", "baseline-v4"}:
                    workflow.reserve_baseline_pilot_attempt(
                        parent_sequence,
                        root=ROOT,
                        orchestrator=f"workflow-matrix:{lane_root.name}",
                        replicate_index=replicate_index,
                    )
            proc = subprocess.run(
                cmd,
                cwd=checkout,
                text=True,
                stdout=log,
                stderr=subprocess.STDOUT,
                env=env,
                pass_fds=pass_fds,
            )
        registry_path = checkout / "data/workflow-sessions.json"
        if not nonsymlink_file_within(checkout, registry_path):
            raise UnsafeLaneOutputError("post-child lane registry path is symlinked, escaped, missing, or unsafe")
        after_sessions = load_json(registry_path).get("sessions", [])
        produced_session_ids = sorted(
            str(session["session_id"])
            for session in after_sessions
            if session.get("session_id") and str(session["session_id"]) not in before_session_ids
        )
        if provider_capable and proc.returncode != 0:
            preserve_discovered_lane_artifacts(
                result=failure_result,
                checkout=checkout,
                artifact_root=artifact_root,
                before_artifact_entries=before_artifact_entries,
                reason=f"lane runner exited nonzero before publication: {proc.returncode}",
            )
        if provider_capable and proc.returncode == 0 and len(produced_session_ids) != 1:
            preserve_discovered_lane_artifacts(
                result=failure_result,
                checkout=checkout,
                artifact_root=artifact_root,
                before_artifact_entries=before_artifact_entries,
                reason=f"provider-capable lane returned success with {len(produced_session_ids)} attributable sessions",
            )
            raise RuntimeError(
                f"provider-capable lane {lane_id} returned success without exactly one attributable session; "
                "checkout retained or evidence preserved"
            )
    except BaseException as exc:
        if provider_capable and lane_dir.resolve() in CLEANUP_PROHIBITED_LANE_DIRS:
            if isinstance(exc, UnsafeLaneOutputError):
                try:
                    retain_lane_checkout(
                        lane_dir,
                        lane_id,
                        f"unsafe lane output identity requires whole-checkout retention: {exc}",
                    )
                except BaseException:
                    pass
            else:
                try:
                    preserve_discovered_lane_artifacts(
                        result=failure_result,
                        checkout=checkout,
                        artifact_root=artifact_root,
                        before_artifact_entries=before_artifact_entries,
                        reason=f"lane execution or post-child discovery raised {type(exc).__name__}: {exc}",
                    )
                except BaseException:
                    # Preserve the initiating exception. The pre-launch sentinel and
                    # in-memory prohibition retain the checkout if preservation fails.
                    pass
        raise

    return {
        "sequence_id": sequence_id,
        "treatment_profile": treatment_profile,
        "lane_id": lane_id,
        "lane_dir": str(lane_dir),
        "run_root": str(lane_root),
        "checkout": str(checkout),
        "log": str(log_path),
        "exit_code": proc.returncode,
        "produced_session_ids": produced_session_ids,
        "expected_session_binding": expected_session_binding,
        "failure_evidence": failure_evidence,
    }


def production_lane_output_declared(result: dict[str, Any]) -> bool:
    produced = result.get("produced_session_ids")
    return (
        result.get("exit_code") == 0
        and isinstance(produced, list)
        and len(produced) == 1
        and isinstance(produced[0], str)
        and bool(produced[0])
    )


def publication_allowed(prepare_only: bool, lane_results: list[dict[str, Any]]) -> bool:
    return not prepare_only and all(
        production_lane_output_declared(result) for result in lane_results
    )


def artifact_merge_allowed(prepare_only: bool, lane_results: list[dict[str, Any]]) -> bool:
    """Preserve every completed compact session even when a sibling lane fails."""
    return not prepare_only and any(result.get("produced_session_ids") for result in lane_results)


def matrix_outputs_complete(
    *,
    prepare_only: bool,
    planned_job_count: int,
    lane_results: list[dict[str, Any]],
    merge_summary: dict[str, Any],
) -> bool:
    if prepare_only or planned_job_count == 0:
        return True
    return (
        len(lane_results) == planned_job_count
        and all(production_lane_output_declared(result) for result in lane_results)
        and merge_summary.get("merged_session_count", 0) == planned_job_count
        and not merge_summary.get("rejected_lane_errors")
    )


def matrix_acceptance_state(
    *, prepare_only: bool, execution_passed: bool, awaiting_quality_review: bool
) -> bool | None:
    """Preparation is not evidence; model-quality review is diagnostic only."""
    if prepare_only:
        return None
    return execution_passed


def matrix_exit_code(
    *,
    prepare_only: bool,
    execution_passed: bool,
    awaiting_quality_review: bool,
    accepted: bool | None,
) -> int:
    if prepare_only:
        return 0 if execution_passed else 1
    return 0 if accepted else 1


def lane_session_records(
    checkout: Path,
    expected: dict[str, Any],
    produced_session_ids: set[str],
) -> list[dict[str, Any]]:
    if len(produced_session_ids) != 1:
        raise ValueError(
            f"matrix lane must produce exactly one session; found {sorted(produced_session_ids)}"
        )
    registry_path = checkout / "data/workflow-sessions.json"
    if not nonsymlink_file_within(checkout, registry_path):
        raise UnsafeLaneOutputError("matrix lane registry path is symlinked, escaped, missing, or unsafe")
    doc = load_json(registry_path)
    records = [
        session
        for session in doc.get("sessions", [])
        if session.get("session_id") in produced_session_ids
    ]
    if len(records) != 1:
        raise ValueError(
            f"matrix lane produced IDs do not resolve to exactly one registry record: {sorted(produced_session_ids)}"
        )
    session = records[0]
    selected = session.get("selected_execution", {})
    bindings_match = (
        session.get("replicate_index") == expected["replicate_index"]
        and session.get("task_sequence", {}).get("sequence_id") == expected["sequence_id"]
        and session.get("profile", {}).get("profile_id") == expected["profile_id"]
        and session.get("frozen_protocol") == expected["frozen_protocol"]
        and session.get("baseline_pool", {}).get("protocol_fingerprint")
        == expected["baseline_pool_fingerprint"]
        and selected == expected["selected_execution"]
    )
    prompt_delivery = session.get("task_sequence", {}).get("prompt_delivery", {})
    if not bindings_match or prompt_delivery.get("mode") != "sequential-one-task-at-a-time":
        raise ValueError(
            f"matrix lane session {session.get('session_id')} does not match its planned job binding"
        )
    return [session]


PRESERVATION_FAILURE_SENTINEL = ".rejected-evidence-preservation-failed.json"
LANE_CLEANUP_PROHIBITION_SENTINEL = ".checkout-cleanup-prohibited.json"
CLEANUP_PROHIBITED_RUN_ROOTS: set[Path] = set()
CLEANUP_PROHIBITED_LANE_DIRS: set[Path] = set()
PRESERVATION_STATE_LOCK = threading.Lock()
ACTIVE_RUN_PRESERVATIONS: dict[Path, int] = {}


def nonsymlink_directory_within(base: Path, target: Path) -> bool:
    """Require every component from base through target to be a real directory."""
    try:
        base_absolute = base.absolute()
        target_absolute = target.absolute()
        relative = target_absolute.relative_to(base_absolute)
        if base_absolute.is_symlink() or not base_absolute.is_dir():
            return False
        resolved_base = base_absolute.resolve(strict=True)
        current = base_absolute
        for part in relative.parts:
            current = current / part
            if current.is_symlink() or not current.is_dir():
                return False
        return current.resolve(strict=True).is_relative_to(resolved_base)
    except (OSError, RuntimeError, ValueError):
        return False


def nonsymlink_directory_ancestry(target: Path) -> bool:
    """Require every existing path component from the filesystem root to be a real directory."""
    try:
        absolute = target.absolute()
        current = Path(absolute.anchor)
        for part in absolute.parts[1:]:
            current = current / part
            metadata = os.lstat(current)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                return False
        return True
    except (OSError, RuntimeError, ValueError):
        return False


def ensure_nonsymlink_directory_ancestry(target: Path) -> bool:
    """Create missing directory components one at a time without traversing aliases."""
    try:
        absolute = target.absolute()
        current = Path(absolute.anchor)
        for part in absolute.parts[1:]:
            child = current / part
            try:
                metadata = os.lstat(child)
            except FileNotFoundError:
                child.mkdir(mode=0o700)
                fsync_directory(current)
                metadata = os.lstat(child)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                return False
            current = child
        return nonsymlink_directory_ancestry(absolute)
    except (OSError, RuntimeError, ValueError):
        return False


def nonsymlink_directory_identity_within(base: Path, target: Path) -> bool:
    """Validate containment and confirm the path via a non-following directory descriptor."""
    if not nonsymlink_directory_within(base, target):
        return False
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(target, flags)
    except OSError:
        return False
    try:
        descriptor_stat = os.fstat(fd)
        path_stat = os.stat(target, follow_symlinks=False)
        return (descriptor_stat.st_dev, descriptor_stat.st_ino) == (path_stat.st_dev, path_stat.st_ino)
    except OSError:
        return False
    finally:
        os.close(fd)


def nonsymlink_file_within(base: Path, target: Path) -> bool:
    """Require contained nonsymlink directory ancestors and a regular target file."""
    try:
        base_absolute = base.absolute()
        target_absolute = target.absolute()
        relative = target_absolute.relative_to(base_absolute)
        if not relative.parts or base_absolute.is_symlink() or not base_absolute.is_dir():
            return False
        resolved_base = base_absolute.resolve(strict=True)
        current = base_absolute
        for part in relative.parts[:-1]:
            current = current / part
            if current.is_symlink() or not current.is_dir():
                return False
        file_path = current / relative.parts[-1]
        return (
            not file_path.is_symlink()
            and file_path.is_file()
            and file_path.resolve(strict=True).is_relative_to(resolved_base)
        )
    except (OSError, RuntimeError, ValueError):
        return False


def begin_run_preservation(run_root: Path, sentinel: Path, lane_id: Any) -> None:
    """Reference-count the shared durable run-root preservation prohibition."""
    with PRESERVATION_STATE_LOCK:
        count = ACTIVE_RUN_PRESERVATIONS.get(run_root, 0) + 1
        ACTIVE_RUN_PRESERVATIONS[run_root] = count
        CLEANUP_PROHIBITED_RUN_ROOTS.add(run_root)
        atomic_write_json(
            sentinel,
            {
                "schema_version": 1,
                "lane_id": lane_id,
                "reason": "rejected evidence preservation is in progress; source checkout must be retained",
                "status": "in-progress",
                "active_preservations": count,
            },
        )
        fsync_directory(run_root)


def finish_run_preservation(run_root: Path, sentinel: Path) -> None:
    """Release the shared prohibition only after every lane copy is durable."""
    with PRESERVATION_STATE_LOCK:
        count = ACTIVE_RUN_PRESERVATIONS.get(run_root, 0)
        if count <= 0:
            raise RuntimeError("run-root preservation reference count is missing")
        if count == 1:
            sentinel.unlink()
            fsync_directory(run_root)
            ACTIVE_RUN_PRESERVATIONS.pop(run_root, None)
            CLEANUP_PROHIBITED_RUN_ROOTS.discard(run_root)
            return
        remaining = count - 1
        ACTIVE_RUN_PRESERVATIONS[run_root] = remaining
        atomic_write_json(
            sentinel,
            {
                "schema_version": 1,
                "reason": "another rejected evidence preservation remains in progress",
                "status": "in-progress",
                "active_preservations": remaining,
            },
        )
        fsync_directory(run_root)


def retain_lane_checkout(lane_dir: Path, lane_id: str, reason: str) -> None:
    """Durably and in-memory prohibit cleanup for one provider-capable lane."""
    resolved = lane_dir.resolve()
    CLEANUP_PROHIBITED_LANE_DIRS.add(resolved)
    sentinel = lane_dir / LANE_CLEANUP_PROHIBITION_SENTINEL
    try:
        atomic_write_json(
            sentinel,
            {
                "schema_version": 1,
                "lane_id": lane_id,
                "status": "cleanup-prohibited",
                "reason": reason,
            },
        )
        fsync_directory(lane_dir)
    except BaseException:
        # The in-memory prohibition remains authoritative for atexit cleanup. A
        # hard process failure cannot run that cleanup, so the checkout remains.
        raise


def release_lane_checkout(lane_dir: Path) -> None:
    """Permit cleanup only after evidence is canonical or atomically preserved."""
    resolved = lane_dir.resolve()
    sentinel = lane_dir / LANE_CLEANUP_PROHIBITION_SENTINEL
    sentinel.unlink(missing_ok=True)
    fsync_directory(lane_dir)
    CLEANUP_PROHIBITED_LANE_DIRS.discard(resolved)


def preserve_discovered_lane_artifacts(
    *,
    result: dict[str, Any],
    checkout: Path,
    artifact_root: Path,
    before_artifact_entries: set[str],
    reason: str,
) -> list[str]:
    """Preserve every new directory or retain the checkout for ambiguous output."""
    lane_dir = Path(result["lane_dir"])
    lane_id = str(result["lane_id"])
    if not nonsymlink_directory_within(checkout, artifact_root):
        retain_lane_checkout(
            lane_dir,
            lane_id,
            f"artifact root is symlinked, escaped, missing, or unsafe after provider-capable launch: {reason}",
        )
        return []
    try:
        entries = [entry for entry in artifact_root.iterdir() if entry.name not in before_artifact_entries]
    except BaseException as exc:
        retain_lane_checkout(lane_dir, lane_id, f"artifact discovery failed: {type(exc).__name__}: {exc}")
        raise
    if not entries:
        retain_lane_checkout(lane_dir, lane_id, f"no attributable artifact output after provider-capable launch: {reason}")
        return []
    if any(
        entry.is_symlink()
        or not entry.is_dir()
        or not entry.name
        or Path(entry.name).name != entry.name
        for entry in entries
    ):
        retain_lane_checkout(lane_dir, lane_id, f"ambiguous or unsafe artifact output after provider-capable launch: {reason}")
        return []
    session_ids = {entry.name for entry in entries}
    preserved = preserve_rejected_lane_artifacts(result, checkout, session_ids, reason)
    if len(preserved) != len(session_ids):
        retain_lane_checkout(lane_dir, lane_id, f"incomplete rejected-evidence preservation: {reason}")
        return preserved
    release_lane_checkout(lane_dir)
    return preserved


def preserve_rejected_lane_artifacts(
    result: dict[str, Any],
    checkout: Path,
    session_ids: set[str],
    reason: str,
) -> list[str]:
    """Atomically preserve bounded compact evidence before rejected-lane cleanup."""
    preserved: list[str] = []
    artifact_root = checkout / WORKFLOW_ARTIFACT_ROOT
    lane_root = Path(result.get("lane_dir", checkout.parent / f"{result.get('lane_id', 'lane')}-failure")).absolute()
    run_root = Path(result.get("run_root", lane_root.parent)).absolute()
    failure_root = lane_root / "rejected-evidence"
    sentinel = run_root / PRESERVATION_FAILURE_SENTINEL
    if not session_ids:
        return preserved
    if (
        lane_root.parent != run_root
        or not nonsymlink_directory_ancestry(run_root)
        or not nonsymlink_directory_identity_within(run_root, lane_root)
    ):
        raise ValueError("unsafe run root or lane ancestor; source checkout retained")
    begin_run_preservation(run_root, sentinel, result.get("lane_id"))
    if not nonsymlink_directory_within(checkout, artifact_root):
        atomic_write_json(
            sentinel,
            {
                "schema_version": 1,
                "lane_id": result.get("lane_id"),
                "reason": "rejected evidence artifact root is symlinked, escaped, missing, or unsafe; source checkout retained",
                "error_type": "UnsafeRejectedEvidenceArtifactRoot",
            },
        )
        raise ValueError("unsafe rejected evidence artifact root; source checkout retained")

    def destination_root_safe() -> bool:
        return (
            nonsymlink_directory_ancestry(run_root)
            and nonsymlink_directory_identity_within(run_root, lane_root)
            and nonsymlink_directory_identity_within(run_root, failure_root)
        )

    if not nonsymlink_directory_identity_within(run_root, lane_root) or failure_root.is_symlink():
        atomic_write_json(
            sentinel,
            {
                "schema_version": 1,
                "lane_id": result.get("lane_id"),
                "reason": "rejected evidence destination root or ancestor is symlinked, escaped, missing, or unsafe; source checkout retained",
                "error_type": "UnsafeRejectedEvidenceDestinationRoot",
            },
        )
        raise ValueError("unsafe rejected evidence destination root; source checkout retained")
    if not failure_root.exists():
        failure_root.mkdir(mode=0o700)
        fsync_directory(lane_root)
    if not destination_root_safe():
        atomic_write_json(
            sentinel,
            {
                "schema_version": 1,
                "lane_id": result.get("lane_id"),
                "reason": "rejected evidence destination root failed non-following identity validation; source checkout retained",
                "error_type": "UnsafeRejectedEvidenceDestinationRoot",
            },
        )
        raise ValueError("unsafe rejected evidence destination root; source checkout retained")
    for session_id in sorted(session_ids):
        if not session_id or Path(session_id).name != session_id:
            atomic_write_json(
                sentinel,
                {
                    "schema_version": 1,
                    "lane_id": result.get("lane_id"),
                    "session_id": session_id,
                    "reason": "rejected evidence session identity is unsafe; source checkout retained",
                    "error_type": "UnsafeRejectedEvidenceSessionId",
                },
            )
            raise ValueError("unsafe rejected evidence session identity; source checkout retained")
        source = artifact_root / session_id
        if not nonsymlink_directory_within(checkout, source):
            atomic_write_json(
                sentinel,
                {
                    "schema_version": 1,
                    "lane_id": result.get("lane_id"),
                    "session_id": session_id,
                    "reason": "rejected evidence source or ancestor is symlinked, escaped, missing, or unsafe; source checkout retained",
                    "error_type": "UnsafeRejectedEvidencePath",
                },
            )
            raise ValueError(f"unsafe rejected evidence path for {session_id}; source checkout retained")
        entries = sorted(source.iterdir())
        if (
            not entries
            or len(entries) > 32
            or any(entry.is_symlink() or not entry.is_file() for entry in entries)
            or sum(entry.stat().st_size for entry in entries) > 128 * 1024 * 1024
        ):
            atomic_write_json(
                sentinel,
                {
                    "schema_version": 1,
                    "lane_id": result.get("lane_id"),
                    "session_id": session_id,
                    "reason": "rejected evidence exceeds the safe atomic-copy contract; source checkout retained",
                    "error_type": "UnsafeRejectedEvidenceShape",
                },
            )
            raise ValueError(f"unsafe rejected evidence shape for {session_id}; source checkout retained")
        if not destination_root_safe():
            atomic_write_json(
                sentinel,
                {
                    "schema_version": 1,
                    "lane_id": result.get("lane_id"),
                    "session_id": session_id,
                    "reason": "rejected evidence destination root changed before preservation; source checkout retained",
                    "error_type": "UnsafeRejectedEvidenceDestinationRoot",
                },
            )
            raise ValueError("unsafe rejected evidence destination root; source checkout retained")
        destination = failure_root / session_id
        if destination.exists() or destination.is_symlink():
            atomic_write_json(
                sentinel,
                {
                    "schema_version": 1,
                    "lane_id": result.get("lane_id"),
                    "session_id": session_id,
                    "reason": "rejected evidence destination collision is unsafe; source checkout retained",
                    "error_type": "RejectedEvidenceDestinationCollision",
                },
            )
            raise FileExistsError(f"rejected evidence destination already exists for {session_id}; source checkout retained")
        temporary = Path(tempfile.mkdtemp(prefix=f".{session_id}.tmp-", dir=failure_root))
        try:
            if not destination_root_safe() or not nonsymlink_directory_identity_within(failure_root, temporary):
                raise ValueError("rejected evidence destination changed after temporary creation")
            for entry in entries:
                if not destination_root_safe() or not nonsymlink_directory_identity_within(failure_root, temporary):
                    raise ValueError("rejected evidence destination changed during copy")
                shutil.copy2(entry, temporary / entry.name)
            atomic_write_json(
                temporary / "rejection.json",
                {
                    "schema_version": 1,
                    "session_id": session_id,
                    "lane_id": result.get("lane_id"),
                    "reason": reason,
                    "accepted_evidence": False,
                },
            )
            fsync_compact_artifact_tree(temporary)
            if not destination_root_safe() or not nonsymlink_directory_identity_within(failure_root, temporary):
                raise ValueError("rejected evidence destination changed before atomic publication")
            os.replace(temporary, destination)
            if not destination_root_safe() or destination.is_symlink() or not destination.is_dir():
                raise ValueError("rejected evidence destination changed after atomic publication")
            fsync_directory(failure_root)
        except BaseException as exc:
            try:
                atomic_write_json(
                    sentinel,
                    {
                        "schema_version": 1,
                        "lane_id": result.get("lane_id"),
                        "session_id": session_id,
                        "reason": "rejected evidence preservation did not complete; source checkout retained",
                        "error_type": type(exc).__name__,
                    },
                )
            finally:
                if temporary.exists():
                    chmod_tree(temporary)
                    shutil.rmtree(temporary, ignore_errors=True)
            raise
        value = str(destination)
        preserved.append(value)
        result.setdefault("failure_evidence", []).append(value)
    finish_run_preservation(run_root, sentinel)
    return preserved


def fsync_directory(directory: Path) -> None:
    fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def fsync_compact_artifact_tree(root: Path) -> None:
    """Persist copied compact files, their directory entries, and parent entry."""
    for path in sorted(root.iterdir()):
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    for directory in (root, root.parent):
        fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def copy_artifacts_for_sessions(
    checkout: Path,
    sessions: list[dict[str, Any]],
    copied: list[str] | None = None,
) -> list[str]:
    if copied is None:
        copied = []
    lane_artifact_root = (checkout / WORKFLOW_ARTIFACT_ROOT).resolve()
    for session in sessions:
        if not workflow.pilot_session_artifacts_valid(session, checkout):
            raise ValueError(
                f"workflow session {session.get('session_id')} failed strict compact artifact ingress validation"
            )
        artifacts = session.get("artifacts", {}) if isinstance(session.get("artifacts"), dict) else {}
        expected_root = f"{WORKFLOW_ARTIFACT_ROOT}/{session['session_id']}"
        root = artifacts.get("root") or ""
        if root != expected_root:
            raise ValueError(
                f"workflow session {session.get('session_id')} declares noncanonical artifact root: {root}"
            )
        rel = Path(root.rstrip("/"))
        if rel.is_absolute() or ".." in rel.parts:
            continue
        src = checkout / rel
        dst = ROOT / rel
        if src.exists():
            resolved = src.resolve()
            if (
                not nonsymlink_directory_within(checkout, src)
                or not resolved.is_relative_to(lane_artifact_root)
            ):
                raise ValueError(f"workflow artifact root escapes lane checkout or has a symlinked ancestor: {src}")
            entries = list(src.iterdir())
            if any(entry.is_symlink() or not entry.is_file() for entry in entries):
                raise ValueError(f"workflow artifact root contains non-file or symlink entries: {src}")
            if {entry.name for entry in entries} != COMPACT_ARTIFACT_NAMES:
                raise ValueError(f"workflow artifact root does not satisfy compact artifact contract: {src}")
            if dst.exists():
                raise FileExistsError(f"workflow artifact destination already exists; refusing overwrite: {dst}")
            copied.append(str(rel))
            shutil.copytree(src, dst)
            fsync_compact_artifact_tree(dst)
    return copied


def atomic_write_bytes(path: Path, content: bytes) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        tmp.unlink(missing_ok=True)


def atomic_write_json(path: Path, data: Any) -> None:
    """Durably replace JSON using a thread-safe same-directory temporary."""
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        tmp.unlink(missing_ok=True)


def merge_lifecycle_v1_replication_attempt_receipt(
    checkout: Path,
    expected: dict[str, Any],
    replicate_index: int,
) -> str | None:
    """Retain an occupied Lifecycle V1 r1 identity even if later publication rolls back."""
    sequence_id = expected.get("sequence_id")
    if (
        replicate_index != 1
        or expected.get("profile_id") != "baseline-bare-codex"
        or not isinstance(sequence_id, str)
        or not sequence_id.endswith("-lifecycle-sequence-v1")
    ):
        return None
    receipt_rel = (
        Path(workflow.LIFECYCLE_V1_REPLICATION_ATTEMPT_DIR)
        / f"{sequence_id.removesuffix('-lifecycle-sequence-v1')}-r1.json"
    )
    source = checkout / receipt_rel
    if not nonsymlink_file_within(checkout, source):
        raise UnsafeLaneOutputError("Lifecycle V1 r1 attempt receipt is missing, symlinked, escaped, or unsafe")
    source_bytes = source.read_bytes()
    try:
        receipt = json.loads(source_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Lifecycle V1 r1 attempt receipt is unreadable: {exc}") from exc
    frozen = receipt.get("frozen_protocol")
    expected_frozen = expected.get("frozen_protocol")
    selected = expected.get("selected_execution")
    expected_keys = {
        "schema_version", "attempt_status", "task_family_generation", "sequence_id", "replicate_index",
        "profile_id", "model_condition_id", "model", "reasoning_effort", "orchestrator", "reserved_at",
        "frozen_protocol", "baseline_pool_fingerprint", "provider_result", "immutable_identity_receipt",
    }
    receipt_is_exact = (
        isinstance(receipt, dict)
        and set(receipt) == expected_keys
        and receipt.get("schema_version") == 1
        and receipt.get("attempt_status") == "reserved-before-provider-task"
        and receipt.get("task_family_generation") == "lifecycle-v1"
        and receipt.get("sequence_id") == sequence_id
        and receipt.get("replicate_index") == 1
        and receipt.get("profile_id") == "baseline-bare-codex"
        and receipt.get("model_condition_id") == "codex-openai-gpt-5-6-sol-high"
        and receipt.get("model") == "gpt-5.6-sol"
        and receipt.get("reasoning_effort") == "high"
        and isinstance(receipt.get("orchestrator"), str)
        and bool(receipt.get("orchestrator"))
        and isinstance(receipt.get("reserved_at"), str)
        and bool(receipt.get("reserved_at"))
        and receipt.get("provider_result") is None
        and receipt.get("immutable_identity_receipt") is True
        and receipt.get("baseline_pool_fingerprint") == expected.get("baseline_pool_fingerprint")
        and isinstance(frozen, dict)
        and isinstance(expected_frozen, dict)
        and frozen.get("protocol_id") == expected_frozen.get("protocol_id")
        and frozen.get("path") == expected_frozen.get("path")
        and frozen.get("sha256") == expected_frozen.get("sha256")
        and frozen.get("baseline_pool_fingerprint") == expected.get("baseline_pool_fingerprint")
        and isinstance(frozen.get("qualification_sha256"), str)
        and len(frozen["qualification_sha256"]) == 64
        and isinstance(selected, dict)
        and frozen.get("selected_execution_sha256") == selected.get("descriptor_sha256")
    )
    if not receipt_is_exact:
        raise ValueError("Lifecycle V1 r1 attempt receipt does not match its planned identity")
    target = ROOT / receipt_rel
    if target.exists():
        if not nonsymlink_file_within(ROOT, target):
            raise UnsafeLaneOutputError("existing Lifecycle V1 r1 attempt receipt is symlinked, escaped, or unsafe")
        if target.read_bytes() != source_bytes:
            raise FileExistsError(f"Lifecycle V1 r1 attempt receipt differs from retained identity: {receipt_rel}")
    else:
        if not ensure_nonsymlink_directory_ancestry(target.parent):
            raise UnsafeLaneOutputError("Lifecycle V1 r1 attempt receipt parent is unsafe")
        atomic_write_bytes(target, source_bytes)
    return receipt_rel.as_posix()


def merge_registry(sessions: list[dict[str, Any]]) -> None:
    path = ROOT / "data/workflow-sessions.json"
    doc = load_json(path)
    retained = list(doc.get("sessions", []))
    existing_ids = {session.get("session_id") for session in retained if session.get("session_id")}
    accepted: list[dict[str, Any]] = []
    for session in sessions:
        if session["session_id"] in existing_ids:
            raise FileExistsError(f"workflow session already exists; refusing overwrite: {session['session_id']}")
        occupied = next(
            (item for item in [*retained, *accepted] if workflow.same_provider_slot(item, session)),
            None,
        )
        if occupied is not None:
            raise FileExistsError(
                "provider sample slot already occupied during matrix publication by "
                f"{occupied.get('session_id')}; refusing {session.get('session_id')}"
            )
        existing_ids.add(session["session_id"])
        accepted.append(session)
    doc["sessions"] = [*retained, *accepted]
    atomic_write_json(path, doc)


def merge_lanes(
    lane_results: list[dict[str, Any]],
    replicate_index: int,
    transaction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    merged_sessions: list[dict[str, Any]] = []
    copied_artifacts: list[str] = []
    copied_attempt_receipts: list[str] = []
    summary = transaction if transaction is not None else {}
    summary.update(
        merged_session_count=0,
        copied_artifact_count=0,
        copied_attempt_receipts=copied_attempt_receipts,
        merged_session_ids=[],
        copied_artifacts=copied_artifacts,
        registry_replacement_attempted=False,
        rejected_session_ids=[],
        rejected_lane_errors=[],
    )
    try:
        for result in lane_results:
            checkout = Path(result["checkout"])
            try:
                copied_receipt = merge_lifecycle_v1_replication_attempt_receipt(
                    checkout,
                    result["expected_session_binding"],
                    replicate_index,
                )
            except BaseException:
                lane_dir = result.get("lane_dir")
                if isinstance(lane_dir, str) and Path(lane_dir).is_dir():
                    retain_lane_checkout(
                        Path(lane_dir),
                        str(result.get("lane_id", result.get("sequence_id", "lane"))),
                        "Lifecycle V1 r1 attempt-receipt ingress failed",
                    )
                raise
            if copied_receipt is not None:
                copied_attempt_receipts.append(copied_receipt)
            produced_session_ids = set(result.get("produced_session_ids", []))
            try:
                sessions = lane_session_records(
                    checkout,
                    result["expected_session_binding"],
                    produced_session_ids,
                )
            except BaseException as exc:
                if isinstance(exc, UnsafeLaneOutputError):
                    retain_lane_checkout(
                        Path(result["lane_dir"]),
                        str(result.get("lane_id", result.get("sequence_id"))),
                        f"unsafe lane output identity during merge: {exc}",
                    )
                    preserved = []
                else:
                    preserved = preserve_rejected_lane_artifacts(result, checkout, produced_session_ids, str(exc))
                    if preserved:
                        release_lane_checkout(Path(result["lane_dir"]))
                summary["rejected_session_ids"].extend(sorted(produced_session_ids))
                summary["rejected_lane_errors"].append(
                    f"{result.get('lane_id', result.get('sequence_id'))}: {exc}"
                )
                if not isinstance(exc, Exception):
                    raise
                continue
            valid_sessions: list[dict[str, Any]] = []
            strict_validation_failed = False
            for session in sessions:
                try:
                    artifacts_valid = workflow.pilot_session_artifacts_valid(session, checkout)
                except BaseException as exc:
                    preserved = preserve_rejected_lane_artifacts(
                        result,
                        checkout,
                        {str(session.get("session_id", ""))},
                        f"strict compact artifact ingress raised {type(exc).__name__}: {exc}",
                    )
                    if preserved:
                        release_lane_checkout(Path(result["lane_dir"]))
                    summary["rejected_session_ids"].append(session.get("session_id"))
                    summary["rejected_lane_errors"].append(
                        f"{result.get('lane_id', result.get('sequence_id'))}: "
                        f"strict compact artifact ingress raised {type(exc).__name__}: {exc}"
                    )
                    strict_validation_failed = True
                    if not isinstance(exc, Exception):
                        raise
                    break
                if artifacts_valid:
                    valid_sessions.append(session)
                else:
                    preserved = preserve_rejected_lane_artifacts(
                        result,
                        checkout,
                        {str(session.get("session_id", ""))},
                        "failed strict compact artifact ingress validation",
                    )
                    if preserved:
                        release_lane_checkout(Path(result["lane_dir"]))
                    summary["rejected_session_ids"].append(session.get("session_id"))
                    summary["rejected_lane_errors"].append(
                        f"{result.get('lane_id', result.get('sequence_id'))}: "
                        f"session {session.get('session_id')} failed strict compact artifact ingress validation"
                    )
            if strict_validation_failed:
                continue
            merged_sessions.extend(valid_sessions)
            try:
                copy_artifacts_for_sessions(checkout, valid_sessions, copied_artifacts)
            except BaseException as exc:
                preserved = preserve_rejected_lane_artifacts(
                    result,
                    checkout,
                    {str(session["session_id"]) for session in valid_sessions},
                    f"compact artifact staging failed: {exc}",
                )
                if preserved:
                    release_lane_checkout(Path(result["lane_dir"]))
                raise
            summary["merged_session_count"] = len(merged_sessions)
            summary["copied_artifact_count"] = len(copied_artifacts)
            summary["merged_session_ids"] = [session["session_id"] for session in merged_sessions]
        if merged_sessions:
            summary.pop("skipped", None)
            summary["registry_replacement_attempted"] = True
            merge_registry(merged_sessions)
    except BaseException:
        # The outer publication transaction owns rollback so it can preserve the
        # initiating error and aggregate every cleanup failure.
        raise
    return summary


def rollback_matrix_publication(
    registry_path: Path,
    registry_before: bytes,
    merge_summary: dict[str, Any],
    published_comparisons: list[str],
    authority_snapshots: dict[Path, bytes],
) -> None:
    rollback_errors: list[BaseException] = []

    def attempt(action: Any) -> None:
        try:
            action()
        except BaseException as exc:
            rollback_errors.append(exc)

    attempt(lambda: atomic_write_bytes(registry_path, registry_before))
    for rel in [*merge_summary.get("copied_artifacts", []), *published_comparisons]:
        path = ROOT / rel

        def remove_path(path: Path = path) -> None:
            if path.is_dir():
                chmod_tree(path)
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()

        attempt(remove_path)
    for path, content in authority_snapshots.items():
        attempt(lambda path=path, content=content: atomic_write_bytes(path, content))
    if rollback_errors:
        raise BaseExceptionGroup("matrix publication rollback failed", rollback_errors)


@contextmanager
def publication_transaction_guard(rollback: Any, *, enabled: bool = True):
    """Keep every publication decision inside an interrupt-safe rollback boundary."""
    try:
        yield
    except BaseException as publication_error:
        if enabled:
            try:
                rollback()
            except BaseException as rollback_error:
                raise BaseExceptionGroup(
                    "matrix publication failed and rollback reported errors",
                    [publication_error, rollback_error],
                ) from None
        raise


def publish_ready_comparisons(
    sequence_ids: list[str],
    profiles: list[str],
    replicate_index: int,
    published: list[str] | None = None,
) -> list[str]:
    if published is None:
        published = []
    if not profiles:
        return published
    registry = load_json(ROOT / "data/workflow-sessions.json")
    for sequence_id in sequence_ids:
        seq = workflow.load_sequence(sequence_id)
        baseline = find_baseline_record(registry, seq, replicate_index)
        if baseline is None or baseline_reuse_state(baseline, ROOT) != "reusable":
            continue
        for profile_id in profiles:
            treatment = workflow.find_pool_profile_record(registry, seq, profile_id, replicate_index)
            if treatment is None or workflow.reviewed_session_reuse_state(treatment, ROOT) != "reusable":
                continue
            project_id = workflow.PROJECT_META[seq["fixture_id"]]["project_id"]
            frozen_pool_fingerprint = treatment.get("baseline_pool", {}).get("protocol_fingerprint")
            if not isinstance(frozen_pool_fingerprint, str) or not frozen_pool_fingerprint:
                frozen_pool_fingerprint = baseline.get("baseline_pool", {}).get("protocol_fingerprint")
            fingerprint = (
                frozen_pool_fingerprint
                if isinstance(frozen_pool_fingerprint, str) and frozen_pool_fingerprint
                else workflow.baseline_protocol_fingerprint(seq)
            )
            comparison_id = (
                f"baseline-{workflow.artifact_lane_label(project_id)}-{workflow.DATE.replace('-', '')}"
                f"-vs-{workflow.artifact_profile_label(profile_id)}-p-{fingerprint}-r{replicate_index}"
            )
            path = ROOT / WORKFLOW_ARTIFACT_ROOT / f"{comparison_id}.json"
            if not path.exists():
                published.append(str(path.relative_to(ROOT)))
                comparison = workflow.write_comparison_if_ready(
                    seq, "phase-2-sequential-workflow-v1", replicate_index, profile_id
                )
                if comparison is None:
                    raise RuntimeError(f"reviewed records did not produce comparison {comparison_id}")
    return published


PROTECTED_CONTROL_PLANE_FILES = workflow.PAID_LAUNCH_PROTECTED_FILES + (
    Path("scripts/test_opencode_workflow_runtime.py"),
)


def restore_protected_control_plane_files(root: Path = ROOT) -> None:
    for relative in PROTECTED_CONTROL_PLANE_FILES:
        if not (root / relative).is_file():
            tracked = subprocess.run(
                ["git", "cat-file", "-e", f"HEAD:{relative.as_posix()}"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            if tracked.returncode != 0:
                continue
            subprocess.run(
                [
                    "git", "restore", "--source=HEAD", "--staged", "--worktree",
                    "--", str(relative),
                ],
                cwd=root,
                check=True,
            )


def refresh_generated_runbook(root: Path = ROOT) -> None:
    subprocess.run(
        [sys.executable, "scripts/update_workflow_runbook.py"],
        cwd=root,
        check=True,
    )


def refresh_cumulative_usage_audit(root: Path = ROOT) -> None:
    subprocess.run(
        [sys.executable, "scripts/audit_codex_cumulative_usage.py"],
        cwd=root,
        check=True,
    )


def refresh_current_sol_panel(root: Path = ROOT) -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/generate_current_evaluation_panel.py",
            "--model-condition-id",
            "codex-openai-gpt-5-6-sol-high",
            "--replicate-index",
            "0",
            "--date",
            "2026-07-29",
        ],
        cwd=root,
        check=True,
    )


def refresh_lifecycle_v1_opencode_sol_high_pair_panels(root: Path = ROOT) -> None:
    """Refresh the canonical accepted-ordinal V1 OpenCode/Codex pair panels."""
    pairs = (
        (1, "lifecycle-v1-sol-high-accepted-pair-01"),
        (2, "lifecycle-v1-sol-high-accepted-pair-02"),
    )
    for replicate_index, pair_id in pairs:
        subprocess.run(
            [
                sys.executable,
                "scripts/generate_current_evaluation_panel.py",
                "--model-condition-id", "opencode-openai-gpt-5-6-sol-high",
                "--replicate-index", str(replicate_index),
                "--comparison-pair-id", pair_id,
                "--date", "2026-08-02",
                "--output", f"sources/evaluations/audits/opencode-openai-gpt-5-6-sol-high-accepted-pair-{replicate_index:02d}-panel-results-20260802.json",
                "--sequence-id", "fastify-lifecycle-sequence-v1",
                "--sequence-id", "beets-lifecycle-sequence-v1",
            ],
            cwd=root,
            check=True,
        )


def retained_claude_lifecycle_v1_recovery_lanes(
    summary: dict[str, Any],
    root: Path = ROOT,
) -> list[dict[str, Any]]:
    """Validate a retained paid Claude V1 run before controller-only recovery."""
    plan = summary.get("plan")
    if not isinstance(plan, dict):
        raise ValueError("retained recovery summary is missing its plan")
    if plan.get("sequences") != list(CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER):
        raise ValueError("retained recovery plan does not have the exact authorized sequence order")
    if plan.get("max_parallel") != 1:
        raise ValueError("retained recovery requires the original serialized Claude Code Lifecycle V1 plan")
    if plan.get("replicate_index") != 0 or plan.get("runner_args") != []:
        raise ValueError("retained recovery plan does not bind the authorized r0 no-retry run")
    condition = plan.get("model_condition")
    if not isinstance(condition, dict) or {
        "id": condition.get("id"),
        "runtime_id": condition.get("runtime_id"),
        "model": condition.get("model"),
        "reasoning_effort": condition.get("reasoning_effort"),
    } != {
        "id": "claude-code-openrouter-gpt-5-6-sol-high",
        "runtime_id": "claude-code",
        "model": "gpt-5.6-sol",
        "reasoning_effort": "high",
    }:
        raise ValueError("retained recovery plan does not bind the authorized Claude Code Sol/high condition")
    results = summary.get("lane_results")
    if not isinstance(results, list) or len(results) != len(CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER):
        raise ValueError("retained recovery summary has an incomplete set of lanes")
    by_sequence = {
        item.get("sequence_id"): item
        for item in results
        if isinstance(item, dict) and isinstance(item.get("sequence_id"), str)
    }
    if set(by_sequence) != set(CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER):
        raise ValueError("retained recovery lanes do not match the authorized sequences")
    ordered: list[dict[str, Any]] = []
    for sequence_id in CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER:
        result = by_sequence[sequence_id]
        if result.get("exit_code") != 0 or not isinstance(result.get("checkout"), str):
            raise ValueError(f"retained recovery lane did not complete successfully: {sequence_id}")
        checkout = Path(result["checkout"])
        if not nonsymlink_directory_ancestry(checkout):
            raise ValueError(f"retained recovery checkout is unsafe: {sequence_id}")
        frozen = result.get("expected_session_binding", {}).get("frozen_protocol")
        if not isinstance(frozen, dict):
            raise ValueError(f"retained recovery binding has no frozen protocol: {sequence_id}")
        protocol_rel = frozen.get("path")
        protocol_sha256 = frozen.get("sha256")
        if (
            not isinstance(protocol_rel, str)
            or Path(protocol_rel).is_absolute()
            or not isinstance(protocol_sha256, str)
            or len(protocol_sha256) != 64
        ):
            raise ValueError(f"retained recovery frozen protocol reference is unsafe: {sequence_id}")
        protocol_path = root / protocol_rel
        if not nonsymlink_file_within(root, protocol_path):
            raise ValueError(f"retained recovery frozen protocol is absent or unsafe: {sequence_id}")
        if hashlib.sha256(protocol_path.read_bytes()).hexdigest() != protocol_sha256:
            raise ValueError(f"retained recovery frozen protocol bytes differ: {sequence_id}")
        authority = load_json(root / CLAUDE_LIFECYCLE_V1_AUTHORITY_REL)
        authority_row = next(
            (
                row for row in authority.get("sequences", [])
                if isinstance(row, dict) and row.get("sequence_id") == sequence_id
            ),
            None,
        ) if isinstance(authority, dict) else None
        if (
            not isinstance(authority_row, dict)
            or authority_row.get("protocol_path") != frozen.get("path")
            or authority_row.get("protocol_sha256") != frozen.get("sha256")
            or authority_row.get("baseline_pool_fingerprint")
            != result.get("expected_session_binding", {}).get("baseline_pool_fingerprint")
        ):
            raise ValueError(f"retained recovery frozen protocol is not the owner-authorized binding: {sequence_id}")
        expected = expected_session_binding_for_protocol(
            sequence_id=sequence_id,
            profile_id="baseline-claude-code-no-mcp",
            replicate_index=0,
            protocol_path=Path(protocol_rel),
            root=root,
        )
        if result.get("expected_session_binding") != expected:
            raise ValueError(f"retained recovery binding does not match current frozen protocol: {sequence_id}")
        produced = result.get("produced_session_ids")
        if not isinstance(produced, list) or len(produced) != 1 or not isinstance(produced[0], str):
            raise ValueError(f"retained recovery lane does not contain exactly one produced session: {sequence_id}")
        receipt_path = claude_lifecycle_v1_attempt_path(sequence_id, 0, root)
        if not receipt_path.is_file() or receipt_path.is_symlink():
            raise ValueError(f"retained recovery immutable receipt is absent or unsafe: {sequence_id}")
        receipt = load_json(receipt_path)
        if not isinstance(receipt, dict) or (
            receipt.get("schema_version") != 1
            or receipt.get("attempt_status") != "reserved-before-provider-task"
            or receipt.get("task_family_generation") != "lifecycle-v1"
            or receipt.get("sequence_id") != sequence_id
            or receipt.get("replicate_index") != 0
            or receipt.get("profile_id") != "baseline-claude-code-no-mcp"
            or receipt.get("model_condition_id") != "claude-code-openrouter-gpt-5-6-sol-high"
            or receipt.get("model") != "gpt-5.6-sol"
            or receipt.get("reasoning_effort") != "high"
            or receipt.get("owner_authorization_message_id") != "1533397324384964609"
            or receipt.get("authority_path") != CLAUDE_LIFECYCLE_V1_AUTHORITY_REL.as_posix()
            or receipt.get("expected_session_binding") != expected
        ):
            raise ValueError(f"retained recovery receipt does not match the authorized identity: {sequence_id}")
        ordered.append(result)
    return ordered


def controller_validation_python() -> str:
    """Return a controller Python with all validation dependencies before spend."""
    configured = os.environ.get("WORKFLOW_VALIDATION_PYTHON")
    candidates = [configured, sys.executable, shutil.which("python3")]
    checked: list[str] = []
    for candidate in candidates:
        if not candidate or candidate in checked:
            continue
        checked.append(candidate)
        try:
            probe = subprocess.run(
                [candidate, "-c", "import jsonschema"],
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError:
            continue
        if probe.returncode == 0:
            return candidate
    raise RuntimeError(
        "no controller Python can import jsonschema; refusing to start lanes before validation is runnable "
        f"(checked={checked}; set WORKFLOW_VALIDATION_PYTHON to a prepared interpreter)"
    )


def run_validation(summary_dir: Path, validation_python: str | None = None) -> dict[str, Any]:
    truthmark_candidates = [
        shutil.which("truthmark"),
        "/opt/data/.local/bin/truthmark",
        str(Path.home() / ".local/bin/truthmark"),
    ]
    truthmark = next(
        (candidate for candidate in truthmark_candidates if candidate and Path(candidate).is_file()),
        truthmark_candidates[-1],
    )
    validation_env = os.environ.copy()
    validation_env["PATH"] = f"{Path(truthmark).parent}:{validation_env.get('PATH', '')}"
    validation_python = validation_python or controller_validation_python()
    commands = [
        [validation_python, "scripts/validate_repository.py"],
        [validation_python, "scripts/test_workflow_evaluation_contract.py"],
        ["git", "diff", "--check"],
        [truthmark, "check", "--json"],
        [truthmark, "index", "--json"],
    ]
    results: list[dict[str, Any]] = []
    for idx, cmd in enumerate(commands, start=1):
        out = summary_dir / f"validation-{idx}-{safe_name(cmd[0])}.txt"
        with out.open("w") as log:
            try:
                proc = subprocess.run(
                    cmd, cwd=ROOT, text=True, stdout=log, stderr=subprocess.STDOUT, env=validation_env
                )
                return_code = proc.returncode
            except OSError as exc:
                log.write(f"unable to execute {cmd[0]}: {exc}\n")
                return_code = 127
        results.append({"command": cmd, "exit_code": return_code, "output": str(out)})
        if len(cmd) > 1 and cmd[1] == "scripts/test_workflow_evaluation_contract.py":
            restore_protected_control_plane_files(ROOT)
    return {"passed": all(item["exit_code"] == 0 for item in results), "results": results}


def recover_retained_claude_lifecycle_v1_run(run_root: Path) -> int:
    """Publish exactly one retained Claude V1 run without any provider invocation."""
    if not nonsymlink_directory_ancestry(run_root):
        raise ValueError("retained recovery run root is unsafe")
    summary_path = run_root / "matrix-summary.json"
    if not nonsymlink_file_within(run_root, summary_path):
        raise ValueError("retained recovery matrix summary is absent or unsafe")
    summary = load_json(summary_path)
    if not isinstance(summary, dict):
        raise ValueError("retained recovery matrix summary is malformed")
    lane_results = retained_claude_lifecycle_v1_recovery_lanes(summary, ROOT)
    source_status = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.splitlines()
    permitted = {
        f"?? {CLAUDE_LIFECYCLE_V1_ATTEMPT_DIR / 'fastify-r0.json'}",
        f"?? {CLAUDE_LIFECYCLE_V1_ATTEMPT_DIR / 'beets-r0.json'}",
    }
    if set(source_status) != permitted:
        raise ValueError("retained recovery requires a clean source worktree except its two immutable attempt receipts")
    registry_path = ROOT / "data/workflow-sessions.json"
    registry_before = registry_path.read_bytes()
    authority_paths = (
        ROOT / "docs/evaluations/operations/runbook.md",
        ROOT / "sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json",
        ROOT / "sources/evaluations/audits/codex-openai-gpt-5-6-sol-high-r0-panel-results-20260729.json",
        ROOT / "sources/evaluations/audits/opencode-openai-gpt-5-6-sol-high-accepted-pair-01-panel-results-20260802.json",
        ROOT / "sources/evaluations/audits/opencode-openai-gpt-5-6-sol-high-accepted-pair-02-panel-results-20260802.json",
    )
    authority_snapshots = {path: path.read_bytes() for path in authority_paths}
    merge_summary: dict[str, Any] = {}
    published_comparisons: list[str] = []

    def rollback() -> None:
        rollback_matrix_publication(
            registry_path,
            registry_before,
            merge_summary,
            published_comparisons,
            authority_snapshots,
        )

    with publication_transaction_guard(rollback):
        merge_lanes(lane_results, 0, merge_summary)
        if merge_summary.get("rejected_session_ids") or merge_summary.get("merged_session_count") != 2:
            raise ValueError("retained recovery strict ingress did not accept both paid lanes")
        refresh_generated_runbook()
        refresh_cumulative_usage_audit()
        refresh_current_sol_panel()
        refresh_lifecycle_v1_opencode_sol_high_pair_panels()
        validation = run_validation(run_root)
        if not validation["passed"]:
            raise RuntimeError("retained recovery post-publication validation failed")
    recovered = {
        "schema_version": 1,
        "recovery_mode": "controller-only-no-provider",
        "source_matrix_summary": str(summary_path),
        "lane_results": [
            {"sequence_id": item["sequence_id"], "session_ids": item["produced_session_ids"]}
            for item in lane_results
        ],
        "merge": merge_summary,
        "validation": validation,
        "accepted": True,
    }
    write_json(run_root / "recovery-summary.json", recovered)
    print(json.dumps(recovered, indent=2), flush=True)
    return 0


def cleanup_lane_checkouts(run_root: Path) -> None:
    resolved_run_root = run_root.resolve()
    if resolved_run_root in CLEANUP_PROHIBITED_RUN_ROOTS or (run_root / PRESERVATION_FAILURE_SENTINEL).exists():
        return
    for checkout in run_root.glob("*/checkout"):
        lane_dir = checkout.parent
        if (
            lane_dir.resolve() in CLEANUP_PROHIBITED_LANE_DIRS
            or (lane_dir / LANE_CLEANUP_PROHIBITION_SENTINEL).exists()
        ):
            continue
        if checkout.exists():
            chmod_tree(checkout)
            shutil.rmtree(checkout, ignore_errors=True)


def execute_lane_jobs(
    jobs: list[tuple[str, str]],
    max_parallel: int,
    run_job: Callable[[tuple[str, str]], dict[str, Any]],
    on_result: Callable[[dict[str, Any]], None] | None = None,
) -> list[dict[str, Any]]:
    """Execute serialized jobs fail-stop; use queued futures only for parallel plans."""
    results: list[dict[str, Any]] = []
    if not jobs:
        return results

    def record(result: dict[str, Any]) -> None:
        results.append(result)
        if on_result is not None:
            on_result(result)

    if max_parallel == 1:
        for job in jobs:
            result = run_job(job)
            record(result)
            if result.get("exit_code") != 0:
                break
        return results
    with futures.ThreadPoolExecutor(max_workers=min(max_parallel, len(jobs))) as pool:
        submitted = [pool.submit(run_job, job) for job in jobs]
        for future in futures.as_completed(submitted):
            record(future.result())
    return results


def selected_model_condition(args: argparse.Namespace, *, configure: bool = False) -> dict[str, str] | None:
    values = (
        args.workflow_model_condition_id,
        args.workflow_model,
        args.workflow_reasoning_effort,
    )
    if not any(values):
        return None
    if not all(values):
        raise SystemExit(
            "--workflow-model-condition-id, --workflow-model, and --workflow-reasoning-effort must be supplied together"
        )
    condition, _ = condition_runtime.resolve_condition_pair(ROOT, str(values[0]))
    if condition.get("model") != values[1] or condition.get("reasoning_effort") != values[2]:
        raise ValueError("registered model condition does not match the requested model/reasoning effort")
    if configure:
        launcher_module = {
            "opencode-cli": opencode_condition_launcher,
            "claude-code": claude_condition_launcher,
        }.get(condition.get("runtime_id"), model_condition_launcher)
        launcher_module.configure_model_condition(*values)
    return {
        "id": str(condition["id"]),
        "runtime_id": str(condition["runtime_id"]),
        "launcher": {
            "opencode-cli": "scripts/run_opencode_workflow_model_condition.py",
            "claude-code": "scripts/run_claude_code_workflow_model_condition.py",
        }.get(str(condition.get("runtime_id")), "scripts/run_codex_workflow_model_condition.py"),
        "model": str(condition["model"]),
        "reasoning_effort": str(condition["reasoning_effort"]),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sequences", nargs="*", help="workflow sequence IDs; defaults to all active sequences")
    parser.add_argument("--max-parallel", type=int, default=3, help="maximum flow lanes to run concurrently (default: 3)")
    parser.add_argument("--replicate-index", type=int, default=0)
    parser.add_argument("--workflow-model-condition-id")
    parser.add_argument("--workflow-model")
    parser.add_argument("--workflow-reasoning-effort")
    parser.add_argument("--lane-root", type=Path, default=DEFAULT_LANE_ROOT)
    parser.add_argument("--source-codex-home", type=Path, help="forwarded to each shared-baseline runner; defaults to runner default/CODEX_HOME")
    parser.add_argument("--treatment-profile", action="append", dest="treatment_profiles", help="treatment profile; repeat to run multiple profiles concurrently after baseline review")
    parser.add_argument("--timeout-per-task", type=int, help="forwarded to each lane runner")
    parser.add_argument("--prepare-only", action="store_true", help="forward prepare-only to lane runners for a no-model-spend concurrency smoke")
    parser.add_argument("--skip-container-preflight", action="store_true", help="forwarded to lane runners; smoke/debug only")
    parser.add_argument("--skip-codex-preflight", action="store_true", help="forwarded to lane runners; smoke/debug only")
    parser.add_argument("--skip-dependency-install", action="store_true", help="forwarded to lane runners; smoke/debug only")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-lanes", action="store_true", help="keep lane checkouts after successful merge for debugging")
    parser.add_argument(
        "--r2-beets-retry",
        action="store_true",
        help="execute exactly one separately-authorized Beets r2 retry after retained evidence ingress failure",
    )
    parser.add_argument(
        "--recover-retained-claude-lifecycle-v1-run-root",
        type=Path,
        help="controller-only recovery of one retained paid Claude Code Lifecycle V1 run; never invokes a provider",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    workflow.clear_ambient_git_object_environment()
    args = parse_args(argv)
    if args.recover_retained_claude_lifecycle_v1_run_root is not None:
        incompatible = (
            args.sequences
            or args.treatment_profiles
            or args.workflow_model_condition_id
            or args.workflow_model
            or args.workflow_reasoning_effort
            or args.prepare_only
            or args.dry_run
        )
        if incompatible:
            raise SystemExit("retained Claude Code Lifecycle V1 recovery accepts no execution-plan arguments")
        return recover_retained_claude_lifecycle_v1_run(args.recover_retained_claude_lifecycle_v1_run_root)
    model_condition = selected_model_condition(args, configure=True)
    sequences = args.sequences or active_sequences()
    valid = set(active_sequences())
    unknown = [seq for seq in sequences if seq not in valid]
    if unknown:
        raise SystemExit(f"Unknown/non-active sequence IDs: {unknown}; active={sorted(valid)}")
    if args.max_parallel < 1:
        raise SystemExit("--max-parallel must be >= 1")
    if (
        isinstance(model_condition, dict)
        and model_condition.get("runtime_id") == "claude-code"
        and any(sequence_id in CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER for sequence_id in sequences)
        and args.max_parallel != 1
    ):
        raise SystemExit("owner-authorized Claude Code Lifecycle V1 requires --max-parallel 1")
    if args.lane_root.exists() and not nonsymlink_directory_ancestry(args.lane_root):
        raise ValueError("lane root contains a symlink or non-directory ancestor")

    production_lock_fd = None
    treatment_profiles = args.treatment_profiles or []
    registry = load_json(ROOT / "data/workflow-sessions.json")
    replacement_runtime = (
        isinstance(model_condition, dict)
        and model_condition.get("runtime_id") in {"opencode-cli", "claude-code"}
    )
    baseline_profile_id = (
        "runtime-opencode-codex-product-v1"
        if isinstance(model_condition, dict) and model_condition.get("runtime_id") == "opencode-cli"
        else "baseline-claude-code-no-mcp"
        if isinstance(model_condition, dict) and model_condition.get("runtime_id") == "claude-code"
        else "baseline-bare-codex"
    )
    if args.r2_beets_retry:
        if (
            sequences != ["beets-lifecycle-sequence-v1"]
            or args.replicate_index != 2
            or args.max_parallel != 1
            or treatment_profiles
            or not isinstance(model_condition, dict)
            or model_condition != {
                "id": "opencode-openai-gpt-5-6-sol-high",
                "runtime_id": "opencode-cli",
                "launcher": "scripts/run_opencode_workflow_model_condition.py",
                "model": "gpt-5.6-sol",
                "reasoning_effort": "high",
            }
            or not opencode_lifecycle_v1_r2_beets_retry_authorized(ROOT)
        ):
            raise SystemExit(
                "--r2-beets-retry requires exactly Beets r2, bare OpenCode Sol/high, --max-parallel 1, "
                "no treatment profile, and its exact owner authorization"
            )

    def baseline_state(sequence_id: str) -> str:
        if args.prepare_only:
            return "missing"
        sequence = workflow.load_sequence(sequence_id)
        if (
            isinstance(model_condition, dict)
            and model_condition.get("runtime_id") == "claude-code"
        ):
            session = workflow.find_comparison_baseline_record(
                registry, sequence, baseline_profile_id, args.replicate_index
            )
            return workflow.reviewed_session_reuse_state(session, ROOT)
        if replacement_runtime:
            session = workflow.find_pool_profile_record(
                registry, sequence, baseline_profile_id, args.replicate_index
            )
            return workflow.reviewed_session_reuse_state(session, ROOT)
        return baseline_campaign_state(
            registry, sequence, args.replicate_index, baseline_profile_id, ROOT
        )

    def profile_state(sequence_id: str, profile_id: str) -> str:
        sequence = workflow.load_sequence(sequence_id)
        session = workflow.find_pool_profile_record(registry, sequence, profile_id, args.replicate_index)
        state = workflow.reviewed_session_reuse_state(session, ROOT)
        if state == "reusable":
            return state
        if (
            isinstance(model_condition, dict)
            and model_condition.get("id") == CLAUDE_ANTHROPIC_SONNET_5_HIGH_CONDITION_ID
            and sequence_id in CLAUDE_LIFECYCLE_V1_SEQUENCE_ORDER
        ):
            attempt = claude_anthropic_sonnet_treatment_attempt_path(
                sequence_id, profile_id, args.replicate_index, ROOT
            )
            if attempt.exists():
                return "occupied"
        return state

    def treatment_gate(sequence_id: str) -> tuple[bool, str]:
        return workflow.baseline_v2_treatment_gate(workflow.load_sequence(sequence_id), ROOT)

    def baseline_run_gate(sequence_id: str) -> tuple[bool, str]:
        if isinstance(model_condition, dict) and model_condition.get("runtime_id") == "opencode-cli":
            return opencode_baseline_run_gate(
                registry,
                sequence_id,
                args.replicate_index,
                ROOT,
                r2_beets_retry=args.r2_beets_retry,
            )
        if isinstance(model_condition, dict) and model_condition.get("runtime_id") == "claude-code":
            if args.dry_run:
                return True, "dry-run only; no provider spend"
            return claude_baseline_run_gate(
                registry,
                sequence_id,
                args.replicate_index,
                ROOT,
                model_condition_id=str(model_condition.get("id")),
            )
        return workflow.baseline_v2_pilot_run_gate(
            workflow.load_sequence(sequence_id), ROOT, args.replicate_index
        )

    if args.prepare_only and treatment_profiles:
        for sequence_id in sequences:
            passed, reason = treatment_gate(sequence_id)
            if not passed:
                raise ValueError(f"treatments are blocked for {sequence_id}: {reason}")
    jobs = (
        [(sequence_id, profile) for sequence_id in sequences for profile in (treatment_profiles or [baseline_profile_id])]
        if args.prepare_only
        else plan_workflow_jobs(
            sequences,
            treatment_profiles,
            baseline_state=baseline_state,
            profile_state=profile_state,
            treatment_gate=treatment_gate,
            baseline_run_gate=baseline_run_gate,
            baseline_profile_id=baseline_profile_id,
        )
    )
    for sequence_id, profile_id in jobs:
        workflow.require_zero_mistake_pilot_replicate(
            workflow.load_sequence(sequence_id),
            profile_id,
            args.replicate_index,
            prepare_only=args.prepare_only,
        )
    serialized_replication_jobs = [
        (sequence_id, profile_id)
        for sequence_id, profile_id in jobs
        if profile_id in {"baseline-bare-codex", "baseline-claude-code-no-mcp", "runtime-opencode-codex-product-v1"}
        and (
            args.replicate_index > 0
            or (
                profile_id == "runtime-opencode-codex-product-v1"
                and workflow.load_sequence(sequence_id).get("task_family_generation") == "lifecycle-v1"
            )
        )
        and workflow.load_sequence(sequence_id).get("task_family_generation") in {"baseline-v3", "baseline-v4", "lifecycle-v1"}
    ]
    if serialized_replication_jobs and args.max_parallel != 1:
        raise SystemExit("owner-authorized current baseline replication requires --max-parallel 1")
    published_launch_commit = None
    if not args.prepare_only and not args.dry_run:
        published_launch_commit = workflow.certified_published_launch_commit(ROOT)
    validation_python = None if args.dry_run else controller_validation_python()
    if not args.dry_run and not ensure_nonsymlink_directory_ancestry(args.lane_root):
        raise ValueError("lane root contains a symlink or non-directory ancestor")
    production_lock_fd = None if args.prepare_only or args.dry_run else acquire_production_lock()
    timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%S%fZ")
    run_root = args.lane_root / f"workflow-matrix-{timestamp}-p{os.getpid()}-r{args.replicate_index}"
    runner_args: list[str] = []
    if args.timeout_per_task is not None:
        runner_args.extend(["--timeout-per-task", str(args.timeout_per_task)])
    for flag in ("prepare_only", "skip_container_preflight", "skip_codex_preflight", "skip_dependency_install"):
        if getattr(args, flag):
            runner_args.append("--" + flag.replace("_", "-"))
    if args.prepare_only:
        runner_args.append("--no-provider")

    job_specs = [
        {
            "sequence_id": sequence_id,
            "profile_id": profile,
            "protocol": str(find_protocol(ROOT, sequence_id, profile, model_condition_override=model_condition).relative_to(ROOT)),
        }
        for sequence_id, profile in jobs
    ]
    plan = {
        "sequences": sequences,
        "treatment_profiles": treatment_profiles,
        "jobs": job_specs,
        "max_parallel": args.max_parallel,
        "replicate_index": args.replicate_index,
        "model_condition": model_condition,
        "lane_root": str(run_root),
        "runner_args": runner_args,
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0

    run_root.mkdir(mode=0o700)
    if not nonsymlink_directory_ancestry(run_root):
        raise ValueError("matrix run root contains a symlink or non-directory ancestor")
    if not args.keep_lanes:
        atexit.register(cleanup_lane_checkouts, run_root)
    write_json(run_root / "plan.json", plan)
    lane_results: list[dict[str, Any]] = []

    def run_job(job: tuple[str, str]) -> dict[str, Any]:
        sequence_id, treatment_profile = job
        return run_flow_lane(
            sequence_id=sequence_id,
            treatment_profile=treatment_profile,
            lane_root=run_root,
            replicate_index=args.replicate_index,
            runner_args=runner_args,
            source_codex_home=args.source_codex_home,
            model_condition=model_condition,
            production_lock_fd=production_lock_fd,
            published_launch_commit=published_launch_commit,
            r2_beets_retry=args.r2_beets_retry,
        )

    lane_results = execute_lane_jobs(
        jobs,
        args.max_parallel,
        run_job,
        on_result=lambda result: print(json.dumps(result, indent=2), flush=True),
    )

    registry_path = ROOT / "data/workflow-sessions.json"
    registry_before = registry_path.read_bytes() if not args.prepare_only else b""
    authority_paths = (
        ROOT / "docs/evaluations/operations/runbook.md",
        ROOT / "sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json",
        ROOT / "sources/evaluations/audits/codex-openai-gpt-5-6-sol-high-r0-panel-results-20260729.json",
        ROOT / "sources/evaluations/audits/opencode-openai-gpt-5-6-sol-high-accepted-pair-01-panel-results-20260802.json",
        ROOT / "sources/evaluations/audits/opencode-openai-gpt-5-6-sol-high-accepted-pair-02-panel-results-20260802.json",
    )
    authority_snapshots = (
        {path: path.read_bytes() for path in authority_paths}
        if not args.prepare_only
        else {}
    )
    lanes_passed = all(result["exit_code"] == 0 for result in lane_results)
    publish_allowed = publication_allowed(args.prepare_only, lane_results)
    merge_allowed = artifact_merge_allowed(args.prepare_only, lane_results)
    merge_summary = {
        "merged_session_count": 0,
        "copied_artifact_count": 0,
        "merged_session_ids": [],
        "copied_artifacts": [],
        "skipped": "prepare-only run" if args.prepare_only else "one or more lanes failed",
    }
    published_comparisons: list[str] = []
    def rollback_publication() -> None:
        rollback_matrix_publication(
            registry_path,
            registry_before,
            merge_summary,
            published_comparisons,
            authority_snapshots,
        )

    with publication_transaction_guard(
        rollback_publication,
        enabled=not args.prepare_only,
    ):
        if merge_allowed:
            merge_lanes(lane_results, args.replicate_index, merge_summary)
        authoritative_outputs_complete = matrix_outputs_complete(
            prepare_only=args.prepare_only,
            planned_job_count=len(jobs),
            lane_results=lane_results,
            merge_summary=merge_summary,
        )
        publish_allowed = publish_allowed and authoritative_outputs_complete
        if publish_allowed:
            publish_ready_comparisons(
                sequences,
                treatment_profiles,
                args.replicate_index,
                published_comparisons,
            )
        restore_protected_control_plane_files()
        refresh_generated_runbook()
        if not args.prepare_only and merge_summary.get("merged_session_count", 0):
            refresh_cumulative_usage_audit()
            refresh_current_sol_panel()
            refresh_lifecycle_v1_opencode_sol_high_pair_panels()
        validation = run_validation(run_root, validation_python)
        if not args.prepare_only and not validation["passed"]:
            rollback_matrix_publication(
                registry_path,
                registry_before,
                merge_summary,
                published_comparisons,
                authority_snapshots,
            )
            merge_summary["rolled_back_after_validation_failure"] = True
            published_comparisons = []
        execution_passed = lanes_passed and authoritative_outputs_complete and validation["passed"]
        awaiting_quality_review = False
        summary = {
            "plan": plan,
            "lane_results": sorted(lane_results, key=lambda item: item["sequence_id"]),
            "merge": merge_summary,
            "published_comparisons": published_comparisons,
            "validation": validation,
            "authoritative_outputs_complete": authoritative_outputs_complete,
            "execution_passed": execution_passed,
            "awaiting_quality_review": awaiting_quality_review,
            "accepted": matrix_acceptance_state(
                prepare_only=args.prepare_only,
                execution_passed=execution_passed,
                awaiting_quality_review=awaiting_quality_review,
            ),
        }
        write_json(run_root / "matrix-summary.json", summary)
    if (
        not args.prepare_only
        and validation["passed"]
        and not merge_summary.get("rolled_back_after_validation_failure")
    ):
        merged_ids = set(merge_summary.get("merged_session_ids", []))
        for result in lane_results:
            produced = set(result.get("produced_session_ids", []))
            if produced and produced <= merged_ids:
                release_lane_checkout(Path(result["lane_dir"]))
    print(json.dumps(summary, indent=2), flush=True)

    if not args.keep_lanes:
        cleanup_lane_checkouts(run_root)
    exit_code = matrix_exit_code(
        prepare_only=args.prepare_only,
        execution_passed=execution_passed,
        awaiting_quality_review=awaiting_quality_review,
        accepted=summary["accepted"],
    )
    if production_lock_fd is not None:
        os.close(production_lock_fd)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
