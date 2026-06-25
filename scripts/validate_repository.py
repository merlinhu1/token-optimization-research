#!/usr/bin/env python3
"""Lightweight structural validation for the token optimization research repository."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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
    "docs/truthmark/engineering/research/software-quality-gates.md",
    "docs/truthmark/engineering/research/stack-compatibility.md",
    "docs/truthmark/engineering/research/current-findings.md",
    "docs/truthmark/engineering/research/agent-workflow.md",
]

REQUIRED_PATHS = [
    "README.md",
    "METHODOLOGY.md",
    "RESEARCH_ROADMAP.md",
    "data/repositories.json",
    "data/techniques.json",
    "data/compatibility-edges.json",
    "data/literature.json",
    "data/evaluations.json",
    "data/evaluation-profiles.json",
    "data/large-project-candidates.json",
    "data/repository-fixtures.json",
    "data/tool-analysis-backlog.json",
    "docs/architecture.md",
    "docs/architecture/README.md",
    "docs/architecture/research-system.md",
    "docs/architecture/domain-model.md",
    "docs/architecture/compatibility-graph.md",
    "docs/architecture/workflows.md",
    "docs/architecture/repository-layout.md",
    "docs/architecture/decision-records/0001-research-kernel.md",
    "docs/taxonomy/compatibility-taxonomy.md",
    "docs/evaluations/evaluation-framework.md",
    "docs/evaluations/fixtures/README.md",
    "docs/evaluations/token-usage-and-quality-standards.md",
    "docs/evaluations/phase-2-benchmark-plan.md",
    "docs/evaluations/immediately-usable-flows.md",
    "docs/evaluations/repository-fixture-framework.md",
    "docs/evaluations/cumulative-result-schema.md",
    "docs/literature/literature-review.md",
    "docs/paper/research-paper-outline.md",
    "docs/reports/phase-1-compatibility-safe-token-saving-stacks.md",
    "docs/standards/research-standards.md",
    "docs/research/tool-research-strategy.md",
    "docs/research/report-writing-and-methodology-skill-patterns.md",
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
    "docs/tool-dossiers/zilliztech-claude-context.md",
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
    "schemas/evaluation-run-record.schema.json",
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

FIXTURE_SCALES = {"synthetic-micro", "recorded-diagnostic", "large-project"}
FIXTURE_EVALUATION_USES = {"calibration", "diagnostic-preservation", "primary-candidate", "primary-objective"}
PROFILE_TYPES = {"control", "individual_tool", "tool_stack", "replacement_runtime", "installer_orchestrator", "comparator"}
OBJECTIVES = {"individual_tool_effectiveness", "stack_effectiveness"}
EVALUATION_RECORD_TYPES = {"run", "paired_comparison", "aggregate_summary"}
EVALUATION_RUN_ROLES = {"baseline", "individual_tool_treatment", "stack_treatment", "replacement_runtime", "audit_only"}
EVALUATION_STATUSES = {"planned", "running", "completed", "failed", "excluded", "superseded"}

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
        if evaluation_use == "primary-objective" and fixture_scale != "large-project":
            errors.append(f"fixture {fid} cannot be primary-objective unless fixture_scale is large-project")

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


def validate_evaluations(evaluation_doc: dict, fixture_doc: dict, profile_ids: set[str], errors: list[str]) -> None:
    if evaluation_doc.get("schema_version") != 3:
        errors.append("data/evaluations.json must use schema_version 3")
    objectives = set(evaluation_doc.get("primary_objectives", []))
    if objectives != OBJECTIVES:
        errors.append("data/evaluations.json must declare both primary objectives")
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
        if ev.get("objective") in OBJECTIVES and ev.get("evidence_stage") == "reproduction":
            if target.get("fixture_scale") != "large-project":
                errors.append(f"evaluation {eid} reproduction objective must target a large-project fixture")



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
    profiles_doc = load_json("data/evaluation-profiles.json")
    large_candidates_doc = load_json("data/large-project-candidates.json")
    fixtures_doc = load_json("data/repository-fixtures.json")
    backlog_doc = load_json("data/tool-analysis-backlog.json")

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
    profile_ids = validate_evaluation_profiles(profiles_doc, fixtures_doc, errors)
    validate_evaluations(evaluations_doc, fixtures_doc, profile_ids, errors)
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
        ROOT / "METHODOLOGY.md",
        ROOT / "docs/research/tool-research-strategy.md",
        ROOT / "docs/tool-dossiers/README.md",
        ROOT / "docs/reports/phase-1-compatibility-safe-token-saving-stacks.md",
        ROOT / "docs/evaluations/evaluation-framework.md",
        ROOT / "docs/evaluations/repository-fixture-framework.md",
        ROOT / "docs/evaluations/cumulative-result-schema.md",
        ROOT / "docs/evaluations/fixtures/README.md",
        ROOT / "docs/evaluations/token-usage-and-quality-standards.md",
        ROOT / "docs/evaluations/phase-2-benchmark-plan.md",
        ROOT / "docs/evaluations/immediately-usable-flows.md",
        ROOT / "docs/research/report-writing-and-methodology-skill-patterns.md",
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

    report_path = ROOT / "docs/reports/phase-1-compatibility-safe-token-saving-stacks.md"
    report_text = report_path.read_text(encoding="utf-8")
    if "Principal sources:" in report_text:
        errors.append("phase-1 report uses ledger-style 'Principal sources' heading; use summarized evidence basis")
    if "sources/discovery/" in report_text:
        errors.append("phase-1 report body references discovery archive paths; summarize provenance instead")
    if re.search(r"sources/discovery/20\d{2}-\d{2}-\d{2}-[^`\s)]*\.json", report_text):
        errors.append("phase-1 report body lists raw discovery JSON artifacts; summarize provenance instead")
    if re.search(r"\|\s*`[^`]+`\s*\|\s*[0-9]\s*\|", report_text):
        errors.append("phase-1 report contains a numeric evidence-stage table row; use named stages")

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
    print(f"- evaluation profiles: {len(profiles_doc.get('profiles', []))}")
    print(f"- large-project candidates: {len(large_candidates_doc.get('candidates', []))}")
    print(f"- repository fixtures: {len(fixtures_doc.get('fixtures', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
