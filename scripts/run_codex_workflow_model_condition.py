#!/usr/bin/env python3
"""Run the workflow evaluator under an explicitly registered non-default model condition."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
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
    condition = registered_condition(condition_id, model, reasoning_effort)
    override = {
        "model_condition_id": condition_id,
        "model": model,
        "reasoning_effort": reasoning_effort,
        "registry_status": condition.get("status"),
        "launcher": launcher_identity(),
    }
    runner.DEFAULT_WORKFLOW_MODEL_CONDITION_ID = condition_id
    runner.DEFAULT_WORKFLOW_MODEL = model
    runner.DEFAULT_WORKFLOW_REASONING_EFFORT = reasoning_effort

    original_baseline: Callable[..., dict[str, Any]] = runner.baseline_protocol_descriptor
    original_execution: Callable[..., dict[str, Any]] = runner.execution_condition_descriptor

    def baseline_descriptor(*args: Any, **kwargs: Any) -> dict[str, Any]:
        descriptor = original_baseline(*args, **kwargs)
        descriptor["model_condition_override"] = override
        return descriptor

    def execution_descriptor(*args: Any, **kwargs: Any) -> dict[str, Any]:
        descriptor = original_execution(*args, **kwargs)
        descriptor["model_condition_override"] = override
        return descriptor

    def validate_selected_condition() -> None:
        registered_condition(condition_id, model, reasoning_effort)

    runner.baseline_protocol_descriptor = baseline_descriptor
    runner.execution_condition_descriptor = execution_descriptor
    runner.validate_default_model_condition = validate_selected_condition


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
