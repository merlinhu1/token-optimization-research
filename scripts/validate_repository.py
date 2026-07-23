#!/usr/bin/env python3
"""Lightweight structural validation for the token optimization research repository."""
from __future__ import annotations

import gzip
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

BASELINE_V3_ACCEPTANCE_ASSET_PATHS = {
    "fastify-lifecycle-feature-v0": ["test/baseline-v3-request-media-type.test.js"],
    "fastify-lifecycle-refactor-v0": ["test/baseline-v3-content-type-cache.test.js"],
    "fastify-lifecycle-review-v0": ["test/baseline-v3-max-param.test.js"],
    "beets-lifecycle-feature-v0": ["test/util/test_functemplate.py"],
    "beets-lifecycle-refactor-v0": [],
    "beets-lifecycle-review-v0": ["test/plugins/test_ftintitle.py"],
    "terraform-lifecycle-feature-v0": ["internal/policy/callback/baseline_v3_deferred_test.go"],
    "terraform-lifecycle-refactor-v0": [
        "internal/configs/parser_config_dir_test.go",
        "internal/configs/baseline_v3_requirement_type_test.go",
    ],
    "terraform-lifecycle-review-v0": ["internal/addrs/baseline_v3_checkable_test.go"],
}

PROVIDER_USAGE_FIELDS = (
    "fresh_input_tokens",
    "cached_input_tokens",
    "cache_write_tokens",
    "output_tokens",
    "reasoning_tokens",
    "total_provider_tokens",
)

LEGACY_RUN_ACCEPTANCE_MISMATCH_SESSION_IDS = {
    "ponytail-fastify-20260719-p-769d40697529-r2",
    "ponytail-beets-20260719-p-b440da225a3a-r2",
    "ponytail-terraform-20260719-p-ded8609b4172-r2",
}


def provider_usage_valid(usage: object, *, allow_legacy_null_cache_write: bool = False) -> bool:
    if (
        not isinstance(usage, dict)
        or usage.get("measurement_source") != "codex-jsonl-usage-events"
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
    total = usage.get("total_provider_tokens")
    expected_total = (
        usage["fresh_input_tokens"]
        + usage["cached_input_tokens"]
        + cache_write_value
        + usage["output_tokens"]
    )
    return (
        type(total) is int
        and total > 0
        and total == expected_total
        and usage["reasoning_tokens"] <= usage["output_tokens"]
    )


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
    run_usage_for_validation = dict(run_usage)
    run_usage_for_validation["measurement_source"] = run_usage.get(
        "measurement_source",
        usage.get("measurement_source"),
    )
    interpretation = session.get("interpretation", {})
    usage_is_decision_bearing = (
        current_contract
        or require_accepted
        or (isinstance(interpretation, dict) and interpretation.get("accepted_for_objective") is True)
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
    legacy_acceptance_mismatch = (
        not current_contract
        and session.get("session_id") in LEGACY_RUN_ACCEPTANCE_MISMATCH_SESSION_IDS
        and run_record.get("accepted") is False
        and expected_accepted is True
    )
    if run_record.get("accepted") != expected_accepted and not legacy_acceptance_mismatch:
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
    qualification_path = str(protocol.get("task_fixture", {}).get("qualification_path", ""))
    return qualification_path.endswith("-baseline-v3.json") or qualification_path.endswith("-baseline-v4.json")


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
    ".agents/skills/stack-ablation-planner.md",
    ".agents/skills/practical-software-quality-reviewer.md",
    ".agents/skills/scientific-report-reviewer.md",
    ".agents/skills/citation-light-prior-art-mapper.md",
    ".agents/skills/figure-table-planner.md",
]

TRUTHMARK_ARTIFACTS = [
    ".truthmark/config.yml",
    "docs/truthmark/routes/areas.md",
    "docs/truthmark/routes/areas/research.md",
    "docs/truthmark/engineering/research/evidence-stages.md",
    "docs/truthmark/engineering/research/methodology.md",
    "docs/truthmark/engineering/research/token-accounting.md",
    "docs/truthmark/engineering/research/software-quality-diagnostics.md",
    "docs/truthmark/engineering/research/stack-compatibility.md",
    "docs/truthmark/engineering/research/current-findings.md",
    "docs/truthmark/engineering/research/agent-workflow.md",
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
    "docs/papers/phase-2-lifecycle-v0-natural-use-screening.md",
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
EVALUATION_RECORD_TYPES = {"run", "paired_comparison", "aggregate_summary"}
EVALUATION_RUN_ROLES = {"baseline", "individual_tool_treatment", "stack_treatment", "replacement_runtime", "audit_only"}
EVALUATION_STATUSES = {"planned", "running", "completed", "failed", "excluded", "superseded"}
WORKFLOW_EVIDENCE_TYPES = {"workflow-simulation", "workflow-ablation", "sanity-check"}
WORKFLOW_SESSION_ROLES = {"baseline", "individual_tool_treatment", "stack_treatment", "ablation", "sanity_check"}
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


def run_truthmark(command: str, errors: list[str]) -> None:
    try:
        result = subprocess.run(
            ["truthmark", command, "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        errors.append("truthmark CLI is required for repository validation")
        return
    if result.returncode not in (0, 1):
        errors.append(f"truthmark {command} failed to run: {result.stderr.strip() or result.stdout.strip()}")
        return
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"truthmark {command} returned invalid JSON: {exc}")
        return
    error_diagnostics = [
        d for d in payload.get("diagnostics", []) if d.get("severity") == "error"
    ]
    for diagnostic in error_diagnostics:
        errors.append(
            f"truthmark {command}: {diagnostic.get('file', '<unknown>')}: {diagnostic.get('message', '<no message>')}"
        )


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
    required_true = ("seeded_verifier_nonzero", "fixed_verifier_zero", "full_fixed_cumulative_verifier_zero", "composite_seed_merge_zero", "composite_seeded_verifiers_nonzero", "no_unmerged_paths", "all_expected_model_concealment_declared")
    if sequence.get("task_family_generation") in {"baseline-v3", "baseline-v4"}:
        required_true += ("no_model_concealed_acceptance_assets", "all_acceptance_behavior_model_visible", "model_visible_acceptance_assets_match_verifier_copies")
        if sequence.get("task_family_generation") == "baseline-v4":
            required_true += ("aggregate_verifier_environment_passed",)
            if q.get("task_family_generation") != "baseline-v4":
                errors.append(f"qualification {rel} must bind task_family_generation=baseline-v4")
        if q.get("no_model_visible_acceptance_assets") is not False:
            errors.append(f"qualification {rel} must not claim Baseline V3 acceptance assets are absent from the model")
        if q.get("acceptance_visibility") != "model-visible-complete":
            errors.append(f"qualification {rel} must record complete model-visible Baseline V3 acceptance")
        expected_asset_count = sum(
            len(BASELINE_V3_ACCEPTANCE_ASSET_PATHS[task["id"]]) for task in ordered
        )
        if expected_asset_count < 1 or q.get("expected_model_visible_acceptance_asset_count") != expected_asset_count:
            errors.append(f"qualification {rel} must record the complete nonempty Baseline V3 acceptance-asset set")
    else:
        required_true += ("no_model_visible_acceptance_assets",)
    if sequence.get("status") == "active":
        required_true += ("fixed_snapshot_model_concealed_paths_safe",)
    if q.get("snapshot") != sequence.get("initial_snapshot", {}).get("commit") or q.get("ordered_task_ids") != [t["id"] for t in ordered] or q.get("qualified_on") != sequence.get("qualification_date"):
        errors.append(f"qualification {rel} snapshot, date, or task order is stale")
    if any(q.get(field) is not True for field in required_true):
        errors.append(f"qualification {rel} must record every executable gate as true")
    if set(q.get("composite_seed_verifier_exits", {}).values()) != {1}:
        errors.append(
            f"qualification {rel} seeded verifiers must fail acceptance with exit 1, not collection or infrastructure"
        )
    boundaries = q.get("cumulative_boundaries", [])
    boundary_invalid = len(boundaries) != len(ordered)
    if not boundary_invalid:
        for task, boundary in zip(ordered, boundaries):
            common_invalid = (
                boundary.get("task_id") != task["id"]
                or boundary.get("seed_apply_check_exit") != 0
                or boundary.get("seed_apply_exit") != 0
                or boundary.get("seeded_verifier_exit") != 1
                or boundary.get("repair_apply_check_exit") != 0
                or boundary.get("repair_apply_exit") != 0
                or any(code != 0 for code in boundary.get("retained_verifier_exits", {}).values())
            )
            refactor_invalid = task.get("task_class") == "behavior-preserving-refactor" and (
                boundary.get("seeded_behavior_exit") != 0
                or boundary.get("seeded_structure_exit") in (None, 0)
                or boundary.get("fixed_behavior_exit") != 0
                or boundary.get("fixed_structure_exit") != 0
            )
            if common_invalid or refactor_invalid:
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
        expected_acceptance_paths = BASELINE_V3_ACCEPTANCE_ASSET_PATHS.get(task["id"], [])
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
    if not isinstance(candidates, list) or not candidates:
        errors.append("data/large-project-candidates.json must contain a non-empty candidates list")
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
    for sequence in sequence_doc.get("sequences", []):
        if not isinstance(sequence, dict) or sequence.get("status") != "active":
            continue
        fixture_id = sequence.get("fixture_id")
        sequence_id = sequence.get("id")
        if isinstance(fixture_id, str) and isinstance(sequence_id, str):
            active_sequences_by_fixture.setdefault(fixture_id, []).append(sequence_id)

    expected_pairs: set[tuple[str, str]] = set()
    for fixture in fixture_doc.get("fixtures", []):
        if not isinstance(fixture, dict):
            continue
        sequence_ids = active_sequences_by_fixture.get(str(fixture.get("id")), [])
        for profile_id in fixture.get("candidate_profiles", []):
            if profile_id == "baseline-bare-codex":
                continue
            for sequence_id in sequence_ids:
                expected_pairs.add((sequence_id, str(profile_id)))

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
    generation_by_fixture = {
        sequence.get("fixture_id"): sequence.get("task_family_generation")
        for sequence in sequences
        if isinstance(sequence, dict)
    }
    for fixture in fixtures:
        generation = str(generation_by_fixture.get(fixture.get("id"), "baseline-v3"))
        generation_label = generation.replace("baseline-v", "Baseline V")
        current_family = fixture.get("current_task_family")
        if not isinstance(current_family, dict) or current_family.get("generation") != generation:
            errors.append(
                f"repository fixture {fixture.get('id')} current_task_family generation must match active sequence generation {generation}"
            )
        required_blocker = f"{generation_label} strongest-model provider pilot must complete with all eight required observed categories recorded as strict integer zero before treatment launch."
        if required_blocker not in fixture.get("blockers", []):
            errors.append(f"repository fixture {fixture.get('id')} must state the complete strict eight-category {generation_label} blocker")
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
        if sequence.get("status") != "active":
            errors.append(f"workflow sequence {sid} must be active; lifecycle v0 keeps no parallel planned or retired lanes")
        if not str(sid).endswith("-lifecycle-sequence-v0"):
            errors.append(f"workflow sequence {sid} must use the lifecycle-sequence-v0 identity")
        if sequence.get("sequence_contract") != "feature-refactor-review":
            errors.append(f"workflow sequence {sid} must use the feature-refactor-review contract")
        is_active = sequence.get("status") == "active"
        if is_active:
            generation = sequence.get("task_family_generation")
            if generation not in {"baseline-v3", "baseline-v4"}:
                errors.append(f"active workflow sequence {sid} must bind task_family_generation=baseline-v3 or baseline-v4")
            gate = sequence.get("mistake_gate")
            expected_gate = {
                "designated_model_condition": "codex-openai-gpt-5-6-sol-high",
                "model": "gpt-5.6-sol",
                "reasoning_effort": "high",
                "allowed_unique_model_incidents": 0,
                "allowed_corrected_implementation_mistakes": 0,
                "allowed_unresolved_defects": 0,
                "allowed_prohibited_operations": 0,
                "allowed_unnecessary_exploration_incidents": 0,
                "allowed_model_caused_failed_commands": 0,
                "allowed_code_rework_events": 0,
                "allowed_verifier_or_environment_failures": 0,
                "incident_counting": "unique-auditable-not-command-count",
                "pilot_audit_path": f"sources/evaluations/audits/{generation}-pilot-zero-mistake.json",
                "attempt_receipt_path": f"sources/evaluations/audits/{generation}-pilot-attempt-{str(sid).split('-lifecycle-sequence-v0')[0]}.json",
                "status": "provider-pilot-required",
                "treatment_launch_policy": "blocked until one first-valid strongest-model pilot is independently audited with all eight required observed counts equal to integer zero",
            }
            if generation == "baseline-v4":
                expected_gate["pilot_authorization_path"] = "sources/evaluations/audits/baseline-v4-task-family-qualification-20260722.json"
            allowed_gate_fields = [key for key in expected_gate if key.startswith("allowed_")]
            gate_values_match = (
                isinstance(gate, dict)
                and all(gate.get(key) == value for key, value in expected_gate.items())
                and all(type(gate.get(key)) is int and gate.get(key) == 0 for key in allowed_gate_fields)
            )
            if not gate_values_match:
                errors.append(f"active workflow sequence {sid} must preserve the {generation} zero-mistake gate with strict integer-zero allowances")
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
            if "declared focused acceptance tests" not in str(sequence.get("reset_policy", "")):
                errors.append(f"active workflow sequence {sid} reset policy must retain declared model-visible acceptance tests")
            if "complete acceptance behavior stays model-visible" not in str(sequence.get("seed_patch_policy", "")):
                errors.append(f"active workflow sequence {sid} seed policy must not describe acceptance as controller-only")
        qualification_path = str(sequence.get("qualification_path", ""))
        qualification_name = Path(qualification_path).name
        expected_qualification_name = f"qualification-lifecycle-v0-{sequence.get('task_family_generation')}.json"
        if is_active and qualification_name != expected_qualification_name:
            errors.append(f"active workflow sequence {sid} must bind {expected_qualification_name}")
        elif re.fullmatch(r"qualification-lifecycle-v0(?:-[a-z0-9-]+)?\.json", qualification_name) is None:
            errors.append(f"workflow sequence {sid} must bind a versioned qualification-lifecycle-v0 JSON artifact")
        if sequence.get("status") == "active" and sequence.get("acceptance_design") != "behavioral":
            errors.append(f"active workflow sequence {sid} must declare acceptance_design=behavioral")
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
            if not str(tid or "").endswith("-v0"):
                errors.append(f"workflow sequence {sid} task {tid} must use a v0 identity")
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
                    generation_label = str(sequence.get("task_family_generation", "")).replace("baseline-v", "Baseline V")
                    required_markers = (
                        f"{generation_label} mechanical",
                        "Do not discover or redesign anything.",
                        "Copy and run this command exactly:",
                        "Do not inspect, search, modify tests, run anything else, or evaluate aggregate Git state.",
                        "stop immediately when it exits 0",
                    )
                    generation_path = f"/{sequence.get('task_family_generation')}/"
                    if generation_path not in str(prompt_path) or any(marker not in prompt_text for marker in required_markers):
                        errors.append(f"active workflow sequence {sid} task {tid} must use the complete {generation_label} routine prompt contract")
                    target_production = [
                        path
                        for path in production
                        if not path.endswith(("_test.go", "_test.py", ".test.js")) and not path.startswith("test/")
                    ]
                    expected_changed = task.get("expected_changed_paths")
                    if not isinstance(expected_changed, list) or sorted(expected_changed) != sorted(target_production) or not 1 <= len(target_production) <= 3:
                        errors.append(f"active workflow sequence {sid} task {tid} must declare one-to-three exact Baseline V3 production targets")
                    anchors = task.get("model_visible_validation_anchors")
                    acceptance_asset_paths = task.get("model_visible_acceptance_asset_paths")
                    verifier_text = verifier_path.read_text() if verifier_path.is_file() else ""
                    if task.get("acceptance_visibility") != "model-visible-complete":
                        errors.append(f"active workflow sequence {sid} task {tid} must declare complete model-visible acceptance")
                    undisclosed_inline_markers = ("<<'NODE'", '<<"NODE"', "<<'PY'", '<<"PY"', "<<'TS'", '<<"TS"', "workflow-hidden")
                    if any(marker in verifier_text and marker not in prompt_text for marker in undisclosed_inline_markers):
                        errors.append(f"active workflow sequence {sid} task {tid} contains undisclosed inline verifier assertions")
                    if not isinstance(anchors, list) or not anchors or any(anchor not in prompt_text or anchor not in verifier_text for anchor in anchors):
                        errors.append(f"active workflow sequence {sid} task {tid} must bind complete model-visible focused validation anchors")
                    expected_acceptance_assets = BASELINE_V3_ACCEPTANCE_ASSET_PATHS.get(str(tid))
                    if (
                        expected_acceptance_assets is None
                        or not isinstance(acceptance_asset_paths, list)
                        or acceptance_asset_paths != expected_acceptance_assets
                    ):
                        errors.append(f"active workflow sequence {sid} task {tid} must declare the exact file-backed Baseline V3 acceptance assets")
                    elif not isinstance(anchors, list) or any(
                        asset not in anchors
                        or asset not in prompt_text
                        or asset not in verifier_text
                        or not (task_dir / "controller-visible" / asset).is_file()
                        for asset in expected_acceptance_assets
                    ):
                        errors.append(f"active workflow sequence {sid} task {tid} has missing or unbound canonical acceptance assets")
                    if task.get("model_concealed_paths"):
                        errors.append(f"active workflow sequence {sid} task {tid} must not hide Baseline V3 validation behavior")
                    if verifier_uses_source_identity(task_dir):
                        errors.append(f"active workflow sequence {sid} task {tid} uses exact-source supplemental guards instead of behavioral acceptance")
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
    if len(active) != 3:
        errors.append(f"production lifecycle-v0 portfolio must contain exactly three active sequences, found {len(active)}")
    if len({sequence.get("fixture_id") for sequence in active}) != len(active):
        errors.append("each lifecycle v0 sequence must own a distinct fixture")
    forbidden_contract_phrases = (
        "one task at a time",
        "alternative-repair",
        "ordered transitions",
    )
    for sequence in active:
        policy = str(sequence.get("seed_patch_policy", "")).lower()
        if "composite broken start" not in policy or "final prompt" not in policy:
            errors.append(f"active workflow sequence {sequence.get('id')} must declare composite pre-seeding and final-only verification")
        if any(phrase in policy for phrase in forbidden_contract_phrases):
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
                v2_readme = fixture_root / "task-generations/baseline-v2/README.md"
                try:
                    fixture_text = fixture_readme.read_text()
                    tasks_text = tasks_readme.read_text()
                    v2_text = v2_readme.read_text()
                except OSError as exc:
                    errors.append(f"fixture {record.get('id')} active-generation documentation is unreadable: {exc}")
                else:
                    generation = str(sequences[sequence_id].get("task_family_generation", ""))
                    generation_label = generation.replace("baseline-v", "Baseline V")
                    if qualification_path.name not in fixture_text or generation not in fixture_text:
                        errors.append(f"fixture {record.get('id')} README does not identify the active {generation_label} qualification")
                    if f"active {generation_label}" not in tasks_text:
                        errors.append(f"fixture {record.get('id')} tasks README does not identify the active {generation_label} generation")
                    if "Active lifecycle-v0 generation" in v2_text or "future execution" in v2_text:
                        errors.append(f"fixture {record.get('id')} Baseline V2 README incorrectly presents a retired generation as active")
            if not active and qualification == "active-reproduction-flow":
                errors.append(f"{label} {record.get('id')} cannot be active-reproduction-flow while sequence {sequence_id} is {statuses[sequence_id]}")
            if not active and record.get("active_profiles"):
                errors.append(f"{label} {record.get('id')} cannot list active_profiles while sequence {sequence_id} is {statuses[sequence_id]}")


def canonical_json_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_required_object(parent: dict, key: str, sid: str, errors: list[str]) -> dict | None:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"workflow session {sid} production-v3 record must include object {key}")
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


def validate_production_v3_schema_shape(session: dict, sid: str, errors: list[str]) -> None:
    required = (
        "schema_version",
        "session_id",
        "record_type",
        "evidence_type",
        "study_id",
        "experiment_group_id",
        "objective",
        "evidence_stage",
        "status",
        "session_role",
        "replicate_index",
        "date",
        "target",
        "task_sequence",
        "profile",
        "agent",
        "state_policy",
        "cumulative_token_usage",
        "per_task_results",
        "software_quality",
        "artifacts",
        "interpretation",
        "frozen_protocol",
        "baseline_pool",
        "selected_execution",
        "docker_image_identity",
        "tool_adapter_identity",
    )
    for key in required:
        if key not in session:
            errors.append(f"workflow session {sid} production-v3 record missing schema field {key}")
    if type(session.get("schema_version")) is not int or session.get("schema_version") not in {1, 2}:
        errors.append(f"workflow session {sid} schema_version must be 1 or 2")
    if session.get("record_type") != "workflow_session":
        errors.append(f"workflow session {sid} record_type must be workflow_session")
    if session.get("evidence_type") not in WORKFLOW_EVIDENCE_TYPES:
        errors.append(f"workflow session {sid} evidence_type is invalid")
    if session.get("objective") not in OBJECTIVES:
        errors.append(f"workflow session {sid} objective is invalid")
    if session.get("evidence_stage") not in {"benchmark_audit", "reproduction"}:
        errors.append(f"workflow session {sid} evidence_stage is invalid")
    if session.get("status") not in EVALUATION_STATUSES:
        errors.append(f"workflow session {sid} status is invalid")
    if session.get("session_role") not in WORKFLOW_SESSION_ROLES:
        errors.append(f"workflow session {sid} session_role is invalid")
    if type(session.get("replicate_index")) is not int or session.get("replicate_index", -1) < 0:
        errors.append(f"workflow session {sid} replicate_index must be a non-negative integer")
    for key in ("target", "task_sequence", "profile", "agent", "state_policy", "cumulative_token_usage", "software_quality", "artifacts", "interpretation"):
        if not isinstance(session.get(key), dict):
            errors.append(f"workflow session {sid} {key} must be an object")
    for key in ("state_observations", "operational_reproducibility", "execution_integrity"):
        if key in session and not isinstance(session[key], dict):
            errors.append(f"workflow session {sid} {key} must be an object when present")
    if not isinstance(session.get("per_task_results"), list):
        errors.append(f"workflow session {sid} per_task_results must be an array")
    validate_invalid_fixture_disposition(session, sid, errors)
    validate_invalid_treatment_disposition(session, sid, errors)
    if requires_structured_task_contract(session):
        validate_structured_task_outcomes(session, sid, errors)


def validate_docker_identity(identity: object, expected: object, sid: str, errors: list[str]) -> None:
    if not isinstance(identity, dict):
        errors.append(f"workflow session {sid} production-v3 record must include Docker image immutable identity")
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
    if profile_id == "baseline-bare-codex":
        if identity is not None:
            errors.append(f"workflow session {sid} baseline production-v3 record must not publish a treatment tool identity")
        return
    if not isinstance(identity, dict):
        errors.append(f"workflow session {sid} treatment production-v3 record must include tool adapter identity")
        return
    binary = identity.get("binary_identity")
    if not isinstance(binary, dict):
        errors.append(f"workflow session {sid} treatment production-v3 record must include tool adapter binary identity")
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


def validate_production_v3_identity(session: dict, run_record: dict | None, sid: str, errors: list[str]) -> None:
    validate_production_v3_schema_shape(session, sid, errors)
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
        errors.append(f"workflow session {sid} production-v3 record must include selected_execution descriptor")
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


def validate_workflow_session_contract(session: dict, canonical_profile: dict | None, errors: list[str]) -> None:
    sid = session.get("session_id") or session.get("id") or "<unknown>"
    sequence = session.get("task_sequence", {})
    frozen_protocol = session.get("frozen_protocol")
    production_v3 = requires_structured_task_contract(session) or (
        isinstance(frozen_protocol, dict)
        and str(frozen_protocol.get("protocol_id", "")).endswith("-v3")
    )
    if production_v3:
        validate_production_v3_identity(session, None, sid, errors)
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
                errors.append(f"workflow session {sid} must use the lifecycle v0 composite seed-delivery contract")
        leakage_controls = sequence.get("leakage_controls") if isinstance(sequence, dict) else None
        precise_visibility = (
            isinstance(leakage_controls, dict)
            and "controller_verifier_scripts_and_canonical_copies_model_visible" in leakage_controls
        )
        verifier_visibility_valid = (
            isinstance(leakage_controls, dict)
            and (
                (
                    leakage_controls.get("controller_verifier_scripts_and_canonical_copies_model_visible") is False
                    and isinstance(leakage_controls.get("model_visible_acceptance_asset_paths"), list)
                    and bool(leakage_controls.get("model_visible_acceptance_asset_paths"))
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
        objective_visibility_valid = (
            (
                leakage_controls.get("controller_verifier_scripts_and_canonical_copies_model_visible") is False
                and isinstance(leakage_controls.get("model_visible_acceptance_asset_paths"), list)
                and bool(leakage_controls.get("model_visible_acceptance_asset_paths"))
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


def validate_workflow_sessions(session_doc: dict, sequence_ids: set[str], fixture_doc: dict, profiles_by_id: dict[str, dict], runtime_ids: set[str], model_condition_ids: set[str], errors: list[str]) -> None:
    if session_doc.get("schema_version") != 1:
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
        if session.get("record_type") != "workflow_session":
            errors.append(f"workflow session {sid} has invalid record_type: {session.get('record_type')}")
        if session.get("evidence_type") not in WORKFLOW_EVIDENCE_TYPES:
            errors.append(f"workflow session {sid} has invalid evidence_type: {session.get('evidence_type')}")
        if session.get("objective") not in OBJECTIVES:
            errors.append(f"workflow session {sid} has invalid objective: {session.get('objective')}")
        if session.get("evidence_stage") not in {"benchmark_audit", "reproduction"}:
            errors.append(f"workflow session {sid} has invalid evidence_stage: {session.get('evidence_stage')}")
        if session.get("status") not in EVALUATION_STATUSES:
            errors.append(f"workflow session {sid} has invalid status: {session.get('status')}")
        if session.get("session_role") not in WORKFLOW_SESSION_ROLES:
            errors.append(f"workflow session {sid} has invalid session_role: {session.get('session_role')}")
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
        baseline_profile = profile_id == "baseline-bare-codex"
        expected_session_role = (
            "baseline"
            if baseline_profile
            else "stack_treatment"
            if isinstance(canonical_profile, dict) and canonical_profile.get("profile_type") == "tool_stack"
            else "individual_tool_treatment"
            if isinstance(canonical_profile, dict)
            else None
        )
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
        validate_workflow_session_contract(session, canonical_profile, errors)
        interpretation = session.get("interpretation", {}) if isinstance(session.get("interpretation"), dict) else {}
        comparison_id = interpretation.get("comparison_baseline_session_id")
        accepted_for_objective = interpretation.get("accepted_for_objective") is True
        if strict_session_contract and not baseline_profile and accepted_for_objective and not comparison_id:
            errors.append(f"accepted treatment workflow session {sid} requires a comparison baseline binding")
        if strict_session_contract and baseline_profile and comparison_id:
            errors.append(f"baseline workflow session {sid} must not carry a comparison baseline binding")
        if comparison_id:
            baseline = sessions_by_id.get(comparison_id)
            if baseline is None:
                errors.append(f"workflow session {sid} references missing comparison baseline {comparison_id}")
            elif (
                baseline.get("replicate_index") != session.get("replicate_index")
                or baseline.get("baseline_pool", {}).get("protocol_fingerprint")
                != session.get("baseline_pool", {}).get("protocol_fingerprint")
                or baseline.get("task_sequence", {}).get("sequence_id")
                != session.get("task_sequence", {}).get("sequence_id")
                or baseline.get("session_role") != "baseline"
                or baseline.get("profile", {}).get("profile_id") != "baseline-bare-codex"
                or baseline.get("status") != "completed"
                or baseline.get("interpretation", {}).get("accepted_for_objective") is not True
                or baseline.get("selected_execution", {}).get("descriptor", {}).get("execution_role") != "baseline"
                or baseline.get("selected_execution", {}).get("descriptor", {}).get("selected_profile", {}).get("profile_id")
                != "baseline-bare-codex"
            ):
                errors.append(f"workflow session {sid} comparison baseline {comparison_id} is not a canonical sequence-, pool-, and replicate-matched baseline")
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
                production_v3 = requires_structured_task_contract(session) or (
                    isinstance(frozen_protocol, dict)
                    and str(frozen_protocol.get("protocol_id", "")).endswith("-v3")
                )
                if production_v3:
                    try:
                        run_record = json.loads((root / "run.json").read_text())
                    except Exception as exc:
                        errors.append(f"workflow session {sid} run.json cannot be parsed: {exc}")
                    else:
                        validate_production_v3_identity(session, run_record, sid, errors)
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
        interpretation = session.get("interpretation", {})
        if profile_id == "baseline-bare-codex" or interpretation.get("accepted_for_objective") is not True:
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


def validate_compact_manifest(root: Path, sid: str, errors: list[str]) -> None:
    allowed_names = {"run.json", "changes.diff", "evidence.jsonl.gz", "manifest.sha256"}
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


def validate_retired_baseline_v2_audit(errors: list[str]) -> None:
    audit_path = ROOT / "sources/evaluations/audits/baseline-v2-task-family-qualification-20260721.json"
    pilot_path = ROOT / "sources/evaluations/audits/baseline-v2-pilot-zero-mistake.json"
    try:
        audit = json.loads(audit_path.read_text())
        pilot = json.loads(pilot_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"retired Baseline V2 authority cannot be read: {exc}")
        return
    supersession = audit.get("supersession", {})
    retired_valid = (
        audit.get("task_family_generation") == "baseline-v2"
        and str(audit.get("decision", "")).startswith("Retire Baseline V2 permanently")
        and supersession.get("status") == "retired-failed-pilot-identity-occupied"
        and supersession.get("superseded_by_generation") == "baseline-v3"
        and supersession.get("paid_pilot_audit") == "sources/evaluations/audits/baseline-v2-pilot-zero-mistake.json"
        and supersession.get("paid_pilot_passed") is False
        and supersession.get("rerun_allowed") is False
        and supersession.get("treatment_launch_allowed") is False
        and audit.get("mistake_gate", {}).get("status") == "failed-pilot-identity-occupied"
        and audit.get("zero_mistake_gate", {}).get("status") == "failed-pilot-identity-occupied"
        and audit.get("treatment_gate", {}).get("status") == "blocked-failed-pilot-identity-occupied"
        and audit.get("treatment_gate", {}).get("pilot_audit_present") is True
        and audit.get("protocols") == []
        and audit.get("totals", {}).get("frozen_pilot_protocols") == 0
        and all(item.get("frozen_baseline_protocols") == [] for item in audit.get("sequences", []))
        and pilot.get("passed") is False
        and pilot.get("status") == "failed-operationally-invalid"
        and pilot.get("publication_status") == "rolled-back-no-sessions-or-comparisons-published"
    )
    if not retired_valid:
        errors.append("retired Baseline V2 qualification authority is stale, runnable, dangling, or inconsistent with its failed pilot")


def validate_baseline_v3_qualification_audit(errors: list[str]) -> None:
    audit_path = ROOT / "sources/evaluations/audits/baseline-v3-task-family-qualification-20260722.json"
    try:
        audit = json.loads(audit_path.read_text())
        sequences_doc = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Baseline V3 qualification audit cannot be read: {exc}")
        return
    v3_sequence_ids = {
        "fastify-lifecycle-sequence-v0",
        "beets-lifecycle-sequence-v0",
        "terraform-lifecycle-sequence-v0",
    }
    active_sequences: dict[str, dict] = {}
    for source_sequence in sequences_doc.get("sequences", []):
        if source_sequence.get("id") not in v3_sequence_ids:
            continue
        sequence = json.loads(json.dumps(source_sequence))
        sequence["task_family_generation"] = "baseline-v3"
        sequence["qualification_path"] = str(sequence.get("qualification_path", "")).replace(
            "baseline-v4", "baseline-v3"
        )
        for task in sequence.get("tasks", []):
            for key in ("prompt_path", "verifier_command"):
                task[key] = str(task.get(key, "")).replace("baseline-v4", "baseline-v3")
        active_sequences[str(sequence["id"])] = sequence

    strict_numeric_keys = {
        "schema_version",
        "persistent_tasks_per_sequence",
        "production_files_per_task_maximum",
        "task_count",
        "expected_model_visible_acceptance_asset_count",
        "provider_free_qualified_sequences",
        "frozen_pilot_protocols",
        "provider_free_lanes",
        "prepared_lanes",
        "undisclosed_inline_verifier_assertions",
        "contract_tests",
        "contract_tests_passed",
        "truthmark_diagnostics",
        "prepare_matrix_lanes",
        "prepare_matrix_passed",
        "order",
        "prompt_command_exit",
        "controller_verifier_exit",
        "receipt_count",
        "post_reservation_contract_tests",
        "dependency_bootstrap_lanes",
        "literal_command_tasks",
        "controller_verifier_tasks",
    }

    def validate_provider_free_numbers(value: object, path: str = "audit") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = f"{path}.{key}"
                numeric_scalar = (
                    key in strict_numeric_keys
                    or key.startswith("allowed_")
                    or (path == "audit.totals" and key in {"sequences", "tasks"})
                )
                if numeric_scalar and type(child) is not int:
                    errors.append(f"Baseline V3 decision-bearing numeric field must be a strict non-boolean integer: {child_path}")
                if key == "production_file_counts" and (
                    not isinstance(child, list) or any(type(item) is not int for item in child)
                ):
                    errors.append(f"Baseline V3 production file counts must be strict non-boolean integers: {child_path}")
                if key in {"provider_calls", "provider_tokens"} and (type(child) is not int or child != 0):
                    errors.append(f"Baseline V3 provider-free numeric field must be strict integer zero: {child_path}")
                validate_provider_free_numbers(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                validate_provider_free_numbers(child, f"{path}[{index}]")

    validate_provider_free_numbers(audit)
    audit_sequence_items = [item for item in audit.get("sequences", []) if isinstance(item, dict)]
    protocol_items = [item for item in audit.get("protocols", []) if isinstance(item, dict)]
    audit_sequence_ids = [item.get("sequence_id") for item in audit_sequence_items]
    protocol_sequence_ids = [item.get("sequence_id") for item in protocol_items]
    audit_sequences = {item.get("sequence_id"): item for item in audit_sequence_items}
    current_refs = {item.get("sequence_id"): item for item in protocol_items}
    rehearsal = audit.get("literal_prompt_command_rehearsal")
    rehearsal_items = (
        [item for item in rehearsal.get("sequences", []) if isinstance(item, dict)]
        if isinstance(rehearsal, dict)
        else []
    )
    rehearsal_sequence_ids = [item.get("sequence_id") for item in rehearsal_items]
    rehearsal_sequences = {item.get("sequence_id"): item for item in rehearsal_items}
    multiplicity_valid = all(
        len(items) == len(active_sequences)
        and len(ids) == len(set(ids))
        for items, ids in (
            (audit_sequence_items, audit_sequence_ids),
            (protocol_items, protocol_sequence_ids),
            (rehearsal_items, rehearsal_sequence_ids),
        )
    )
    if not multiplicity_valid:
        errors.append("Baseline V3 qualification audit must not contain missing or duplicate sequence identities")
    if (
        not isinstance(rehearsal, dict)
        or rehearsal.get("status") != "passed"
        or type(rehearsal.get("provider_calls")) is not int
        or rehearsal.get("provider_calls") != 0
        or type(rehearsal.get("provider_tokens")) is not int
        or rehearsal.get("provider_tokens") != 0
        or set(rehearsal_sequences) != set(active_sequences)
    ):
        errors.append("Baseline V3 qualification audit must record one zero-provider passed literal prompt-command rehearsal for every active sequence")
    else:
        for sequence_id, sequence in active_sequences.items():
            expected = [
                (str(task["id"]), int(task["order"]), 0, 0, True)
                for task in sorted(sequence.get("tasks", []), key=lambda item: int(item["order"]))
            ]
            observed = [
                (
                    str(task.get("task_id")),
                    task.get("order"),
                    task.get("prompt_command_exit"),
                    task.get("controller_verifier_exit"),
                    task.get("model_visible_focused_test_selected"),
                )
                for task in rehearsal_sequences[sequence_id].get("tasks", [])
                if isinstance(task, dict)
            ]
            numeric_values_valid = all(
                type(value) is int
                for row in observed
                for value in row[1:4]
            )
            if observed != expected or not numeric_values_valid:
                errors.append(f"Baseline V3 literal prompt-command rehearsal is incomplete for {sequence_id}")

    receipt_index_path = ROOT / "sources/evaluations/audits/baseline-v3-literal-command-receipts-20260722/index.json"
    try:
        receipt_index = json.loads(receipt_index_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Baseline V3 immutable literal-command receipt index is unreadable: {exc}")
        receipt_index = {}
    expected_tasks = {
        str(task["id"]): (sequence_id, task, sequence)
        for sequence_id, sequence in active_sequences.items()
        for task in sequence.get("tasks", [])
    }
    receipt_items = [item for item in receipt_index.get("receipts", []) if isinstance(item, dict)]
    receipt_task_ids = [str(item.get("task_id")) for item in receipt_items]
    if (
        type(receipt_index.get("schema_version")) is not int
        or receipt_index.get("schema_version") != 1
        or receipt_index.get("passed") is not True
        or type(receipt_index.get("provider_calls")) is not int
        or receipt_index.get("provider_calls") != 0
        or type(receipt_index.get("provider_tokens")) is not int
        or receipt_index.get("provider_tokens") != 0
        or type(receipt_index.get("receipt_count")) is not int
        or receipt_index.get("receipt_count") != len(expected_tasks)
        or len(receipt_items) != len(expected_tasks)
        or len(receipt_task_ids) != len(set(receipt_task_ids))
        or set(receipt_task_ids) != set(expected_tasks)
    ):
        errors.append("Baseline V3 immutable literal-command receipt index must cover each active task exactly once with zero provider use")
    else:
        expected_image_id = "sha256:6f86d01f2c63f5029c6bb874d8f3694c24d5cd567e3d09413eccc956ba3feafe"
        for item in receipt_items:
            task_id = str(item["task_id"])
            sequence_id, task, sequence = expected_tasks[task_id]
            receipt_path = ROOT / str(item.get("path"))
            try:
                receipt_bytes = receipt_path.read_bytes()
                receipt = json.loads(receipt_bytes)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"Baseline V3 literal-command receipt {task_id} is unreadable: {exc}")
                continue
            prompt_path = ROOT / str(task.get("prompt_path"))
            verifier_path = ROOT / str(task.get("verifier_command"))
            prompt_text = prompt_path.read_text()
            command_match = re.search(r"```bash\n(.*?)\n```", prompt_text, re.S)
            command_block = command_match.group(1) if command_match else ""
            selected_names = (
                sorted(set(re.findall(r"Test[A-Za-z0-9_]+", command_block)))
                if sequence_id == "terraform-lifecycle-sequence-v0"
                else []
            )
            literal = receipt.get("literal_command", {})
            verifier = receipt.get("controller_verifier", {})
            bootstrap = receipt.get("production_bootstrap", {})
            command_log = ROOT / str(literal.get("log_path"))
            verifier_log = ROOT / str(verifier.get("log_path"))
            bootstrap_log = ROOT / str(bootstrap.get("log_path"))
            hashes_valid = all(
                path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash
                for path, expected_hash in (
                    (receipt_path, str(item.get("sha256"))),
                    (prompt_path, str(literal.get("prompt_sha256"))),
                    (verifier_path, str(verifier.get("sha256"))),
                    (command_log, str(literal.get("log_sha256"))),
                    (verifier_log, str(verifier.get("log_sha256"))),
                    (bootstrap_log, str(bootstrap.get("log_sha256"))),
                )
            )
            receipt_valid = (
                type(receipt.get("schema_version")) is int
                and receipt.get("schema_version") == 1
                and receipt.get("passed") is True
                and type(receipt.get("provider_calls")) is int
                and receipt.get("provider_calls") == 0
                and type(receipt.get("provider_tokens")) is int
                and receipt.get("provider_tokens") == 0
                and receipt.get("sequence_id") == sequence_id
                and receipt.get("task_id") == task_id
                and type(receipt.get("task_order")) is int
                and receipt.get("task_order") == task.get("order")
                and receipt.get("fixture_commit") == sequence.get("initial_snapshot", {}).get("commit")
                and receipt.get("dependency_lockfiles") == sequence.get("initial_snapshot", {}).get("dependency_lockfiles")
                and receipt.get("container", {}).get("image_id") == expected_image_id
                and bootstrap.get("shell") == ["bash", "-c"]
                and type(bootstrap.get("exit_code")) is int
                and bootstrap.get("exit_code") == 0
                and literal.get("command_block") == command_block
                and literal.get("command_sha256") == hashlib.sha256((command_block + "\n").encode()).hexdigest()
                and type(literal.get("exit_code")) is int
                and literal.get("exit_code") == 0
                and literal.get("selected_test_names") == selected_names
                and type(verifier.get("exit_code")) is int
                and verifier.get("exit_code") == 0
                and hashes_valid
            )
            if not receipt_valid:
                errors.append(f"Baseline V3 immutable literal-command receipt is invalid for {task_id}")
    if set(audit_sequences) != set(active_sequences) or set(current_refs) != set(active_sequences):
        errors.append("Baseline V3 qualification audit must cover exactly the active sequences")
        return
    for sequence_id, sequence in active_sequences.items():
        entry = audit_sequences[sequence_id]
        current_ref = current_refs[sequence_id]
        frozen_refs = entry.get("frozen_baseline_protocols")
        protocol_rel = current_ref.get("path")
        if not isinstance(protocol_rel, str) or not protocol_rel:
            errors.append(f"Baseline V3 audit {sequence_id} current protocol path is missing")
            continue
        protocol_path = ROOT / protocol_rel
        try:
            protocol_bytes = protocol_path.read_bytes()
            protocol = json.loads(protocol_bytes)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"Baseline V3 audit {sequence_id} current protocol is unreadable: {exc}")
            continue
        qualification_rel = sequence.get("qualification_path")
        qualification_path = ROOT / str(qualification_rel)
        try:
            qualification_sha = hashlib.sha256(qualification_path.read_bytes()).hexdigest()
        except OSError as exc:
            errors.append(f"Baseline V3 audit {sequence_id} qualification is unreadable: {exc}")
            continue
        protocol_sha = hashlib.sha256(protocol_bytes).hexdigest()
        protocol_id = protocol.get("protocol_id")
        selected = protocol.get("selected_execution", {})
        descriptor = selected.get("descriptor", {}) if isinstance(selected, dict) else {}
        model_condition_id = descriptor.get("agent_condition", {}).get("model_condition_id")
        expected_frozen = {
            "path": protocol_rel,
            "protocol_id": protocol_id,
            "protocol_sha256": protocol_sha,
            "status": protocol.get("status"),
            "baseline_pool_fingerprint": protocol.get("baseline_pool", {}).get("protocol_fingerprint"),
            "qualification_sha256": qualification_sha,
            "selected_execution_sha256": selected.get("descriptor_sha256") if isinstance(selected, dict) else None,
            "model_condition_id": model_condition_id,
        }
        if current_ref != {
            "sequence_id": sequence_id,
            "protocol_id": protocol_id,
            "path": protocol_rel,
            "sha256": protocol_sha,
        }:
            errors.append(f"Baseline V3 audit {sequence_id} current protocol reference is stale")
        if frozen_refs != [expected_frozen]:
            errors.append(f"Baseline V3 audit {sequence_id} frozen baseline protocol reference is stale")
        if (
            entry.get("current_protocol_id") != protocol_id
            or entry.get("current_protocol_path") != protocol_rel
        ):
            errors.append(f"Baseline V3 audit {sequence_id} per-sequence current protocol binding is stale")
        if entry.get("qualification_path") != qualification_rel or entry.get("qualification_sha256") != qualification_sha:
            errors.append(f"Baseline V3 audit {sequence_id} qualification reference is stale")
        task_fixture = protocol.get("task_fixture", {})
        if (
            protocol_id != protocol_path.stem
            or task_fixture.get("qualification_path") != qualification_rel
            or task_fixture.get("qualification_sha256") != qualification_sha
            or model_condition_id != "codex-openai-gpt-5-6-sol-high"
        ):
            errors.append(f"Baseline V3 audit {sequence_id} does not identify the current canonical pilot protocol")
    prepare = audit.get("latest_prepare_matrix")
    if prepare != {
        "evidence_classification": "non-authoritative-scratch",
        "repository_artifact": None,
        "provider_free_lanes": 3,
        "prepared_lanes": 3,
        "provider_calls": 0,
        "provider_tokens": 0,
    }:
        errors.append("Baseline V3 qualification audit prepare-matrix note must remain non-authoritative scratch metadata")


def validate_baseline_v4_evidence_identity(
    audit: dict[str, Any],
    index: dict[str, Any],
    receipt_documents: dict[str, dict[str, Any]],
    prepare_manifest: dict[str, Any],
    prepare_files: dict[str, bytes],
    expected_sequences: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    """Validate exact V4 task/evidence coverage and provider-free preparation identity."""
    ordered_sequence_ids = list(expected_sequences)
    records = audit.get("sequences")
    if not isinstance(records, list) or [item.get("sequence_id") for item in records if isinstance(item, dict)] != ordered_sequence_ids:
        errors.append("Baseline V4 audit sequence records must exactly cover active V4 sequences once and in order")
        return
    expected_coordinates: list[tuple[str, str, int]] = []
    nested_items: list[dict[str, Any]] = []
    for record in records:
        sequence_id = record["sequence_id"]
        sequence = expected_sequences[sequence_id]
        tasks = sorted(sequence.get("tasks", []), key=lambda item: int(item["order"]))
        if type(record.get("task_count")) is not int or record.get("task_count") != len(tasks):
            errors.append(f"Baseline V4 task_count must be a strict integer for {sequence_id}")
        if record.get("fixture_id") != sequence.get("fixture_id") or record.get("task_family_generation") != "baseline-v4":
            errors.append(f"Baseline V4 audit sequence identity is stale for {sequence_id}")
        expected_for_sequence = [(sequence_id, str(task["id"]), int(task["order"])) for task in tasks]
        expected_coordinates.extend(expected_for_sequence)
        nested = record.get("literal_command_receipts")
        if not isinstance(nested, list):
            errors.append(f"Baseline V4 nested receipts are missing for {sequence_id}")
            continue
        nested_items.extend(item for item in nested if isinstance(item, dict))
        actual_nested = [(item.get("sequence_id"), item.get("task_id")) for item in nested if isinstance(item, dict)]
        if actual_nested != [(item[0], item[1]) for item in expected_for_sequence]:
            errors.append(f"Baseline V4 nested receipts must exactly cover ordered tasks for {sequence_id}")

    receipts = index.get("receipts")
    if type(index.get("schema_version")) is not int or index.get("schema_version") != 1 or index.get("generation") != "baseline-v4":
        errors.append("Baseline V4 receipt index schema or generation is invalid")
    if not isinstance(receipts, list):
        errors.append("Baseline V4 receipt index is missing receipts")
        return
    actual_coordinates = [
        (item.get("sequence_id"), item.get("task_id"))
        for item in receipts
        if isinstance(item, dict)
    ]
    expected_pairs = [(item[0], item[1]) for item in expected_coordinates]
    if actual_coordinates != expected_pairs or len(receipts) != len(expected_pairs):
        errors.append("Baseline V4 receipt index must exactly cover every ordered task once")
    if nested_items != receipts:
        errors.append("Baseline V4 nested receipt references must exactly match the receipt index")
    if set(receipt_documents) != {str(item.get("path")) for item in receipts if isinstance(item, dict)}:
        errors.append("Baseline V4 receipt documents do not exactly match indexed paths")
    for item, (sequence_id, task_id, order) in zip(receipts, expected_coordinates, strict=False):
        if not isinstance(item, dict):
            errors.append("Baseline V4 receipt index entries must be objects")
            continue
        path = item.get("path")
        receipt = receipt_documents.get(str(path))
        if not isinstance(path, str) or not isinstance(receipt, dict):
            errors.append(f"Baseline V4 indexed receipt is missing: {path}")
            continue
        if (
            type(receipt.get("schema_version")) is not int
            or receipt.get("schema_version") != 1
            or receipt.get("generation") != "baseline-v4"
            or receipt.get("sequence_id") != sequence_id
            or receipt.get("task_id") != task_id
            or type(receipt.get("order")) is not int
            or receipt.get("order") != order
        ):
            errors.append(f"Baseline V4 receipt identity is invalid: {path}")

    if type(prepare_manifest.get("schema_version")) is not int or prepare_manifest.get("schema_version") != 1:
        errors.append("Baseline V4 prepare manifest schema_version must be strict integer 1")
    if prepare_manifest.get("generation") != "baseline-v4":
        errors.append("Baseline V4 prepare manifest generation is invalid")
    for key in ("provider_calls", "provider_tokens"):
        if type(prepare_manifest.get(key)) is not int or prepare_manifest.get(key) != 0:
            errors.append(f"Baseline V4 prepare manifest {key} must be strict integer zero")
    for key in ("execution_passed", "validation_passed", "authoritative_outputs_complete"):
        if prepare_manifest.get(key) is not True:
            errors.append(f"Baseline V4 prepare manifest {key} must be true")
    lane_exits = prepare_manifest.get("lane_exit_codes")
    if not isinstance(lane_exits, dict) or list(lane_exits) != ordered_sequence_ids or any(
        type(value) is not int or value != 0 for value in lane_exits.values()
    ):
        errors.append("Baseline V4 prepare manifest lane exits must exactly cover active V4 sequences with strict integer zero")
    declared_files = prepare_manifest.get("files")
    if not isinstance(declared_files, dict) or set(declared_files) != {"plan.json", "matrix-summary.json"}:
        errors.append("Baseline V4 prepare manifest must bind exactly plan.json and matrix-summary.json")
    else:
        for name, expected_sha in declared_files.items():
            content = prepare_files.get(name)
            if not isinstance(content, bytes) or hashlib.sha256(content).hexdigest() != expected_sha:
                errors.append(f"Baseline V4 prepare manifest file hash is stale: {name}")
    try:
        plan = json.loads(prepare_files["plan.json"], object_pairs_hook=_json_object_without_duplicate_keys)
        summary = json.loads(prepare_files["matrix-summary.json"], object_pairs_hook=_json_object_without_duplicate_keys)
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"Baseline V4 prepare evidence cannot be parsed: {exc}")
        return
    records_by_sequence = {record["sequence_id"]: record for record in records}
    expected_jobs = [
        {
            "sequence_id": sequence_id,
            "profile_id": "baseline-bare-codex",
            "protocol": records_by_sequence[sequence_id].get("protocol_path"),
        }
        for sequence_id in ordered_sequence_ids
    ]
    first_gate = expected_sequences[ordered_sequence_ids[0]].get("mistake_gate", {}) if ordered_sequence_ids else {}
    expected_condition = {
        "id": first_gate.get("designated_model_condition"),
        "model": first_gate.get("model"),
        "reasoning_effort": first_gate.get("reasoning_effort"),
    }
    if (
        plan.get("sequences") != ordered_sequence_ids
        or plan.get("treatment_profiles") != []
        or plan.get("jobs") != expected_jobs
        or type(plan.get("max_parallel")) is not int
        or plan.get("max_parallel") != 1
        or type(plan.get("replicate_index")) is not int
        or plan.get("replicate_index") != 0
        or plan.get("model_condition") != expected_condition
        or plan.get("runner_args") != ["--prepare-only", "--no-provider"]
    ):
        errors.append("Baseline V4 prepare plan does not match the exact provider-free serial V4 baseline matrix")
    if summary.get("plan") != plan:
        errors.append("Baseline V4 prepare summary plan does not match plan.json")
    lane_results = summary.get("lane_results")
    if not isinstance(lane_results, list) or [item.get("sequence_id") for item in lane_results if isinstance(item, dict)] != ordered_sequence_ids:
        errors.append("Baseline V4 prepare summary must contain exactly one ordered result per V4 sequence")
    else:
        for item, sequence_id in zip(lane_results, ordered_sequence_ids, strict=True):
            record = records_by_sequence[sequence_id]
            binding = item.get("expected_session_binding", {})
            frozen = binding.get("frozen_protocol", {}) if isinstance(binding, dict) else {}
            try:
                protocol = json.loads(
                    (ROOT / str(record.get("protocol_path"))).read_text(),
                    object_pairs_hook=_json_object_without_duplicate_keys,
                )
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"Baseline V4 prepare protocol cannot be loaded for {sequence_id}: {exc}")
                protocol = {}
            if (
                item.get("treatment_profile") != "baseline-bare-codex"
                or item.get("lane_id") != f"{sequence_id}--baseline-bare-codex"
                or type(item.get("exit_code")) is not int
                or item.get("exit_code") != 0
                or item.get("produced_session_ids") != []
                or item.get("failure_evidence") != []
                or binding.get("sequence_id") != sequence_id
                or binding.get("profile_id") != "baseline-bare-codex"
                or type(binding.get("replicate_index")) is not int
                or binding.get("replicate_index") != 0
                or frozen.get("protocol_id") != record.get("protocol_id")
                or frozen.get("path") != record.get("protocol_path")
                or frozen.get("sha256") != record.get("protocol_sha256")
                or binding.get("baseline_pool_fingerprint") != record.get("baseline_pool_fingerprint")
                or binding.get("selected_execution") != protocol.get("selected_execution")
            ):
                errors.append(f"Baseline V4 prepare lane identity is invalid for {sequence_id}")
    merge = summary.get("merge", {})
    if (
        type(merge.get("merged_session_count")) is not int
        or merge.get("merged_session_count") != 0
        or type(merge.get("copied_artifact_count")) is not int
        or merge.get("copied_artifact_count") != 0
        or merge.get("merged_session_ids") != []
        or merge.get("copied_artifacts") != []
        or merge.get("skipped") != "prepare-only run"
        or summary.get("published_comparisons") != []
        or summary.get("execution_passed") is not True
        or summary.get("authoritative_outputs_complete") is not True
    ):
        errors.append("Baseline V4 prepare summary must prove a provider-free, publication-free prepare-only result")
    validation = summary.get("validation", {})
    validation_results = validation.get("results") if isinstance(validation, dict) else None
    expected_validation_commands = [
        ["/opt/hermes/.venv/bin/python", "scripts/validate_repository.py"],
        ["/opt/hermes/.venv/bin/python", "scripts/test_workflow_evaluation_contract.py"],
        ["git", "diff", "--check"],
        ["/opt/data/.local/bin/truthmark", "check", "--json"],
        ["/opt/data/.local/bin/truthmark", "index", "--json"],
    ]
    if (
        validation.get("passed") is not True
        or not isinstance(validation_results, list)
        or [item.get("command") for item in validation_results if isinstance(item, dict)] != expected_validation_commands
        or any(
            not isinstance(item, dict) or type(item.get("exit_code")) is not int or item.get("exit_code") != 0
            for item in validation_results
        )
    ):
        errors.append("Baseline V4 prepare summary validation commands or results are incomplete, noncanonical, or nonzero")


def validate_baseline_v4_qualification_audit(errors: list[str]) -> None:
    audit_path = ROOT / "sources/evaluations/audits/baseline-v4-task-family-qualification-20260722.json"
    try:
        audit = json.loads(audit_path.read_text(), object_pairs_hook=_json_object_without_duplicate_keys)
        sequence_doc = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"Baseline V4 qualification audit cannot be read: {exc}")
        return
    if type(audit.get("schema_version")) is not int or audit.get("schema_version") != 1:
        errors.append("Baseline V4 qualification audit must use strict integer schema_version 1")
    for key in ("provider_calls", "provider_tokens"):
        if type(audit.get(key)) is not int or audit.get(key) != 0:
            errors.append(f"Baseline V4 qualification audit {key} must be strict integer zero")
    if audit.get("passed") is not True or audit.get("paid_pilot_authorized") is not False or audit.get("treatment_unlocked") is not False:
        errors.append("Baseline V4 qualification audit must pass provider-free while leaving paid pilot and treatment locked")
    if audit.get("task_difficulty_changed") is not False or audit.get("v3_attempt_evidence_mutated") is not False:
        errors.append("Baseline V4 qualification audit must preserve task difficulty and immutable V3 evidence")
    expected_sequences = {
        item["id"]: item
        for item in sequence_doc.get("sequences", [])
        if item.get("status") == "active" and item.get("task_family_generation") == "baseline-v4"
    }
    if set(audit.get("scope", [])) != set(expected_sequences):
        errors.append("Baseline V4 qualification audit scope must cover exactly the active V4 sequences")
    records = audit.get("sequences")
    if not isinstance(records, list) or {item.get("sequence_id") for item in records if isinstance(item, dict)} != set(expected_sequences):
        errors.append("Baseline V4 qualification audit must contain one record for each active V4 sequence")
        return
    index_rel = audit.get("literal_command_receipt_index")
    if not isinstance(index_rel, str):
        errors.append("Baseline V4 qualification audit is missing its literal receipt index")
        return
    index_path = ROOT / index_rel
    try:
        index_bytes = index_path.read_bytes()
        index = json.loads(index_bytes, object_pairs_hook=_json_object_without_duplicate_keys)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"Baseline V4 literal receipt index cannot be read: {exc}")
        return
    if hashlib.sha256(index_bytes).hexdigest() != audit.get("literal_command_receipt_index_sha256"):
        errors.append("Baseline V4 literal receipt index hash is stale")
    if any(type(index.get(key)) is not int or index.get(key) != 0 for key in ("provider_calls", "provider_tokens")):
        errors.append("Baseline V4 literal receipt index provider counts must be strict integer zero")
    receipts = index.get("receipts")
    if not isinstance(receipts, list) or len(receipts) != 6 or index.get("passed") is not True:
        errors.append("Baseline V4 literal receipt index must contain six passing receipts")
        return
    receipt_documents: dict[str, dict[str, Any]] = {}
    for item in receipts:
        receipt_path = ROOT / str(item.get("path", ""))
        try:
            receipt_bytes = receipt_path.read_bytes()
            receipt = json.loads(receipt_bytes, object_pairs_hook=_json_object_without_duplicate_keys)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"Baseline V4 literal receipt cannot be read: {exc}")
            continue
        receipt_documents[str(item.get("path", ""))] = receipt
        if hashlib.sha256(receipt_bytes).hexdigest() != item.get("sha256"):
            errors.append(f"Baseline V4 literal receipt hash is stale: {receipt_path}")
        for key in ("schema_version", "order", "provider_calls", "provider_tokens", "command_exit", "controller_verifier_exit"):
            if type(receipt.get(key)) is not int:
                errors.append(f"Baseline V4 literal receipt {receipt_path} {key} must be a strict integer")
        if any(receipt.get(key) != 0 for key in ("provider_calls", "provider_tokens", "command_exit", "controller_verifier_exit")) or receipt.get("passed") is not True:
            errors.append(f"Baseline V4 literal receipt did not pass provider-free: {receipt_path}")
    prepare_rel = audit.get("prepare_only_manifest")
    prepare_manifest: dict[str, Any] = {}
    prepare_files: dict[str, bytes] = {}
    if not isinstance(prepare_rel, str) or not prepare_rel:
        errors.append("Baseline V4 qualification audit is missing its prepare-only manifest")
    else:
        prepare_path = ROOT / prepare_rel
        try:
            prepare_bytes = prepare_path.read_bytes()
            prepare_manifest = json.loads(prepare_bytes, object_pairs_hook=_json_object_without_duplicate_keys)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"Baseline V4 prepare-only manifest cannot be read: {exc}")
        else:
            if hashlib.sha256(prepare_bytes).hexdigest() != audit.get("prepare_only_manifest_sha256"):
                errors.append("Baseline V4 prepare-only manifest hash is stale")
            declared_files = prepare_manifest.get("files")
            if isinstance(declared_files, dict):
                for name in declared_files:
                    if not isinstance(name, str) or PurePosixPath(name).name != name:
                        errors.append(f"Baseline V4 prepare-only manifest has unsafe file name: {name}")
                        continue
                    try:
                        prepare_files[name] = (prepare_path.parent / name).read_bytes()
                    except OSError as exc:
                        errors.append(f"Baseline V4 prepare-only evidence cannot be read: {name}: {exc}")
    validate_baseline_v4_evidence_identity(
        audit,
        index,
        receipt_documents,
        prepare_manifest,
        prepare_files,
        expected_sequences,
        errors,
    )
    from scripts import run_codex_workflow_evaluation as workflow
    for record in records:
        sequence = expected_sequences.get(record.get("sequence_id"))
        if sequence is None:
            continue
        qualification_path = ROOT / sequence["qualification_path"]
        try:
            qualification_bytes = qualification_path.read_bytes()
            qualification = json.loads(qualification_bytes)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"Baseline V4 qualification cannot be read: {exc}")
            continue
        if hashlib.sha256(qualification_bytes).hexdigest() != record.get("qualification_sha256"):
            errors.append(f"Baseline V4 qualification hash is stale for {sequence['id']}")
        exits = record.get("aggregate_verifier_task_exits")
        if record.get("aggregate_verifier_environment_passed") is not True or type(record.get("aggregate_verifier_exit")) is not int or record.get("aggregate_verifier_exit") != 0 or not isinstance(exits, list) or exits != [0, 0, 0] or any(type(value) is not int for value in exits):
            errors.append(f"Baseline V4 aggregate verifier did not execute all three tasks for {sequence['id']}")
        if qualification.get("aggregate_verifier_environment_passed") is not True:
            errors.append(f"Baseline V4 qualification lacks aggregate environment proof for {sequence['id']}")
        if qualification.get("task_family_generation") != "baseline-v4":
            errors.append(f"Baseline V4 qualification lacks explicit generation for {sequence['id']}")
        try:
            identity, protocol = workflow.current_baseline_v2_protocol(sequence, sequence["mistake_gate"], ROOT)
        except ValueError as exc:
            errors.append(f"Baseline V4 current protocol cannot be resolved for {sequence['id']}: {exc}")
            continue
        if record.get("protocol_id") != identity["protocol_id"] or record.get("protocol_path") != identity["path"] or record.get("protocol_sha256") != identity["sha256"] or record.get("baseline_pool_fingerprint") != identity["baseline_pool_fingerprint"]:
            errors.append(f"Baseline V4 protocol binding is stale for {sequence['id']}")
        if protocol.get("task_fixture", {}).get("qualification_sha256") != record.get("qualification_sha256"):
            errors.append(f"Baseline V4 protocol qualification binding is stale for {sequence['id']}")
        if protocol.get("task_fixture", {}).get("task_family_generation") != "baseline-v4" or protocol.get("baseline_pool", {}).get("descriptor", {}).get("task_family_generation") != "baseline-v4":
            errors.append(f"Baseline V4 protocol lacks explicit generation binding for {sequence['id']}")
        receipt_path = workflow.baseline_pilot_attempt_receipt_path(sequence, ROOT)
        if receipt_path.exists():
            errors.append(f"Baseline V4 provider pilot identity is already occupied: {receipt_path}")
    for slug in ("beets", "terraform"):
        if not (ROOT / f"sources/evaluations/audits/baseline-v3-pilot-attempt-{slug}.json").is_file():
            errors.append(f"immutable Baseline V3 attempt receipt is missing for {slug}")


def validate_frozen_protocol_bindings(errors: list[str]) -> None:
    session_doc = json.loads((ROOT / "data/workflow-sessions.json").read_text())
    executed_protocols: dict[str, set[str]] = {}
    historical_qualification_cache: dict[tuple[str, str], bool] = {}

    def historical_qualification_exists(relative_path: str, expected_sha256: str) -> bool:
        """Verify a superseded mutable qualification through retained Git history."""
        key = (relative_path, expected_sha256)
        if key in historical_qualification_cache:
            return historical_qualification_cache[key]
        history = subprocess.run(
            ["git", "log", "--all", "--format=%H", "--", relative_path],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        matched = False
        if history.returncode == 0:
            for revision in history.stdout.splitlines():
                blob = subprocess.run(
                    ["git", "show", f"{revision}:{relative_path}"],
                    cwd=ROOT,
                    capture_output=True,
                    check=False,
                )
                if blob.returncode == 0 and hashlib.sha256(blob.stdout).hexdigest() == expected_sha256:
                    matched = True
                    break
        historical_qualification_cache[key] = matched
        return matched

    for session in session_doc.get("sessions", []):
        frozen = session.get("frozen_protocol", {})
        protocol_path = frozen.get("path")
        protocol_sha = frozen.get("sha256")
        if isinstance(protocol_path, str) and isinstance(protocol_sha, str):
            executed_protocols.setdefault(protocol_path, set()).add(protocol_sha)
    try:
        from scripts import run_codex_workflow_evaluation as runner
        from scripts import run_codex_workflow_model_condition as model_condition_runner
    except Exception as exc:
        errors.append(f"cannot import workflow runner for protocol binding validation: {exc}")
        runner = None
        model_condition_runner = None
    current_sequence_bindings: set[str] = set()
    for path in (ROOT / "sources/evaluations/protocols").glob("*.json"):
        protocol = json.loads(path.read_text())
        sequence_id = protocol.get("task_fixture", {}).get("sequence_id")
        if not isinstance(sequence_id, str) or not sequence_id.endswith("-lifecycle-sequence-v0"):
            errors.append(f"execution contract {path.name} is not lifecycle v0")
            continue
        if protocol.get("status") == "frozen-ready-not-run" and "gpt-5.5" in json.dumps(protocol):
            errors.append(f"execution contract {path.name} uses unsupported gpt-5.5")
        if protocol.get("status") != "frozen-ready-not-run":
            errors.append(f"execution contract {path.name} must be frozen-ready-not-run")
            continue
        fixture = protocol.get("task_fixture", {})
        qualification_rel = fixture.get("qualification_path")
        qualification_path = ROOT / str(qualification_rel or "")
        if not qualification_rel or not qualification_path.is_file():
            errors.append(f"frozen protocol {path.name} is missing qualification evidence")
            continue
        actual = hashlib.sha256(qualification_path.read_bytes()).hexdigest()
        qualification_hash_matches_current_file = fixture.get("qualification_sha256") == actual
        if runner is not None:
            expected_descriptor = None
            expected_override = None
            try:
                seq = runner.load_sequence(str(fixture.get("sequence_id")))
                if seq.get("status") != "active":
                    errors.append(f"execution contract {path.name} references an inactive sequence")
                    continue
                expected_qualification_sha = str(fixture.get("qualification_sha256", ""))
                if not qualification_hash_matches_current_file:
                    historical_match = (
                        qualification_rel != seq.get("qualification_path")
                        and historical_qualification_exists(str(qualification_rel), expected_qualification_sha)
                    )
                    if not historical_match:
                        errors.append(f"frozen protocol {path.name} has a stale qualification hash")
                        continue
                frozen_descriptor = protocol.get("baseline_pool", {}).get("descriptor", {})
                actual_fingerprint = protocol.get("baseline_pool", {}).get("protocol_fingerprint")
                try:
                    frozen_fingerprint = runner.baseline_protocol_fingerprint_from_descriptor(frozen_descriptor)
                except Exception as exc:
                    errors.append(f"execution contract {path.name} has an invalid frozen baseline descriptor: {exc}")
                    continue
                if actual_fingerprint != frozen_fingerprint:
                    errors.append(f"execution contract {path.name} has an internally inconsistent baseline fingerprint")
                    continue
                protocol_rel = path.relative_to(ROOT).as_posix()
                frozen_hashes = executed_protocols.get(protocol_rel)
                if frozen_hashes:
                    actual_protocol_sha = hashlib.sha256(path.read_bytes()).hexdigest()
                    if frozen_hashes != {actual_protocol_sha}:
                        errors.append(
                            f"executed protocol {path.name} bytes do not match retained session references"
                        )
                        continue
                if qualification_rel != seq.get("qualification_path"):
                    selected = protocol.get("selected_execution", {})
                    selected_descriptor = selected.get("descriptor", {})
                    if selected.get("descriptor_sha256") != runner._json_hash(selected_descriptor):
                        errors.append(f"historical execution contract {path.name} has an invalid selected-execution hash")
                        continue
                    selected_pool = selected_descriptor.get("baseline_pool_reference", {}).get("protocol_fingerprint")
                    if selected_pool != actual_fingerprint:
                        errors.append(f"historical execution contract {path.name} has an inconsistent baseline-pool reference")
                    continue
                expected_descriptor = runner.baseline_protocol_descriptor(seq)
                override = frozen_descriptor.get("model_condition_override") if isinstance(frozen_descriptor, dict) else None
                if override is not None:
                    if not isinstance(override, dict) or model_condition_runner is None:
                        raise ValueError("invalid model-condition override")
                    condition = model_condition_runner.registered_condition(
                        str(override.get("model_condition_id", "")),
                        str(override.get("model", "")),
                        str(override.get("reasoning_effort", "")),
                    )
                    expected_override = {
                        "model_condition_id": condition["id"],
                        "model": condition["model"],
                        "reasoning_effort": condition["reasoning_effort"],
                        "registry_status": condition.get("status"),
                        "launcher": model_condition_runner.launcher_identity(),
                    }
                    if override != expected_override:
                        raise ValueError("model-condition override does not match its registry entry and launcher")
                    expected_descriptor["agent"].update({
                        "model": condition["model"],
                        "model_condition_id": condition["id"],
                        "reasoning_effort": condition["reasoning_effort"],
                    })
                    expected_descriptor["runtime_inputs"]["codex_runtime_condition"] = condition["id"]
                    expected_descriptor["model_condition_override"] = expected_override
                    comparison_descriptor = runner.baseline_comparison_descriptor(seq)
                    comparison_descriptor["agent"] = expected_descriptor["agent"]
                    comparison_descriptor["runtime_inputs"] = expected_descriptor["runtime_inputs"]
                    encoded = json.dumps(comparison_descriptor, sort_keys=True, separators=(",", ":")).encode()
                    full_hash = hashlib.sha256(encoded).hexdigest()
                    expected_fingerprint = runner.COMPARISON_IDENTITY_ALIASES.get(
                        full_hash, full_hash[:runner.BASELINE_POOL_FINGERPRINT_LENGTH]
                    )
                else:
                    expected_fingerprint = runner.baseline_protocol_fingerprint(seq)
            except Exception as exc:
                errors.append(f"frozen protocol {path.name} cannot compute current runner fingerprint: {exc}")
            else:
                actual_fingerprint = protocol.get("baseline_pool", {}).get("protocol_fingerprint")
                if actual_fingerprint != expected_fingerprint:
                    errors.append(f"execution contract {path.name} has a stale baseline fingerprint")
                    continue
                selected = protocol.get("selected_execution", {})
                selected_descriptor = selected.get("descriptor", {})
                selected_profile = selected_descriptor.get("selected_profile", {}).get("profile_id")
                protocol_rel = path.relative_to(ROOT).as_posix()
                frozen_hashes = executed_protocols.get(protocol_rel)
                if frozen_hashes:
                    actual_protocol_sha = hashlib.sha256(path.read_bytes()).hexdigest()
                    if frozen_hashes != {actual_protocol_sha}:
                        errors.append(
                            f"executed protocol {path.name} bytes do not match retained session references"
                        )
                        continue
                profile_status = None
                if selected_profile and selected_profile != "baseline-bare-codex":
                    try:
                        profile_status = runner.profile_registry_entry(str(selected_profile)).get("status")
                    except KeyError:
                        profile_status = None
                historical_executed = bool(frozen_hashes) and profile_status == "historical-profile"
                if not historical_executed:
                    try:
                        runner.assert_profile_runnable(str(selected_profile or "baseline-bare-codex"))
                    except ValueError as exc:
                        errors.append(f"execution contract {path.name} selects a non-runnable profile: {exc}")
                        continue
                descriptor = protocol.get("baseline_pool", {}).get("descriptor")
                if not runner.baseline_protocol_descriptor_compatible(
                    descriptor, expected_descriptor
                ):
                    errors.append(f"execution contract {path.name} has a stale causal baseline descriptor")
                    continue
                docker_image = selected_descriptor.get("runtime", {}).get("docker_image")
                timeout_for_execution = int(fixture.get("timeout_seconds_per_task", 3600))
                expected_execution = runner.execution_condition_descriptor(
                    seq,
                    str(selected_profile or "baseline-bare-codex"),
                    timeout_seconds_per_task=timeout_for_execution,
                    docker_image=str(docker_image or runner.DEFAULT_DOCKER_IMAGE),
                )
                if expected_override is not None:
                    expected_execution["agent_condition"].update({
                        "model": expected_override["model"],
                        "model_condition_id": expected_override["model_condition_id"],
                        "reasoning_effort": expected_override["reasoning_effort"],
                    })
                    expected_execution["baseline_pool_reference"]["protocol_fingerprint"] = expected_fingerprint
                    expected_execution["model_condition_override"] = expected_override
                    selected_override = selected_descriptor.get("model_condition_override")
                    agent_block = protocol.get("baseline", {}) if selected_profile == "baseline-bare-codex" else protocol.get("treatment", {})
                    required_model_args = (
                        "scripts/run_codex_workflow_model_condition.py",
                        f"--workflow-model-condition-id {expected_override['model_condition_id']}",
                        f"--workflow-model {expected_override['model']}",
                        f"--workflow-reasoning-effort {expected_override['reasoning_effort']}",
                    )
                    if selected_override != expected_override:
                        errors.append(f"execution contract {path.name} has inconsistent model-condition overrides")
                        continue
                    if any(required not in str(agent_block.get("command", "")) for required in required_model_args):
                        errors.append(f"execution contract {path.name} command does not bind its model-condition override")
                        continue
                    if any(agent_block.get(key) != expected_override[override_key] for key, override_key in (
                        ("model", "model"),
                        ("model_condition_id", "model_condition_id"),
                        ("reasoning_effort", "reasoning_effort"),
                    )):
                        errors.append(f"execution contract {path.name} agent block does not bind its model-condition override")
                        continue
                protocol_rel = path.relative_to(ROOT).as_posix()
                frozen_hashes = executed_protocols.get(protocol_rel)
                if frozen_hashes:
                    actual_protocol_sha = hashlib.sha256(path.read_bytes()).hexdigest()
                    if frozen_hashes != {actual_protocol_sha}:
                        errors.append(
                            f"executed protocol {path.name} bytes do not match retained session references"
                        )
                        continue
                elif selected.get("descriptor") != expected_execution or selected.get("descriptor_sha256") != runner._json_hash(expected_execution):
                    errors.append(f"execution contract {path.name} has a stale selected-execution descriptor")
                    continue
                if not frozen_hashes:
                    expected_protocol_id = runner.canonical_protocol_id(
                        seq,
                        str(selected_profile or "baseline-bare-codex"),
                        baseline_descriptor=expected_descriptor,
                        selected_execution=expected_execution,
                    )
                    if protocol.get("protocol_id") != expected_protocol_id or path.stem != expected_protocol_id:
                        errors.append(f"execution contract {path.name} does not use its canonical protocol ID and path")
                        continue
                current_sequence_bindings.add(str(seq["id"]))
        timeout = fixture.get("timeout_seconds_per_task")
        selected = protocol.get("selected_execution", {})
        selected_profile = selected.get("descriptor", {}).get("selected_profile", {}).get("profile_id", "baseline-bare-codex")
        agent_block = protocol.get("baseline", {}) if selected_profile == "baseline-bare-codex" else protocol.get("treatment", {})
        command = agent_block.get("command", "")
        if timeout and f"--timeout-per-task {timeout}" not in command:
            errors.append(f"frozen protocol {path.name} command does not bind timeout {timeout}")
        docker_image = selected.get("descriptor", {}).get("runtime", {}).get("docker_image")
        if docker_image and f"--docker-image {docker_image}" not in command:
            errors.append(f"frozen protocol {path.name} command does not bind docker image {docker_image}")
        fields = protocol.get("token_accounting_boundary", {}).get("fields", [])
        if "total_provider_tokens" not in fields:
            errors.append(f"frozen protocol {path.name} must bind total_provider_tokens")
    if runner is not None:
        missing = sorted(set(runner.active_sequence_ids()) - current_sequence_bindings)
        if missing:
            errors.append(f"active workflow sequences missing current v0 execution contracts: {', '.join(missing)}")


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
            if fixtures_by_id.get(fixture_id, {}).get("status") != "treatment-ready"
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


def main() -> int:
    errors: list[str] = []
    for rel in REQUIRED_PATHS + LOCAL_SKILL_ARTIFACTS + TRUTHMARK_ARTIFACTS:
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
    validate_retired_baseline_v2_audit(errors)
    validate_baseline_v3_qualification_audit(errors)
    validate_baseline_v4_qualification_audit(errors)
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

    run_truthmark("check", errors)
    run_truthmark("index", errors)

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
