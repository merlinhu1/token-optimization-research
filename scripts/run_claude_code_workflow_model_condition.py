#!/usr/bin/env python3
"""Run the workflow evaluator under the registered Claude Code condition."""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_codex_workflow_evaluation as runner  # type: ignore
import workflow_model_condition_runtime as condition_runtime  # type: ignore

LAUNCHER_PATH = "scripts/run_claude_code_workflow_model_condition.py"


def launcher_identity() -> dict[str, str]:
    path = ROOT / LAUNCHER_PATH
    runtime_path = ROOT / "scripts/workflow_model_condition_runtime.py"
    return {
        "path": LAUNCHER_PATH,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "condition_runtime_path": "scripts/workflow_model_condition_runtime.py",
        "condition_runtime_sha256": hashlib.sha256(runtime_path.read_bytes()).hexdigest(),
    }


def registered_condition(condition_id: str, model: str, reasoning_effort: str) -> dict[str, object]:
    selected, _ = condition_runtime.resolve_condition_pair(ROOT, condition_id)
    if (
        selected.get("runtime_id") != "claude-code"
        or selected.get("model") != model
        or selected.get("reasoning_effort") != reasoning_effort
    ):
        raise ValueError(f"expected one registered Claude Code condition for {condition_id}/{model}/{reasoning_effort}")
    return selected


def configure_model_condition(condition_id: str, model: str, reasoning_effort: str) -> None:
    selected, _ = condition_runtime.resolve_condition_pair(ROOT, condition_id)
    if selected.get("runtime_id") != "claude-code" or selected.get("provider") != "anthropic":
        raise ValueError("Claude Code launcher requires a claude-code Anthropic model condition")
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
    configure_model_condition(args.workflow_model_condition_id, args.workflow_model, args.workflow_reasoning_effort)
    return runner.main(remaining)


if __name__ == "__main__":
    raise SystemExit(main())
