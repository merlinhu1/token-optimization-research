#!/usr/bin/env python3
"""Freeze derived workflow contracts without rewriting qualification evidence.

Qualification JSON is executable evidence and may only be written by
``generate_workflow_qualification.py``. This command validates that evidence,
then refreshes one frozen execution protocol per selected sequence/profile.
"""
from __future__ import annotations

import argparse
import hashlib
import json

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import run_codex_workflow_evaluation as runner


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, indent=2) + "\n"
    if path.exists():
        if path.read_text() == rendered:
            return
        raise FileExistsError(f"refusing to overwrite immutable frozen protocol: {path}")
    path.write_text(rendered)


def protocol_id(seq: dict[str, Any], profile_id: str) -> str:
    execution = runner.execution_condition_descriptor(
        seq,
        profile_id,
        timeout_seconds_per_task=3600,
        docker_image=runner.DEFAULT_DOCKER_IMAGE,
    )
    identity = {
        "baseline_protocol": runner.baseline_protocol_descriptor(seq),
        "selected_execution": execution,
    }
    return "-".join(
        (
            runner.safe_profile_key(seq["id"]),
            runner.safe_profile_key(profile_id),
            runner._json_hash(identity)[:12],
        )
    )


def frozen_protocol(
    seq: dict[str, Any],
    profile_id: str,
    qualification_path: Path,
) -> dict[str, Any]:
    pid = protocol_id(seq, profile_id)
    protocol_path = ROOT / "sources/evaluations/protocols" / f"{pid}.json"
    descriptor = runner.baseline_protocol_descriptor(seq)
    execution = runner.execution_condition_descriptor(
        seq,
        profile_id,
        timeout_seconds_per_task=3600,
        docker_image=runner.DEFAULT_DOCKER_IMAGE,
    )
    command = (
        "python3 scripts/run_codex_workflow_evaluation.py "
        f"--sequence-id {seq['id']} --profile-id {profile_id} "
        f"--timeout-per-task 3600 --protocol {protocol_path.relative_to(ROOT)} "
        f"--docker-image {runner.DEFAULT_DOCKER_IMAGE}"
    )
    agent = {
        "profile_id": profile_id,
        "provider": "openai",
        "model": runner.DEFAULT_WORKFLOW_MODEL,
        "model_condition_id": runner.DEFAULT_WORKFLOW_MODEL_CONDITION_ID,
        "reasoning_effort": runner.DEFAULT_WORKFLOW_REASONING_EFFORT,
        "command": command,
    }
    baseline = {
        "profile_id": "baseline-bare-codex",
        "provider": "openai",
        "model": runner.DEFAULT_WORKFLOW_MODEL,
        "model_condition_id": runner.DEFAULT_WORKFLOW_MODEL_CONDITION_ID,
        "reasoning_effort": runner.DEFAULT_WORKFLOW_REASONING_EFFORT,
        "command": command if profile_id == "baseline-bare-codex" else "",
    }
    treatment = {} if profile_id == "baseline-bare-codex" else agent
    return {
        "protocol_schema_version": 3,
        "protocol_id": pid,
        "status": "frozen-ready-not-run",
        "outcome": f"Frozen {profile_id} protocol for {seq['id']}; no provider/model run has occurred.",
        "frozen_at": seq["protocol_freeze_date"],
        "hypothesis": f"{profile_id} produces reproducible provider-reported token and software-quality evidence for {seq['id']}",
        "evidence_stage_target": "reproduction",
        "task_fixture": {
            "fixture_id": seq["fixture_id"],
            "sequence_id": seq["id"],
            "repository": seq["initial_snapshot"]["upstream"],
            "snapshot": seq["initial_snapshot"]["commit"],
            "qualification_path": str(qualification_path.relative_to(ROOT)),
            "qualification_sha256": digest(qualification_path),
            "timeout_seconds_per_task": 3600,
        },
        "baseline": baseline,
        "treatment": treatment,
        "token_accounting_boundary": {
            "fields": [
                "fresh_input_tokens",
                "cached_input_tokens",
                "cache_write_tokens",
                "output_tokens",
                "reasoning_tokens",
                "total_provider_tokens",
            ]
        },
        "baseline_pool": {
            "protocol_version": runner.BASELINE_POOL_PROTOCOL_VERSION,
            "protocol_fingerprint": runner.baseline_protocol_fingerprint(seq),
            "descriptor": descriptor,
        },
        "selected_execution": {
            "descriptor_sha256": runner._json_hash(execution),
            "descriptor": execution,
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sequence-id", action="append", dest="sequence_ids", help="active sequence; repeat to select several (default: all active)")
    parser.add_argument("--profile-id", default="baseline-bare-codex", choices=sorted(runner.PROFILE_META))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    runner.validate_default_model_condition()
    runner.assert_profile_runnable(args.profile_id)
    sequence_ids = args.sequence_ids or runner.active_sequence_ids()
    for sequence_id in sequence_ids:
        seq = runner.load_sequence(sequence_id)
        if seq.get("status") != "active":
            raise ValueError(f"cannot freeze a non-active sequence: {sequence_id}")
        current, _ = runner.qualification_is_current(seq)
        if not current:
            raise ValueError(
                f"qualification evidence is stale for {sequence_id}; run and review generate_workflow_qualification.py explicitly"
            )
        qualification_path = ROOT / seq["qualification_path"]
        protocol = frozen_protocol(seq, args.profile_id, qualification_path)
        path = ROOT / "sources/evaluations/protocols" / f"{protocol['protocol_id']}.json"
        write_json(path, protocol)
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
