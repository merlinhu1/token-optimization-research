#!/usr/bin/env python3
"""Run the independent OpenCode/OpenRouter Lifecycle V1 control condition.

This launcher deliberately does not share the Codex/OpenAI replacement-runtime
condition runtime. Its baseline is OpenCode through OpenRouter, so it cannot
borrow a Codex receipt or participate in a cross-provider token comparison.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_PATH = "scripts/run_opencode_openrouter_workflow_model_condition.py"
CONDITION_ID = "opencode-openrouter-gpt-5-6-sol-medium"
PROFILE_ID = "baseline-opencode-openrouter-no-mcp"
MODEL = "gpt-5.6-sol"
REASONING_EFFORT = "medium"


def launcher_identity() -> dict[str, str]:
    path = ROOT / LAUNCHER_PATH
    return {"path": LAUNCHER_PATH, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def registered_condition(root: Path = ROOT) -> dict[str, Any]:
    conditions = json.loads((root / "data/evaluation-agent-runtimes.json").read_text()).get("model_conditions", [])
    matches = [
        item for item in conditions
        if isinstance(item, dict)
        and item.get("id") == CONDITION_ID
        and item.get("status") == "configured-provider-free"
        and item.get("runtime_id") == "opencode-cli"
        and item.get("provider") == "openrouter"
        and item.get("model") == MODEL
        and item.get("reasoning_effort") == REASONING_EFFORT
    ]
    if len(matches) != 1:
        raise ValueError("OpenCode/OpenRouter Lifecycle V1 condition must resolve exactly once")
    return matches[0]


def condition_override(condition: dict[str, Any]) -> dict[str, Any]:
    return {
        "model_condition_id": condition["id"],
        "runtime_id": condition["runtime_id"],
        "provider": condition["provider"],
        "model": condition["model"],
        "reasoning_effort": condition["reasoning_effort"],
        "registry_status": condition["status"],
        "launcher": launcher_identity(),
    }


def apply_agent_condition(agent: dict[str, Any], condition: dict[str, Any]) -> None:
    agent.pop("codex_version_condition", None)
    agent.pop("runtime_version_condition", None)
    agent.update(
        {
            "runtime_id": condition["runtime_id"],
            "provider": condition["provider"],
            "model": condition["model"],
            "model_condition_id": condition["id"],
            "reasoning_effort": condition["reasoning_effort"],
            "runtime_version_condition": "captured-at-run-and-bound-to-record",
        }
    )


def configure_runner(runner: ModuleType) -> dict[str, Any]:
    """Bind a runner module to this provider-free OpenRouter control condition."""
    condition = registered_condition(Path(runner.ROOT))
    original_validate = runner.validate_default_model_condition
    original_baseline_descriptor = runner.baseline_protocol_descriptor
    original_execution_descriptor = runner.execution_condition_descriptor

    setattr(runner, "DEFAULT_WORKFLOW_MODEL_CONDITION_ID", CONDITION_ID)
    setattr(runner, "DEFAULT_WORKFLOW_MODEL", MODEL)
    setattr(runner, "DEFAULT_WORKFLOW_REASONING_EFFORT", REASONING_EFFORT)

    def validate_condition() -> None:
        actual = registered_condition(Path(runner.ROOT))
        if actual != condition:
            raise ValueError("OpenCode/OpenRouter Lifecycle V1 condition drifted")

    def baseline_descriptor(sequence: dict[str, Any], root: Path = runner.ROOT) -> dict[str, Any]:
        descriptor = original_baseline_descriptor(sequence, root)
        profile = runner.profile_registry_entry(PROFILE_ID, Path(root))
        descriptor["baseline_profile"] = {
            "profile_id": PROFILE_ID,
            "profile_type": profile["profile_type"],
            "enabled_surfaces": profile.get("enabled_surfaces", []),
            "disabled_overlaps": profile.get("disabled_overlaps", []),
        }
        descriptor["model_facing_prompts"] = runner.model_facing_prompt_descriptor(
            sequence, PROFILE_ID, Path(root)
        )
        apply_agent_condition(descriptor["agent"], condition)
        descriptor["runtime_inputs"]["opencode_runtime_condition"] = CONDITION_ID
        descriptor["runtime_inputs"]["model_condition_id"] = CONDITION_ID
        descriptor["runtime_inputs"]["model_condition_launcher"] = LAUNCHER_PATH
        descriptor["runtime_inputs"].pop("codex_runtime_condition", None)
        descriptor["model_condition_override"] = condition_override(condition)
        return descriptor

    def execution_descriptor(*args: Any, **kwargs: Any) -> dict[str, Any]:
        descriptor = original_execution_descriptor(*args, **kwargs)
        apply_agent_condition(descriptor["agent_condition"], condition)
        runtime = descriptor["runtime"]
        runtime["agent_runtime_id"] = condition["runtime_id"]
        runtime["model_condition"] = {
            "id": CONDITION_ID,
            "provider": condition["provider"],
            "model": MODEL,
            "reasoning_effort": REASONING_EFFORT,
            "launcher": LAUNCHER_PATH,
        }
        descriptor["baseline_pool_reference"]["protocol_fingerprint"] = runner.baseline_protocol_fingerprint(
            args[0] if args else kwargs["seq"], kwargs.get("root", runner.ROOT)
        )
        descriptor["model_condition_override"] = condition_override(condition)
        return descriptor

    setattr(runner, "validate_default_model_condition", validate_condition)
    setattr(runner, "baseline_protocol_descriptor", baseline_descriptor)
    setattr(runner, "execution_condition_descriptor", execution_descriptor)
    setattr(runner, "_unconfigured_validate_default_model_condition", original_validate)
    return condition


def parse_args(argv: list[str] | None = None) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--workflow-model-condition-id", required=True)
    parser.add_argument("--workflow-model", required=True)
    parser.add_argument("--workflow-reasoning-effort", required=True)
    return parser.parse_known_args(argv)


def main(argv: list[str] | None = None) -> int:
    args, remaining = parse_args(argv)
    if (
        args.workflow_model_condition_id != CONDITION_ID
        or args.workflow_model != MODEL
        or args.workflow_reasoning_effort != REASONING_EFFORT
    ):
        raise ValueError("OpenCode/OpenRouter launcher requires the exact registered Sol/medium condition")
    sys.path.insert(0, str(ROOT / "scripts"))
    import run_codex_workflow_evaluation as runner  # type: ignore

    configure_runner(runner)
    return runner.main(remaining)


if __name__ == "__main__":
    raise SystemExit(main())
