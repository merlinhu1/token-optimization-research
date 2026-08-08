#!/usr/bin/env python3
"""Publish provider-free integration qualification from an executed matrix receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--purpose", required=True)
    args = parser.parse_args()

    summary = json.loads(args.matrix_summary.read_text())
    plan = summary["plan"]
    runner_args = plan.get("runner_args", [])
    require("--prepare-only" in runner_args, "matrix did not run prepare-only")
    require("--no-provider" in runner_args, "matrix did not disable provider execution")
    require(not summary.get("merge", {}).get("merged_session_ids"), "provider sessions were merged")

    jobs = {(job["sequence_id"], job["profile_id"]): job for job in plan["jobs"]}
    lanes: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for lane_result in summary["lane_results"]:
        key = (lane_result["sequence_id"], lane_result["treatment_profile"])
        job = jobs[key]
        lane_log = Path(lane_result["log"])
        lane = json.loads(lane_log.read_text())
        protocol = ROOT / job["protocol"]
        checks = {
            "lane_exit_zero": lane_result["exit_code"] == 0,
            "prepared": lane.get("prepared") is True,
            "prepare_verification": lane.get("prepare_verification", {}).get("passed") is True,
            "host_integration": lane.get("host_integration", {}).get("passed") is True,
            "codex_preflight": lane.get("codex_preflight", {}).get("passed") is True,
            "warmup": lane.get("tool_warmup_exit_code") in (None, 0),
        }
        handshake = lane.get("mcp_handshake")
        if handshake is not None:
            checks["mcp_handshake"] = handshake.get("passed") is True
        if not all(checks.values()):
            failures.append({"sequence_id": key[0], "profile_id": key[1], "checks": checks})
        lane["protocol_path"] = job["protocol"]
        lane["protocol_sha256"] = sha256(protocol)
        lane["qualification_checks"] = checks
        preparation = lane["prepare_verification"]
        preparation["concealment_passed"] = preparation.get("concealment", {}).get("passed") is True
        preparation["composite_seed_delivery_passed"] = preparation.get("composite_seed_delivery", {}).get("passed") is True
        if handshake is not None:
            handshake["tool_count"] = len(handshake.get("tool_names", []))
        lanes.append(lane)

    profiles = sorted({lane["profile_id"] for lane in lanes})
    sequences = sorted({lane["sequence_id"] for lane in lanes})
    receipt = {
        "schema_version": 1,
        "date": datetime.now(timezone.utc).date().isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "purpose": args.purpose,
        "profiles": profiles,
        "sequences": sequences,
        "no_provider": True,
        "execution_mode": "prepare-only-no-provider",
        "provider_calls": 0,
        "summary": {
            "expected": len(plan["jobs"]),
            "passed": len(lanes) - len(failures),
            "failed": len(failures),
            "provider_backed_sessions_created": 0,
        },
        "failures": failures,
        "source_matrix_sha256": sha256(args.matrix_summary),
        "controller_provenance": {
            "fixture_runner_sha256": sha256(ROOT / "scripts/run_codex_fixture_evaluation.py"),
            "workflow_runner_sha256": sha256(ROOT / "scripts/run_codex_workflow_evaluation.py"),
            "matrix_runner_sha256": sha256(ROOT / "scripts/run_sequential_workflow_matrix.py"),
            "qualification_publisher_sha256": sha256(Path(__file__)),
        },
        "lanes": lanes,
    }
    require(not failures, f"qualification failed: {failures}")
    require(len(lanes) == len(plan["jobs"]), "lane/job count mismatch")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
