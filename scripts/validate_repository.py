#!/usr/bin/env python3
"""Lightweight structural validation for the token optimization research repository."""
from __future__ import annotations

import copy
import functools
import gzip
import importlib
import json
import re
import subprocess
import hashlib
from pathlib import Path, PurePosixPath
from typing import Any
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

WORKFLOW_SESSION_SCHEMA_REL = "schemas/workflow-session-record.schema.json"
WORKFLOW_SESSION_SCHEMA_UNAVAILABLE = (
    f"jsonschema is required to gate registry records on {WORKFLOW_SESSION_SCHEMA_REL}; "
    "install it or set WORKFLOW_VALIDATION_PYTHON to a prepared controller interpreter"
)

PROVIDER_USAGE_FIELDS = (
    "fresh_input_tokens",
    "cached_input_tokens",
    "cache_write_tokens",
    "output_tokens",
    "reasoning_tokens",
    "total_provider_tokens",
)

# Compact-v1 final diffs are task deltas: the 316 retained bundles have a 5 KB median and a
# 0.26 MB 99th percentile. The three sessions below predate this gate and are frozen evidence,
# so they are grandfathered rather than rewritten; the cap applies to every future capture.
MAX_COMPACT_DIFF_BYTES = 1024 * 1024
OVERSIZED_COMPACT_DIFF_SESSION_IDS = {
    "token-savior-beets-20260805-p-d8cfc5066f76-r0",
    "token-savior-fastify-20260805-p-72ac148f730b-r0",
    "sdl-mcp-codex-v1-fastify-20260807-p-72ac148f730b-r1",
}

def provider_usage_valid(usage: object, *, allow_legacy_null_cache_write: bool = False) -> bool:
    if (
        not isinstance(usage, dict)
        or usage.get("measurement_source") not in {
            "codex-jsonl-usage-events",
            "opencode-jsonl-step-finish-usage",
            "claude-code-stream-json-assistant-usage",
            "claude-code-stream-json-result-usage",
        }
        or not set(PROVIDER_USAGE_FIELDS).issubset(usage)
    ):
        return False
    for key in ("fresh_input_tokens", "cached_input_tokens", "output_tokens", "reasoning_tokens"):
        value = usage.get(key)
        if type(value) is not int or value < 0:
            return False
    cache_write = usage.get("cache_write_tokens")
    if cache_write is None:
        if not allow_legacy_null_cache_write:
            return False
        cache_write_value = 0
    elif type(cache_write) is int and cache_write >= 0:
        cache_write_value = cache_write
    else:
        return False
    # cache_write_tokens is an explicit audit subset of fresh_input_tokens,
    # not an additional provider-token dimension for total arithmetic.
    if cache_write_value > usage["fresh_input_tokens"]:
        return False
    measurement_source = usage["measurement_source"]
    if measurement_source in {
        "claude-code-stream-json-assistant-usage",
        "claude-code-stream-json-result-usage",
    }:
        details = usage.get("provider_usage_details")
        if not isinstance(details, dict):
            return False
        if details.get("fresh_input_formula") != "input_tokens + cache_creation_input_tokens":
            return False
        expected_mode = (
            "sum-unique-assistant-message-usage"
            if measurement_source == "claude-code-stream-json-assistant-usage"
            else "result-usage-fallback-no-assistant-usage"
        )
        if details.get("accounting_mode") != expected_mode:
            return False
        if details.get("result_usage_counted") is not (measurement_source == "claude-code-stream-json-result-usage"):
            return False
        components = details.get("canonical_components")
        if not isinstance(components, dict):
            return False
        for key in (
            "input_tokens",
            "cache_creation_input_tokens",
            "cache_read_input_tokens",
            "output_tokens",
            "reasoning_tokens",
        ):
            value = components.get(key)
            if type(value) is not int or value < 0:
                return False
        if components["input_tokens"] + components["cache_creation_input_tokens"] != usage["fresh_input_tokens"]:
            return False
        if components["cache_read_input_tokens"] != usage["cached_input_tokens"]:
            return False
        if components["output_tokens"] != usage["output_tokens"]:
            return False
        if components["reasoning_tokens"] != usage["reasoning_tokens"]:
            return False
    total = usage.get("total_provider_tokens")
    expected_total = (
        usage["fresh_input_tokens"]
        + usage["cached_input_tokens"]
        + usage["output_tokens"]
    )
    if type(total) is not int or total < 0:
        return False
    if total != expected_total:
        return False
    if usage["reasoning_tokens"] > usage["output_tokens"]:
        return False
    if measurement_source == "claude-code-stream-json-assistant-usage" and total == 0:
        return False
    return True


def model_condition_override_matches(actual: object, expected: object) -> bool:
    if actual == expected:
        return True
    if not isinstance(actual, dict) or not isinstance(expected, dict):
        return False
    actual_launcher = actual.get("launcher")
    expected_launcher = expected.get("launcher")
    if actual.get("runtime_id") != "opencode-cli" or not isinstance(actual_launcher, dict) or not isinstance(expected_launcher, dict):
        return False
    if actual_launcher.get("path") != expected_launcher.get("path"):
        return False
    actual_copy = copy.deepcopy(actual)
    expected_copy = copy.deepcopy(expected)
    actual_copy["launcher"].pop("condition_runtime_sha256", None)
    expected_copy["launcher"].pop("condition_runtime_sha256", None)
    return actual_copy == expected_copy


def compact_run_record_matches_session(
    session: dict,
    run_record: object,
    *,
    current_contract: bool,
    require_accepted: bool,
) -> bool:
    if not isinstance(run_record, dict):
        return False
    usage = session.get("cumulative_token_usage")
    run_usage = run_record.get("token_usage")
    if not isinstance(usage, dict) or not isinstance(run_usage, dict):
        return False
    usage_keys = PROVIDER_USAGE_FIELDS
    if any(run_usage.get(key) != usage.get(key) for key in usage_keys):
        return False
    if (
        "provider_usage_details" in usage
        or "provider_usage_details" in run_usage
    ) and run_usage.get("provider_usage_details") != usage.get("provider_usage_details"):
        return False
    run_usage_for_validation = dict(run_usage)
    run_usage_for_validation["measurement_source"] = run_usage.get(
        "measurement_source",
        usage.get("measurement_source"),
    )
    interpretation = session.get("interpretation", {})
    accounting_invalid = (
        isinstance(interpretation, dict)
        and interpretation.get("evaluation_validity") == "invalid-accounting"
    )
    usage_is_decision_bearing = (
        not accounting_invalid
        and (
            current_contract
            or require_accepted
            or (isinstance(interpretation, dict) and interpretation.get("accepted_for_objective") is True)
        )
    )
    if usage_is_decision_bearing and (
        not provider_usage_valid(
            usage,
            allow_legacy_null_cache_write=not current_contract,
        )
        or not provider_usage_valid(
            run_usage_for_validation,
            allow_legacy_null_cache_write=not current_contract,
        )
    ):
        return False
    if current_contract and run_usage.get("measurement_source") != usage.get("measurement_source"):
        return False
    expected_accepted = interpretation.get("accepted_for_execution") if isinstance(interpretation, dict) else None
    integrity = session.get("execution_integrity", {})
    expected_verifier_integrity = (
        integrity.get("verifier_integrity_passed") if isinstance(integrity, dict) else None
    )
    expected = {
        "session_id": session.get("session_id"),
        "replicate_index": session.get("replicate_index"),
        "workflow_sequence_id": session.get("task_sequence", {}).get("sequence_id"),
        "profile_id": session.get("profile", {}).get("profile_id"),
        "frozen_protocol": session.get("frozen_protocol"),
        "baseline_pool": session.get("baseline_pool"),
        "selected_execution": session.get("selected_execution"),
        "docker_image_identity": session.get("docker_image_identity"),
        "tool_adapter_identity": session.get("tool_adapter_identity"),
        "per_task_results": session.get("per_task_results"),
        "verifier_integrity_passed": expected_verifier_integrity,
    }
    if any(run_record.get(key) != value for key, value in expected.items()):
        return False
    if run_record.get("accepted") != expected_accepted:
        return False
    if require_accepted and run_record.get("accepted") is not True:
        return False
    if current_contract:
        expected_agent = session.get("agent")
        run_agent = run_record.get("agent_condition")
        agent_keys = ("runtime_id", "provider", "model", "model_condition_id", "reasoning_effort")
        if (
            not isinstance(expected_agent, dict)
            or not isinstance(run_agent, dict)
            or any(run_agent.get(key) != expected_agent.get(key) for key in agent_keys)
        ):
            return False
    return True


def current_provider_usage_contract(session: dict) -> bool:
    leakage = session.get("task_sequence", {}).get("leakage_controls", {})
    if isinstance(leakage, dict) and "controller_verifier_scripts_and_canonical_copies_model_visible" in leakage:
        return True
    frozen = session.get("frozen_protocol", {})
    path_value = frozen.get("path") if isinstance(frozen, dict) else None
    if not isinstance(path_value, str) or not path_value:
        return False
    path = Path(path_value)
    if path.is_absolute() or ".." in path.parts:
        return False
    try:
        protocol = json.loads((ROOT / path).read_text())
    except (OSError, json.JSONDecodeError):
        return False
    return protocol.get("task_fixture", {}).get("task_family_generation") == "lifecycle-v1"


def _json_object_without_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def evidence_bundle_valid(
    path: Path,
    max_uncompressed_bytes: int = 64 * 1024 * 1024,
    max_record_bytes: int = 8 * 1024 * 1024,
) -> bool:
    """Parse a compact evidence bundle without allowing unbounded decompression."""
    seen_paths: set[str] = set()
    total_bytes = 0
    records = 0
    try:
        with gzip.open(path, "rb") as stream:
            while True:
                raw_line = stream.readline(max_record_bytes + 1)
                if not raw_line:
                    break
                if len(raw_line) > max_record_bytes:
                    return False
                total_bytes += len(raw_line)
                if total_bytes > max_uncompressed_bytes or not raw_line.endswith(b"\n"):
                    return False
                line = raw_line.decode("utf-8")
                if not line.strip():
                    return False
                record = json.loads(
                    line,
                    object_pairs_hook=_json_object_without_duplicate_keys,
                )
                if not isinstance(record, dict) or set(record) != {"path", "content"}:
                    return False
                evidence_path = record.get("path")
                content = record.get("content")
                if not isinstance(evidence_path, str) or not evidence_path or not isinstance(content, str):
                    return False
                canonical = PurePosixPath(evidence_path)
                canonical_text = canonical.as_posix()
                if (
                    canonical.is_absolute()
                    or ".." in canonical.parts
                    or "." in canonical.parts
                    or "\\" in evidence_path
                    or canonical_text != evidence_path
                    or canonical_text in {"", "."}
                    or canonical_text in seen_paths
                ):
                    return False
                seen_paths.add(canonical_text)
                records += 1
    except (OSError, EOFError, UnicodeDecodeError, ValueError):
        return False
    return records > 0


LOCAL_SKILL_ARTIFACTS = [
    "AGENTS.md",
    ".agents/skills/index.md",
    ".agents/skills/benchmark-protocol-writer.md",
    ".agents/skills/claim-evidence-auditor.md",
    ".agents/skills/practical-software-quality-reviewer.md",
]

DECISION_RECORDS = [
    "docs/architecture/decision-records/0001-research-kernel.md",
    "docs/architecture/decision-records/0002-evidence-stages.md",
    "docs/architecture/decision-records/0003-methodology-and-reporting.md",
    "docs/architecture/decision-records/0004-stack-compatibility.md",
    "docs/architecture/decision-records/0005-token-accounting-and-protocol-identity.md",
    "docs/architecture/decision-records/0006-repository-workflow-and-validation.md",
]

REQUIRED_PATHS = [
    "README.md",
    "docs/methodology/README.md",
    "docs/research/roadmap.md",
    "data/repositories.json",
    "data/techniques.json",
    "data/compatibility-edges.json",
    "data/literature.json",
    "data/evaluations.json",
    "data/evaluation-profiles.json",
    "data/evaluation-agent-runtimes.json",
    "data/workflow-task-sequences.json",
    "data/workflow-sessions.json",
    "data/large-project-candidates.json",
    "data/medium-project-candidates.json",
    "data/repository-fixtures.json",
    "data/tool-analysis-backlog.json",
    "docs/README.md",
    "docs/architecture/README.md",
    "docs/architecture/research-system.md",
    "docs/architecture/domain-model.md",
    "docs/architecture/compatibility-graph.md",
    "docs/architecture/workflows.md",
    "docs/architecture/repository-layout.md",
    "docs/architecture/decision-records/0001-research-kernel.md",
    "docs/reference/compatibility-taxonomy.md",
    "docs/reference/README.md",
    "docs/evaluations/README.md",
    "docs/evaluations/design/README.md",
    "docs/evaluations/design/framework.md",
    "docs/evaluations/operations/fixture-guide.md",
    "docs/evaluations/design/token-and-quality-policy.md",
    "docs/evaluations/design/tool-isolation-policy.md",
    "docs/evaluations/plans/phase-2-benchmark-plan.md",
    "docs/evaluations/plans/README.md",
    "docs/evaluations/design/workflow-model.md",
    "docs/evaluations/operations/runbook.md",
    "docs/evaluations/operations/README.md",
    "docs/evaluations/operations/runner-reference.md",
    "docs/evaluations/operations/workflow-guide.md",
    "docs/evaluations/design/fixture-design.md",
    "docs/evaluations/design/result-schema.md",
    "docs/reference/literature-review.md",
    "templates/README.md",
    "templates/evaluation-protocol.md",
    "templates/research-paper-outline.md",
    "docs/papers/README.md",
    "docs/papers/phase-1-compatibility-safe-token-saving-stacks.md",
    "docs/papers/phase-2-lifecycle-v1-natural-use-screening.md",
    "docs/reference/research-standards.md",
    "docs/research/README.md",
    "docs/research/roadmap.md",
    "docs/research/tool-research-strategy.md",
    "docs/methodology/README.md",
    "docs/methodology/discovery-protocol.md",
    "docs/methodology/evidence-and-provenance.md",
    "docs/methodology/report-writing-patterns.md",
    "docs/methodology/case-studies/graphify-discovery-correction.md",
    "docs/methodology/case-studies/README.md",
    "docs/tool-dossiers/README.md",
    "docs/tool-dossiers/README.md",
    "docs/tool-dossiers/rtk-ai-rtk.md",
    "docs/tool-dossiers/repowise-dev-repowise.md",
    "docs/tool-dossiers/colbymchenry-codegraph.md",
    "docs/tool-dossiers/dietrichgebert-ponytail.md",
    "docs/tool-dossiers/mibayy-token-savior.md",
    "docs/tool-dossiers/juliusbrussee-caveman.md",
    "docs/tool-dossiers/chopratejas-headroom.md",
    "docs/tool-dossiers/yamadashy-repomix.md",
    "docs/tool-dossiers/oraios-serena.md",
    "docs/tool-dossiers/mksglu-context-mode.md",
    "docs/tool-dossiers/thedotmack-claude-mem.md",
    "docs/tool-dossiers/tirth8205-code-review-graph.md",
    "docs/tool-dossiers/coderamp-labs-gitingest.md",
    "docs/tool-dossiers/yvgude-lean-ctx.md",
    "docs/tool-dossiers/cocoindex-io-cocoindex-code.md",
    "docs/tool-dossiers/open-compress-claw-compactor.md",
    "docs/tool-dossiers/jgravelle-jcodemunch-mcp.md",
    "docs/tool-dossiers/mex-memory-mex.md",
    "docs/tool-dossiers/juliusbrussee-cavemem.md",
    "docs/tool-dossiers/zdk-lowfat.md",
    "docs/tool-dossiers/manojmallick-sigmap.md",
    "docs/tool-dossiers/vincentkoc-tokenjuice.md",
    "docs/tool-dossiers/ldomaradzki-xcsift.md",
    "docs/tool-dossiers/context-engine-ai-context-engine.md",
    "docs/tool-dossiers/edouard-claude-snip.md",
    "docs/tool-dossiers/portofcontext-pctx.md",
    "docs/tool-dossiers/agentforce314-clawcodex.md",
    "sources/evaluations/README.md",
    "sources/discovery/2026-06-26-five-more-tool-source-structures.json",
    "sources/discovery/2026-06-26-five-more-tool-code-inspection.json",
    "sources/discovery/2026-06-26-eight-more-tool-source-structures.json",
    "sources/discovery/2026-06-26-eight-more-tool-code-inspection.json",
    "sources/discovery/2026-06-26-ten-more-tool-source-structures.json",
    "sources/discovery/2026-06-26-ten-more-tool-code-inspection.json",
    "sources/discovery/2026-06-26-source-logic-uplift-source-structures.json",
    "sources/discovery/2026-06-26-source-logic-uplift-code-inspection.json",
    "sources/discovery/2026-06-26-final-lead-uplift-source-structures.json",
    "sources/discovery/2026-06-26-final-lead-uplift-code-inspection.json",
    "sources/discovery/2026-06-26-tokless-go-test.json",
    "sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json",
    "sources/discovery/2026-08-09-repowise-source-logic.json",
    "sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json",
    "templates/repository-entry.md",
    "templates/repository-fixture.md",
    "templates/technique-entry.md",
    "templates/claim-entry.md",
    "templates/evaluation-record.md",
    "templates/evaluation-task.md",
    "templates/evaluation-run-record.json",
    "scripts/update_workflow_runbook.py",
    "schemas/evaluation-run-record.schema.json",
    "schemas/workflow-session-record.schema.json",
    "templates/report.md",
    "templates/tool-dossier.md",
    "prompts/researcher.md",
    "prompts/evaluator.md",
    "prompts/paper-writer.md",
    "scripts/audit_dossier_snapshots.py",
]

SURFACE_IDS = {
    "terminal_output_owner",
    "code_retrieval_authority",
    "tool_response_owner",
    "workflow_execution_owner",
    "context_compression_owner",
    "memory_authority",
    "output_style_controller",
    "artifact_policy_controller",
    "routing_authority",
}

FIXTURE_STATES = {
    "candidate-fixture",
    "qualified-fixture",
    "baseline-run",
    "treatment-ready",
    "retired-fixture",
}

FIXTURE_TASK_CLASSES = {
    "feature-implementation",
    "behavior-preserving-refactor",
    "code-review",
    "code-review-correction",
    "noisy-terminal-repair",
    "build-repair",
    "large-codebase-navigation",
    "multi-file-refactor",
    "memory-rediscovery",
    "broad-owner-context",
    "mcp-tool-heavy",
    "apple-build-repair",
    "replacement-runtime-comparison",
}

FIXTURE_TOKEN_WASTE_SURFACES = {
    "terminal-output",
    "build-output",
    "retrieval-context",
    "memory-rediscovery",
    "broad-context-owner",
    "mcp-tool-trace",
    "apple-build-output",
    "replacement-runtime",
}

FIXTURE_SCALES = {"synthetic-micro", "recorded-diagnostic", "medium-project", "large-project"}
FIXTURE_EVALUATION_USES = {
    "calibration",
    "diagnostic-preservation",
    "historical-evidence",
    "primary-candidate",
    "primary-objective",
}
PROFILE_TYPES = {"control", "individual_tool", "tool_stack", "replacement_runtime", "installer_orchestrator", "comparator"}
OBJECTIVES = {"individual_tool_effectiveness", "stack_effectiveness"}
NON_RUNNABLE_PROFILE_STATUSES = {
    "blocked-profile",
    "historical-profile",
    "deferred-profile",
    "invalid-profile",
}
GENERIC_ARTIFACT_SLUGS = {
    "codex",
    "owner",
    "product",
    "profile",
    "runtime",
    "tool",
    "v0",
    "v1",
    "v2",
}
EVALUATION_RECORD_TYPES = {"run", "paired_comparison", "aggregate_summary"}
EVALUATION_RUN_ROLES = {"baseline", "individual_tool_treatment", "stack_treatment", "replacement_runtime", "audit_only"}
EVALUATION_STATUSES = {"planned", "running", "completed", "failed", "excluded", "superseded"}
WORKFLOW_EVIDENCE_TYPES = {"workflow-simulation", "workflow-ablation", "sanity-check"}
WORKFLOW_SESSION_ROLES = {
    "baseline",
    "individual_tool_treatment",
    "stack_treatment",
    "replacement_runtime",
    "ablation",
    "sanity_check",
}
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
DOCKER_IMAGE_ID_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
REPO_DIGEST_RE = re.compile(r"^.+@sha256:[a-f0-9]{64}$")

DOSSIER_SNAPSHOT_STATUSES = {
    "pinned-commit",
    "unpinned-historical-inspection",
}

DOSSIER_REQUIRED_SECTIONS = (
    "## Identity",
    "## Summary",
    "## Evidence inventory",
    "## Installation and integration behavior",
    "## Runtime behavior",
    "## Token-saving mechanism",
    "## Compatibility notes",
    "## Failure modes and limits",
)

DOSSIER_STALE_PHRASES = (
    "not recorded during original pass",
    "GitHub `HEAD` tree",
    "Source-behavior review has started",
    "requires source-logic inspection",
    "Not yet reviewed beyond source-tree and metadata inspection in this dossier",
)


@functools.lru_cache(maxsize=1)
def workflow_session_schema_validator() -> Any | None:
    """Return the published-schema validator, or None when jsonschema is unavailable."""
    try:
        import jsonschema
    except ImportError:
        return None
    schema = json.loads((ROOT / WORKFLOW_SESSION_SCHEMA_REL).read_text())
    return jsonschema.Draft202012Validator(schema)


def validate_session_schema_conformance(session: dict, sid: str, errors: list[str]) -> None:
    """Gate one session record on the published JSON Schema, failing closed without jsonschema."""
    validator = workflow_session_schema_validator()
    if validator is None:
        if WORKFLOW_SESSION_SCHEMA_UNAVAILABLE not in errors:
            errors.append(WORKFLOW_SESSION_SCHEMA_UNAVAILABLE)
        return
    for violation in sorted(validator.iter_errors(session), key=lambda item: list(item.absolute_path)):
        location = "/".join(str(part) for part in violation.absolute_path) or "<record>"
        message = (
            f"workflow session {sid} violates {WORKFLOW_SESSION_SCHEMA_REL} "
            f"at {location}: {violation.message}"
        )
        if message not in errors:
            errors.append(message)


def load_json(rel: str) -> dict:
    path = ROOT / rel
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"Invalid JSON in {rel}: {exc}") from exc


TASK_ASSETS = {"agent-prompt.txt", "task.md", "setup.sh", "reset.sh", "seed-regression.patch", "verify.sh"}
SOURCE_SCAN_RE = re.compile(
    r"(?im)^.*(?:"
    r"(?:command\s+)?(?:grep|rg|awk|sed|perl|cmp|diff)\b|git\s+diff\b"
    r").*(?:^|[\s'\"])(?:[A-Za-z0-9_.-]+/)+(?:[A-Za-z0-9_.-]+)\.(?:c|cc|cpp|cs|go|java|js|jsx|mjs|py|rb|rs|ts|tsx)\b.*$"
    r"|^.*(?:python(?:3)?|node)\b.*(?:(?:open\(|read_text|read_bytes|readFile|readFileSync).*(?:\.c|\.cc|\.cpp|\.cs|\.go|\.java|\.js|\.jsx|\.mjs|\.py|\.rb|\.rs|\.ts|\.tsx)\b|(?:\.c|\.cc|\.cpp|\.cs|\.go|\.java|\.js|\.jsx|\.mjs|\.py|\.rb|\.rs|\.ts|\.tsx)\b.*(?:open\(|read_text|read_bytes|readFile|readFileSync)).*$"
    r"|^\s*(?:assert|test|expect|require)\b.*(?:read_text|read_bytes|readFile|open\().*$"
)


def patch_paths(path: Path) -> list[str]:
    paths: set[str] = set()
    for line in path.read_text(errors="replace").splitlines():
        match = re.match(r"^diff --git a/(.+) b/(.+)$", line)
        if match:
            paths.add(match.group(2))
    return sorted(paths)


def is_production_path(path: str) -> bool:
    low = path.lower()
    parsed = Path(low)
    parts = set(parsed.parts)
    name = parsed.name
    if parts & {"test", "tests", "testing", "fixture", "fixtures", "docs", "doc", "generated", "dist", "build", "coverage", "tasks", "controller"}:
        return False
    if (
        name.endswith(("_test.go", ".test.js", ".test.jsx", ".test.mjs", ".test.ts", ".test.tsx"))
        or (name.startswith("test_") and parsed.suffix == ".py")
        or (name.endswith("_test.py"))
    ):
        return False
    if low.endswith((".md", ".rst", ".txt", ".snap", ".patch", ".lock", ".map")):
        return False
    return parsed.suffix in {".c", ".cc", ".cpp", ".cs", ".cshtml", ".go", ".java", ".js", ".jsx", ".mjs", ".py", ".rb", ".rs", ".ts", ".tsx", ".yaml", ".yml"}


def patch_behavior_bearing_paths(path: Path) -> list[str]:
    """Production paths with a non-comment, non-whitespace patch change.

    A five-file floor is a causal-scope floor, not permission to add formatting
    or prose-only files. This intentionally works from the controller patch so
    it also catches deleted comment-only padding.
    """
    current = ""
    bearing: set[str] = set()
    for line in path.read_text(errors="replace").splitlines():
        match = re.match(r"^diff --git a/(.+) b/(.+)$", line)
        if match:
            current = match.group(2)
            continue
        if not current or not line.startswith(("+", "-")) or line.startswith(("+++", "---")):
            continue
        value = line[1:].strip()
        if value and not value.startswith(("//", "/*", "*", "#", "<!--", "--")):
            bearing.add(current)
    return sorted(bearing)


def task_directory_sha256(task_dir: Path) -> str:
    """Hash every controller task byte with its relative path, deterministically."""
    digest = hashlib.sha256()
    for path in sorted(item for item in task_dir.rglob("*") if item.is_file()):
        digest.update(str(path.relative_to(task_dir)).encode() + b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def verifier_uses_source_identity(task_dir: Path) -> bool:
    verifier = task_dir / "verify.sh"
    texts = [verifier.read_text(errors="replace")]
    for path in task_dir.rglob("*"):
        if (
            path.is_file()
            and path.name not in TASK_ASSETS
            and path.suffix.lower() in {".sh", ".py", ".js", ".mjs", ".cjs", ".ts"}
        ):
            texts.append(path.read_text(errors="replace"))
    return any(SOURCE_SCAN_RE.search(text) for text in texts)


def expected_task_concealed_paths(task: dict) -> list[str]:
    expected = set()
    expected.update(str(path) for path in task.get("upstream_test_paths", []))
    expected.update(str(path) for path in task.get("compatibility_rebased_test_paths", []))
    return sorted(expected)


def validate_qualification(sequence: dict, errors: list[str]) -> None:
    sid = sequence["id"]
    rel = sequence.get("qualification_path")
    if not rel or not (ROOT / rel).is_file():
        errors.append(f"active workflow sequence {sid} missing generated qualification evidence: {rel or '<unset>'}")
        return
    q = load_json(rel)

    def qualification_numeric_types_valid(value: object, parent_key: str = "") -> bool:
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "schema_version" or key.endswith(("_exit", "_count", "_order")):
                    if type(child) is not int:
                        return False
                if key.endswith(("_exits", "_counts")):
                    if isinstance(child, dict):
                        if any(type(item) is not int for item in child.values()):
                            return False
                    elif isinstance(child, list):
                        if any(type(item) is not int for item in child):
                            return False
                    else:
                        return False
                if not qualification_numeric_types_valid(child, key):
                    return False
        elif isinstance(value, list):
            return all(qualification_numeric_types_valid(item, parent_key) for item in value)
        return True

    if not qualification_numeric_types_valid(q):
        errors.append(f"qualification {rel} decision-bearing numeric evidence must use strict non-boolean integers")
    ordered = sorted(sequence["tasks"], key=lambda item: item["order"])
    controller_hidden = (ROOT / ordered[0]["prompt_path"]).parent.parents[1] / "controller-hidden"
    expected_controller_hidden_sha = task_directory_sha256(controller_hidden) if controller_hidden.is_dir() else None
    if q.get("controller_hidden_sha256") != expected_controller_hidden_sha:
        errors.append(f"qualification {rel} shared controller-hidden asset binding is stale")
    production_by_task = {
        task["id"]: [
            path
            for path in patch_paths((ROOT / task["prompt_path"]).parent / "seed-regression.patch")
            if is_production_path(path)
        ]
        for task in ordered
    }
    generation = sequence.get("task_family_generation")
    if generation != "lifecycle-v1":
        errors.append(f"qualification {rel} references retired generation {generation!r}")
        return
    required_true = ("fixed_verifier_zero", "full_fixed_cumulative_verifier_zero", "composite_seed_merge_zero", "no_unmerged_paths", "all_expected_model_concealment_declared")
    required_true += (
        "seeded_compile_outcomes_valid",
        "composite_seed_compile_outcomes_valid",
        "no_model_visible_acceptance_assets",
        "no_model_concealed_acceptance_assets",
        "controller_compile_policy_not_model_facing",
        "model_visible_acceptance_assets_match_verifier_copies",
        "aggregate_verifier_environment_passed",
        "project_compile_passed",
    )
    if q.get("schema_version") != 5:
        errors.append(f"qualification {rel} must use schema_version=5 for controller-only Lifecycle V1")
    if q.get("task_family_generation") != "lifecycle-v1":
        errors.append(f"qualification {rel} must bind task_family_generation=lifecycle-v1")
    if q.get("acceptance_visibility") != "controller-only-compile-policy":
        errors.append(f"qualification {rel} must record controller-only compile policy visibility")
    if q.get("all_acceptance_behavior_model_visible") is not False:
        errors.append(f"qualification {rel} must not claim internal acceptance behavior is model-visible")
    if q.get("expected_model_visible_acceptance_asset_count") != 0:
        errors.append(f"qualification {rel} compile-only acceptance must not require file-backed test assets")
    if q.get("project_compile_command") != sequence.get("project_compile_command"):
        errors.append(f"qualification {rel} project-wide compile command does not match the active sequence")
    if sequence.get("status") == "active":
        required_true += ("fixed_snapshot_model_concealed_paths_safe",)
    if q.get("snapshot") != sequence.get("initial_snapshot", {}).get("commit") or q.get("ordered_task_ids") != [t["id"] for t in ordered] or q.get("qualified_on") != sequence.get("qualification_date"):
        errors.append(f"qualification {rel} snapshot, date, or task order is stale")
    if any(q.get(field) is not True for field in required_true):
        errors.append(f"qualification {rel} must record every executable gate as true")
    composite_seed_exits = q.get("composite_seed_verifier_exits", {})
    composite_seed_exits_invalid = (
        set(composite_seed_exits) != {task["id"] for task in ordered}
        or any(code not in {0, 1} for code in composite_seed_exits.values())
    )
    if composite_seed_exits_invalid:
        errors.append(
            f"qualification {rel} seeded verifiers must record only compiler pass/fail exits, not collection or infrastructure failures"
        )
    boundaries = q.get("cumulative_boundaries", [])
    boundary_invalid = len(boundaries) != len(ordered)
    if not boundary_invalid:
        for task, boundary in zip(ordered, boundaries):
            common_invalid = (
                boundary.get("task_id") != task["id"]
                or boundary.get("seed_apply_check_exit") != 0
                or boundary.get("seed_apply_exit") != 0
                or boundary.get("seeded_verifier_exit") not in {0, 1}
                or boundary.get("repair_apply_check_exit") != 0
                or boundary.get("repair_apply_exit") != 0
                or any(code != 0 for code in boundary.get("retained_verifier_exits", {}).values())
            )
            if common_invalid:
                boundary_invalid = True
                break
    if boundary_invalid:
        errors.append(f"qualification {rel} lacks fresh cumulative seed/repair boundary evidence")
    records = q.get("tasks", [])
    if len(records) != len(ordered):
        errors.append(f"qualification {rel} task count does not match sequence")
        return
    for task, record in zip(ordered, records):
        task_dir = (ROOT / task["prompt_path"]).parent
        files = production_by_task[task["id"]]
        hashes = {name: hashlib.sha256((task_dir / name).read_bytes()).hexdigest() for name in ("agent-prompt.txt", "seed-regression.patch", "verify.sh")}
        controller_visible = task_dir / "controller-visible"
        expected_acceptance_paths: list[str] = []
        controller_visible_assets = [
            {
                "path": str(Path("controller-visible") / path_text),
                "model_visible_path": path_text,
                "sha256": hashlib.sha256((controller_visible / path_text).read_bytes()).hexdigest(),
            }
            for path_text in expected_acceptance_paths
            if (controller_visible / path_text).is_file()
        ]
        production_file_count = record.get("production_file_count")
        if (
            not set(record.get("production_files", []))
            or type(production_file_count) is not int
            or production_file_count < 1
        ):
            errors.append(f"qualification {rel} task {task['id']} records no production/type files")
        if record.get("task_id") != task["id"] or record.get("production_files") != files or record.get("production_file_count") != len(files) or record.get("agent_prompt_sha256") != hashes["agent-prompt.txt"] or record.get("seed_patch_sha256") != hashes["seed-regression.patch"] or record.get("verifier_sha256") != hashes["verify.sh"] or record.get("controller_visible_acceptance_assets") != controller_visible_assets or record.get("model_visible_acceptance_asset_paths") != expected_acceptance_paths or len(controller_visible_assets) != len(expected_acceptance_paths) or record.get("task_directory_sha256") != task_directory_sha256(task_dir):
            errors.append(f"qualification {rel} task {task['id']} has stale hashes, files, or count")
        expected = expected_task_concealed_paths(task)
        declared = sorted(str(path) for path in task.get("model_concealed_paths", []))
        if declared != expected:
            errors.append(f"active workflow sequence {sid} task {task['id']} omits expected model-concealed tests: {sorted(set(expected) - set(declared))}")
        if (
            record.get("expected_model_concealed_paths") != expected
            or record.get("model_concealed_paths") != declared
            or record.get("omitted_expected_model_concealed_paths") != []
            or record.get("declared_concealment_matches_expected") is not True
            or (sequence.get("status") == "active" and record.get("fixed_snapshot_model_concealed_safe") is not True)
        ):
            errors.append(f"qualification {rel} task {task['id']} concealment evidence is stale or incomplete")
        if q.get("task_binding", {}).get("task_directories", {}).get(task["id"]) != task_directory_sha256(task_dir):
            errors.append(f"qualification {rel} task {task['id']} directory-byte binding is stale")


def qualification_is_current(sequence: dict) -> tuple[bool, dict]:
    errors: list[str] = []
    validate_qualification(sequence, errors)
    rel = sequence.get("qualification_path")
    qualification = load_json(rel) if rel and (ROOT / rel).is_file() else {}
    return not errors, qualification


def validate_repository_fixtures(fixture_doc: dict, errors: list[str]) -> None:
    if fixture_doc.get("schema_version") != 1:
        errors.append("data/repository-fixtures.json must use schema_version 1")

    fixtures = fixture_doc.get("fixtures")
    if not isinstance(fixtures, list):
        errors.append("data/repository-fixtures.json must contain a fixtures list")
        return

    seen: set[str] = set()
    kebab = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    readiness_states = {"qualified-fixture", "baseline-run", "treatment-ready"}
    required_list_fields = ("future_evaluation_lanes", "candidate_profiles", "blockers", "caveats")
    for index, fixture in enumerate(fixtures):
        if not isinstance(fixture, dict):
            errors.append(f"fixture record at index {index} must be an object")
            continue

        fid = fixture.get("id")
        if not fid:
            errors.append(f"fixture record at index {index} missing id")
            continue
        if not kebab.match(fid):
            errors.append(f"fixture {fid} id must be kebab-case")
        if fid in seen:
            errors.append(f"duplicate fixture id: {fid}")
        seen.add(fid)

        status = fixture.get("status")
        if status not in FIXTURE_STATES:
            errors.append(f"fixture {fid} has invalid status: {status}")

        task_classes = fixture.get("task_classes")
        if not isinstance(task_classes, list) or not task_classes:
            errors.append(f"fixture {fid} must list at least one task class")
        else:
            for task_class in task_classes:
                if task_class not in FIXTURE_TASK_CLASSES:
                    errors.append(f"fixture {fid} has invalid task class: {task_class}")

        primary_surface = fixture.get("primary_token_waste_surface")
        if primary_surface not in FIXTURE_TOKEN_WASTE_SURFACES:
            errors.append(f"fixture {fid} has invalid primary_token_waste_surface: {primary_surface}")

        fixture_scale = fixture.get("fixture_scale")
        if fixture_scale not in FIXTURE_SCALES:
            errors.append(f"fixture {fid} has invalid fixture_scale: {fixture_scale}")
        evaluation_use = fixture.get("evaluation_use")
        if evaluation_use not in FIXTURE_EVALUATION_USES:
            errors.append(f"fixture {fid} has invalid evaluation_use: {evaluation_use}")
        if evaluation_use == "primary-objective" and fixture_scale not in {"large-project", "medium-project"}:
            errors.append(f"fixture {fid} cannot be primary-objective unless fixture_scale is large-project or medium-project")

        artifact_paths = fixture.get("artifact_paths")
        if not isinstance(artifact_paths, dict) or not artifact_paths.get("root"):
            errors.append(f"fixture {fid} must define artifact_paths.root")

        for key in required_list_fields:
            if not isinstance(fixture.get(key), list):
                errors.append(f"fixture {fid} must define {key} list")

        repository = fixture.get("repository")
        if not isinstance(repository, dict) or not (
            repository.get("id") or repository.get("url") or repository.get("path")
        ):
            errors.append(f"fixture {fid} must define repository id, url, or path")

        for key in ("setup", "reset", "verifier"):
            value = fixture.get(key)
            if not isinstance(value, dict):
                errors.append(f"fixture {fid} must define {key} object")
                continue
            if not value.get("command") and not value.get("blocker"):
                errors.append(f"fixture {fid} must define {key}.command or {key}.blocker")

        snapshot = fixture.get("snapshot")
        prompt = fixture.get("prompt")
        if status in readiness_states:
            if not isinstance(snapshot, dict) or not (
                snapshot.get("commit") or snapshot.get("snapshot_policy")
            ):
                errors.append(
                    f"fixture {fid} with status {status} must define snapshot.commit or snapshot.snapshot_policy"
                )
            if not isinstance(prompt, dict) or not (
                prompt.get("path") or prompt.get("prompt_policy")
            ):
                errors.append(
                    f"fixture {fid} with status {status} must define prompt.path or prompt.prompt_policy"
                )
            for key in ("setup", "reset", "verifier"):
                value = fixture.get(key, {})
                if not value.get("command"):
                    errors.append(f"fixture {fid} with status {status} must define {key}.command")


def validate_large_project_candidates(candidate_doc: dict, fixture_doc: dict, errors: list[str]) -> None:
    if candidate_doc.get("schema_version") != 1:
        errors.append("data/large-project-candidates.json must use schema_version 1")
    candidates = candidate_doc.get("candidates")
    # The list may be empty: the active Lifecycle V1 portfolio currently has no large-project lane.
    # removed Terraform. The file still carries the selection policy for a future large lane.
    if not isinstance(candidates, list):
        errors.append("data/large-project-candidates.json must contain a candidates list")
        return
    fixture_ids = {fixture.get("id") for fixture in fixture_doc.get("fixtures", [])}
    for candidate in candidates:
        cid = candidate.get("id")
        if not cid:
            errors.append("large-project candidate missing id")
            continue
        if cid not in fixture_ids:
            errors.append(f"large-project candidate {cid} is not represented in data/repository-fixtures.json")
        for key in ("github", "url", "language", "size_kb", "default_branch", "setup_policy", "verifier_policy"):
            if candidate.get(key) in (None, ""):
                errors.append(f"large-project candidate {cid} missing {key}")


def validate_medium_project_candidates(candidate_doc: dict, fixture_doc: dict, errors: list[str]) -> None:
    if candidate_doc.get("schema_version") != 1:
        errors.append("data/medium-project-candidates.json must use schema_version 1")
    candidates = candidate_doc.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        errors.append("data/medium-project-candidates.json must contain a non-empty candidates list")
        return
    fixture_ids = {fixture.get("id") for fixture in fixture_doc.get("fixtures", [])}
    for candidate in candidates:
        cid = candidate.get("id")
        if not cid:
            errors.append("medium-project candidate missing id")
            continue
        if cid not in fixture_ids:
            errors.append(f"medium-project candidate {cid} is not represented in data/repository-fixtures.json")
        for key in ("github", "url", "language", "size_kb", "default_branch", "setup_policy", "verifier_policy"):
            if candidate.get(key) in (None, ""):
                errors.append(f"medium-project candidate {cid} missing {key}")
        if not candidate.get("tasks") and candidate.get("qualification_status") != "fixture-redesign-required":
            errors.append(f"medium-project candidate {cid} missing tasks")
        if candidate.get("qualification_status") == "fixture-redesign-required" and not candidate.get("task_backlog"):
            errors.append(f"medium-project candidate {cid} redesign status requires a task_backlog")


def validate_evaluation_profiles(profile_doc: dict, fixture_doc: dict, errors: list[str]) -> set[str]:
    if profile_doc.get("schema_version") != 1:
        errors.append("data/evaluation-profiles.json must use schema_version 1")
    profiles = profile_doc.get("profiles")
    if not isinstance(profiles, list):
        errors.append("data/evaluation-profiles.json must contain a profiles list")
        return set()
    fixture_profile_ids = {
        profile_id
        for fixture in fixture_doc.get("fixtures", [])
        for profile_id in fixture.get("candidate_profiles", [])
    }
    seen: set[str] = set()
    seen_artifact_slugs: dict[str, str] = {}
    for index, profile in enumerate(profiles):
        if not isinstance(profile, dict):
            errors.append(f"profile record at index {index} must be an object")
            continue
        pid = profile.get("id")
        if not pid:
            errors.append(f"profile record at index {index} missing id")
            continue
        if pid in seen:
            errors.append(f"duplicate evaluation profile id: {pid}")
        seen.add(pid)
        if profile.get("status") not in NON_RUNNABLE_PROFILE_STATUSES:
            artifact_slug = profile.get("artifact_slug")
            if not isinstance(artifact_slug, str) or not artifact_slug:
                errors.append(f"runnable profile {pid} missing artifact_slug")
            elif re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", artifact_slug) is None:
                errors.append(f"runnable profile {pid} has invalid artifact_slug: {artifact_slug}")
            else:
                if artifact_slug in GENERIC_ARTIFACT_SLUGS:
                    errors.append(f"runnable profile {pid} has generic artifact_slug: {artifact_slug}")
                previous = seen_artifact_slugs.get(artifact_slug)
                if previous is not None:
                    errors.append(
                        f"duplicate artifact_slug {artifact_slug}: runnable profiles {previous} and {pid}"
                    )
                else:
                    seen_artifact_slugs[artifact_slug] = pid
        if profile.get("profile_type") not in PROFILE_TYPES:
            errors.append(f"profile {pid} has invalid profile_type: {profile.get('profile_type')}")
        if profile.get("objective_scope") not in OBJECTIVES | {"control"}:
            errors.append(f"profile {pid} has invalid objective_scope: {profile.get('objective_scope')}")
        for key in ("enabled_surfaces", "disabled_overlaps", "components"):
            if not isinstance(profile.get(key), list):
                errors.append(f"profile {pid} must define {key} list")
        if profile.get("profile_type") == "tool_stack" and len(profile.get("components", [])) < 2:
            errors.append(f"stack profile {pid} must list at least two components")
        if not isinstance(profile.get("install"), dict) or not isinstance(profile.get("reset"), dict):
            errors.append(f"profile {pid} must define install and reset objects")
    missing = sorted(fixture_profile_ids - seen)
    for pid in missing:
        errors.append(f"fixture references unknown evaluation profile: {pid}")
    return seen


def protocol_matches_active_sequence(protocol: dict, sequence: dict) -> bool:
    """Return whether an unexecuted protocol belongs to the active fixture/model generation."""
    task_fixture = protocol.get("task_fixture", {})
    agent_condition = (
        protocol.get("selected_execution", {})
        .get("descriptor", {})
        .get("agent_condition", {})
    )
    mistake_gate = sequence.get("mistake_gate", {})
    allowed_model_conditions = {
        str(mistake_gate.get("designated_model_condition")),
        *{
            str(condition)
            for condition in mistake_gate.get("allowed_treatment_model_conditions", [])
            if condition
        },
    }
    return (
        task_fixture.get("sequence_id") == sequence.get("id")
        and task_fixture.get("qualification_path") == sequence.get("qualification_path")
        and agent_condition.get("model_condition_id") in allowed_model_conditions
        and agent_condition.get("model") == mistake_gate.get("model")
        and agent_condition.get("reasoning_effort") == mistake_gate.get("reasoning_effort")
    )


def validate_candidate_profile_launch_readiness(
    profile_doc: dict,
    fixture_doc: dict,
    sequence_doc: dict,
    parity_doc: dict,
    qualification_docs: list[dict],
    protocol_docs: dict[str, dict],
    errors: list[str],
    executed_protocol_paths: set[str] | None = None,
) -> None:
    """Fail closed before provider execution for every non-baseline fixture candidate."""
    executed_protocol_paths = executed_protocol_paths or set()
    profiles_by_id = {
        profile.get("id"): profile
        for profile in profile_doc.get("profiles", [])
        if isinstance(profile, dict) and profile.get("id")
    }
    candidate_profiles = {
        profile_id
        for fixture in fixture_doc.get("fixtures", [])
        if isinstance(fixture, dict)
        for profile_id in fixture.get("candidate_profiles", [])
        if profile_id != "baseline-bare-codex"
    }
    approved_profiles = set(
        parity_doc.get("corrected_contracts", {}).get("approved_profile_ids", [])
    )
    if approved_profiles != candidate_profiles:
        errors.append(
            "future candidate parity-approved profile set must exactly match non-baseline fixture candidates: "
            f"approved={sorted(approved_profiles)} candidates={sorted(candidate_profiles)}"
        )

    active_sequences_by_fixture: dict[str, list[str]] = {}
    active_sequences_by_id: dict[str, dict] = {}
    for sequence in sequence_doc.get("sequences", []):
        if not isinstance(sequence, dict) or sequence.get("status") != "active":
            continue
        fixture_id = sequence.get("fixture_id")
        sequence_id = sequence.get("id")
        if isinstance(fixture_id, str) and isinstance(sequence_id, str):
            active_sequences_by_fixture.setdefault(fixture_id, []).append(sequence_id)
            active_sequences_by_id[sequence_id] = sequence

    if active_sequences_by_id and all(
        sequence.get("task_family_generation") == "lifecycle-v1"
        and sequence.get("mistake_gate", {}).get("status") == "provider-pilot-required"
        for sequence in active_sequences_by_id.values()
    ):
        # V1 treatment contracts cannot be frozen before its first valid baseline
        # pilot; historical V0 treatment protocols remain frozen evidence only.
        return

    expected_pairs: set[tuple[str, str]] = set()
    for fixture in fixture_doc.get("fixtures", []):
        if not isinstance(fixture, dict):
            continue
        sequence_ids = active_sequences_by_fixture.get(str(fixture.get("id")), [])
        for lane in fixture.get("future_evaluation_lanes", []):
            if not isinstance(lane, dict) or lane.get("status") != "ready-for-paid-launch":
                continue
            profile_id = lane.get("id")
            if not isinstance(profile_id, str) or profile_id == "baseline-bare-codex":
                continue
            for sequence_id in sequence_ids:
                expected_pairs.add((sequence_id, profile_id))

    eligible_lanes: list[dict] = []
    for receipt in qualification_docs:
        if not isinstance(receipt, dict):
            continue
        if receipt.get("execution_mode") != "prepare-only-no-provider":
            continue
        if receipt.get("provider_calls") != 0:
            continue
        if receipt.get("summary", {}).get("provider_backed_sessions_created") != 0:
            continue
        eligible_lanes.extend(
            lane for lane in receipt.get("lanes", []) if isinstance(lane, dict)
        )

    completed_pairs: set[tuple[str, str]] = set()
    for protocol_path in executed_protocol_paths:
        record = protocol_docs.get(protocol_path, {})
        protocol = record.get("document", {}) if isinstance(record, dict) else {}
        selected = protocol.get("selected_execution", {}).get("descriptor", {})
        sequence_id = selected.get("sequence_id")
        profile_id = selected.get("selected_profile", {}).get("profile_id")
        if isinstance(sequence_id, str) and isinstance(profile_id, str):
            completed_pairs.add((sequence_id, profile_id))

    for sequence_id, profile_id in sorted(expected_pairs):
        if (sequence_id, profile_id) in completed_pairs:
            continue
        profile = profiles_by_id.get(profile_id)
        if not profile or profile.get("status") != "screening-shortlist":
            errors.append(
                f"future candidate {profile_id} must be a screening-shortlist profile before launch"
            )

        matching_protocols: list[tuple[str, dict]] = []
        for protocol_path, record in protocol_docs.items():
            if not isinstance(record, dict):
                continue
            protocol = record.get("document", {})
            selected = protocol.get("selected_execution", {}).get("descriptor", {})
            if (
                protocol_path not in executed_protocol_paths
                and selected.get("sequence_id") == sequence_id
                and selected.get("selected_profile", {}).get("profile_id") == profile_id
                and protocol.get("status") == "frozen-ready-not-run"
                and protocol_matches_active_sequence(protocol, active_sequences_by_id[sequence_id])
            ):
                matching_protocols.append((protocol_path, record))
        if len(matching_protocols) != 1:
            errors.append(
                f"future candidate {sequence_id}/{profile_id} must bind exactly one current frozen protocol; "
                f"found {len(matching_protocols)}"
            )
            continue

        protocol_path, protocol_record = matching_protocols[0]
        protocol_sha = protocol_record.get("sha256")
        matching_lanes = [
            lane
            for lane in eligible_lanes
            if lane.get("sequence_id") == sequence_id
            and lane.get("profile_id") == profile_id
            and lane.get("protocol_path") == protocol_path
            and lane.get("protocol_sha256") == protocol_sha
        ]
        if len(matching_lanes) != 1:
            errors.append(
                f"future candidate {sequence_id}/{profile_id} is missing matching provider-free qualification "
                f"for {protocol_path}@{protocol_sha}"
            )
            continue

        lane = matching_lanes[0]
        preparation = lane.get("prepare_verification", {})
        host = lane.get("host_integration", {})
        if lane.get("prepared") is not True or preparation.get("passed") is not True:
            errors.append(f"future candidate {sequence_id}/{profile_id} lacks successful fixture preparation")
        if preparation.get("concealment_passed") is not True:
            errors.append(f"future candidate {sequence_id}/{profile_id} lacks concealment proof")
        if preparation.get("composite_seed_delivery_passed") is not True:
            errors.append(f"future candidate {sequence_id}/{profile_id} lacks composite seed-delivery proof")
        if host.get("passed") is not True or host.get("missing_required_files"):
            errors.append(f"future candidate {sequence_id}/{profile_id} lacks successful host-integration proof")
        if any(code != 0 for code in host.get("install_exit_codes", [])) or any(
            code != 0 for code in host.get("verify_exit_codes", [])
        ):
            errors.append(f"future candidate {sequence_id}/{profile_id} has failed host-integration commands")
        if lane.get("tool_warmup_exit_code") != 0:
            errors.append(f"future candidate {sequence_id}/{profile_id} lacks successful tool warmup")

        protocol = protocol_record.get("document", {})
        tool_config = (
            protocol.get("selected_execution", {})
            .get("descriptor", {})
            .get("tool_adapter", {})
            .get("tool_config", {})
        )
        mcp_required = bool(tool_config.get("mcp_handshake", {}).get("required"))
        handshake = lane.get("mcp_handshake", {})
        if bool(handshake.get("required")) != mcp_required:
            errors.append(f"future candidate {sequence_id}/{profile_id} has mismatched MCP requirement proof")
        if mcp_required:
            tool_names = handshake.get("tool_names", [])
            tool_count = handshake.get("tool_count", 0)
            if not (
                handshake.get("passed") is True
                and handshake.get("initialize_passed") is True
                and handshake.get("tools_list_passed") is True
                and isinstance(tool_count, int)
                and tool_count > 0
                and isinstance(tool_names, list)
                and len(tool_names) == tool_count
                and not handshake.get("errors")
            ):
                errors.append(
                    f"future candidate {sequence_id}/{profile_id} lacks non-empty MCP tools/list proof"
                )


def executed_protocol_paths_from_registry(workflow_sessions_doc: dict) -> set[str]:
    return {
        str(session.get("frozen_protocol", {}).get("path"))
        for session in workflow_sessions_doc.get("sessions", [])
        if session.get("status") == "completed"
        and session.get("interpretation", {}).get("accepted_for_execution") is True
        and isinstance(session.get("frozen_protocol", {}).get("path"), str)
    }


def current_candidate_profile_launch_readiness_errors(root: Path = ROOT) -> list[str]:
    profile_doc = json.loads((root / "data/evaluation-profiles.json").read_text())
    fixture_doc = json.loads((root / "data/repository-fixtures.json").read_text())
    sequence_doc = json.loads((root / "data/workflow-task-sequences.json").read_text())
    workflow_sessions_doc = json.loads((root / "data/workflow-sessions.json").read_text())
    parity_doc = json.loads(
        (root / "sources/evaluations/audits/official-integration-parity-20260718.json").read_text()
    )
    qualification_docs = [
        json.loads(path.read_text())
        for path in sorted(
            (root / "sources/evaluations/audits").glob("corrected-integration-qualification-*.json")
        )
    ]
    protocol_docs = {
        path.relative_to(root).as_posix(): {
            "document": json.loads(path.read_text()),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in (root / "sources/evaluations/protocols").glob("*.json")
    }
    errors: list[str] = []
    validate_candidate_profile_launch_readiness(
        profile_doc,
        fixture_doc,
        sequence_doc,
        parity_doc,
        qualification_docs,
        protocol_docs,
        errors,
        executed_protocol_paths_from_registry(workflow_sessions_doc),
    )
    return errors


def validate_agent_runtimes(runtime_doc: dict, errors: list[str]) -> tuple[set[str], set[str]]:
    if runtime_doc.get("schema_version") != 1:
        errors.append("data/evaluation-agent-runtimes.json must use schema_version 1")
    runtimes = runtime_doc.get("agent_runtimes")
    if not isinstance(runtimes, list) or not runtimes:
        errors.append("data/evaluation-agent-runtimes.json must contain agent_runtimes")
        runtimes = []
    runtime_ids: set[str] = set()
    for index, runtime in enumerate(runtimes):
        if not isinstance(runtime, dict):
            errors.append(f"agent runtime at index {index} must be an object")
            continue
        rid = runtime.get("id")
        if not rid:
            errors.append(f"agent runtime at index {index} missing id")
            continue
        if rid in runtime_ids:
            errors.append(f"duplicate agent runtime id: {rid}")
        runtime_ids.add(rid)
        for key in ("status", "runner", "provider_family", "usage_extractor"):
            if not runtime.get(key):
                errors.append(f"agent runtime {rid} missing {key}")
    conditions = runtime_doc.get("model_conditions")
    if not isinstance(conditions, list) or not conditions:
        errors.append("data/evaluation-agent-runtimes.json must contain model_conditions")
        conditions = []
    condition_ids: set[str] = set()
    for index, condition in enumerate(conditions):
        if not isinstance(condition, dict):
            errors.append(f"model condition at index {index} must be an object")
            continue
        cid = condition.get("id")
        if not cid:
            errors.append(f"model condition at index {index} missing id")
            continue
        if cid in condition_ids:
            errors.append(f"duplicate model condition id: {cid}")
        condition_ids.add(cid)
        runtime_id = condition.get("runtime_id")
        if runtime_id not in runtime_ids:
            errors.append(f"model condition {cid} references unknown runtime_id: {runtime_id}")
        for key in ("provider", "model", "usage_accounting"):
            if not condition.get(key):
                errors.append(f"model condition {cid} missing {key}")
    active_defaults = [condition for condition in conditions if condition.get("status") == "active-default"]
    if len(active_defaults) != 1 or active_defaults[0].get("id") != "codex-openai-gpt-5-6-luna-xhigh" or active_defaults[0].get("model") != "gpt-5.6-luna" or active_defaults[0].get("reasoning_effort") != "xhigh":
        errors.append("the only active default model condition must be codex-openai-gpt-5-6-luna-xhigh")
    return runtime_ids, condition_ids


def validate_evaluations(evaluation_doc: dict, fixture_doc: dict, profile_ids: set[str], runtime_ids: set[str], model_condition_ids: set[str], errors: list[str]) -> None:
    if evaluation_doc.get("schema_version") != 3:
        errors.append("data/evaluations.json must use schema_version 3")
    objectives = set(evaluation_doc.get("primary_objectives", []))
    if objectives != OBJECTIVES:
        errors.append("data/evaluations.json must declare both primary objectives")
    required_model_keys = {"agent.runtime_id", "agent.provider", "agent.model", "agent.model_condition_id"}
    if not required_model_keys.issubset(set(evaluation_doc.get("aggregation_keys", []))):
        errors.append("data/evaluations.json aggregation_keys must include agent runtime/provider/model/model_condition_id")
    evaluations = evaluation_doc.get("evaluations")
    if not isinstance(evaluations, list):
        errors.append("data/evaluations.json must contain an evaluations list")
        return
    fixture_ids = {fixture.get("id") for fixture in fixture_doc.get("fixtures", [])}
    seen: set[str] = set()
    for index, ev in enumerate(evaluations):
        if not isinstance(ev, dict):
            errors.append(f"evaluation record at index {index} must be an object")
            continue
        eid = ev.get("evaluation_id") or ev.get("id")
        if not eid:
            errors.append(f"evaluation record at index {index} missing evaluation_id")
            continue
        if eid in seen:
            errors.append(f"duplicate evaluation id: {eid}")
        seen.add(eid)
        if ev.get("record_type") not in EVALUATION_RECORD_TYPES:
            errors.append(f"evaluation {eid} has invalid record_type: {ev.get('record_type')}")
        if ev.get("objective") not in OBJECTIVES:
            errors.append(f"evaluation {eid} has invalid objective: {ev.get('objective')}")
        if ev.get("evidence_stage") not in {"benchmark_audit", "reproduction"}:
            errors.append(f"evaluation {eid} has invalid evidence_stage: {ev.get('evidence_stage')}")
        if ev.get("status") not in EVALUATION_STATUSES:
            errors.append(f"evaluation {eid} has invalid status: {ev.get('status')}")
        if ev.get("run_role") and ev.get("run_role") not in EVALUATION_RUN_ROLES:
            errors.append(f"evaluation {eid} has invalid run_role: {ev.get('run_role')}")
        target = ev.get("target", {})
        if isinstance(target, dict) and target.get("fixture_id") and target.get("fixture_id") not in fixture_ids:
            errors.append(f"evaluation {eid} references unknown fixture {target.get('fixture_id')}")
        profile = ev.get("profile", {})
        if isinstance(profile, dict) and profile.get("profile_id") and profile.get("profile_id") not in profile_ids:
            errors.append(f"evaluation {eid} references unknown profile {profile.get('profile_id')}")
        agent = ev.get("agent", {})
        if not isinstance(agent, dict):
            errors.append(f"evaluation {eid} must define agent object")
        else:
            runtime_id = agent.get("runtime_id")
            model_condition_id = agent.get("model_condition_id")
            status = ev.get("status")
            is_planned = status == "planned"
            placeholders = ("bind at run start", "record at run start", "exact model id to bind")
            def is_placeholder(value: object) -> bool:
                text = str(value or "").lower()
                return any(marker in text for marker in placeholders)
            if runtime_id and runtime_id not in runtime_ids:
                errors.append(f"evaluation {eid} references unknown agent.runtime_id {runtime_id}")
            if model_condition_id and model_condition_id not in model_condition_ids:
                errors.append(f"evaluation {eid} references unknown agent.model_condition_id {model_condition_id}")
            for key in ("name", "model", "provider"):
                if not agent.get(key):
                    errors.append(f"evaluation {eid} missing agent.{key}")
                elif not is_planned and is_placeholder(agent.get(key)):
                    errors.append(f"evaluation {eid} has unbound agent.{key} after planning stage")
        if ev.get("objective") in OBJECTIVES and ev.get("evidence_stage") == "reproduction":
            if target.get("fixture_scale") not in {"large-project", "medium-project"}:
                errors.append(f"evaluation {eid} reproduction objective must target a large-project or medium-project fixture")



def validate_workflow_task_sequences(sequence_doc: dict, fixture_doc: dict, errors: list[str]) -> set[str]:
    from scripts import run_codex_workflow_evaluation as workflow

    if sequence_doc.get("schema_version") != 1:
        errors.append("data/workflow-task-sequences.json must use schema_version 1")
    sequences = sequence_doc.get("sequences")
    if not isinstance(sequences, list):
        errors.append("data/workflow-task-sequences.json must contain a sequences list")
        return set()
    fixtures = fixture_doc.get("fixtures", [])
    fixture_ids = {fixture.get("id") for fixture in fixtures}
    active_sequences = [
        sequence for sequence in sequences
        if isinstance(sequence, dict) and sequence.get("status") == "active"
    ]
    sequence_by_fixture = {
        sequence.get("fixture_id"): sequence
        for sequence in active_sequences
    }
    for fixture in fixtures:
        sequence = sequence_by_fixture.get(fixture.get("id"))
        if not isinstance(sequence, dict):
            # Retired fixtures may retain immutable evidence but have no current launch authority.
            continue
        generation = str(sequence.get("task_family_generation"))
        generation_label = generation.replace("baseline-v", "Baseline V")
        current_family = fixture.get("current_task_family")
        if not isinstance(current_family, dict) or current_family.get("generation") != generation:
            errors.append(
                f"repository fixture {fixture.get('id')} current_task_family generation must match active sequence generation {generation}"
            )
        sequence = sequence_by_fixture.get(fixture.get("id"))
        treatment_ready, _treatment_reason = (
            workflow.lifecycle_v1_treatment_gate(sequence, ROOT)
            if isinstance(sequence, dict)
            else (False, "missing active sequence")
        )
        if generation == "lifecycle-v1":
            required_blocker = "Lifecycle V1 compile-only provider pilot must complete every task with all affected-component compile verifiers exiting zero before treatment launch."
            completed_status = "completed-passed-compilation"
            completion_label = "compile-passing Lifecycle V1"
        else:
            required_blocker = f"{generation_label} strongest-model provider pilot must complete with all eight required observed categories recorded as strict integer zero before treatment launch."
            completed_status = "completed-passed-zero-incident"
            completion_label = f"zero-incident {generation_label}"
        blockers = fixture.get("blockers", [])
        provider_pilot_status = current_family.get("provider_pilot_status") if isinstance(current_family, dict) else None
        lane_statuses = {
            lane.get("status")
            for lane in fixture.get("future_evaluation_lanes", [])
            if isinstance(lane, dict)
        }
        if treatment_ready:
            if required_blocker in blockers or provider_pilot_status != completed_status:
                errors.append(f"repository fixture {fixture.get('id')} must record its completed {completion_label} pilot")
            if f"blocked-{generation}-pilot" in lane_statuses:
                errors.append(f"repository fixture {fixture.get('id')} treatment lanes must not remain blocked by its completed {generation_label} pilot")
        elif required_blocker not in blockers or provider_pilot_status != "required":
            errors.append(f"repository fixture {fixture.get('id')} must state the complete {generation_label} pilot blocker")
    sequence_ids: set[str] = set()
    for index, sequence in enumerate(sequences):
        if not isinstance(sequence, dict):
            errors.append(f"workflow sequence at index {index} must be an object")
            continue
        sid = sequence.get("id")
        if not sid:
            errors.append(f"workflow sequence at index {index} missing id")
            continue
        if sid in sequence_ids:
            errors.append(f"duplicate workflow sequence id: {sid}")
        sequence_ids.add(sid)
        is_active = sequence.get("status") == "active"
        if not is_active:
            errors.append(f"workflow sequence {sid} must be active Lifecycle V1")
            continue
        if not str(sid).endswith("-lifecycle-sequence-v1"):
            errors.append(f"workflow sequence {sid} must use the lifecycle-sequence-v1 identity")
        if sequence.get("sequence_contract") != "feature-refactor-review":
            errors.append(f"workflow sequence {sid} must use the feature-refactor-review contract")
        if is_active:
            generation = sequence.get("task_family_generation")
            if generation != "lifecycle-v1":
                errors.append(f"active workflow sequence {sid} must bind task_family_generation=lifecycle-v1")
            gate = sequence.get("mistake_gate")
            treatment_ready, _treatment_reason = workflow.lifecycle_v1_treatment_gate(sequence, ROOT)
            if generation == "lifecycle-v1":
                gate_status = "passed-compilation" if treatment_ready else "provider-pilot-required"
                launch_policy = (
                    "eligible for treatment protocol freeze after the first-valid strongest-model pilot completed every task and every affected-component compile verifier exited zero; all other quality findings are diagnostic only"
                    if treatment_ready
                    else "blocked until one first-valid strongest-model pilot completes every task and every affected-component compile verifier exits zero; all other quality findings are diagnostic only"
                )
                expected_gate = {
                    "designated_model_condition": "codex-openai-gpt-5-6-sol-high",
                    "model": "gpt-5.6-sol",
                    "reasoning_effort": "high",
                    "compile_required": True,
                    "quality_diagnostics_gate": False,
                    "pilot_audit_path": "sources/evaluations/audits/lifecycle-v1-corrected-pilot-compile-only.json",
                    "attempt_receipt_path": f"sources/evaluations/audits/lifecycle-v1-corrected-pilot-attempt-{str(sid).split('-lifecycle-sequence-v1')[0]}.json",
                    "pilot_authorization_path": "sources/evaluations/audits/lifecycle-v1-corrected-task-family-readiness-20260813.json",
                    "status": gate_status,
                    "treatment_launch_policy": launch_policy,
                }
                authorization_path = ROOT / expected_gate["pilot_authorization_path"]
                try:
                    authorization = json.loads(authorization_path.read_text())
                    paid_pilot_authorized = authorization.get("paid_pilot_authorized") is True
                    pilot_attempt = (
                        authorization.get("pilot_attempts", {}).get(sid)
                        if isinstance(authorization.get("pilot_attempts"), dict)
                        else None
                    )
                except (OSError, json.JSONDecodeError):
                    paid_pilot_authorized = False
                    pilot_attempt = None
                if treatment_ready:
                    expected_readiness_blockers: list[str] = []
                elif isinstance(pilot_attempt, dict) and pilot_attempt.get("status") == "accepted":
                    expected_readiness_blockers = [
                        "provider-backed strongest-model compile-only Lifecycle V1 pilot executed; treatment audit is pending"
                    ]
                elif isinstance(pilot_attempt, dict) and pilot_attempt.get("status") == "rejected":
                    expected_readiness_blockers = [
                        "provider-backed strongest-model compile-only Lifecycle V1 r0 pilot attempt was rejected; explicit owner reauthorization is required"
                    ]
                else:
                    expected_readiness_blockers = [
                        "provider-backed strongest-model compile-only Lifecycle V1 pilot is authorized but not executed"
                        if paid_pilot_authorized
                        else "provider-backed strongest-model compile-only Lifecycle V1 pilot is not authorized or executed"
                    ]
                if sequence.get("readiness_blockers") != expected_readiness_blockers:
                    errors.append(
                        f"active workflow sequence {sid} readiness blockers must state: {expected_readiness_blockers}"
                    )
                gate_values_match = isinstance(gate, dict) and gate == expected_gate
                if not gate_values_match:
                    errors.append(f"active workflow sequence {sid} must preserve the Lifecycle V1 compile-only gate")
            if isinstance(gate, dict):
                for field in ("pilot_audit_path", "attempt_receipt_path", "pilot_authorization_path"):
                    if field not in gate:
                        continue
                    relative = gate.get(field)
                    if not isinstance(relative, str) or not relative:
                        errors.append(f"active workflow sequence {sid} {field} must be a non-empty repository-relative path")
                        continue
                    try:
                        workflow.repository_authority_path(ROOT, relative, field)
                    except ValueError:
                        errors.append(f"active workflow sequence {sid} {field} escapes the repository authority root")
            required_lockfiles = {
                "medium-fastify-fastify": {"package.json": "b273320af1bb4cfc0f9334457c8e3b1d035fde0da14f9db65e8ef97d361d0be3"},
                "medium-beetbox-beets": {"uv.lock": "fbf1d7a9c84b658a2433035221ba18c57508c254d711a06f305e2f610839a45f"},
                "large-hashicorp-terraform": {"go.sum": "be9ec949db0a0b135197f2c78b6d9821d764cc9b8c362b4860e3d5a1e9c74b9e"},
            }
            observed_lockfiles = {
                str(item.get("path")): str(item.get("sha256"))
                for item in sequence.get("initial_snapshot", {}).get("dependency_lockfiles", [])
                if isinstance(item, dict)
            }
            if observed_lockfiles != required_lockfiles.get(str(sequence.get("fixture_id")), {}):
                errors.append(f"active workflow sequence {sid} must bind its exact {generation} dependency lock inputs")
            if sequence.get("fixture_id") == "medium-beetbox-beets":
                setup_text = (ROOT / "sources/evaluations/fixtures/medium/beetbox-beets/setup.sh").read_text()
                if "uv sync --group test --frozen" not in setup_text:
                    errors.append(f"Beets {generation} setup must enforce uv.lock with --frozen")
            if isinstance(gate, dict):
                receipt_rel = gate.get("attempt_receipt_path")
                receipt_path = ROOT / str(receipt_rel)
                if receipt_path.exists():
                    try:
                        receipt = json.loads(receipt_path.read_text())
                    except (OSError, json.JSONDecodeError) as exc:
                        errors.append(f"active workflow sequence {sid} pilot attempt receipt is unreadable: {exc}")
                    else:
                        expected_receipt_identity = {
                            "schema_version": 1,
                            "task_family_generation": generation,
                            "sequence_id": sid,
                            "replicate_index": 0,
                            "profile_id": "baseline-bare-codex",
                            "model_condition_id": expected_gate["designated_model_condition"],
                            "model": expected_gate["model"],
                            "reasoning_effort": expected_gate["reasoning_effort"],
                            "immutable_identity_receipt": True,
                        }
                        if any(receipt.get(key) != value for key, value in expected_receipt_identity.items()):
                            errors.append(f"active workflow sequence {sid} pilot attempt receipt identity is invalid")
            reset_policy = str(sequence.get("reset_policy", ""))
            seed_policy = str(sequence.get("seed_patch_policy", ""))
            if "controller-only affected-component compile command" not in reset_policy or "not disclosed" not in reset_policy:
                errors.append(f"active workflow sequence {sid} reset policy must bind undisclosed controller-only compilation assessment")
            if "Model-facing prompts describe the software objective" not in seed_policy or "not disclosed" not in seed_policy:
                errors.append(f"active workflow sequence {sid} seed policy must keep controller scoring out of the agent task")
        qualification_path = str(sequence.get("qualification_path", ""))
        qualification_name = Path(qualification_path).name
        expected_qualification_name = "qualification-lifecycle-v1-20260813.json"
        if qualification_name != expected_qualification_name:
            errors.append(f"active workflow sequence {sid} must bind {expected_qualification_name}")
        if sequence.get("status") == "active":
            expected_design = "compile-only"
            if sequence.get("acceptance_design") != expected_design:
                errors.append(f"active workflow sequence {sid} must declare acceptance_design={expected_design}")
            if expected_design == "compile-only" and sequence.get("acceptance_policy") != {
                "gate": "affected-component-compilation",
                "visibility": "controller-only",
                "quality_diagnostics_gate": False,
                "tests_required": False,
                "source_review_required": False,
            }:
                errors.append(f"active workflow sequence {sid} must declare the exact compile-only acceptance policy")
            if expected_design == "compile-only" and (
                not isinstance(sequence.get("project_compile_command"), str)
                or not sequence.get("project_compile_command")
            ):
                errors.append(f"active workflow sequence {sid} must bind a nonempty project-wide compile command")
        if sequence.get("status") == "active" and sequence.get("scope") != "production-primary":
            errors.append(f"active workflow sequence {sid} must declare scope=production-primary")
        if sequence.get("status") == "active":
            freeze_date = sequence.get("protocol_freeze_date")
            qualification_date = sequence.get("qualification_date")
            if (
                not isinstance(freeze_date, str)
                or not isinstance(qualification_date, str)
                or freeze_date < qualification_date
            ):
                errors.append(
                    f"active workflow sequence {sid} protocol freeze date must be explicit and not predate qualification"
                )
        fixture_id = sequence.get("fixture_id")
        if fixture_id not in fixture_ids:
            errors.append(f"workflow sequence {sid} references unknown fixture {fixture_id}")
        if sequence.get("objective") not in OBJECTIVES:
            errors.append(f"workflow sequence {sid} has invalid objective: {sequence.get('objective')}")
        if "cumulative provider-reported" not in str(sequence.get("primary_metric", "")):
            errors.append(f"workflow sequence {sid} primary_metric must name cumulative provider-reported tokens")
        tasks = sequence.get("tasks")
        if not isinstance(tasks, list) or not tasks:
            errors.append(f"workflow sequence {sid} must define a non-empty tasks list")
            continue
        orders = []
        task_ids: set[str] = set()
        production_by_task: dict[str, list[str]] = {}
        for task in tasks:
            if not isinstance(task, dict):
                errors.append(f"workflow sequence {sid} contains non-object task")
                continue
            tid = task.get("id")
            if not tid:
                errors.append(f"workflow sequence {sid} has task missing id")
            elif tid in task_ids:
                errors.append(f"workflow sequence {sid} has duplicate task id {tid}")
            else:
                task_ids.add(tid)
            expected_task_suffix = "-v1" if is_active else "-v0"
            if not str(tid or "").endswith(expected_task_suffix):
                errors.append(f"workflow sequence {sid} task {tid} must use a {expected_task_suffix.removeprefix('-')} identity")
            order = task.get("order")
            if not isinstance(order, int) or order < 1:
                errors.append(f"workflow sequence {sid} task {tid} has invalid order {order}")
            else:
                orders.append(order)
            prompt_path = task.get("prompt_path")
            if prompt_path and not (ROOT / prompt_path).exists():
                errors.append(f"workflow sequence {sid} task {tid} prompt_path does not exist: {prompt_path}")
            verifier_command = task.get("verifier_command")
            if not verifier_command:
                errors.append(f"workflow sequence {sid} task {tid} missing verifier_command")
            elif sequence.get("status") == "active":
                verifier_path = ROOT / verifier_command
                if verifier_path.exists():
                    task_dir = (ROOT / prompt_path).parent
                    missing = sorted(name for name in TASK_ASSETS if not (task_dir / name).is_file())
                    if missing:
                        errors.append(f"active workflow sequence {sid} task {tid} missing assets: {', '.join(missing)}")
                    production = [path for path in patch_paths(task_dir / "seed-regression.patch") if is_production_path(path)] if (task_dir / "seed-regression.patch").is_file() else []
                    production_by_task[str(tid)] = production
                    if not production:
                        errors.append(f"active workflow sequence {sid} task {tid} seed patch has no production/type files")
                    prompt_text = (ROOT / prompt_path).read_text() if prompt_path else ""
                    generation = str(sequence.get("task_family_generation", ""))
                    generation_path = f"/{generation}/"
                    target_production = [
                        path
                        for path in production
                        if not path.endswith(("_test.go", "_test.py", ".test.js")) and not path.startswith("test/")
                    ]
                    expected_changed = task.get("expected_changed_paths")
                    anchors = task.get("model_visible_validation_anchors")
                    acceptance_asset_paths = task.get("model_visible_acceptance_asset_paths")
                    verifier_text = verifier_path.read_text() if verifier_path.is_file() else ""
                    if generation == "lifecycle-v1":
                        required_markers = (
                            "Implement the task completely and correctly.",
                            "Search and inspect the repository as needed",
                            "run relevant existing tests and checks when practical",
                        )
                        forbidden_markers = (
                            "compile-only",
                            "only acceptance gate",
                            "sole pass/fail gate",
                            "diagnostics only",
                            "do not determine pass/fail",
                            "stop when the command exits 0",
                            "Do not discover or redesign anything.",
                            "Copy and run this command exactly:",
                            "Do not inspect, search",
                            "p.write_text(",
                        )
                        compile_command = task.get("compile_command")
                        if (
                            generation_path not in str(prompt_path)
                            or any(marker not in prompt_text for marker in required_markers)
                            or any(marker.lower() in prompt_text.lower() for marker in forbidden_markers)
                            or (isinstance(compile_command, str) and compile_command in prompt_text)
                        ):
                            errors.append(f"active workflow sequence {sid} task {tid} must use the complete Lifecycle V1 software-objective prompt contract without controller scoring policy")
                        if not isinstance(expected_changed, list) or sorted(expected_changed) != sorted(target_production) or not 1 <= len(target_production) <= 2:
                            errors.append(f"active workflow sequence {sid} task {tid} must declare one-to-two exact Lifecycle V1 semantic production targets")
                        if (
                            not isinstance(compile_command, str)
                            or not compile_command
                            or compile_command not in verifier_text
                            or anchors != []
                        ):
                            errors.append(f"active workflow sequence {sid} task {tid} must bind one controller-only affected-component compile command")
                        if task.get("acceptance_visibility") != "controller-only-compile-policy":
                            errors.append(f"active workflow sequence {sid} task {tid} must declare controller-only compile policy visibility")
                        if acceptance_asset_paths != []:
                            errors.append(f"active workflow sequence {sid} task {tid} compile-only controller assessment must not inject test assets")
                    undisclosed_inline_markers = ("<<'NODE'", '<<"NODE"', "<<'PY'", '<<"PY"', "<<'TS'", '<<"TS"', "workflow-hidden")
                    if any(marker in verifier_text and marker not in prompt_text for marker in undisclosed_inline_markers):
                        errors.append(f"active workflow sequence {sid} task {tid} contains undisclosed inline verifier assertions")
                    if task.get("model_concealed_paths"):
                        errors.append(f"active workflow sequence {sid} task {tid} must not hide active validation behavior")
                    if verifier_uses_source_identity(task_dir):
                        errors.append(f"active workflow sequence {sid} task {tid} uses exact-source supplemental guards instead of acceptance")
                    review_patch_name = task.get("review_patch_path")
                    if task.get("task_class") == "code-review-correction":
                        review_patch = task_dir / str(review_patch_name or "")
                        if not review_patch_name or not review_patch.is_file() or "diff --git" not in review_patch.read_text():
                            errors.append(f"active workflow sequence {sid} task {tid} must provide a non-empty proposed review patch")
                    elif review_patch_name:
                        errors.append(f"active workflow sequence {sid} non-review task {tid} must not disclose a review patch")
        if orders and sorted(orders) != list(range(1, len(orders) + 1)):
            errors.append(f"workflow sequence {sid} task orders must be contiguous starting at 1")
        task_classes = [
            task.get("task_class", "")
            for task in sorted(tasks, key=lambda item: item.get("order", 0))
        ]
        if sequence.get("sequence_contract") == "feature-refactor-review" and task_classes != [
            "feature-implementation",
            "behavior-preserving-refactor",
            "code-review-correction",
        ]:
            errors.append(
                f"workflow sequence {sid} feature-refactor-review contract must order feature implementation, behavior-preserving refactor, and code review/correction"
            )
        if sequence.get("status") == "active" and len(production_by_task) == len(tasks):
            validate_qualification(sequence, errors)
    active = [sequence for sequence in sequences if sequence.get("status") == "active"]
    expected_active_ids = ["fastify-lifecycle-sequence-v1", "beets-lifecycle-sequence-v1"]
    if [sequence.get("id") for sequence in active] != expected_active_ids:
        errors.append(
            "production lifecycle-v1 portfolio must contain exactly the two active sequences "
            f"{expected_active_ids}, found {[sequence.get('id') for sequence in active]}"
        )
    if len({sequence.get("fixture_id") for sequence in active}) != len(active):
        errors.append("each lifecycle v1 sequence must own a distinct fixture")
    forbidden_contract_phrases = (
        "one task at a time",
        "alternative-repair",
        "ordered transitions",
    )
    for sequence in active:
        seed_policy = str(sequence.get("seed_patch_policy", "")).lower()
        if sequence.get("task_family_generation") == "lifecycle-v1":
            if (
                "applied as one composite start before task 1" not in seed_policy
                or "final controller verification runs once after the final prompt" not in seed_policy
            ):
                errors.append(f"active workflow sequence {sequence.get('id')} must declare semantic pre-seeding and final-only controller verification")
        elif "composite broken start" not in seed_policy or "final prompt" not in seed_policy:
            errors.append(f"active workflow sequence {sequence.get('id')} must declare composite pre-seeding and final-only verification")
        if any(phrase in seed_policy for phrase in forbidden_contract_phrases):
            errors.append(f"active workflow sequence {sequence.get('id')} describes a non-v0 seed-delivery contract")
    for surface in ("README.md", "docs/research/roadmap.md"):
        text = (ROOT / surface).read_text().lower()
        if any(phrase in text for phrase in forbidden_contract_phrases):
            errors.append(f"{surface} describes non-v0 seed-delivery gates")
    return sequence_ids


def validate_fixture_sequence_status_consistency(
    workflow_doc: dict,
    fixtures_doc: dict,
    large_candidates_doc: dict,
    medium_candidates_doc: dict,
    errors: list[str],
) -> None:
    sequences = {
        sequence.get("id"): sequence
        for sequence in workflow_doc.get("sequences", [])
        if sequence.get("id")
    }
    statuses = {sequence_id: sequence.get("status") for sequence_id, sequence in sequences.items()}
    for label, candidate_doc in (
        ("large candidate", large_candidates_doc),
        ("medium candidate", medium_candidates_doc),
    ):
        records = candidate_doc.get("candidates", [])
        expected_count = sum(record.get("qualification_status") == "active-reproduction-flow" for record in records)
        policy = candidate_doc.get("selection_policy", {})
        if policy.get("active_fixture_count") != expected_count:
            errors.append(f"{label} selection policy active_fixture_count must equal {expected_count}")
        target_matrix = str(policy.get("target_matrix", "")).lower()
        active_names = {
            str(record.get("github", "")).rsplit("/", 1)[-1].lower()
            for record in records
            if record.get("qualification_status") == "active-reproduction-flow"
        }
        if any(name and name not in target_matrix for name in active_names) or any(
            phrase in target_matrix for phrase in ("retired", "no active", "zero active")
        ):
            errors.append(f"{label} selection policy target_matrix must name every active fixture without retired-state prose")
    surfaces = [
        ("fixture", fixtures_doc.get("fixtures", [])),
        ("large candidate", large_candidates_doc.get("candidates", [])),
        ("medium candidate", medium_candidates_doc.get("candidates", [])),
    ]
    for label, records in surfaces:
        for record in records:
            sequence_id = record.get("workflow_sequence_id")
            if not sequence_id:
                continue
            if sequence_id not in statuses:
                errors.append(f"{label} {record.get('id')} references unknown workflow sequence {sequence_id}")
                continue
            active = statuses[sequence_id] == "active"
            qualification = record.get("qualification_status")
            if active and qualification != "active-reproduction-flow":
                errors.append(f"{label} {record.get('id')} must be active-reproduction-flow when sequence {sequence_id} is active")
            if active and record.get("qualification_evidence") != sequences[sequence_id].get("qualification_path"):
                errors.append(
                    f"{label} {record.get('id')} must reference the active qualification for {sequence_id}"
                )
            if active and label == "fixture":
                qualification_path = Path(str(sequences[sequence_id].get("qualification_path", "")))
                fixture_root = ROOT / qualification_path.parent
                fixture_readme = fixture_root / "README.md"
                tasks_readme = fixture_root / "tasks/README.md"
                try:
                    fixture_text = fixture_readme.read_text()
                    tasks_text = tasks_readme.read_text()
                except OSError as exc:
                    errors.append(f"fixture {record.get('id')} active-generation documentation is unreadable: {exc}")
                else:
                    generation = str(sequences[sequence_id].get("task_family_generation", ""))
                    generation_label = "Lifecycle V1" if generation == "lifecycle-v1" else generation.replace("baseline-v", "Baseline V")
                    if qualification_path.name not in fixture_text or generation not in fixture_text:
                        errors.append(f"fixture {record.get('id')} README does not identify the active {generation_label} qualification")
                    if f"active {generation_label}" not in tasks_text:
                        errors.append(f"fixture {record.get('id')} tasks README does not identify the active {generation_label} generation")
            if not active and qualification == "active-reproduction-flow":
                errors.append(f"{label} {record.get('id')} cannot be active-reproduction-flow while sequence {sequence_id} is {statuses[sequence_id]}")
            if not active and record.get("active_profiles"):
                errors.append(f"{label} {record.get('id')} cannot list active_profiles while sequence {sequence_id} is {statuses[sequence_id]}")


def canonical_json_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_required_object(parent: dict, key: str, sid: str, errors: list[str]) -> dict | None:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"workflow session {sid} structured record must include object {key}")
        return None
    return value


def validate_invalid_fixture_disposition(
    session: dict,
    sid: str,
    errors: list[str],
) -> None:
    interpretation = session.get("interpretation", {})
    if not isinstance(interpretation, dict):
        return
    if interpretation.get("evaluation_validity") != "invalid-fixture":
        return
    if session.get("status") != "excluded":
        errors.append(f"workflow session {sid} invalid fixture evidence must be excluded")
    if interpretation.get("accepted_for_execution") is not False:
        errors.append(f"workflow session {sid} invalid fixture evidence cannot be execution-accepted")
    if interpretation.get("accepted_for_objective") is not False:
        errors.append(f"workflow session {sid} invalid fixture evidence cannot be objective-accepted")
    if interpretation.get("primary_objective_hard_baseline") is not False:
        errors.append(f"workflow session {sid} invalid fixture evidence cannot be a hard baseline")
    if interpretation.get("usable_for_primary_objective_token_comparison") is not False:
        errors.append(f"workflow session {sid} invalid fixture evidence cannot be used for token comparison")
    reasons = interpretation.get("invalidity_reasons")
    if not isinstance(reasons, list) or not reasons or any(not isinstance(reason, str) or not reason for reason in reasons):
        errors.append(f"workflow session {sid} invalid fixture evidence must record invalidity reasons")


def validate_invalid_accounting_disposition(
    session: dict,
    sid: str,
    errors: list[str],
) -> None:
    interpretation = session.get("interpretation", {})
    if not isinstance(interpretation, dict):
        return
    if interpretation.get("evaluation_validity") != "invalid-accounting":
        return
    if session.get("status") != "excluded":
        errors.append(f"workflow session {sid} invalid accounting evidence must be excluded")
    if interpretation.get("accepted_for_execution") is not True:
        errors.append(f"workflow session {sid} invalid accounting evidence must preserve execution acceptance")
    for key in (
        "accepted_for_objective",
        "primary_objective_hard_baseline",
        "usable_for_primary_objective_token_comparison",
        "operationally_completed",
    ):
        if interpretation.get(key) is not False:
            errors.append(f"workflow session {sid} invalid accounting evidence cannot be used as objective evidence")
    if interpretation.get("comparison_baseline_session_id"):
        errors.append(f"workflow session {sid} invalid accounting evidence cannot retain an active comparison baseline")
    reasons = interpretation.get("invalidity_reasons")
    if not isinstance(reasons, list) or not reasons or any(not isinstance(reason, str) or not reason for reason in reasons):
        errors.append(f"workflow session {sid} invalid accounting evidence must record invalidity reasons")



def validate_invalid_treatment_disposition(
    session: dict,
    sid: str,
    errors: list[str],
) -> None:
    interpretation = session.get("interpretation", {})
    if not isinstance(interpretation, dict):
        return
    validity = interpretation.get("evaluation_validity")
    if validity not in {"invalid-treatment-configuration", "unverified-treatment-assignment"}:
        return
    label = "invalid treatment configuration" if validity == "invalid-treatment-configuration" else "unverified treatment assignment"
    if session.get("status") != "excluded":
        errors.append(f"workflow session {sid} {label} must be excluded")
    if interpretation.get("accepted_for_execution") is not True:
        errors.append(f"workflow session {sid} completed ineligible treatment evidence must preserve execution acceptance")
    if interpretation.get("accepted_for_objective") is not False:
        errors.append(f"workflow session {sid} {label} cannot be objective-accepted")
    if interpretation.get("primary_objective_hard_baseline") is not False:
        errors.append(f"workflow session {sid} {label} cannot be a hard baseline")
    if interpretation.get("usable_for_primary_objective_token_comparison") is not False:
        errors.append(f"workflow session {sid} {label} cannot be used for token comparison")
    if interpretation.get("comparison_baseline_session_id"):
        errors.append(f"workflow session {sid} {label} cannot retain an active comparison baseline")
    reasons = interpretation.get("invalidity_reasons")
    if not isinstance(reasons, list) or not reasons or any(not isinstance(reason, str) or not reason for reason in reasons):
        errors.append(f"workflow session {sid} {label} must record invalidity reasons")


def validate_structured_session_schema(
    session: dict, sid: str, errors: list[str], *, schema_checked: bool = False
) -> None:
    """Gate record shape on the published schema, then add the constraints it cannot express.

    `schema_checked` lets the registry pass skip a re-validation it already performed; the
    default keeps direct callers fully gated.
    """
    if not schema_checked:
        validate_session_schema_conformance(session, sid, errors)
    # The published schema requires these only under its schema_version 2 branch, and never
    # requires baseline_pool. Structured production records require all of them outright.
    for key in (
        "frozen_protocol",
        "baseline_pool",
        "selected_execution",
        "docker_image_identity",
        "tool_adapter_identity",
    ):
        if key not in session:
            errors.append(f"workflow session {sid} structured record missing schema field {key}")
    # JSON Schema numeric equality accepts 1.0 for `enum: [1, 2]` and for `type: integer`.
    # Provider accounting keys off exact integers, so these two stay hand-checked.
    if type(session.get("schema_version")) is not int or session.get("schema_version") not in {1, 2}:
        errors.append(f"workflow session {sid} schema_version must be 1 or 2")
    if type(session.get("replicate_index")) is not int or session.get("replicate_index", -1) < 0:
        errors.append(f"workflow session {sid} replicate_index must be a non-negative integer")
    validate_invalid_fixture_disposition(session, sid, errors)
    validate_invalid_accounting_disposition(session, sid, errors)
    validate_invalid_treatment_disposition(session, sid, errors)
    if requires_structured_task_contract(session):
        validate_structured_task_outcomes(session, sid, errors)


def validate_docker_identity(identity: object, expected: object, sid: str, errors: list[str]) -> None:
    if not isinstance(identity, dict):
        errors.append(f"workflow session {sid} structured record must include Docker image immutable identity")
        return
    if not isinstance(identity.get("image_ref"), str) or not identity.get("image_ref"):
        errors.append(f"workflow session {sid} Docker image identity must include image_ref")
    if not isinstance(identity.get("image_id"), str) or not DOCKER_IMAGE_ID_RE.fullmatch(identity["image_id"]):
        errors.append(f"workflow session {sid} Docker image identity must be sha256:<64 lowercase hex>")
    repo_digests = identity.get("repo_digests")
    if not isinstance(repo_digests, list) or any(not isinstance(value, str) or not REPO_DIGEST_RE.fullmatch(value) for value in repo_digests):
        errors.append(f"workflow session {sid} Docker repo_digests must use repo@sha256:<64 lowercase hex>")
    if "repo_tags" in identity and (not isinstance(identity["repo_tags"], list) or any(not isinstance(value, str) for value in identity["repo_tags"])):
        errors.append(f"workflow session {sid} Docker repo_tags must be strings")
    if identity != expected:
        errors.append(f"workflow session {sid} Docker image identity does not match selected_execution descriptor")


def validate_tool_adapter_identity(identity: object, expected: object, profile_id: str | None, sid: str, errors: list[str]) -> None:
    if profile_id in {"baseline-bare-codex", "baseline-claude-code-no-mcp"}:
        if identity is not None:
            errors.append(f"workflow session {sid} baseline structured record must not publish a treatment tool identity")
        return
    if not isinstance(identity, dict):
        errors.append(f"workflow session {sid} treatment structured record must include tool adapter identity")
        return
    binary = identity.get("binary_identity")
    if not isinstance(binary, dict):
        errors.append(f"workflow session {sid} treatment structured record must include tool adapter binary identity")
    elif binary.get("kind") == "generated-by-host-integration":
        if not isinstance(binary.get("command_template"), str) or not binary["command_template"]:
            errors.append(f"workflow session {sid} generated treatment identity missing command_template")
        if not isinstance(binary.get("install_commands"), list) or not binary["install_commands"]:
            errors.append(f"workflow session {sid} generated treatment identity missing install_commands")
        install_hash = binary.get("install_contract_sha256")
        if not isinstance(install_hash, str) or not SHA256_RE.fullmatch(install_hash):
            errors.append(
                f"workflow session {sid} generated treatment identity install_contract_sha256 must be 64 lowercase hex"
            )
    else:
        for key in ("executable_token", "resolved_path", "realpath"):
            if not isinstance(binary.get(key), str) or not binary.get(key):
                errors.append(f"workflow session {sid} treatment executable identity missing {key}")
        if not isinstance(binary.get("sha256"), str) or not SHA256_RE.fullmatch(binary["sha256"]):
            errors.append(f"workflow session {sid} treatment executable identity sha256 must be 64 lowercase hex")
        metadata = binary.get("metadata")
        if not isinstance(metadata, dict) or not isinstance(metadata.get("size"), int) or not isinstance(metadata.get("mode"), str):
            errors.append(f"workflow session {sid} treatment executable identity metadata has invalid shape")
        version = binary.get("version")
        if not isinstance(version, dict) or not isinstance(version.get("captured"), bool) or not isinstance(version.get("command"), list):
            errors.append(f"workflow session {sid} treatment executable identity version has invalid shape")
    if identity != expected:
        errors.append(f"workflow session {sid} treatment tool identity does not match selected_execution descriptor")


def validate_structured_session_identity(
    session: dict, run_record: dict | None, sid: str, errors: list[str], *, schema_checked: bool = False
) -> None:
    validate_structured_session_schema(session, sid, errors, schema_checked=schema_checked)
    frozen_protocol = validate_required_object(session, "frozen_protocol", sid, errors)
    baseline_pool = validate_required_object(session, "baseline_pool", sid, errors)
    selected = validate_required_object(session, "selected_execution", sid, errors)
    if frozen_protocol is None or baseline_pool is None or selected is None:
        return

    protocol_id = frozen_protocol.get("protocol_id")
    protocol_rel = frozen_protocol.get("path")
    recorded_protocol_hash = frozen_protocol.get("sha256")
    if not isinstance(protocol_id, str) or not protocol_id:
        errors.append(f"workflow session {sid} frozen_protocol protocol_id must be a non-empty string")
    if not isinstance(protocol_rel, str) or not protocol_rel:
        errors.append(f"workflow session {sid} frozen_protocol missing path")
        protocol_path = None
    else:
        protocol_path = ROOT / protocol_rel
        if Path(protocol_rel).is_absolute() or ".." in Path(protocol_rel).parts:
            errors.append(f"workflow session {sid} frozen_protocol path must be repository-relative")
        elif not protocol_path.is_file():
            errors.append(f"workflow session {sid} frozen protocol file does not exist: {protocol_rel}")
    if not isinstance(recorded_protocol_hash, str) or not SHA256_RE.fullmatch(recorded_protocol_hash):
        errors.append(f"workflow session {sid} frozen_protocol sha256 must be 64 lowercase hex")

    protocol = None
    if protocol_path is not None and protocol_path.is_file():
        protocol_bytes = protocol_path.read_bytes()
        actual_protocol_hash = hashlib.sha256(protocol_bytes).hexdigest()
        if recorded_protocol_hash != actual_protocol_hash:
            errors.append(f"workflow session {sid} frozen protocol sha256 does not match file bytes")
        try:
            protocol = json.loads(protocol_bytes)
        except Exception as exc:
            errors.append(f"workflow session {sid} frozen protocol cannot be parsed: {exc}")

    descriptor = selected.get("descriptor")
    descriptor_hash = selected.get("descriptor_sha256")
    if not isinstance(descriptor, dict):
        errors.append(f"workflow session {sid} structured record must include selected_execution descriptor")
        descriptor = {}
    if not isinstance(descriptor_hash, str) or not SHA256_RE.fullmatch(descriptor_hash):
        errors.append(f"workflow session {sid} selected_execution descriptor_sha256 must be 64 lowercase hex")
    elif descriptor_hash != canonical_json_hash(descriptor):
        errors.append(f"workflow session {sid} selected_execution descriptor_sha256 does not match canonical descriptor bytes")

    if protocol is not None:
        protocol_is_v3 = protocol.get("protocol_schema_version") == 3 or str(protocol_id).endswith("-v3")
        if not protocol_is_v3:
            errors.append(f"workflow session {sid} frozen protocol must declare protocol_schema_version=3")
        if protocol.get("protocol_id") != protocol_id:
            errors.append(f"workflow session {sid} frozen protocol ID does not match recorded value")
        protocol_baseline = protocol.get("baseline_pool", {})
        protocol_selected = protocol.get("selected_execution", {})
        if baseline_pool.get("protocol_version") != protocol_baseline.get("protocol_version"):
            errors.append(f"workflow session {sid} baseline pool protocol_version does not match frozen protocol")
        if baseline_pool.get("protocol_fingerprint") != protocol_baseline.get("protocol_fingerprint"):
            errors.append(f"workflow session {sid} baseline pool fingerprint does not match frozen protocol")
        if protocol_selected != selected:
            errors.append(f"workflow session {sid} selected_execution does not match frozen protocol")

    if baseline_pool.get("identity_policy") != "frozen-protocol-and-replicate; execution date is metadata only":
        errors.append(f"workflow session {sid} baseline pool identity_policy is invalid")
    if not isinstance(baseline_pool.get("protocol_fingerprint"), str) or not re.fullmatch(r"[a-f0-9]{12}", baseline_pool.get("protocol_fingerprint", "")):
        errors.append(f"workflow session {sid} baseline pool protocol_fingerprint must be 12 lowercase hex")

    runtime = descriptor.get("runtime", {}) if isinstance(descriptor, dict) else {}
    validate_docker_identity(session.get("docker_image_identity"), runtime.get("docker_image_identity"), sid, errors)
    profile_id = session.get("profile", {}).get("profile_id") if isinstance(session.get("profile"), dict) else None
    validate_tool_adapter_identity(session.get("tool_adapter_identity"), descriptor.get("tool_adapter"), profile_id, sid, errors)

    if run_record is not None and not compact_run_record_matches_session(
        session,
        run_record,
        current_contract=current_provider_usage_contract(session),
        require_accepted=False,
    ):
        errors.append(f"workflow session {sid} run.json does not exactly match registry session")


def requires_structured_task_contract(session: dict) -> bool:
    return type(session.get("schema_version")) is int and session.get("schema_version") == 2


def validate_structured_task_outcomes(session: dict, sid: str, errors: list[str]) -> None:
    task_sequence = session.get("task_sequence")
    expected_ids = task_sequence.get("task_ids") if isinstance(task_sequence, dict) else None
    results = session.get("per_task_results")
    quality = session.get("software_quality")
    if (
        not isinstance(expected_ids, list)
        or not expected_ids
        or any(not isinstance(task_id, str) or not task_id for task_id in expected_ids)
        or len(set(expected_ids)) != len(expected_ids)
        or not isinstance(results, list)
    ):
        errors.append(f"workflow session {sid} structured task contract requires exact task coverage")
        return
    if not isinstance(quality, dict):
        errors.append(f"workflow session {sid} structured task contract requires software_quality totals")
        return
    usage = session.get("cumulative_token_usage")
    if not isinstance(usage, dict) or not isinstance(usage.get("accounting_basis"), str) or not usage.get("accounting_basis"):
        errors.append(f"workflow session {sid} schema-v2 token usage requires accounting_basis")
    elif any(key in usage for key in ("estimated_cost_usd", "pricing_basis")):
        errors.append(f"workflow session {sid} schema-v2 token usage must not contain monetary fields")
    integrity = session.get("execution_integrity")
    integrity_fields = {
        "verifier_integrity_passed",
        "tool_isolation_audit_passed",
        "external_retrieval_hits",
        "pass_through_tool_command_hits",
    }
    if not isinstance(integrity, dict) or not integrity_fields.issubset(integrity):
        errors.append(f"workflow session {sid} schema-v2 record requires complete execution_integrity evidence")
    elif not isinstance(integrity["external_retrieval_hits"], list) or not isinstance(
        integrity["pass_through_tool_command_hits"], list
    ):
        errors.append(f"workflow session {sid} execution_integrity hit fields must be arrays")

    required_fields = {
        "task_id",
        "task_alias",
        "order",
        "agent_attempted",
        "codex_exit_code",
        "controller_verification",
        "verifier_exit_code",
        "verifier_passed",
        "accepted",
        "operational_retry_count",
    }
    coverage = [item.get("task_id") if isinstance(item, dict) else None for item in results]
    orders = [item.get("order") if isinstance(item, dict) else None for item in results]
    if coverage != expected_ids or orders != list(range(1, len(expected_ids) + 1)):
        errors.append(f"workflow session {sid} structured task results do not provide exact task coverage")

    attempted = 0
    passed = 0
    all_verifiers_passed = len(results) == len(expected_ids)
    for index, item in enumerate(results, start=1):
        label = f"workflow session {sid} structured task result {index}"
        if not isinstance(item, dict) or not required_fields.issubset(item):
            errors.append(f"{label} is missing required structured fields for exact task coverage")
            all_verifiers_passed = False
            continue
        if not isinstance(item["task_alias"], str) or not item["task_alias"]:
            errors.append(f"{label} task_alias must be a non-empty string")
        agent_attempted = item["agent_attempted"]
        codex_exit = item["codex_exit_code"]
        if not isinstance(agent_attempted, bool):
            errors.append(f"{label} agent_attempted must be boolean")
        elif agent_attempted:
            attempted += 1
            if not isinstance(codex_exit, int) or isinstance(codex_exit, bool):
                errors.append(f"{label} attempted task requires an integer codex_exit_code")
        elif codex_exit is not None:
            errors.append(f"{label} unattempted task requires null codex_exit_code")
        retries = item["operational_retry_count"]
        if not isinstance(retries, int) or isinstance(retries, bool) or retries < 0:
            errors.append(f"{label} operational_retry_count must be a non-negative integer")

        controller = item["controller_verification"]
        verifier_exit = item["verifier_exit_code"]
        verifier_passed = item["verifier_passed"]
        accepted = item["accepted"]
        if controller == "passed":
            consistent = verifier_exit == 0 and verifier_passed is True and accepted is True
        elif controller == "failed":
            consistent = (
                isinstance(verifier_exit, int)
                and not isinstance(verifier_exit, bool)
                and verifier_exit != 0
                and verifier_passed is False
                and accepted is False
            )
        elif controller == "not-run":
            consistent = verifier_exit is None and verifier_passed is None and accepted is None
        else:
            consistent = False
        if not consistent:
            errors.append(f"{label} verifier outcome fields are inconsistent")
        if accepted is True:
            passed += 1
        if verifier_passed is not True:
            all_verifiers_passed = False

    if quality.get("tasks_attempted") != attempted:
        errors.append(f"workflow session {sid} software_quality.tasks_attempted does not match structured outcomes")
    if quality.get("tasks_passed") != passed:
        errors.append(f"workflow session {sid} software_quality.tasks_passed does not match structured accepted outcomes")
    if quality.get("final_verifier_passed") is not all_verifiers_passed:
        errors.append(f"workflow session {sid} software_quality.final_verifier_passed does not match structured outcomes")
    functional = all_verifiers_passed and passed == len(expected_ids)
    if quality.get("functional_verifier_passed") is not functional:
        errors.append(f"workflow session {sid} software_quality.functional_verifier_passed does not match structured outcomes")


def validate_workflow_session_contract(
    session: dict, canonical_profile: dict | None, errors: list[str], *, schema_checked: bool = False
) -> None:
    sid = session.get("session_id") or session.get("id") or "<unknown>"
    sequence = session.get("task_sequence", {})
    frozen_protocol = session.get("frozen_protocol")
    structured_session = requires_structured_task_contract(session) or (
        isinstance(frozen_protocol, dict)
        and str(frozen_protocol.get("protocol_id", "")).endswith("-v3")
    )
    if structured_session:
        validate_structured_session_identity(session, None, sid, errors, schema_checked=schema_checked)
    if session.get("status") == "completed" and session.get("evidence_type") == "workflow-simulation" and session.get("evidence_stage") == "reproduction":
        prompt_delivery = sequence.get("prompt_delivery") if isinstance(sequence, dict) else None
        if not isinstance(prompt_delivery, dict):
            errors.append(f"workflow session {sid} must record task_sequence.prompt_delivery for completed workflow reproduction")
        else:
            if prompt_delivery.get("mode") != "sequential-one-task-at-a-time":
                errors.append(f"workflow session {sid} must use sequential-one-task-at-a-time prompt delivery")
            if prompt_delivery.get("future_tasks_visible") is not False:
                errors.append(f"workflow session {sid} must hide future tasks during workflow reproduction")
            if prompt_delivery.get("future_prompts_materialized_lazily") is not True:
                errors.append(f"workflow session {sid} future prompts must be materialized lazily")
            composite_seed_delivery = (
                prompt_delivery.get("seed_delivery_mode") == "preseeded-composite"
                and prompt_delivery.get("future_seed_regressions_visible") is True
                and prompt_delivery.get("controller_verification") == "final-only"
            )
            if not composite_seed_delivery:
                errors.append(f"workflow session {sid} must use the Lifecycle V1 composite seed-delivery contract")
        leakage_controls = sequence.get("leakage_controls") if isinstance(sequence, dict) else None
        precise_visibility = (
            isinstance(leakage_controls, dict)
            and "controller_verifier_scripts_and_canonical_copies_model_visible" in leakage_controls
        )
        lifecycle_v1 = str(sequence.get("sequence_id", "")).endswith("-lifecycle-sequence-v1")
        verifier_visibility_valid = (
            isinstance(leakage_controls, dict)
            and (
                (
                    leakage_controls.get("controller_verifier_scripts_and_canonical_copies_model_visible") is False
                    and isinstance(leakage_controls.get("model_visible_acceptance_asset_paths"), list)
                    and (
                        not leakage_controls.get("model_visible_acceptance_asset_paths")
                        if lifecycle_v1
                        else bool(leakage_controls.get("model_visible_acceptance_asset_paths"))
                    )
                )
                if precise_visibility
                else leakage_controls.get("verifier_assets_model_visible") is False
            )
        )
        if not isinstance(leakage_controls, dict) or leakage_controls.get("seed_origin_concealed") is not True:
            errors.append(f"workflow session {sid} must record seed_origin_concealed leakage control for completed workflow reproduction")
        elif leakage_controls.get("task_directories_model_visible") is not False:
            errors.append(f"workflow session {sid} task directories must not be model-visible")
        if not isinstance(leakage_controls, dict) or leakage_controls.get("seed_patches_model_visible") is not False:
            errors.append(f"workflow session {sid} seed patches must not be model-visible")
        if not isinstance(leakage_controls, dict) or leakage_controls.get("git_baseline_true_root_at_lane_start") is not True:
            errors.append(f"workflow session {sid} must use a verified true-root Git baseline at lane start")
        if not isinstance(leakage_controls, dict) or leakage_controls.get("fixed_snapshot_objects_model_visible") is not False or leakage_controls.get("pre_seed_reflog_entries_visible") is not False:
            errors.append(f"workflow session {sid} fixed snapshot objects and pre-seed reflogs must not be model-visible")
        if not isinstance(leakage_controls, dict) or leakage_controls.get("concealment_verification_passed") is not True:
            errors.append(f"workflow session {sid} must pass seed concealment verification")
        if not verifier_visibility_valid:
            errors.append(f"workflow session {sid} must distinguish hidden controller verifier/canonical assets from model-visible acceptance tests")
        if not isinstance(leakage_controls, dict) or leakage_controls.get("verifier_integrity_passed") is not True:
            errors.append(f"workflow session {sid} must pass verifier integrity checks")

    profile = session.get("profile", {})
    if canonical_profile is not None and isinstance(profile, dict):
        expected = {
            "profile_type": canonical_profile.get("profile_type"),
            "enabled_surfaces": canonical_profile.get("enabled_surfaces", []),
            "disabled_overlaps": canonical_profile.get("disabled_overlaps", []),
            "component_ids": [component.get("component_id") for component in canonical_profile.get("components", [])],
        }
        actual = {key: profile.get(key) for key in expected}
        if actual != expected:
            errors.append(f"workflow session {sid} profile metadata does not match canonical evaluation profile")

    quality = session.get("software_quality", {})
    interpretation = session.get("interpretation", {})
    review_status = quality.get("quality_review_status") if isinstance(quality, dict) else None
    quality_score = quality.get("quality_score") if isinstance(quality, dict) else None
    if review_status == "not-reviewed" and quality_score is not None:
        errors.append(f"workflow session {sid} unreviewed quality_score must be null")
    if isinstance(interpretation, dict) and interpretation.get("accepted_for_objective") is True:
        token_usage = session.get("cumulative_token_usage", {})
        if not provider_usage_valid(
            token_usage,
            allow_legacy_null_cache_write=not current_provider_usage_contract(session),
        ):
            errors.append(
                f"workflow session {sid} objective acceptance requires exact canonical non-boolean provider-token usage and arithmetic"
            )
        prompt_delivery = sequence.get("prompt_delivery", {}) if isinstance(sequence, dict) else {}
        leakage_controls = sequence.get("leakage_controls", {}) if isinstance(sequence, dict) else {}
        lifecycle_v1 = str(sequence.get("sequence_id", "")).endswith("-lifecycle-sequence-v1")
        objective_visibility_valid = (
            (
                leakage_controls.get("controller_verifier_scripts_and_canonical_copies_model_visible") is False
                and isinstance(leakage_controls.get("model_visible_acceptance_asset_paths"), list)
                and (
                    not leakage_controls.get("model_visible_acceptance_asset_paths")
                    if lifecycle_v1
                    else bool(leakage_controls.get("model_visible_acceptance_asset_paths"))
                )
            )
            if "controller_verifier_scripts_and_canonical_copies_model_visible" in leakage_controls
            else leakage_controls.get("verifier_assets_model_visible") is False
        )
        composite_seed_delivery = (
            prompt_delivery.get("seed_delivery_mode") == "preseeded-composite"
            and prompt_delivery.get("future_seed_regressions_visible") is True
            and prompt_delivery.get("controller_verification") == "final-only"
            and leakage_controls.get("git_baseline_true_root_at_lane_start") is True
        )
        structurally_isolated = (
            prompt_delivery.get("future_tasks_visible") is False
            and prompt_delivery.get("future_prompts_materialized_lazily") is True
            and composite_seed_delivery
            and leakage_controls.get("task_directories_model_visible") is False
            and objective_visibility_valid
            and leakage_controls.get("verifier_integrity_passed") is True
            and leakage_controls.get("seed_patches_model_visible") is False
            and leakage_controls.get("fixed_snapshot_objects_model_visible") is False
            and leakage_controls.get("pre_seed_reflog_entries_visible") is False
            and leakage_controls.get("concealment_verification_passed") is True
        )
        if (
            session.get("status") != "completed"
            or interpretation.get("accepted_for_execution") is not True
            or not structurally_isolated
        ):
            errors.append(
                f"workflow session {sid} token-objective acceptance requires a completed, execution-accepted, and structurally isolated provider run"
            )
        if requires_structured_task_contract(session):
            integrity = session.get("execution_integrity", {})
            if (
                not isinstance(integrity, dict)
                or integrity.get("verifier_integrity_passed") is not True
                or integrity.get("tool_isolation_audit_passed") is not True
                or integrity.get("external_retrieval_hits") != []
            ):
                errors.append(
                    f"workflow session {sid} objective acceptance requires clean execution integrity"
                )


def expected_workflow_session_role(profile_id: str, canonical_profile: dict | None) -> str | None:
    del profile_id
    if not isinstance(canonical_profile, dict):
        return None
    profile_type = canonical_profile.get("profile_type")
    if profile_type == "control":
        return "baseline"
    if profile_type == "tool_stack":
        return "stack_treatment"
    if profile_type == "replacement_runtime":
        return "replacement_runtime"
    return "individual_tool_treatment"


def comparison_replicate_binding_matches(
    treatment: dict[str, Any],
    baseline: dict[str, Any],
) -> bool:
    """Validate either same-index pairing or the explicit V1 accepted-order map.

    ``replicate_index`` is a runtime-local attempt identity.  It is only a
    comparison identity when both conditions use the same accepted-attempt
    numbering.  Lifecycle V1 OpenCode lost r0 before objective acceptance, so
    its accepted r1/r2 runs pair with bare-Codex r0/r1 by accepted ordinal.
    """
    treatment_index = treatment.get("replicate_index")
    baseline_index = baseline.get("replicate_index")
    if type(treatment_index) is not int or type(baseline_index) is not int:
        return False
    pair = treatment.get("interpretation", {}).get("comparison_pair")
    if treatment_index == baseline_index:
        return pair in (None, {})
    if not isinstance(pair, dict):
        return False
    ordinal = pair.get("accepted_replicate_ordinal")
    treatment_prompts = (
        treatment.get("selected_execution", {})
        .get("descriptor", {})
        .get("model_facing_prompts", {})
        .get("tasks", [])
    )
    baseline_prompts = (
        baseline.get("selected_execution", {})
        .get("descriptor", {})
        .get("model_facing_prompts", {})
        .get("tasks", [])
    )
    return (
        treatment.get("profile", {}).get("profile_id") == "runtime-opencode-codex-product-v1"
        and treatment.get("agent", {}).get("model_condition_id") == "opencode-openai-gpt-5-6-sol-high"
        and baseline.get("profile", {}).get("profile_id") == "baseline-bare-codex"
        and baseline.get("agent", {}).get("model_condition_id") == "codex-openai-gpt-5-6-sol-high"
        and treatment.get("task_sequence", {}).get("sequence_id")
        in {"fastify-lifecycle-sequence-v1", "beets-lifecycle-sequence-v1"}
        and treatment.get("agent", {}).get("model") == baseline.get("agent", {}).get("model") == "gpt-5.6-sol"
        and treatment.get("agent", {}).get("reasoning_effort")
        == baseline.get("agent", {}).get("reasoning_effort")
        == "high"
        and isinstance(ordinal, int)
        and ordinal >= 1
        and pair.get("id") == f"lifecycle-v1-sol-high-accepted-pair-{ordinal:02d}"
        and pair.get("basis") == "accepted-replicate-ordinal"
        and pair.get("treatment_runtime_replicate_index") == treatment_index == ordinal
        and pair.get("baseline_runtime_replicate_index") == baseline_index == ordinal - 1
        and treatment_prompts == baseline_prompts
    )


def comparison_baseline_matches_treatment(
    treatment: dict[str, Any],
    baseline: dict[str, Any],
) -> bool:
    treatment_runtime = treatment.get("agent", {}).get("runtime_id")
    treatment_profile = treatment.get("profile", {}).get("profile_id")
    if treatment_runtime == "opencode-cli" and treatment_profile != "runtime-opencode-codex-product-v1":
        expected_profile = "runtime-opencode-codex-product-v1"
        expected_role = "replacement_runtime"
        expected_runtime = "opencode-cli"
    elif treatment_runtime == "claude-code" and treatment_profile != "baseline-claude-code-no-mcp":
        expected_profile = "baseline-claude-code-no-mcp"
        expected_role = "baseline"
        expected_runtime = "claude-code"
    else:
        expected_profile = "baseline-bare-codex"
        expected_role = "baseline"
        expected_runtime = "codex-cli"
    descriptor = baseline.get("selected_execution", {}).get("descriptor", {})
    return (
        baseline.get("profile", {}).get("profile_id") == expected_profile
        and baseline.get("session_role") == expected_role
        and (
            treatment_runtime not in {"codex-cli", "opencode-cli"}
            or baseline.get("agent", {}).get("runtime_id") == expected_runtime
        )
        and descriptor.get("execution_role") == expected_role
        and descriptor.get("selected_profile", {}).get("profile_id") == expected_profile
    )


def validate_workflow_sessions(session_doc: dict, sequence_ids: set[str], fixture_doc: dict, profiles_by_id: dict[str, dict], runtime_ids: set[str], model_condition_ids: set[str], errors: list[str]) -> None:
    if type(session_doc.get("schema_version")) is not int or session_doc.get("schema_version") != 1:
        errors.append("data/workflow-sessions.json must use schema_version 1")
    if session_doc.get("primary_metric") != "cumulative provider-reported workflow tokens":
        errors.append("data/workflow-sessions.json primary_metric must be cumulative provider-reported workflow tokens")
    sessions = session_doc.get("sessions")
    if not isinstance(sessions, list):
        errors.append("data/workflow-sessions.json must contain a sessions list")
        return
    if session_doc.get("production_status") == "pre-production":
        if sessions:
            errors.append("pre-production workflow session registry must be empty")
        artifact_root = ROOT / "sources/evaluations/workflow-sessions"
        if artifact_root.exists() and any(path.is_file() for path in artifact_root.rglob("*")):
            errors.append("pre-production workflow-session artifact directory must contain no result files")
    fixture_ids = {fixture.get("id") for fixture in fixture_doc.get("fixtures", [])}
    sessions_by_id = {
        session.get("session_id") or session.get("id"): session
        for session in sessions
        if isinstance(session, dict) and (session.get("session_id") or session.get("id"))
    }
    seen: set[str] = set()
    for index, session in enumerate(sessions):
        if not isinstance(session, dict):
            errors.append(f"workflow session at index {index} must be an object")
            continue
        sid = session.get("session_id") or session.get("id")
        if not sid:
            errors.append(f"workflow session at index {index} missing session_id")
            continue
        if sid in seen:
            errors.append(f"duplicate workflow session id: {sid}")
        seen.add(sid)
        # record_type, evidence_type, objective, evidence_stage, status and session_role are
        # enum-gated by the published schema above; only cross-file references remain here.
        validate_session_schema_conformance(session, sid, errors)
        target = session.get("target", {})
        if isinstance(target, dict) and target.get("fixture_id") and target.get("fixture_id") not in fixture_ids:
            errors.append(f"workflow session {sid} references unknown fixture {target.get('fixture_id')}")
        sequence = session.get("task_sequence", {})
        if isinstance(sequence, dict) and sequence.get("sequence_id") and sequence.get("sequence_id") not in sequence_ids:
            errors.append(f"workflow session {sid} references unknown sequence {sequence.get('sequence_id')}")
        profile = session.get("profile", {})
        profile_id = profile.get("profile_id") if isinstance(profile, dict) else None
        canonical_profile = profiles_by_id.get(profile_id) if profile_id else None
        if profile_id and canonical_profile is None:
            errors.append(f"workflow session {sid} references unknown profile {profile_id}")
        expected_session_role = expected_workflow_session_role(profile_id, canonical_profile) if profile_id else None
        baseline_profile = expected_session_role == "baseline"
        schema_version = session.get("schema_version")
        valid_schema_version = type(schema_version) is int and schema_version in {1, 2}
        if not valid_schema_version:
            errors.append(f"workflow session {sid} schema_version must be 1 or 2")
        strict_session_contract = requires_structured_task_contract(session)
        if strict_session_contract and profile_id and session.get("session_role") != expected_session_role:
            errors.append(
                f"workflow session {sid} role/profile mismatch: {session.get('session_role')} vs {profile_id}"
            )
        selected_descriptor = session.get("selected_execution", {}).get("descriptor", {})
        if strict_session_contract and isinstance(selected_descriptor, dict) and selected_descriptor:
            if (
                selected_descriptor.get("execution_role") != expected_session_role
                or selected_descriptor.get("selected_profile", {}).get("profile_id") != profile_id
            ):
                errors.append(f"workflow session {sid} selected execution does not match top-level role/profile")
        validate_workflow_session_contract(session, canonical_profile, errors, schema_checked=True)
        interpretation = session.get("interpretation", {}) if isinstance(session.get("interpretation"), dict) else {}
        comparison_id = interpretation.get("comparison_baseline_session_id")
        accepted_for_objective = interpretation.get("accepted_for_objective") is True
        standalone_runtime_control = (
            profile_id == "runtime-opencode-codex-product-v1"
            and interpretation.get("standalone_runtime_control") is True
            and not comparison_id
        )
        if (
            strict_session_contract
            and not baseline_profile
            and accepted_for_objective
            and not comparison_id
            and not standalone_runtime_control
        ):
            errors.append(f"accepted treatment workflow session {sid} requires a comparison baseline binding")
        if strict_session_contract and baseline_profile and comparison_id:
            errors.append(f"baseline workflow session {sid} must not carry a comparison baseline binding")
        if comparison_id:
            baseline = sessions_by_id.get(comparison_id)
            if baseline is None:
                errors.append(f"workflow session {sid} references missing comparison baseline {comparison_id}")
            elif (
                not comparison_replicate_binding_matches(session, baseline)
                or baseline.get("baseline_pool", {}).get("protocol_fingerprint")
                != session.get("baseline_pool", {}).get("protocol_fingerprint")
                or baseline.get("task_sequence", {}).get("sequence_id")
                != session.get("task_sequence", {}).get("sequence_id")
                or not comparison_baseline_matches_treatment(session, baseline)
                or baseline.get("status") != "completed"
                or baseline.get("interpretation", {}).get("accepted_for_objective") is not True
            ):
                errors.append(
                    f"workflow session {sid} comparison baseline {comparison_id} is not a canonical sequence-, pool-, and accepted-replicate-matched baseline"
                )
        agent = session.get("agent", {})
        if isinstance(agent, dict):
            runtime_id = agent.get("runtime_id")
            model_condition_id = agent.get("model_condition_id")
            if runtime_id and runtime_id not in runtime_ids:
                errors.append(f"workflow session {sid} references unknown agent.runtime_id {runtime_id}")
            if model_condition_id and model_condition_id not in model_condition_ids:
                errors.append(f"workflow session {sid} references unknown agent.model_condition_id {model_condition_id}")
        elif session.get("status") != "planned":
            errors.append(f"workflow session {sid} must define agent object")
        if session.get("evidence_type") == "workflow-simulation" and session.get("evidence_stage") == "reproduction":
            if target.get("fixture_scale") not in {"large-project", "medium-project"}:
                errors.append(f"workflow session {sid} reproduction must target a large-project or medium-project fixture")
        artifacts = session.get("artifacts", {})
        if isinstance(artifacts, dict) and artifacts.get("artifact_contract") == "compact-v1-four-files":
            expected_artifact_root = Path(f"sources/evaluations/workflow-sessions/{sid}")
            frozen_protocol = session.get("frozen_protocol", {})
            frozen_protocol_path = (
                ROOT / frozen_protocol.get("path", "missing")
                if isinstance(frozen_protocol, dict)
                else ROOT / "missing"
            )
            try:
                frozen_protocol_doc = json.loads(frozen_protocol_path.read_text())
            except (OSError, json.JSONDecodeError):
                frozen_protocol_doc = {}
            strict_compact_contract = requires_structured_task_contract(session)
            if (
                strict_compact_contract
                and artifacts.get("root") is not None
                and artifacts.get("root") != str(expected_artifact_root)
            ) or (
                current_provider_usage_contract(session)
                and artifacts.get("root") != str(expected_artifact_root)
            ):
                errors.append(
                    f"workflow session {sid} compact artifact root must be {expected_artifact_root}"
                )
            required = {"run_record", "final_diff", "evidence_bundle", "manifest"}
            missing = sorted(required - set(artifacts))
            if missing:
                errors.append(f"workflow session {sid} compact artifacts missing keys: {', '.join(missing)}")
            artifact_paths = []
            canonical_names = {
                "run_record": "run.json",
                "final_diff": "changes.diff",
                "evidence_bundle": "evidence.jsonl.gz",
                "manifest": "manifest.sha256",
            }
            declared_paths: dict[str, Path] = {}
            for key in sorted(required):
                value = artifacts.get(key)
                if not isinstance(value, str) or not value:
                    continue
                path = Path(value)
                if path.is_absolute() or ".." in path.parts:
                    errors.append(f"workflow session {sid} compact artifact {key} must be repository-relative: {value}")
                    continue
                full = ROOT / path
                artifact_paths.append(full)
                declared_paths[key] = path
                if path.name != canonical_names[key]:
                    errors.append(f"workflow session {sid} compact artifact {key} must reference {canonical_names[key]}")
                if not full.exists():
                    errors.append(f"workflow session {sid} compact artifact {key} does not exist: {value}")
            if len(set(declared_paths.values())) != len(required):
                errors.append(f"workflow session {sid} compact artifact keys must reference four distinct canonical files")
            roots = {path.parent for path in artifact_paths}
            if len(roots) == 1:
                root = next(iter(roots))
                expected_full_root = (ROOT / expected_artifact_root).absolute()
                resolved_artifact_root = root.resolve()
                if strict_compact_contract and (
                    root.absolute() != expected_full_root
                    or resolved_artifact_root != expected_full_root
                    or not resolved_artifact_root.is_relative_to(ROOT.resolve())
                    or root.is_symlink()
                ):
                    errors.append(
                        f"workflow session {sid} compact artifact paths must use exact root {expected_artifact_root}"
                    )
                allowed_names = {"run.json", "changes.diff", "evidence.jsonl.gz", "manifest.sha256"}
                if root.is_dir():
                    entries = list(root.iterdir())
                else:
                    entries = []
                    errors.append(
                        f"workflow session {sid} compact artifact root does not exist as a directory: {root.relative_to(ROOT)}"
                    )
                actual_names = {path.name for path in entries}
                if (
                    len(entries) != len(allowed_names)
                    or any(path.is_symlink() or not path.is_file() for path in entries)
                    or actual_names != allowed_names
                ):
                    errors.append(f"workflow session {sid} compact artifact directory must contain exactly four nonsymlink regular files {sorted(allowed_names)}; found {sorted(actual_names)}")
                validate_compact_manifest(root, sid, errors)
                if not evidence_bundle_valid(root / "evidence.jsonl.gz"):
                    errors.append(
                        f"workflow session {sid} evidence.jsonl.gz must be a bounded nonempty canonical gzip JSONL bundle"
                    )
                frozen_protocol = session.get("frozen_protocol")
                structured_session = requires_structured_task_contract(session) or (
                    isinstance(frozen_protocol, dict)
                    and str(frozen_protocol.get("protocol_id", "")).endswith("-v3")
                )
                if structured_session:
                    try:
                        run_record = json.loads((root / "run.json").read_text())
                    except Exception as exc:
                        errors.append(f"workflow session {sid} run.json cannot be parsed: {exc}")
                    else:
                        validate_structured_session_identity(session, run_record, sid, errors, schema_checked=True)
            elif len(roots) > 1:
                errors.append(f"workflow session {sid} compact artifacts must share one directory")

    # Accepted schema-v2 treatments may compare only against a baseline that
    # itself survived every strict canonical session, protocol, provider-usage,
    # and compact-artifact check above. This second pass prevents a structurally
    # plausible legacy or malformed record from satisfying the cross-record bind.
    for session in sessions:
        if not isinstance(session, dict) or session.get("schema_version") != 2:
            continue
        profile_id = session.get("profile", {}).get("profile_id")
        canonical_profile = profiles_by_id.get(profile_id) if isinstance(profile_id, str) else None
        interpretation = session.get("interpretation", {})
        if (
            isinstance(canonical_profile, dict)
            and canonical_profile.get("profile_type") == "control"
            or interpretation.get("accepted_for_objective") is not True
            or (
                profile_id == "runtime-opencode-codex-product-v1"
                and interpretation.get("standalone_runtime_control") is True
                and not interpretation.get("comparison_baseline_session_id")
            )
        ):
            continue
        sid = session.get("session_id") or session.get("id")
        comparison_id = interpretation.get("comparison_baseline_session_id")
        baseline = sessions_by_id.get(comparison_id)
        baseline_has_errors = any(
            f"workflow session {comparison_id} " in error
            for error in errors
        )
        if (
            not isinstance(baseline, dict)
            or baseline.get("schema_version") != 2
            or baseline_has_errors
        ):
            errors.append(
                f"accepted treatment workflow session {sid} comparison baseline {comparison_id} must be an error-free canonical schema-v2 baseline with intact provider and compact evidence"
            )


def validate_compact_diff_size(root: Path, sid: str, errors: list[str]) -> None:
    """Keep compact-v1 final diffs compact. Frozen oversized evidence is grandfathered by id."""
    diff = root / "changes.diff"
    if not diff.is_file() or sid in OVERSIZED_COMPACT_DIFF_SESSION_IDS:
        return
    size = diff.stat().st_size
    if size > MAX_COMPACT_DIFF_BYTES:
        errors.append(
            f"workflow session {sid} changes.diff is {size} bytes, over the "
            f"{MAX_COMPACT_DIFF_BYTES}-byte compact-v1 limit; a final diff this large usually means "
            "treatment product state leaked into the captured task delta"
        )


def validate_compact_manifest(root: Path, sid: str, errors: list[str]) -> None:
    allowed_names = {"run.json", "changes.diff", "evidence.jsonl.gz", "manifest.sha256"}
    validate_compact_diff_size(root, sid, errors)
    manifest = root / "manifest.sha256"
    if not manifest.is_file():
        errors.append(f"workflow session {sid} compact manifest is missing")
        return
    seen_manifest: set[str] = set()
    for line in manifest.read_text().splitlines():
        parts = line.split()
        if len(parts) != 2:
            errors.append(f"workflow session {sid} manifest has malformed line: {line}")
            continue
        digest, name = parts
        if name in seen_manifest:
            errors.append(f"workflow session {sid} manifest contains duplicate artifact: {name}")
        seen_manifest.add(name)
        target = root / name
        if name == "manifest.sha256" or name not in allowed_names or not target.is_file():
            errors.append(f"workflow session {sid} manifest references invalid artifact: {name}")
        elif hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            errors.append(f"workflow session {sid} manifest digest mismatch for {name}")
    expected_manifest_names = allowed_names - {"manifest.sha256"}
    if seen_manifest != expected_manifest_names:
        errors.append(f"workflow session {sid} manifest must cover exactly {sorted(expected_manifest_names)}; found {sorted(seen_manifest)}")


def dossier_field(text: str, field: str) -> str | None:
    match = re.search(rf"^- {re.escape(field)}:\s*(.*)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def validate_tool_dossier_snapshots(errors: list[str]) -> None:
    dossier_dir = ROOT / "docs" / "tool-dossiers"
    commit_pattern = re.compile(r"[0-9a-f]{7,40}", re.IGNORECASE)
    for path in sorted(dossier_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        version_ref = dossier_field(text, "Version/ref inspected")
        snapshot_status = dossier_field(text, "Snapshot status")
        commit = dossier_field(text, "Commit inspected")
        source_artifact = dossier_field(text, "Source artifact path")
        evidence_stage = dossier_field(text, "Evidence stage")

        for section in DOSSIER_REQUIRED_SECTIONS:
            if section not in text:
                errors.append(f"{rel} missing required section {section}")
        for stale_phrase in DOSSIER_STALE_PHRASES:
            if stale_phrase in text:
                errors.append(f"{rel} contains stale dossier-quality phrase: {stale_phrase}")

        if not version_ref:
            errors.append(f"{rel} missing Version/ref inspected")
        if snapshot_status not in DOSSIER_SNAPSHOT_STATUSES:
            errors.append(f"{rel} missing valid Snapshot status")
            continue
        if not source_artifact:
            errors.append(f"{rel} missing Source artifact path")
        else:
            artifact_rel = source_artifact.strip().strip("`")
            if not (ROOT / artifact_rel).exists():
                errors.append(f"{rel} Source artifact path does not exist: {artifact_rel}")
        if not evidence_stage or "source-logic" not in evidence_stage:
            errors.append(f"{rel} must state source-logic-or-better Evidence stage")
        if not re.search(r"benchmark-audit|reproduction", text, re.IGNORECASE):
            errors.append(f"{rel} must include benchmark-audit or reproduction limitation/follow-up")

        if snapshot_status == "pinned-commit":
            normalized_commit = (commit or "").strip().strip("`")
            if not commit_pattern.fullmatch(normalized_commit):
                errors.append(f"{rel} has pinned-commit status but invalid Commit inspected")
        elif snapshot_status == "unpinned-historical-inspection":
            if commit != "not recorded during original pass":
                errors.append(
                    f"{rel} has unpinned-historical-inspection status but Commit inspected is not the required disclosure"
                )


def validate_frozen_protocol_bindings(errors: list[str]) -> None:
    """Validate the two live contracts and the archived protocol bytes."""
    try:
        from scripts import run_codex_workflow_evaluation as runner
    except Exception as exc:
        errors.append(f"cannot import workflow runner for protocol validation: {exc}")
        return

    active_paths = set((ROOT / "sources/evaluations/protocols").glob("*.json"))
    expected_paths: set[Path] = set()
    for sequence_id in runner.active_sequence_ids():
        sequence = runner.load_sequence(sequence_id)
        try:
            binding, protocol = runner.current_lifecycle_v1_protocol(
                sequence, sequence.get("mistake_gate", {}), ROOT
            )
        except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
            errors.append(f"active sequence {sequence_id} has no unique current baseline protocol: {exc}")
            continue
        path = ROOT / binding["path"]
        expected_paths.add(path)
        fixture = protocol.get("task_fixture", {})
        selected = protocol.get("selected_execution", {})
        baseline_pool = protocol.get("baseline_pool", {})
        if (
            protocol.get("protocol_schema_version") != 3
            or protocol.get("status") != "frozen-ready-not-run"
            or protocol.get("protocol_id") != path.stem
            or fixture.get("sequence_id") != sequence_id
            or fixture.get("task_family_generation") != "lifecycle-v1"
            or fixture.get("qualification_path") != sequence.get("qualification_path")
            or selected.get("descriptor_sha256") != runner._json_hash(selected.get("descriptor"))
            or baseline_pool.get("protocol_fingerprint")
            != runner.baseline_protocol_fingerprint_from_descriptor(baseline_pool.get("descriptor", {}))
            or hashlib.sha256(path.read_bytes()).hexdigest() != binding["sha256"]
            or "total_provider_tokens" not in protocol.get("token_accounting_boundary", {}).get("fields", [])
        ):
            errors.append(f"active protocol {path.name} does not match its Lifecycle V1 contract")
    if active_paths != expected_paths:
        unexpected = sorted(str(path.relative_to(ROOT)) for path in active_paths ^ expected_paths)
        errors.append(f"active protocol directory must contain only the two current baselines: {unexpected}")

    archive_root = ROOT / "sources/evaluations/archive/lifecycle-v1-pre-corrected-prompts-20260813"
    archived_protocols = list((archive_root / "protocols").glob("*.json"))
    if len(archived_protocols) != 140:
        errors.append(f"archived pre-correction corpus must retain 140 protocols; found {len(archived_protocols)}")
    archived_audits = [path for path in (archive_root / "audits").rglob("*") if path.is_file()]
    if len(archived_audits) != 152:
        errors.append(f"archived pre-correction corpus must retain 152 audit files; found {len(archived_audits)}")
    by_name: dict[str, Path] = {}
    for path in archived_protocols:
        try:
            protocol = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"archived protocol {path.name} is unreadable: {exc}")
            continue
        if path.name in by_name:
            errors.append(f"duplicate archived protocol filename: {path.name}")
        by_name[path.name] = path
        if protocol.get("protocol_id") != path.stem or protocol.get("status") != "frozen-ready-not-run":
            errors.append(f"archived protocol {path.name} has invalid frozen identity")
    try:
        archived_registry = json.loads((archive_root / "workflow-sessions-registry.json").read_text())
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"archived session registry is unreadable: {exc}")
        return
    for session in archived_registry.get("sessions", []):
        frozen = session.get("frozen_protocol", {})
        original_path = frozen.get("path")
        expected_sha = frozen.get("sha256")
        archived_path = by_name.get(Path(str(original_path or "")).name)
        if (
            not isinstance(expected_sha, str)
            or archived_path is None
            or hashlib.sha256(archived_path.read_bytes()).hexdigest() != expected_sha
        ):
            errors.append(f"archived session {session.get('session_id')} has no matching frozen protocol bytes")


def validate_document_lifecycle(
    session_doc: dict,
    fixture_doc: dict,
    sequence_doc: dict,
    errors: list[str],
) -> None:
    accepted_baselines = [
        session
        for session in session_doc.get("sessions", [])
        if session.get("status") == "completed"
        and session.get("session_role") == "baseline"
        and session.get("interpretation", {}).get("accepted_for_objective") is True
    ]
    if accepted_baselines:
        stale_claims = {
            "docs/evaluations/README.md": ("No production result exists",),
            "sources/evaluations/README.md": (
                "There are no retained production results",
                "empty until a production run occurs",
            ),
            "data/workflow-task-sequences.json": ("pre-production evaluation portfolio",),
            "data/repository-fixtures.json": ("No production result has been recorded",),
        }
        for rel, phrases in stale_claims.items():
            text = (ROOT / rel).read_text()
            for phrase in phrases:
                if phrase in text:
                    errors.append(f"{rel} retains stale post-baseline claim: {phrase}")
        sequence_to_fixture = {
            sequence.get("id"): sequence.get("fixture_id")
            for sequence in sequence_doc.get("sequences", [])
        }
        completed_fixture_ids = {
            fixture_id
            for session in accepted_baselines
            if isinstance(
                fixture_id := sequence_to_fixture.get(
                    session.get("task_sequence", {}).get("sequence_id")
                ),
                str,
            )
        }
        fixtures_by_id = {
            fixture.get("id"): fixture
            for fixture in fixture_doc.get("fixtures", [])
        }
        non_ready = [
            fixture_id
            for fixture_id in sorted(completed_fixture_ids)
            if fixtures_by_id.get(fixture_id, {}).get("evaluation_use") == "primary-objective"
            and fixtures_by_id.get(fixture_id, {}).get("status") != "treatment-ready"
        ]
        if non_ready:
            errors.append(
                "fixtures with retained operational baselines must be treatment-ready: "
                + ", ".join(str(item) for item in non_ready)
            )
    agents = (ROOT / "AGENTS.md").read_text()
    if "## Documentation lifecycle" not in agents:
        errors.append("AGENTS.md must define the evidence-driven documentation lifecycle")
    retired_paths = (
        "docs/evaluations/progressive-repository-evaluation-plan.md",
        "docs/evaluations/changes",
        "templates/progressive-evaluation-change",
        "templates/workflow-session-record.json",
    )
    for rel in retired_paths:
        if (ROOT / rel).exists():
            errors.append(f"retired duplicate evaluation surface still exists: {rel}")


def validate_lifecycle_v1_authorization(errors: list[str]) -> None:
    """Validate the sole current paid-pilot authority without reopening archived campaigns."""
    from scripts import run_codex_workflow_evaluation as workflow

    path = ROOT / "sources/evaluations/audits/lifecycle-v1-corrected-task-family-readiness-20260813.json"
    try:
        authority = json.loads(path.read_text(), object_pairs_hook=_json_object_without_duplicate_keys)
        sequences = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"corrected Lifecycle V1 readiness authority cannot be read: {exc}")
        return
    active_ids = [
        item.get("id")
        for item in sequences.get("sequences", [])
        if item.get("status") == "active" and item.get("task_family_generation") == "lifecycle-v1"
    ]
    paid = authority.get("paid_pilot_authorized")
    authorization = authority.get("pilot_authorization")
    if (
        authority.get("schema_version") != 2
        or type(authority.get("schema_version")) is not int
        or authority.get("generation") != "lifecycle-v1"
        or authority.get("active_sequence_ids") != active_ids
        or type(paid) is not bool
        or not isinstance(authority.get("pilot_attempts"), dict)
        or (paid is False and authorization is not None)
        or (
            paid is True
            and (
                workflow.LIFECYCLE_V1_PILOT_AUTHORIZATION is None
                or authorization != workflow.LIFECYCLE_V1_PILOT_AUTHORIZATION
            )
        )
    ):
        errors.append("corrected Lifecycle V1 readiness authority has invalid scope or paid-pilot state")


def main() -> int:
    errors: list[str] = []
    for rel in REQUIRED_PATHS + LOCAL_SKILL_ARTIFACTS + DECISION_RECORDS:
        if not (ROOT / rel).exists():
            errors.append(f"missing required path: {rel}")

    techniques_doc = load_json("data/techniques.json")
    repositories_doc = load_json("data/repositories.json")
    compatibility_doc = load_json("data/compatibility-edges.json")
    literature_doc = load_json("data/literature.json")
    evaluations_doc = load_json("data/evaluations.json")
    workflow_sequences_doc = load_json("data/workflow-task-sequences.json")
    workflow_sessions_doc = load_json("data/workflow-sessions.json")
    profiles_doc = load_json("data/evaluation-profiles.json")
    agent_runtimes_doc = load_json("data/evaluation-agent-runtimes.json")
    large_candidates_doc = load_json("data/large-project-candidates.json")
    medium_candidates_doc = load_json("data/medium-project-candidates.json")
    fixtures_doc = load_json("data/repository-fixtures.json")
    backlog_doc = load_json("data/tool-analysis-backlog.json")
    parity_doc = load_json("sources/evaluations/audits/official-integration-parity-20260718.json")
    qualification_docs = [
        json.loads(path.read_text())
        for path in sorted(
            (ROOT / "sources/evaluations/audits").glob("corrected-integration-qualification-*.json")
        )
    ]
    protocol_docs = {
        path.relative_to(ROOT).as_posix(): {
            "document": json.loads(path.read_text()),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in (ROOT / "sources/evaluations/protocols").glob("*.json")
    }

    technique_ids = {t.get("id") for t in techniques_doc.get("techniques", [])}
    if not technique_ids:
        errors.append("data/techniques.json has no techniques")

    repo_ids = set()
    for repo in repositories_doc.get("repositories", []):
        rid = repo.get("id")
        if not rid:
            errors.append("repository record missing id")
            continue
        if rid in repo_ids:
            errors.append(f"duplicate repository id: {rid}")
        repo_ids.add(rid)
        for tid in repo.get("technique_ids", []):
            if tid not in technique_ids:
                errors.append(f"repository {rid} references unknown technique {tid}")
        if repo.get("kind") == "bundle" and repo.get("technique_ids"):
            errors.append(f"bundle {rid} should reference components, not claim atomic technique_ids")
        if not repo.get("sources"):
            errors.append(f"repository {rid} has no sources")

    allowed_edge_targets = technique_ids | SURFACE_IDS
    allowed_edge_sources = technique_ids | SURFACE_IDS
    for edge in compatibility_doc.get("edges", []):
        source = edge.get("source_id")
        target = edge.get("target_id")
        if source not in allowed_edge_sources:
            errors.append(f"compatibility edge has unknown source_id: {source}")
        if target not in allowed_edge_targets:
            errors.append(f"compatibility edge has unknown target_id: {target}")
        if not edge.get("rationale"):
            errors.append(f"compatibility edge {source}->{target} missing rationale")

    validate_repository_fixtures(fixtures_doc, errors)
    validate_large_project_candidates(large_candidates_doc, fixtures_doc, errors)
    validate_medium_project_candidates(medium_candidates_doc, fixtures_doc, errors)
    profile_ids = validate_evaluation_profiles(profiles_doc, fixtures_doc, errors)
    profiles_by_id = {profile["id"]: profile for profile in profiles_doc.get("profiles", []) if profile.get("id")}
    runtime_ids, model_condition_ids = validate_agent_runtimes(agent_runtimes_doc, errors)
    validate_evaluations(evaluations_doc, fixtures_doc, profile_ids, runtime_ids, model_condition_ids, errors)
    workflow_sequence_ids = validate_workflow_task_sequences(workflow_sequences_doc, fixtures_doc, errors)
    validate_candidate_profile_launch_readiness(
        profiles_doc,
        fixtures_doc,
        workflow_sequences_doc,
        parity_doc,
        qualification_docs,
        protocol_docs,
        errors,
        executed_protocol_paths_from_registry(workflow_sessions_doc),
    )
    validate_fixture_sequence_status_consistency(workflow_sequences_doc, fixtures_doc, large_candidates_doc, medium_candidates_doc, errors)
    validate_workflow_sessions(workflow_sessions_doc, workflow_sequence_ids, fixtures_doc, profiles_by_id, runtime_ids, model_condition_ids, errors)
    validate_document_lifecycle(workflow_sessions_doc, fixtures_doc, workflow_sequences_doc, errors)
    validate_lifecycle_v1_authorization(errors)
    validate_frozen_protocol_bindings(errors)
    for path in (ROOT / "data/workflow-task-sequences.json", ROOT / "templates/evaluation-run-record.json"):
        if "gpt-5.5" in path.read_text():
            errors.append(f"active workflow surface {path.relative_to(ROOT)} uses historical-inactive gpt-5.5")
    validate_tool_dossier_snapshots(errors)

    for lit in literature_doc.get("literature", []):
        if not lit.get("id") or not lit.get("sources"):
            errors.append("literature record missing id or sources")

    allowed_stages = {"lead", "source_logic", "benchmark_audit", "reproduction"}
    retired_review_map_key = "review" + "_levels"
    retired_current_key = "current" + "_level"
    retired_target_key = "target" + "_level"
    if retired_review_map_key in backlog_doc:
        errors.append("tool-analysis backlog uses retired review-level map; use evidence_stages")
    for item in backlog_doc.get("items", []):
        if retired_current_key in item or retired_target_key in item:
            errors.append(f"backlog item {item.get('tool')} uses retired numeric evidence-stage fields")
        current_stage = item.get("current_stage")
        target_stage = item.get("target_stage")
        if current_stage not in allowed_stages:
            errors.append(f"backlog item {item.get('tool')} has invalid current_stage: {current_stage}")
        if target_stage not in allowed_stages:
            errors.append(f"backlog item {item.get('tool')} has invalid target_stage: {target_stage}")
        if item.get("dossier") and current_stage == "lead":
            errors.append(f"backlog item {item.get('tool')} has a dossier but remains lead-stage")
        if not item.get("dossier") and current_stage != "lead":
            errors.append(f"backlog item {item.get('tool')} lacks a dossier but is not lead-stage")

    active_text_paths = [
        ROOT / "docs/methodology/README.md",
        ROOT / "docs/research/tool-research-strategy.md",
        ROOT / "docs/tool-dossiers/README.md",
        ROOT / "docs/papers/phase-1-compatibility-safe-token-saving-stacks.md",
        ROOT / "docs/evaluations/design/framework.md",
        ROOT / "docs/evaluations/design/fixture-design.md",
        ROOT / "docs/evaluations/design/result-schema.md",
        ROOT / "docs/evaluations/operations/fixture-guide.md",
        ROOT / "docs/evaluations/design/token-and-quality-policy.md",
        ROOT / "docs/evaluations/plans/phase-2-benchmark-plan.md",
        ROOT / "docs/evaluations/design/workflow-model.md",
        ROOT / "docs/evaluations/operations/runbook.md",
        ROOT / "docs/evaluations/operations/workflow-guide.md",
        ROOT / "docs/methodology/report-writing-patterns.md",
        ROOT / "templates/report.md",
        ROOT / "templates/repository-entry.md",
        ROOT / "templates/repository-fixture.md",
        ROOT / "templates/tool-dossier.md",
        ROOT / "prompts/researcher.md",
        ROOT / "prompts/paper-writer.md",
    ]
    retired_patterns = [
        r"Lev" + r"el [0-5]",
        r"lev" + r"el [0-5]",
        r"review " + r"level",
        r"Review " + r"level",
        r"dossier " + r"level",
        r"Dossier " + r"level",
        retired_current_key,
        retired_target_key,
        "source-" + "behavior",
        "0-" + "discovery",
        "1-" + "surface",
        "2-" + "integration",
        "3-" + "source",
        "4-" + "benchmark",
        "5-" + "reproduction",
        "level" + "2-uplift",
    ]
    retired_terms = re.compile("|".join(retired_patterns))
    for path in active_text_paths:
        text = path.read_text(encoding="utf-8")
        if retired_terms.search(text):
            errors.append(f"{path.relative_to(ROOT)} contains retired dossier-stage terminology")

    report_path = ROOT / "docs/papers/phase-1-compatibility-safe-token-saving-stacks.md"
    report_text = report_path.read_text(encoding="utf-8")
    if "Principal sources:" in report_text:
        errors.append("phase-1 report uses ledger-style 'Principal sources' heading; use summarized evidence basis")
    if "sources/discovery/" in report_text:
        errors.append("phase-1 report body references discovery archive paths; summarize provenance instead")
    if re.search(r"sources/discovery/20\d{2}-\d{2}-\d{2}-[^`\s)]*\.json", report_text):
        errors.append("phase-1 report body lists raw discovery JSON artifacts; summarize provenance instead")
    if re.search(r"\|\s*`[^`]+`\s*\|\s*[0-9]\s*\|", report_text):
        errors.append("phase-1 report contains a numeric evidence-stage table row; use named stages")

    runbook_check = subprocess.run(
        ["python3", "scripts/update_workflow_runbook.py", "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if runbook_check.returncode != 0:
        errors.append((runbook_check.stderr or runbook_check.stdout or "workflow runbook is stale").strip())

    summary_check = subprocess.run(
        ["python3", "scripts/update_registry_summaries.py", "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if summary_check.returncode != 0:
        errors.append(
            (summary_check.stderr or summary_check.stdout or "registry summaries are stale").strip()
        )


    if errors:
        print("Validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    # Repo-local research skills should remain limited to the recommended set.
    skill_dir = ROOT / ".agents" / "skills"
    expected_skill_files = {
        Path(p).name
        for p in LOCAL_SKILL_ARTIFACTS
        if p.startswith(".agents/skills/") and p.endswith(".md") and not p.endswith("index.md")
    }
    actual_skill_files = {p.name for p in skill_dir.glob("*.md") if p.name != "index.md"}
    if actual_skill_files != expected_skill_files:
        missing = sorted(expected_skill_files - actual_skill_files)
        extra = sorted(actual_skill_files - expected_skill_files)
        raise SystemExit(f"repo-local skill set mismatch; missing={missing}, extra={extra}")
    agents_text = (ROOT / "AGENTS.md").read_text()
    for rel in LOCAL_SKILL_ARTIFACTS:
        if rel.startswith(".agents/skills/") and rel.endswith(".md") and not rel.endswith("index.md"):
            if rel not in agents_text:
                raise SystemExit(f"AGENTS.md does not reference local skill: {rel}")

    print("Validation passed")
    print(f"- techniques: {len(techniques_doc.get('techniques', []))}")
    print(f"- repositories: {len(repositories_doc.get('repositories', []))}")
    print(f"- compatibility edges: {len(compatibility_doc.get('edges', []))}")
    print(f"- literature records: {len(literature_doc.get('literature', []))}")
    print(f"- evaluations: {len(evaluations_doc.get('evaluations', []))}")
    print(f"- workflow task sequences: {len(workflow_sequences_doc.get('sequences', []))}")
    print(f"- workflow sessions: {len(workflow_sessions_doc.get('sessions', []))}")
    print(f"- evaluation profiles: {len(profiles_doc.get('profiles', []))}")
    print(f"- agent runtimes: {len(agent_runtimes_doc.get('agent_runtimes', []))}")
    print(f"- model conditions: {len(agent_runtimes_doc.get('model_conditions', []))}")
    print(f"- large-project candidates: {len(large_candidates_doc.get('candidates', []))}")
    print(f"- medium-project candidates: {len(medium_candidates_doc.get('candidates', []))}")
    print(f"- repository fixtures: {len(fixtures_doc.get('fixtures', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
