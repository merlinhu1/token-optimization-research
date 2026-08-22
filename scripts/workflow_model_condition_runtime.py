"""Bind workflow protocols to a selected model condition and a comparable baseline.

The selected condition may use a replacement runtime such as OpenCode. In that
case the baseline remains the uniquely matching Codex condition with the same
provider, model, and reasoning effort; runtime is the only model-facing axis
that changes.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from types import ModuleType
from typing import Any


def model_conditions(root: Path) -> list[dict[str, Any]]:
    data = json.loads((root / "data/evaluation-agent-runtimes.json").read_text())
    conditions = data.get("model_conditions")
    if not isinstance(conditions, list):
        raise ValueError("evaluation runtime registry is missing model_conditions")
    return [item for item in conditions if isinstance(item, dict)]


def published_baseline_descriptor(
    root: Path,
    sequence_id: str,
    model_condition_id: str,
    replicate_index: int = 0,
) -> dict[str, Any]:
    registry = json.loads((root / "data/workflow-sessions.json").read_text())
    candidates = [
        session
        for session in registry.get("sessions", [])
        if session.get("profile", {}).get("profile_id") == "baseline-bare-codex"
        and session.get("task_sequence", {}).get("sequence_id") == sequence_id
        and session.get("agent", {}).get("model_condition_id") == model_condition_id
        and session.get("replicate_index") == replicate_index
        and session.get("interpretation", {}).get("accepted_for_execution") is True
    ]
    if not candidates:
        raise ValueError(
            f"no accepted published baseline for {sequence_id}/{model_condition_id}/r{replicate_index}"
        )
    session = max(
        candidates,
        key=lambda item: (str(item.get("date", "")), str(item.get("session_id", ""))),
    )
    frozen = session.get("frozen_protocol", {})
    path = root / str(frozen.get("path", ""))
    if not path.is_file():
        raise ValueError(f"published baseline protocol is missing: {path}")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != frozen.get("sha256"):
        raise ValueError(f"published baseline protocol hash drifted: {path}")
    protocol = json.loads(raw)
    pool = protocol.get("baseline_pool", {})
    if pool.get("protocol_fingerprint") != session.get("baseline_pool", {}).get("protocol_fingerprint"):
        raise ValueError("published baseline protocol/session fingerprint mismatch")
    descriptor = pool.get("descriptor")
    if not isinstance(descriptor, dict):
        raise ValueError("published baseline protocol is missing its descriptor")
    agent = descriptor.get("agent_condition", descriptor.get("agent", {}))
    if agent.get("model_condition_id") != model_condition_id:
        raise ValueError("published baseline descriptor uses the wrong model condition")
    return copy.deepcopy(descriptor)


def resolve_condition_pair(root: Path, selected_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    conditions = model_conditions(root)
    selected_matches = [item for item in conditions if item.get("id") == selected_id]
    if len(selected_matches) != 1:
        raise ValueError(f"model condition must resolve exactly once: {selected_id}")
    selected = selected_matches[0]
    if selected.get("runtime_id") == "codex-cli":
        return selected, selected
    # OpenCode is paired with a published Codex control; Claude Code starts its
    # own bare-runtime control pool and must never borrow an incompatible one.
    if selected.get("runtime_id") == "claude-code":
        if selected.get("provider") not in {"anthropic"}:
            raise ValueError("Claude Code conditions must use Anthropic-compatible provider")
        return selected, selected
    if selected.get("provider") != "openai":
        raise ValueError("replacement workflow conditions must use a supported provider")
    baseline_matches = [
        item
        for item in conditions
        if item.get("runtime_id") == "codex-cli"
        and item.get("provider") == selected.get("provider")
        and item.get("model") == selected.get("model")
        and item.get("reasoning_effort") == selected.get("reasoning_effort")
    ]
    if len(baseline_matches) != 1:
        raise ValueError(
            f"replacement runtime condition {selected_id} requires exactly one matching Codex baseline condition"
        )
    return selected, baseline_matches[0]


def _version_key(runtime_id: str) -> str:
    return "codex_version_condition" if runtime_id == "codex-cli" else "runtime_version_condition"


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
            _version_key(str(condition["runtime_id"])): "captured-at-run-and-bound-to-record",
        }
    )


def condition_override(condition: dict[str, Any], launcher_identity: str | dict[str, str]) -> dict[str, Any]:
    return {
        "model_condition_id": condition["id"],
        "runtime_id": condition["runtime_id"],
        "provider": condition["provider"],
        "model": condition["model"],
        "reasoning_effort": condition["reasoning_effort"],
        "registry_status": condition.get("status"),
        "launcher": launcher_identity,
    }


def configure_runner(
    runner: ModuleType,
    *,
    selected_condition_id: str,
    expected_model: str,
    expected_reasoning_effort: str,
    launcher_identity: str | dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    selected, baseline = resolve_condition_pair(Path(runner.ROOT), selected_condition_id)
    launcher_path = (
        launcher_identity["path"]
        if isinstance(launcher_identity, dict)
        else launcher_identity
    )
    if selected.get("model") != expected_model:
        raise ValueError("requested model does not match the registered model condition")
    if selected.get("reasoning_effort") != expected_reasoning_effort:
        raise ValueError("requested reasoning effort does not match the registered model condition")

    original_validate = runner.validate_default_model_condition
    original_baseline_descriptor = runner.baseline_protocol_descriptor
    original_execution_descriptor = runner.execution_condition_descriptor
    original_current_baseline_protocol = runner.current_lifecycle_protocol
    original_baseline_treatment_gate = runner.lifecycle_treatment_gate
    original_require_treatment_gate = runner.require_lifecycle_treatment_gate

    setattr(runner, "DEFAULT_WORKFLOW_MODEL_CONDITION_ID", str(selected["id"]))
    setattr(runner, "DEFAULT_WORKFLOW_MODEL", str(selected["model"]))
    setattr(runner, "DEFAULT_WORKFLOW_REASONING_EFFORT", str(selected["reasoning_effort"]))

    def validate_condition() -> None:
        matches = [
            item
            for item in model_conditions(Path(runner.ROOT))
            if item.get("id") == selected["id"]
            and item.get("runtime_id") == selected["runtime_id"]
            and item.get("provider") == selected["provider"]
            and item.get("model") == selected["model"]
            and item.get("reasoning_effort") == selected["reasoning_effort"]
        ]
        if len(matches) != 1:
            raise ValueError(f"registered model condition drifted: {selected['id']}")

    def baseline_descriptor(sequence: dict[str, Any], root: Path = runner.ROOT) -> dict[str, Any]:
        if selected["runtime_id"] == "opencode-cli":
            return published_baseline_descriptor(
                Path(root), str(sequence["id"]), str(baseline["id"])
            )
        descriptor = original_baseline_descriptor(sequence, root)
        if selected["runtime_id"] == "claude-code":
            profile = runner.profile_registry_entry("baseline-claude-code-no-mcp", Path(root))
            descriptor["baseline_profile"] = {
                "profile_id": "baseline-claude-code-no-mcp",
                "profile_type": profile["profile_type"],
                "enabled_surfaces": profile.get("enabled_surfaces", []),
                "disabled_overlaps": profile.get("disabled_overlaps", []),
            }
            descriptor["model_facing_prompts"] = runner.model_facing_prompt_descriptor(
                sequence, "baseline-claude-code-no-mcp", Path(root)
            )
            descriptor["runtime_inputs"]["claude_runtime_condition"] = selected["id"]
            descriptor["runtime_inputs"].pop("codex_runtime_condition", None)
        agent_key = "agent_condition" if "agent_condition" in descriptor else "agent"
        apply_agent_condition(descriptor[agent_key], baseline)
        descriptor["runtime_inputs"]["model_condition_id"] = baseline["id"]
        descriptor["runtime_inputs"]["model_condition_launcher"] = launcher_path
        descriptor["model_condition_override"] = condition_override(baseline, launcher_identity)
        return descriptor

    def execution_descriptor(*args: Any, **kwargs: Any) -> dict[str, Any]:
        descriptor = original_execution_descriptor(*args, **kwargs)
        apply_agent_condition(descriptor["agent_condition"], selected)
        runtime = descriptor["runtime"]
        runtime["agent_runtime_id"] = selected["runtime_id"]
        runtime["model_condition"] = {
            "id": selected["id"],
            "provider": selected["provider"],
            "model": selected["model"],
            "reasoning_effort": selected["reasoning_effort"],
            "launcher": launcher_path,
        }
        descriptor["model_condition_override"] = condition_override(selected, launcher_identity)
        return descriptor

    def require_treatment_gate(*args: Any, **kwargs: Any) -> None:
        current_baseline = runner.baseline_protocol_descriptor
        current_execution = runner.execution_condition_descriptor
        setattr(runner, "baseline_protocol_descriptor", original_baseline_descriptor)
        setattr(runner, "execution_condition_descriptor", original_execution_descriptor)
        try:
            original_require_treatment_gate(*args, **kwargs)
        finally:
            setattr(runner, "baseline_protocol_descriptor", current_baseline)
            setattr(runner, "execution_condition_descriptor", current_execution)

    def baseline_treatment_gate(*args: Any, **kwargs: Any) -> tuple[bool, str]:
        current_baseline = runner.baseline_protocol_descriptor
        current_execution = runner.execution_condition_descriptor
        setattr(runner, "baseline_protocol_descriptor", original_baseline_descriptor)
        setattr(runner, "execution_condition_descriptor", original_execution_descriptor)
        try:
            return original_baseline_treatment_gate(*args, **kwargs)
        finally:
            setattr(runner, "baseline_protocol_descriptor", current_baseline)
            setattr(runner, "execution_condition_descriptor", current_execution)

    def current_baseline_protocol(*args: Any, **kwargs: Any) -> tuple[str, dict[str, Any]]:
        current_baseline = runner.baseline_protocol_descriptor
        current_execution = runner.execution_condition_descriptor
        setattr(runner, "baseline_protocol_descriptor", original_baseline_descriptor)
        setattr(runner, "execution_condition_descriptor", original_execution_descriptor)
        try:
            return original_current_baseline_protocol(*args, **kwargs)
        finally:
            setattr(runner, "baseline_protocol_descriptor", current_baseline)
            setattr(runner, "execution_condition_descriptor", current_execution)

    setattr(runner, "validate_default_model_condition", validate_condition)
    setattr(runner, "baseline_protocol_descriptor", baseline_descriptor)
    setattr(runner, "execution_condition_descriptor", execution_descriptor)
    setattr(runner, "current_lifecycle_protocol", current_baseline_protocol)
    setattr(runner, "lifecycle_treatment_gate", baseline_treatment_gate)
    setattr(runner, "require_lifecycle_treatment_gate", require_treatment_gate)
    # Keep a handle only for diagnostic callers that need to prove this is a
    # deliberate replacement; it is never called during normal execution.
    setattr(runner, "_unconfigured_validate_default_model_condition", original_validate)
    return selected, baseline
