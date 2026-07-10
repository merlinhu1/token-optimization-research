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
import concurrent.futures as futures
import datetime as dt
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
DEFAULT_LANE_ROOT = Path("/opt/data/eval-workflow-lanes")
WORKFLOW_ARTIFACT_ROOT = Path("sources/evaluations/workflow-sessions")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


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
    if "workflow-sessions" in parts:
        if "codex-homes" in names:
            ignored.add("codex-homes")
        # Existing workflow-session materialized repositories are bulky and are
        # not needed to start a fresh lane run. Fresh model-facing repos are
        # fetched under the lane checkout by the workflow runner.
        if current_path.name == "project" and "repo" in names:
            ignored.add("repo")
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
        "--exclude=/sources/evaluations/workflow-sessions/*/project/repo/",
        "--exclude=/sources/evaluations/workflow-sessions/*/codex-homes/",
        str(source.resolve()) + "/",
        str(destination.resolve()) + "/",
    ]
    subprocess.run(cmd, check=True)


def plan_workflow_jobs(
    sequence_ids: list[str],
    treatment_profiles: list[str],
    *,
    baseline_state: Callable[[str], str],
) -> list[tuple[str, str]]:
    """Plan one baseline gate per sequence, or one independent lane per treatment.

    A missing/non-reusable baseline deliberately collapses a multi-profile request
    to one pair invocation, preventing duplicate baseline provider spend. Once the
    baseline is reviewed reusable, all requested treatment profiles are separate
    jobs and may run concurrently in isolated checkouts.
    """
    if not treatment_profiles:
        raise ValueError("at least one treatment profile is required")
    if len(set(sequence_ids)) != len(sequence_ids):
        raise ValueError("duplicate sequence IDs are not allowed in one matrix")
    if len(set(treatment_profiles)) != len(treatment_profiles):
        raise ValueError("duplicate treatment profiles are not allowed in one matrix")
    jobs: list[tuple[str, str]] = []
    for sequence_id in sequence_ids:
        if baseline_state(sequence_id) == "reusable":
            jobs.extend((sequence_id, profile) for profile in treatment_profiles)
        else:
            jobs.append((sequence_id, treatment_profiles[0]))
    return jobs


def run_flow_lane(
    *,
    sequence_id: str,
    treatment_profile: str,
    lane_root: Path,
    replicate_index: int,
    runner_args: list[str],
    source_codex_home: Path | None,
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
    before_comparison_files = {
        path.name for path in (checkout / WORKFLOW_ARTIFACT_ROOT).glob("*.json")
    }

    cmd = ["bash", "scripts/run_sequential_workflow_pair.sh", sequence_id, "--treatment-profile", treatment_profile, *runner_args]
    if source_codex_home is not None:
        cmd.extend(["--source-codex-home", str(source_codex_home)])
    env = os.environ.copy()
    env["TMPDIR"] = str(tmp)
    env["REPLICATE_INDEX"] = str(replicate_index)
    env["SKIP_PAIR_VALIDATION"] = "1"
    env["WORKFLOW_LANE_DISABLE_AUTH_SYNC"] = "1"
    log_path = logs / "pair.log"
    with log_path.open("w") as log:
        proc = subprocess.run(cmd, cwd=checkout, text=True, stdout=log, stderr=subprocess.STDOUT, env=env)
    after_sessions = load_json(checkout / "data/workflow-sessions.json").get("sessions", [])
    produced_session_ids = sorted(
        str(session["session_id"])
        for session in after_sessions
        if session.get("session_id") and str(session["session_id"]) not in before_session_ids
    )
    produced_comparison_files = sorted(
        path.name
        for path in (checkout / WORKFLOW_ARTIFACT_ROOT).glob("*.json")
        if path.name not in before_comparison_files
    )
    return {
        "sequence_id": sequence_id,
        "treatment_profile": treatment_profile,
        "lane_id": lane_id,
        "lane_dir": str(lane_dir),
        "checkout": str(checkout),
        "log": str(log_path),
        "exit_code": proc.returncode,
        "produced_session_ids": produced_session_ids,
        "produced_comparison_files": produced_comparison_files,
    }


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
            if dst.exists():
                raise FileExistsError(f"workflow artifact destination already exists; refusing overwrite: {dst}")
            shutil.copytree(src, dst)
            copied.append(str(rel))
    return copied


def copy_comparisons(checkout: Path, sequence_id: str, replicate_index: int, produced_files: set[str] | None = None) -> list[str]:
    copied: list[str] = []
    src_root = checkout / WORKFLOW_ARTIFACT_ROOT
    if not src_root.exists():
        return copied
    for src in src_root.glob("*.json"):
        if produced_files is not None and src.name not in produced_files:
            continue
        try:
            data = load_json(src)
        except Exception:
            continue
        comparison_id = str(data.get("comparison_id", ""))
        if data.get("sequence_id") != sequence_id:
            continue
        if "sequential-workflow" not in comparison_id:
            continue
        if not comparison_id.endswith(f"-r{replicate_index}"):
            continue
        dst = ROOT / WORKFLOW_ARTIFACT_ROOT / src.name
        if dst.exists():
            raise FileExistsError(f"workflow comparison already exists; refusing overwrite: {dst}")
        shutil.copy2(src, dst)
        copied.append(str(WORKFLOW_ARTIFACT_ROOT / src.name))
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
    merged_sessions: list[dict[str, Any]] = []
    copied_artifacts: list[str] = []
    copied_comparisons: list[str] = []
    for result in lane_results:
        checkout = Path(result["checkout"])
        sequence_id = result["sequence_id"]
        produced_session_ids = set(result.get("produced_session_ids", []))
        produced_comparison_files = set(result.get("produced_comparison_files", []))
        sessions = lane_session_records(checkout, sequence_id, replicate_index, produced_session_ids)
        merged_sessions.extend(sessions)
        copied_artifacts.extend(copy_artifacts_for_sessions(checkout, sessions))
        copied_comparisons.extend(copy_comparisons(checkout, sequence_id, replicate_index, produced_comparison_files))
    if merged_sessions:
        merge_registry(merged_sessions)
    return {
        "merged_session_count": len(merged_sessions),
        "copied_artifact_count": len(copied_artifacts),
        "copied_comparison_count": len(copied_comparisons),
        "merged_session_ids": [session["session_id"] for session in merged_sessions],
        "copied_artifacts": copied_artifacts,
        "copied_comparisons": copied_comparisons,
    }


def run_validation(summary_dir: Path) -> dict[str, Any]:
    commands = [
        [sys.executable, "scripts/validate_repository.py"],
        ["git", "diff", "--check"],
        ["truthmark", "check", "--json"],
        ["truthmark", "index", "--json"],
    ]
    results: list[dict[str, Any]] = []
    for idx, cmd in enumerate(commands, start=1):
        out = summary_dir / f"validation-{idx}-{safe_name(cmd[0])}.txt"
        with out.open("w") as log:
            proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=log, stderr=subprocess.STDOUT)
        results.append({"command": cmd, "exit_code": proc.returncode, "output": str(out)})
    return {"passed": all(item["exit_code"] == 0 for item in results), "results": results}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sequences", nargs="*", help="workflow sequence IDs; defaults to all active sequences")
    parser.add_argument("--max-parallel", type=int, default=3, help="maximum flow lanes to run concurrently (default: 3)")
    parser.add_argument("--replicate-index", type=int, default=0)
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
    sequences = args.sequences or active_sequences()
    valid = set(active_sequences())
    unknown = [seq for seq in sequences if seq not in valid]
    if unknown:
        raise SystemExit(f"Unknown/non-active sequence IDs: {unknown}; active={sorted(valid)}")
    if args.max_parallel < 1:
        raise SystemExit("--max-parallel must be >= 1")

    treatment_profiles = args.treatment_profiles or ["retrieval-leanctx"]
    registry = load_json(ROOT / "data/workflow-sessions.json")

    def baseline_state(sequence_id: str) -> str:
        sequence = workflow.load_sequence(sequence_id)
        baseline = workflow.find_canonical_baseline_record(registry, sequence, args.replicate_index)
        return workflow.reviewed_session_reuse_state(baseline, ROOT)

    jobs = plan_workflow_jobs(sequences, treatment_profiles, baseline_state=baseline_state)
    timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    run_root = args.lane_root / f"workflow-matrix-{timestamp}-r{args.replicate_index}"
    runner_args: list[str] = []
    if args.timeout_per_task is not None:
        runner_args.extend(["--timeout-per-task", str(args.timeout_per_task)])
    for flag in ("prepare_only", "skip_container_preflight", "skip_codex_preflight", "skip_dependency_install"):
        if getattr(args, flag):
            runner_args.append("--" + flag.replace("_", "-"))

    plan = {
        "sequences": sequences,
        "treatment_profiles": treatment_profiles,
        "jobs": [{"sequence_id": sequence_id, "treatment_profile": profile} for sequence_id, profile in jobs],
        "max_parallel": args.max_parallel,
        "replicate_index": args.replicate_index,
        "lane_root": str(run_root),
        "runner_args": runner_args,
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0

    run_root.mkdir(parents=True, exist_ok=True)
    write_json(run_root / "plan.json", plan)
    lane_results: list[dict[str, Any]] = []
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
            )
            for sequence_id, treatment_profile in jobs
        ]
        for fut in futures.as_completed(submitted):
            result = fut.result()
            lane_results.append(result)
            print(json.dumps(result, indent=2), flush=True)

    merge_summary = {
        "merged_session_count": 0,
        "copied_artifact_count": 0,
        "copied_comparison_count": 0,
        "merged_session_ids": [],
        "copied_artifacts": [],
        "copied_comparisons": [],
        "skipped": "prepare-only run" if args.prepare_only else "",
    } if args.prepare_only else merge_lanes(lane_results, args.replicate_index)
    validation = run_validation(run_root)
    summary = {
        "plan": plan,
        "lane_results": sorted(lane_results, key=lambda item: item["sequence_id"]),
        "merge": merge_summary,
        "validation": validation,
        "accepted": all(result["exit_code"] == 0 for result in lane_results) and validation["passed"],
    }
    write_json(run_root / "matrix-summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)

    if summary["accepted"] and not args.keep_lanes:
        # Keep logs and summary, remove bulky checkouts.
        for result in lane_results:
            checkout = Path(result["checkout"])
            if checkout.exists():
                chmod_tree(checkout)
                shutil.rmtree(checkout)
    return 0 if summary["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
