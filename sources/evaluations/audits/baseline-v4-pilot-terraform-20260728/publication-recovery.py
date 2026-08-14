#!/usr/bin/env python3
"""Provider-free recovery of the already-spent Baseline V4 Terraform publication."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(os.environ.get("RECOVERY_REPO", "/opt/data/repos/token-optimization-research"))
RUN_ROOT = Path(os.environ.get("RECOVERY_RUN_ROOT", "/opt/data/eval-workflow-lanes/workflow-matrix-20260728T140706909793Z-p3249263-r0"))
RECOVERY_ROOT = Path(os.environ.get("RECOVERY_OUTPUT_ROOT", str(RUN_ROOT / "publication-recovery-20260728")))
EXPECTED_SESSION = "baseline-terraform-20260728-p-5811b463c1e9-r0"
EXPECTED_RECEIPT = REPO / "sources/evaluations/audits/baseline-v4-pilot-attempt-terraform.json"
EXPECTED_TEST = REPO / "scripts/test_workflow_evaluation_contract.py"

sys.path.insert(0, str(REPO / "scripts"))
os.chdir(REPO)
import run_sequential_workflow_matrix as matrix  # type: ignore  # noqa: E402


def main() -> int:
    original = json.loads((RUN_ROOT / "matrix-summary.json").read_text())
    lane_results = original["lane_results"]
    if len(lane_results) != 1 or lane_results[0].get("exit_code") != 0:
        raise RuntimeError("recovery requires exactly one successful preserved lane")
    if lane_results[0].get("produced_session_ids") != [EXPECTED_SESSION]:
        raise RuntimeError("preserved lane session identity is not the paid Terraform r0 identity")
    if not EXPECTED_RECEIPT.is_file():
        raise RuntimeError("immutable paid-attempt receipt is missing")
    if not EXPECTED_TEST.is_file():
        raise RuntimeError("protected contract test is missing before recovery")
    if not matrix.artifact_merge_allowed(False, lane_results):
        raise RuntimeError("preserved lane is not eligible for strict artifact merge")

    RECOVERY_ROOT.mkdir(mode=0o700, exist_ok=False)
    registry_path = REPO / "data/workflow-sessions.json"
    registry_before = registry_path.read_bytes()
    authority_paths = (
        REPO / "docs/evaluations/operations/runbook.md",
        REPO / "sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json",
    )
    authority_snapshots = {path: path.read_bytes() for path in authority_paths}
    merge_summary = {
        "merged_session_count": 0,
        "copied_artifact_count": 0,
        "merged_session_ids": [],
        "copied_artifacts": [],
        "skipped": "provider-free recovery of preserved paid lane",
    }
    published_comparisons: list[str] = []
    lock_fd = matrix.acquire_production_lock()

    def rollback() -> None:
        matrix.rollback_matrix_publication(
            registry_path,
            registry_before,
            merge_summary,
            published_comparisons,
            authority_snapshots,
        )

    try:
        with matrix.publication_transaction_guard(rollback, enabled=True):
            matrix.merge_lanes(lane_results, 0, merge_summary)
            complete = matrix.matrix_outputs_complete(
                prepare_only=False,
                planned_job_count=1,
                lane_results=lane_results,
                merge_summary=merge_summary,
            )
            if not complete:
                raise RuntimeError("recovered authoritative outputs are incomplete")
            matrix.verify_protected_control_plane_files()
            if not EXPECTED_TEST.is_file():
                raise RuntimeError("protected contract test disappeared during recovery")
            matrix.refresh_generated_runbook()
            matrix.refresh_cumulative_usage_audit()
            validation = matrix.run_validation(
                RECOVERY_ROOT,
                "/opt/hermes/.venv/bin/python3",
            )
            if not validation["passed"]:
                raise RuntimeError("provider-free recovered publication failed repository validation")
            recovery = {
                "schema_version": 1,
                "provider_calls": 0,
                "provider_tokens": 0,
                "source_matrix_summary": str(RUN_ROOT / "matrix-summary.json"),
                "source_session_id": EXPECTED_SESSION,
                "source_lane_exit_code": lane_results[0]["exit_code"],
                "source_matrix_rolled_back_after_validation_failure": True,
                "recovery_reason": "post-merge tests encoded only the partial V4 pilot state; no provider rerun",
                "merge": merge_summary,
                "published_comparisons": published_comparisons,
                "validation": validation,
                "authoritative_outputs_complete": complete,
                "execution_passed": True,
                "accepted": True,
            }
            matrix.write_json(RECOVERY_ROOT / "recovery-summary.json", recovery)
    finally:
        os.close(lock_fd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
