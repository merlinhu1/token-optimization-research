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


def compact_artifacts_intact(session: dict[str, Any] | None, root: Path = ROOT) -> bool:
    if not isinstance(session, dict):
        return False
    artifacts = session.get("artifacts", {})
    if not isinstance(artifacts, dict):
        return False
    required = [artifacts.get(key) for key in ("run_record", "final_diff", "evidence_bundle", "manifest")]
    if not all(isinstance(rel, str) and rel for rel in required):
        return False
    paths = [root / str(rel) for rel in required]
    if not all(path.is_file() for path in paths):
        return False
    artifact_root = paths[-1].parent
    try:
        for line in paths[-1].read_text().splitlines():
            expected, name = line.split(maxsplit=1)
            candidate = artifact_root / name.strip().lstrip("*")
            if candidate.parent != artifact_root or not candidate.is_file():
                return False
            if hashlib.sha256(candidate.read_bytes()).hexdigest() != expected:
                return False
    except (OSError, ValueError):
        return False
    return True


def hard_baseline_usable(session: dict[str, Any] | None, root: Path = ROOT) -> bool:
    if not isinstance(session, dict):
        return False
    interpretation = session.get("interpretation", {})
    quality = session.get("software_quality", {})
    usage = session.get("cumulative_token_usage", {})
    if not all(isinstance(value, dict) for value in (interpretation, quality, usage)):
        return False
    if interpretation.get("evaluation_validity") == "invalid-fixture":
        return False
    # Model quality is an observed outcome, not an eligibility gate for this
    # token-usage study. Reuse the first operationally valid provider sample for
    # the frozen protocol rather than rerunning until the model passes.
    return (
        interpretation.get("primary_objective_hard_baseline") is True
        and interpretation.get("usable_for_primary_objective_token_comparison") is True
        and interpretation.get("operationally_completed") is True
        and interpretation.get("agent_declared_task_completion_count") == quality.get("tasks_attempted")
        and isinstance(usage.get("total_provider_tokens"), int)
        and usage.get("total_provider_tokens", 0) > 0
        and compact_artifacts_intact(session, root)
    )


def baseline_reuse_state(session: dict[str, Any] | None, root: Path = ROOT) -> str:
    state = workflow.reviewed_session_reuse_state(session, root)
    return "reusable" if state != "reusable" and hard_baseline_usable(session, root) else state


def find_baseline_record(registry: dict[str, Any], seq: dict[str, Any], replicate_index: int) -> dict[str, Any] | None:
    normal = workflow.find_canonical_baseline_record(registry, seq, replicate_index)
    if normal is not None:
        return normal
    fingerprint = workflow.baseline_protocol_fingerprint(seq)
    matches = [
        session for session in registry.get("sessions", [])
        if session.get("schema_version") == 2
        and session.get("baseline_pool", {}).get("protocol_fingerprint") == fingerprint
        and session.get("replicate_index") == replicate_index
        and session.get("session_role") == "baseline"
        and session.get("task_sequence", {}).get("sequence_id") == seq["id"]
        and hard_baseline_usable(session, ROOT)
    ]
    if len(matches) > 1:
        raise RuntimeError(f"ambiguous hard baselines for {seq['id']} r{replicate_index}: {[item['session_id'] for item in matches]}")
    return matches[0] if matches else None


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
    matches: list[Path] = []
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
            matches.append(path)
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one frozen protocol for {sequence_id}/{profile_id}; found {[path.name for path in matches]}"
        )
    return matches[0]


def plan_workflow_jobs(
    sequence_ids: list[str],
    treatment_profiles: list[str],
    *,
    baseline_state: Callable[[str], str],
    profile_state: Callable[[str, str], str],
) -> list[tuple[str, str]]:
    """Plan one baseline lane per missing sequence or treatment lanes after a reusable token baseline exists."""
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
    log_path = logs / "lane.log"
    with log_path.open("w") as log:
        proc = subprocess.run(cmd, cwd=checkout, text=True, stdout=log, stderr=subprocess.STDOUT, env=env)
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
        "failure_evidence": failure_evidence,
    }


def publication_allowed(prepare_only: bool, lane_results: list[dict[str, Any]]) -> bool:
    return not prepare_only and all(result["exit_code"] == 0 for result in lane_results)


def artifact_merge_allowed(prepare_only: bool, lane_results: list[dict[str, Any]]) -> bool:
    """Preserve every completed compact session even when a sibling lane fails."""
    return not prepare_only and any(result.get("produced_session_ids") for result in lane_results)


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


def lane_session_records(checkout: Path, sequence_id: str, replicate_index: int, produced_session_ids: set[str] | None = None) -> list[dict[str, Any]]:
    doc = load_json(checkout / "data/workflow-sessions.json")
    out: list[dict[str, Any]] = []
    for session in doc.get("sessions", []):
        if produced_session_ids is not None and session.get("session_id") not in produced_session_ids:
            continue
        if session.get("replicate_index") != replicate_index:
            continue
        if session.get("task_sequence", {}).get("sequence_id") != sequence_id:
            continue
        prompt_delivery = session.get("task_sequence", {}).get("prompt_delivery", {})
        if prompt_delivery.get("mode") != "sequential-one-task-at-a-time":
            continue
        out.append(session)
    return out


def copy_artifacts_for_sessions(checkout: Path, sessions: list[dict[str, Any]]) -> list[str]:
    copied: list[str] = []
    lane_artifact_root = (checkout / WORKFLOW_ARTIFACT_ROOT).resolve()
    for session in sessions:
        artifacts = session.get("artifacts", {}) if isinstance(session.get("artifacts"), dict) else {}
        root = artifacts.get("root") or ""
        if not root:
            for key in ("run_record", "evidence_bundle", "final_diff", "manifest"):
                artifact_path = artifacts.get(key)
                if artifact_path:
                    root = str(Path(str(artifact_path)).parent)
                    break
        if not root or root == ".":
            continue
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
            shutil.copytree(src, dst)
            copied.append(str(rel))
    return copied


def merge_registry(sessions: list[dict[str, Any]]) -> None:
    path = ROOT / "data/workflow-sessions.json"
    doc = load_json(path)
    existing = {session.get("session_id") for session in doc.get("sessions", []) if session.get("session_id")}
    for session in sessions:
        if session["session_id"] in existing:
            raise FileExistsError(f"workflow session already exists; refusing overwrite: {session['session_id']}")
        existing.add(session["session_id"])
    doc["sessions"].extend(sessions)
    write_json(path, doc)


def merge_lanes(lane_results: list[dict[str, Any]], replicate_index: int) -> dict[str, Any]:
    registry_path = ROOT / "data/workflow-sessions.json"
    registry_before = registry_path.read_bytes()
    merged_sessions: list[dict[str, Any]] = []
    copied_artifacts: list[str] = []
    try:
        for result in lane_results:
            checkout = Path(result["checkout"])
            sequence_id = result["sequence_id"]
            produced_session_ids = set(result.get("produced_session_ids", []))
            sessions = lane_session_records(checkout, sequence_id, replicate_index, produced_session_ids)
            merged_sessions.extend(sessions)
            copied_artifacts.extend(copy_artifacts_for_sessions(checkout, sessions))
        if merged_sessions:
            merge_registry(merged_sessions)
    except Exception:
        registry_path.write_bytes(registry_before)
        for rel in copied_artifacts:
            path = ROOT / rel
            if path.is_dir():
                chmod_tree(path)
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
        raise
    return {
        "merged_session_count": len(merged_sessions),
        "copied_artifact_count": len(copied_artifacts),
        "merged_session_ids": [session["session_id"] for session in merged_sessions],
        "copied_artifacts": copied_artifacts,
    }


def write_hard_baseline_comparison(
    seq: dict[str, Any], baseline: dict[str, Any], treatment: dict[str, Any], profile_id: str, replicate_index: int
) -> Path:
    project_id = workflow.PROJECT_META[seq["fixture_id"]]["project_id"]
    fingerprint = workflow.baseline_protocol_fingerprint(seq)
    comparison_id = (
        f"baseline-{workflow.artifact_lane_label(project_id)}-{workflow.DATE.replace('-', '')}"
        f"-vs-{workflow.artifact_profile_label(profile_id)}-p-{fingerprint}-r{replicate_index}"
    )
    path = ROOT / WORKFLOW_ARTIFACT_ROOT / f"{comparison_id}.json"
    if path.exists():
        raise FileExistsError(f"workflow comparison already exists; refusing overwrite: {path}")
    b_tokens = baseline.get("cumulative_token_usage", {}).get("total_provider_tokens")
    t_tokens = treatment.get("cumulative_token_usage", {}).get("total_provider_tokens")
    b_passed = baseline.get("software_quality", {}).get("tasks_passed")
    t_passed = treatment.get("software_quality", {}).get("tasks_passed")
    if not all(isinstance(value, (int, float)) for value in (b_tokens, t_tokens, b_passed, t_passed)):
        raise ValueError("hard-lane comparison requires numeric provider tokens and verified task counts")
    delta = t_tokens - b_tokens
    correctness_improved = t_passed > b_passed
    token_efficiency_improved = t_tokens < b_tokens
    comparison = {
        "schema_version": 4,
        "comparison_id": comparison_id,
        "study_id": treatment.get("study_id"),
        "objective": treatment.get("objective"),
        "experiment_group_id": treatment.get("experiment_group_id"),
        "comparison_design": "token-objective-compatible-pair-v1",
        "baseline_protocol_fingerprint": fingerprint,
        "replicate_count": 1,
        "sequence_id": seq["id"],
        "baseline_session_id": baseline["session_id"],
        "treatment_session_id": treatment["session_id"],
        "baseline_total_provider_tokens": b_tokens,
        "treatment_total_provider_tokens": t_tokens,
        "delta_total_provider_tokens": delta,
        "delta_percent": workflow.percent_delta(delta, b_tokens),
        "baseline_agent_declared_tasks": baseline.get("software_quality", {}).get("tasks_agent_claimed_complete"),
        "treatment_agent_declared_tasks": treatment.get("software_quality", {}).get("tasks_agent_claimed_complete"),
        "baseline_verified_tasks": b_passed,
        "treatment_verified_tasks": t_passed,
        "correctness_improved": correctness_improved,
        "token_efficiency_improved": token_efficiency_improved,
        "primary_token_objective_improved": token_efficiency_improved,
        "interpretation": "Token-objective comparison. Provider-token change is the primary result. Verified-task outcomes are reported separately as diagnostic model behavior and do not gate or select the pair.",
    }
    write_json(path, comparison)
    return path


def publish_ready_comparisons(sequence_ids: list[str], profiles: list[str], replicate_index: int) -> list[str]:
    if not profiles:
        return []
    registry = load_json(ROOT / "data/workflow-sessions.json")
    published: list[str] = []
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
                if hard_baseline_usable(baseline, ROOT):
                    path = write_hard_baseline_comparison(seq, baseline, treatment, profile_id, replicate_index)
                else:
                    comparison = workflow.write_comparison_if_ready(
                        seq, "phase-2-sequential-workflow-v1", replicate_index, profile_id
                    )
                    if comparison is None:
                        raise RuntimeError(f"reviewed records did not produce comparison {comparison_id}")
                published.append(str(path.relative_to(ROOT)))
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

    jobs = (
        [(sequence_id, profile) for sequence_id in sequences for profile in (treatment_profiles or ["baseline-bare-codex"])]
        if args.prepare_only
        else plan_workflow_jobs(sequences, treatment_profiles, baseline_state=baseline_state, profile_state=profile_state)
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
                )
                for sequence_id, treatment_profile in jobs
            ]
            for fut in futures.as_completed(submitted):
                result = fut.result()
                lane_results.append(result)
                print(json.dumps(result, indent=2), flush=True)

    registry_path = ROOT / "data/workflow-sessions.json"
    registry_before = registry_path.read_bytes() if not args.prepare_only else b""
    lanes_passed = all(result["exit_code"] == 0 for result in lane_results)
    publish_allowed = publication_allowed(args.prepare_only, lane_results)
    merge_allowed = artifact_merge_allowed(args.prepare_only, lane_results)
    merge_summary = {
        "merged_session_count": 0,
        "copied_artifact_count": 0,
        "merged_session_ids": [],
        "copied_artifacts": [],
        "skipped": "prepare-only run" if args.prepare_only else "one or more lanes failed",
    } if not merge_allowed else merge_lanes(lane_results, args.replicate_index)
    published_comparisons = [] if not publish_allowed else publish_ready_comparisons(
        sequences, treatment_profiles, args.replicate_index
    )
    restore_protected_control_plane_files()
    refresh_generated_runbook()
    if not args.prepare_only and merge_summary.get("merged_session_count", 0):
        refresh_cumulative_usage_audit()
    validation = run_validation(run_root)
    if not args.prepare_only and not validation["passed"]:
        for rel in published_comparisons:
            path = ROOT / rel
            if path.is_dir():
                chmod_tree(path)
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
        merge_summary["validation_failed_artifacts_preserved"] = True
        published_comparisons = []
    execution_passed = lanes_passed and validation["passed"]
    awaiting_quality_review = False
    summary = {
        "plan": plan,
        "lane_results": sorted(lane_results, key=lambda item: item["sequence_id"]),
        "merge": merge_summary,
        "published_comparisons": published_comparisons,
        "validation": validation,
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
