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
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_codex_workflow_evaluation as workflow  # type: ignore
import run_codex_workflow_model_condition as model_condition_launcher  # type: ignore
DEFAULT_LANE_ROOT = Path("/opt/data/eval-workflow-lanes")
WORKFLOW_ARTIFACT_ROOT = Path("sources/evaluations/workflow-sessions")
COMPACT_ARTIFACT_NAMES = {"run.json", "changes.diff", "evidence.jsonl.gz", "manifest.sha256"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def baseline_reuse_state(session: dict[str, Any] | None, root: Path = ROOT) -> str:
    return workflow.reviewed_session_reuse_state(session, root)


def find_baseline_record(registry: dict[str, Any], seq: dict[str, Any], replicate_index: int) -> dict[str, Any] | None:
    return workflow.find_canonical_baseline_record(registry, seq, replicate_index)


def baseline_campaign_state(
    registry: dict[str, Any],
    seq: dict[str, Any],
    replicate_index: int,
    root: Path = ROOT,
) -> str:
    """Separate reusable-baseline selection from replicate occupancy."""
    baseline = find_baseline_record(registry, seq, replicate_index)
    if baseline is not None:
        return baseline_reuse_state(baseline, root)
    occupied = workflow.find_pool_profile_record(
        registry,
        seq,
        "baseline-bare-codex",
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
        str(source.resolve()) + "/",
        str(destination.resolve()) + "/",
    ]
    subprocess.run(cmd, check=True)


def find_protocol(root: Path, sequence_id: str, profile_id: str) -> Path:
    sequences = load_json(root / "data/workflow-task-sequences.json").get("sequences", [])
    active_sequence = next((item for item in sequences if item.get("id") == sequence_id), None)
    if not isinstance(active_sequence, dict) or active_sequence.get("status") != "active":
        raise ValueError(f"unknown or non-active workflow sequence: {sequence_id}")
    active_qualification = active_sequence.get("qualification_path")
    current_fingerprint = workflow.baseline_protocol_fingerprint(active_sequence)
    current_baseline_descriptor = workflow.baseline_protocol_descriptor(active_sequence)
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


def plan_workflow_jobs(
    sequence_ids: list[str],
    treatment_profiles: list[str],
    *,
    baseline_state: Callable[[str], str],
    profile_state: Callable[[str, str], str],
    treatment_gate: Callable[[str], tuple[bool, str]] | None = None,
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
                jobs.append((sequence_id, "baseline-bare-codex"))
            else:
                raise ValueError(f"baseline for {sequence_id} is {state}; no new baseline run is needed")
        elif state == "reusable":
            if treatment_gate is None:
                raise ValueError("treatment planning requires an explicit Baseline V2 pilot gate")
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
            jobs.append((sequence_id, "baseline-bare-codex"))
        else:
            raise ValueError(
                f"baseline for {sequence_id} is {state}; review it or choose a new replicate before treatment execution"
            )
    return jobs


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
        cmd = [
            sys.executable,
            "scripts/run_codex_workflow_model_condition.py",
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
    if profile_id != "baseline-bare-codex":
        cmd.extend(["--comparison-profile-id", profile_id])
    return cmd


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
) -> dict[str, Any]:
    lane_id = safe_name(f"{sequence_id}--{treatment_profile}")
    lane_dir = lane_root / lane_id
    checkout = lane_dir / "checkout"
    tmp = lane_dir / "tmp"
    logs = lane_dir / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)
    rsync_checkout(ROOT, checkout)
    before_session_ids = {
        str(session.get("session_id"))
        for session in load_json(checkout / "data/workflow-sessions.json").get("sessions", [])
        if session.get("session_id")
    }
    artifact_root = checkout / WORKFLOW_ARTIFACT_ROOT
    before_artifact_dirs = {path.name for path in artifact_root.iterdir() if path.is_dir()}

    protocol = find_protocol(checkout, sequence_id, treatment_profile).relative_to(checkout)
    protocol_doc = load_json(checkout / protocol)
    expected_session_binding = {
        "sequence_id": sequence_id,
        "profile_id": treatment_profile,
        "replicate_index": replicate_index,
        "frozen_protocol": {
            "protocol_id": protocol_doc["protocol_id"],
            "path": str(protocol),
            "sha256": hashlib.sha256((checkout / protocol).read_bytes()).hexdigest(),
        },
        "baseline_pool_fingerprint": protocol_doc["baseline_pool"]["protocol_fingerprint"],
        "selected_execution": protocol_doc["selected_execution"],
    }
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
    env = os.environ.copy()
    env["TMPDIR"] = str(tmp)
    env["SKIP_PAIR_VALIDATION"] = "1"
    env["WORKFLOW_LANE_DISABLE_AUTH_SYNC"] = "1"
    pass_fds: tuple[int, ...] = ()
    if production_lock_fd is not None:
        env[workflow.PRODUCTION_LOCK_FD_ENV] = str(production_lock_fd)
        pass_fds = (production_lock_fd,)
    log_path = logs / "lane.log"
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
    after_sessions = load_json(checkout / "data/workflow-sessions.json").get("sessions", [])
    produced_session_ids = sorted(
        str(session["session_id"])
        for session in after_sessions
        if session.get("session_id") and str(session["session_id"]) not in before_session_ids
    )
    failure_evidence: list[str] = []
    if proc.returncode != 0:
        failure_root = lane_dir / "failure-evidence"
        for path in artifact_root.iterdir():
            if not path.is_dir() or path.name in before_artifact_dirs or path.is_symlink():
                continue
            entries = list(path.iterdir())
            if any(entry.is_symlink() or not entry.is_file() for entry in entries):
                continue
            if {entry.name for entry in entries} != COMPACT_ARTIFACT_NAMES:
                continue
            failure_root.mkdir(exist_ok=True)
            destination = failure_root / path.name
            shutil.copytree(path, destination)
            failure_evidence.append(str(destination))

    return {
        "sequence_id": sequence_id,
        "treatment_profile": treatment_profile,
        "lane_id": lane_id,
        "lane_dir": str(lane_dir),
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
    doc = load_json(checkout / "data/workflow-sessions.json")
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
            if src.is_symlink() or not resolved.is_relative_to(lane_artifact_root):
                raise ValueError(f"workflow artifact root escapes lane checkout: {src}")
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
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with tmp.open("wb") as handle:
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
    """Durably replace a JSON authority from a same-directory temporary file."""
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with tmp.open("w") as handle:
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
    replicate_index: int,
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
            except Exception as exc:
                summary["rejected_session_ids"].extend(sorted(produced_session_ids))
                summary["rejected_lane_errors"].append(
                    f"{result.get('lane_id', result.get('sequence_id'))}: {exc}"
                )
                continue
            valid_sessions: list[dict[str, Any]] = []
            for session in sessions:
                if workflow.pilot_session_artifacts_valid(session, checkout):
                    valid_sessions.append(session)
                else:
                    summary["rejected_session_ids"].append(session.get("session_id"))
                    summary["rejected_lane_errors"].append(
                        f"{result.get('lane_id', result.get('sequence_id'))}: "
                        f"session {session.get('session_id')} failed strict compact artifact ingress validation"
                    )
            merged_sessions.extend(valid_sessions)
            copy_artifacts_for_sessions(checkout, valid_sessions, copied_artifacts)
            summary["merged_session_count"] = len(merged_sessions)
            summary["copied_artifact_count"] = len(copied_artifacts)
            summary["merged_session_ids"] = [session["session_id"] for session in merged_sessions]
        if merged_sessions:
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
            fingerprint = workflow.baseline_protocol_fingerprint(seq)
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


PROTECTED_CONTROL_PLANE_FILES = (Path("scripts/test_workflow_evaluation_contract.py"),)


def restore_protected_control_plane_files(root: Path = ROOT) -> None:
    for relative in PROTECTED_CONTROL_PLANE_FILES:
        if not (root / relative).is_file():
            subprocess.run(
                ["git", "restore", "--worktree", "--", str(relative)],
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


def run_validation(summary_dir: Path) -> dict[str, Any]:
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
    commands = [
        [sys.executable, "scripts/validate_repository.py"],
        [sys.executable, "scripts/test_workflow_evaluation_contract.py"],
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
    return {"passed": all(item["exit_code"] == 0 for item in results), "results": results}


def cleanup_lane_checkouts(run_root: Path) -> None:
    for checkout in run_root.glob("*/checkout"):
        if checkout.exists():
            chmod_tree(checkout)
            shutil.rmtree(checkout, ignore_errors=True)


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
    condition = model_condition_launcher.registered_condition(*values)
    if configure:
        model_condition_launcher.configure_model_condition(*values)
    return {
        "id": str(condition["id"]),
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
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    model_condition = selected_model_condition(args, configure=True)
    sequences = args.sequences or active_sequences()
    valid = set(active_sequences())
    unknown = [seq for seq in sequences if seq not in valid]
    if unknown:
        raise SystemExit(f"Unknown/non-active sequence IDs: {unknown}; active={sorted(valid)}")
    if args.max_parallel < 1:
        raise SystemExit("--max-parallel must be >= 1")

    production_lock_fd = None if args.prepare_only or args.dry_run else acquire_production_lock()
    treatment_profiles = args.treatment_profiles or []
    registry = load_json(ROOT / "data/workflow-sessions.json")

    def baseline_state(sequence_id: str) -> str:
        if args.prepare_only:
            return "missing"
        sequence = workflow.load_sequence(sequence_id)
        return baseline_campaign_state(registry, sequence, args.replicate_index, ROOT)

    def profile_state(sequence_id: str, profile_id: str) -> str:
        sequence = workflow.load_sequence(sequence_id)
        session = workflow.find_pool_profile_record(registry, sequence, profile_id, args.replicate_index)
        return workflow.reviewed_session_reuse_state(session, ROOT)

    def treatment_gate(sequence_id: str) -> tuple[bool, str]:
        return workflow.baseline_v2_treatment_gate(workflow.load_sequence(sequence_id), ROOT)

    if args.prepare_only and treatment_profiles:
        for sequence_id in sequences:
            passed, reason = treatment_gate(sequence_id)
            if not passed:
                raise ValueError(f"treatments are blocked for {sequence_id}: {reason}")
    jobs = (
        [(sequence_id, profile) for sequence_id in sequences for profile in (treatment_profiles or ["baseline-bare-codex"])]
        if args.prepare_only
        else plan_workflow_jobs(
            sequences,
            treatment_profiles,
            baseline_state=baseline_state,
            profile_state=profile_state,
            treatment_gate=treatment_gate,
        )
    )
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
            "protocol": str(find_protocol(ROOT, sequence_id, profile).relative_to(ROOT)),
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

    run_root.mkdir(parents=True, exist_ok=True)
    if not args.keep_lanes:
        atexit.register(cleanup_lane_checkouts, run_root)
    write_json(run_root / "plan.json", plan)
    lane_results: list[dict[str, Any]] = []
    if jobs:
        with futures.ThreadPoolExecutor(max_workers=min(args.max_parallel, len(jobs))) as pool:
            submitted = [
                pool.submit(
                    run_flow_lane,
                    sequence_id=sequence_id,
                    treatment_profile=treatment_profile,
                    lane_root=run_root,
                    replicate_index=args.replicate_index,
                    runner_args=runner_args,
                    source_codex_home=args.source_codex_home,
                    model_condition=model_condition,
                    production_lock_fd=production_lock_fd,
                )
                for sequence_id, treatment_profile in jobs
            ]
            for fut in futures.as_completed(submitted):
                result = fut.result()
                lane_results.append(result)
                print(json.dumps(result, indent=2), flush=True)

    registry_path = ROOT / "data/workflow-sessions.json"
    registry_before = registry_path.read_bytes() if not args.prepare_only else b""
    authority_paths = (
        ROOT / "docs/evaluations/operations/runbook.md",
        ROOT / "sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json",
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
        validation = run_validation(run_root)
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
