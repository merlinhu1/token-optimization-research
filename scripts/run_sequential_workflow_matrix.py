#!/usr/bin/env python3
"""Run multiple sequential workflow shared-baseline lanes in isolated parallel checkouts.

This is the concurrency wrapper for whatever workflow sequences are currently active.
Each flow runs in its own rsync-materialized checkout so parallel runs do not race on
`data/workflow-sessions.json`, workflow-session artifact directories, Codex home
roots, or tool caches. After lanes finish, this
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
CLAUDE_BASELINE_AUTHORITY_REL = Path(
    "sources/evaluations/audits/claude-code-sol-high-normal-baseline-authorization-20260731.json"
)
CLAUDE_ANTHROPIC_OPUS_5_HIGH_CONDITION_ID = "claude-code-anthropic-opus-5-high"
CLAUDE_ANTHROPIC_OPUS_5_MEDIUM_CONDITION_ID = "claude-code-anthropic-opus-5-medium"
WORKFLOW_ARTIFACT_ROOT = Path("sources/evaluations/workflow-sessions")
COMPACT_ARTIFACT_NAMES = {"run.json", "changes.diff", "evidence.jsonl.gz", "manifest.sha256"}


class UnsafeLaneOutputError(ValueError):
    """The provider-capable lane changed a controller output path unsafely."""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())




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










def claude_baseline_run_gate(
    registry: dict[str, Any],
    sequence_id: str,
    replicate_index: int,
    root: Path = ROOT,
    model_condition_id: str | None = None,
) -> tuple[bool, str]:
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


SERIALIZED_REPLICATION_PROFILE_IDS = {
    "baseline-claude-code-no-mcp",
    "runtime-opencode-codex-product-v1",
}
# Every supported family serializes: the race this prevents is over lane artifacts and
# the session registry, which is a property of the harness, not of a task family.
SERIALIZED_REPLICATION_GENERATIONS = set(workflow.repository_validation.SUPPORTED_TASK_FAMILY_GENERATIONS)


def serialized_replication_lanes(
    jobs: list[tuple[str, str]], *, replicate_index: int
) -> list[tuple[str, str]]:
    """Lanes an owner-authorized replication must run one at a time."""
    selected: list[tuple[str, str]] = []
    for sequence_id, profile_id in jobs:
        if profile_id not in SERIALIZED_REPLICATION_PROFILE_IDS:
            continue
        generation = workflow.load_sequence(sequence_id).get("task_family_generation")
        if generation not in SERIALIZED_REPLICATION_GENERATIONS:
            continue
        if replicate_index > 0 or (
            profile_id == "runtime-opencode-codex-product-v1"
            and generation in SERIALIZED_REPLICATION_GENERATIONS
        ):
            selected.append((sequence_id, profile_id))
    return selected


def requires_serialized_replication(
    sequences: list[str],
    treatment_profiles: list[str] | None,
    *,
    baseline_profile_id: str,
    replicate_index: int,
) -> bool:
    """Whether the requested lanes -- before planning -- must be serialized."""
    requested = [
        (sequence_id, profile)
        for sequence_id in sequences
        for profile in (treatment_profiles or [baseline_profile_id])
    ]
    return bool(serialized_replication_lanes(requested, replicate_index=replicate_index))


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











def opencode_baseline_run_gate(
    registry: dict[str, Any],
    sequence_id: str,
    replicate_index: int,
    root: Path = ROOT,
    *,
    r2_beets_retry: bool = False,
) -> tuple[bool, str]:
    # Both authorised OpenCode baseline paths belonged to the retired high-effort campaign,
    # whose receipts were deleted with that corpus. No standalone OpenCode baseline remains.
    return False, "no current OpenCode baseline authorization"


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
    if provider_capable and not published_launch_commit:
        raise ValueError("provider-capable lane requires a certified published launch commit")
    # The OpenCode and direct-Anthropic baseline reservations belonged to retired campaigns
    # whose authority receipts were deleted with their corpus. Nothing reserves a parent
    # receipt now; the lane runs against its frozen protocol alone.
    parent_claude_receipt_binding: dict[str, Any] | None = None
    parent_opencode_receipt_binding: dict[str, Any] | None = None
    if provider_capable:
        clone_published_checkout(checkout, published_launch_commit)
    else:
        rsync_checkout(ROOT, checkout)
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
    # Credential sync existed for the direct-Anthropic campaigns, which are retired.
    env = workflow_lane_environment(tmp)
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
    transaction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    merged_sessions: list[dict[str, Any]] = []
    copied_artifacts: list[str] = []
    summary = transaction if transaction is not None else {}
    summary.update(
        merged_session_count=0,
        copied_artifact_count=0,
        merged_session_ids=[],
        copied_artifacts=copied_artifacts,
        registry_replacement_attempted=False,
        rejected_session_ids=[],
        rejected_lane_errors=[],
    )
    try:
        for result in lane_results:
            checkout = Path(result["checkout"])
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


PROTECTED_CONTROL_PLANE_FILES = workflow.PAID_LAUNCH_PROTECTED_FILES


@contextmanager
def isolated_validation_test_checkout(root: Path = ROOT):
    """Run contract tests from a disposable snapshot, never from the mutable controller worktree."""
    verify_protected_control_plane_files(root)
    temp_root = Path(tempfile.mkdtemp(prefix="workflow-validation-test-"))
    checkout = temp_root / "checkout"
    try:
        subprocess.run(
            ["git", "clone", "--quiet", "--no-local", str(root), str(checkout)],
            cwd=root,
            check=True,
        )
        diff = subprocess.run(
            ["git", "diff", "--binary", "HEAD"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
        ).stdout
        if diff:
            subprocess.run(
                ["git", "apply", "--binary", "-"],
                cwd=checkout,
                input=diff,
                check=True,
            )
        untracked_output = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=root,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout or ""
        untracked = untracked_output.splitlines()
        for relative_text in untracked:
            relative = Path(relative_text)
            source = root / relative
            destination = checkout / relative
            if source.is_symlink():
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.unlink(missing_ok=True)
                destination.symlink_to(source.readlink())
            elif source.is_dir():
                shutil.copytree(source, destination, symlinks=True, dirs_exist_ok=True)
            elif source.is_file():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        yield checkout
    finally:
        chmod_tree(temp_root)
        shutil.rmtree(temp_root, ignore_errors=True)


def restore_protected_control_plane_files(root: Path = ROOT) -> None:
    """Recover only missing protected files from HEAD for legacy callers/tests."""
    for relative in PROTECTED_CONTROL_PLANE_FILES:
        path = root / relative
        if path.is_file() and not path.is_symlink():
            continue
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
            ["git", "restore", "--source=HEAD", "--staged", "--worktree", "--", relative.as_posix()],
            cwd=root,
            check=True,
        )


def verify_protected_control_plane_files(root: Path = ROOT) -> None:
    missing = [
        relative.as_posix()
        for relative in PROTECTED_CONTROL_PLANE_FILES
        if not (root / relative).is_file() or (root / relative).is_symlink()
    ]
    if missing:
        raise RuntimeError(
            "protected control-plane file is missing; refusing to mutate the worktree: "
            + ", ".join(missing)
        )


def refresh_generated_runbook(root: Path = ROOT) -> None:
    """Regenerate every derived surface before post-publication validation.

    validate_repository fails on drift in both the runbook and the registry-derived corpus
    summaries, so publishing a session without regenerating them rolls the transaction back
    for a reason that has nothing to do with the run.
    """
    for script in ("scripts/update_workflow_runbook.py", "scripts/update_registry_summaries.py"):
        subprocess.run([sys.executable, script], cwd=root, check=True)



def controller_validation_python() -> str:
    """Return a controller Python with all validation dependencies before spend."""
    configured = os.environ.get("WORKFLOW_VALIDATION_PYTHON")
    candidates = [
        configured,
        sys.executable,
        str(ROOT / ".venv" / "bin" / "python3"),
        shutil.which("python3"),
    ]
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
    restore_protected_control_plane_files(ROOT)
    validation_env = os.environ.copy()
    validation_python = validation_python or controller_validation_python()
    commands = [
        [validation_python, "scripts/validate_repository.py"],
        [validation_python, "scripts/test_workflow_evaluation_contract.py"],
        [validation_python, "scripts/test_claude_code_usage_contract.py"],
        ["git", "diff", "--check"],
    ]
    results: list[dict[str, Any]] = []
    for idx, cmd in enumerate(commands, start=1):
        out = summary_dir / f"validation-{idx}-{safe_name(cmd[0])}.txt"
        is_contract_test = len(cmd) > 1 and cmd[1] == "scripts/test_workflow_evaluation_contract.py"
        command_cwd = ROOT
        with out.open("w") as log:
            try:
                if is_contract_test:
                    with isolated_validation_test_checkout(ROOT) as test_checkout:
                        command_cwd = test_checkout
                        proc = subprocess.run(
                            cmd,
                            cwd=test_checkout,
                            text=True,
                            stdout=log,
                            stderr=subprocess.STDOUT,
                            env=validation_env,
                        )
                else:
                    proc = subprocess.run(
                        cmd,
                        cwd=ROOT,
                        text=True,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        env=validation_env,
                    )
                return_code = proc.returncode
            except OSError as exc:
                log.write(f"unable to execute {cmd[0]}: {exc}\n")
                return_code = 127
        results.append({"command": cmd, "cwd": str(command_cwd), "exit_code": return_code, "output": str(out)})
    return {"passed": all(item["exit_code"] == 0 for item in results), "results": results}


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
    if condition.get("status") == "historical-inactive":
        raise ValueError(f"historical model condition cannot launch a new evaluation: {values[0]}")
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
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    workflow.clear_ambient_git_object_environment()
    args = parse_args(argv)
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
        and args.max_parallel != 1
    ):
        raise SystemExit("owner-authorized current baseline replication requires --max-parallel 1")
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
        raise SystemExit("--r2-beets-retry belonged to a retired campaign and has no authorization")

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
        return state

    def treatment_gate(sequence_id: str) -> tuple[bool, str]:
        return workflow.lifecycle_treatment_gate(workflow.load_sequence(sequence_id), ROOT)

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
        return workflow.lifecycle_treatment_gate(workflow.load_sequence(sequence_id), ROOT)

    if args.prepare_only and treatment_profiles:
        for sequence_id in sequences:
            passed, reason = treatment_gate(sequence_id)
            if not passed:
                raise ValueError(f"treatments are blocked for {sequence_id}: {reason}")
    # Serialization is a property of the requested lanes, not only the planned ones.
    if requires_serialized_replication(
        sequences,
        treatment_profiles,
        baseline_profile_id=baseline_profile_id,
        replicate_index=args.replicate_index,
    ) and args.max_parallel != 1:
        raise SystemExit("owner-authorized current baseline replication requires --max-parallel 1")
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
        workflow.require_lifecycle_baseline_replicate(
            workflow.load_sequence(sequence_id),
            profile_id,
            args.replicate_index,
            prepare_only=args.prepare_only,
        )
    planned_serialized_lanes = serialized_replication_lanes(jobs, replicate_index=args.replicate_index)
    if planned_serialized_lanes and args.max_parallel != 1:
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
    authority_paths = (ROOT / "docs/evaluations/operations/runbook.md",)
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
            merge_lanes(lane_results, merge_summary)
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
        verify_protected_control_plane_files()
        refresh_generated_runbook()
        validation = run_validation(run_root, validation_python)
        if not args.prepare_only and not validation["passed"]:
            rollback_matrix_publication(
                registry_path,
                registry_before,
                merge_summary,
                published_comparisons,
                authority_snapshots,
            )
            # The pre-validation refresh regenerated the runbook and corpus summaries against a
            # registry that no longer holds these sessions. Restoring only the registry and the
            # artifacts leaves those generated surfaces describing sessions that do not exist,
            # and every later `make check` fails on the drift rather than on the real failure.
            refresh_generated_runbook()
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
