#!/usr/bin/env python3
"""Run the workflow evaluator under an explicitly registered non-default model condition."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import workflow_model_condition_runtime as condition_runtime  # type: ignore
import run_codex_workflow_evaluation as runner  # type: ignore

LAUNCHER_PATH = "scripts/run_codex_workflow_model_condition.py"


def launcher_identity() -> dict[str, str]:
    path = ROOT / LAUNCHER_PATH
    return {"path": LAUNCHER_PATH, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def registered_condition(condition_id: str, model: str, reasoning_effort: str) -> dict[str, Any]:
    conditions = json.loads((ROOT / "data/evaluation-agent-runtimes.json").read_text()).get("model_conditions", [])
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
    return matches[0]


def configure_model_condition(condition_id: str, model: str, reasoning_effort: str) -> None:
    registered_condition(condition_id, model, reasoning_effort)
    condition_runtime.configure_runner(
        runner,
        selected_condition_id=condition_id,
        expected_model=model,
        expected_reasoning_effort=reasoning_effort,
        launcher_identity=launcher_identity(),
    )


def parse_args(argv: list[str] | None = None) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--workflow-model-condition-id", required=True)
    parser.add_argument("--workflow-model", required=True)
    parser.add_argument("--workflow-reasoning-effort", required=True)
    return parser.parse_known_args(argv)


def main(argv: list[str] | None = None) -> int:
    args, remaining = parse_args(argv)
    configure_model_condition(
        args.workflow_model_condition_id,
        args.workflow_model,
        args.workflow_reasoning_effort,
    )
    return runner.main(remaining)


if __name__ == "__main__":
    raise SystemExit(main())
