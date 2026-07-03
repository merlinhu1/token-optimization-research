#!/usr/bin/env python3
"""Lightweight structural validation for the token optimization research repository."""
from __future__ import annotations

import json
import re
import subprocess
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
    "docs/architecture/README.md",
    "docs/architecture/research-system.md",
    "docs/architecture/domain-model.md",
    "docs/architecture/compatibility-graph.md",
    "docs/architecture/workflows.md",
    "docs/architecture/repository-layout.md",
    "docs/architecture/decision-records/0001-research-kernel.md",
    "docs/taxonomy/compatibility-taxonomy.md",
    "docs/evaluations/README.md",
    "docs/evaluations/evaluation-framework.md",
    "docs/evaluations/fixtures/README.md",
    "docs/evaluations/token-usage-and-quality-standards.md",
    "docs/evaluations/phase-2-benchmark-plan.md",
    "docs/evaluations/continuous-workflow-simulation.md",
    "docs/evaluations/workflow-evaluation-runbook.md",
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
    "templates/workflow-session-record.json",
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
    parts = set(Path(low).parts)
    if parts & {"test", "tests", "testing", "fixture", "fixtures", "docs", "doc", "generated", "dist", "build", "coverage", "tasks", "controller"}:
        return False
    if low.endswith((".md", ".rst", ".txt", ".snap", ".patch", ".lock", ".map")):
        return False
    return Path(low).suffix in {".c", ".cc", ".cpp", ".cs", ".cshtml", ".go", ".java", ".js", ".jsx", ".mjs", ".py", ".rb", ".rs", ".ts", ".tsx", ".yaml", ".yml"}


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
    required_true = ("seeded_verifier_nonzero", "fixed_verifier_zero", "full_fixed_cumulative_verifier_zero", "composite_seed_merge_zero", "composite_seeded_verifiers_nonzero", "no_unmerged_paths", "no_model_visible_acceptance_assets", "all_expected_model_concealment_declared")
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
        if not set(record.get("production_files", [])) or record.get("production_file_count", 0) < 1:
            errors.append(f"qualification {rel} task {task['id']} records no production/type files")
        if record.get("task_id") != task["id"] or record.get("production_files") != files or record.get("production_file_count") != len(files) or record.get("agent_prompt_sha256") != hashes["agent-prompt.txt"] or record.get("seed_patch_sha256") != hashes["seed-regression.patch"] or record.get("verifier_sha256") != hashes["verify.sh"] or record.get("task_directory_sha256") != task_directory_sha256(task_dir):
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
    if sequence_doc.get("schema_version") != 1:
        errors.append("data/workflow-task-sequences.json must use schema_version 1")
    sequences = sequence_doc.get("sequences")
    if not isinstance(sequences, list):
        errors.append("data/workflow-task-sequences.json must contain a sequences list")
        return set()
    fixture_ids = {fixture.get("id") for fixture in fixture_doc.get("fixtures", [])}
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
        if sequence.get("status") not in {"planned", "active", "retired"}:
            errors.append(f"workflow sequence {sid} has invalid status: {sequence.get('status')}")
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
        if sequence.get("status") == "planned" and not sequence.get("readiness_blockers"):
            errors.append(f"planned workflow sequence {sid} must record readiness_blockers")
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
                    behavior_bearing = patch_behavior_bearing_paths(task_dir / "seed-regression.patch")
                    padded = sorted(set(production) - set(behavior_bearing))
                    if padded and str(tid) == "terraform-9ae470-objchange-validation-regression":
                        errors.append(f"active workflow sequence {sid} task {tid} pads its production scope with comment-only files: {', '.join(padded)}")
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
            task.get("task_class", "maintenance-regression")
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
    retired_contract_phrases = (
        "one task at a time",
        "alternative-repair",
        "ordered transitions",
    )
    for sequence in active:
        policy = str(sequence.get("seed_patch_policy", "")).lower()
        if "composite broken start" not in policy or "final prompt" not in policy:
            errors.append(f"active workflow sequence {sequence.get('id')} must declare composite pre-seeding and final-only verification")
        if any(phrase in policy for phrase in retired_contract_phrases):
            errors.append(f"active workflow sequence {sequence.get('id')} still describes the retired lazy-seed contract")
    for surface in ("README.md", "docs/research/roadmap.md"):
        text = (ROOT / surface).read_text().lower()
        if any(phrase in text for phrase in retired_contract_phrases):
            errors.append(f"{surface} still describes retired lazy-seed qualification gates")
    return sequence_ids


def validate_fixture_sequence_status_consistency(
    workflow_doc: dict,
    fixtures_doc: dict,
    large_candidates_doc: dict,
    medium_candidates_doc: dict,
    errors: list[str],
) -> None:
    statuses = {
        sequence.get("id"): sequence.get("status")
        for sequence in workflow_doc.get("sequences", [])
        if sequence.get("id")
    }
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
    if session.get("schema_version") not in {1, 2}:
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
    if not isinstance(session.get("replicate_index"), int) or session.get("replicate_index", -1) < 0:
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

    if run_record is not None:
        identity_keys = ("frozen_protocol", "baseline_pool", "selected_execution", "docker_image_identity", "tool_adapter_identity")
        for key in identity_keys:
            if run_record.get(key) != session.get(key):
                errors.append(f"workflow session {sid} run.json {key} does not match registry session")


def requires_structured_task_contract(session: dict) -> bool:
    return session.get("schema_version") == 2


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
            legacy_seed_delivery = (
                prompt_delivery.get("seed_delivery_mode") == "lazy-one-task-at-a-time"
                and prompt_delivery.get("future_seed_regressions_visible") is False
            )
            warm_seed_delivery = (
                prompt_delivery.get("seed_delivery_mode") == "preseeded-composite"
                and prompt_delivery.get("future_seed_regressions_visible") is True
                and prompt_delivery.get("controller_verification") == "final-only"
            )
            if not (legacy_seed_delivery or warm_seed_delivery):
                errors.append(f"workflow session {sid} must use a recognized frozen seed-delivery contract")
        leakage_controls = sequence.get("leakage_controls") if isinstance(sequence, dict) else None
        if not isinstance(leakage_controls, dict) or leakage_controls.get("seed_origin_concealed") is not True:
            errors.append(f"workflow session {sid} must record seed_origin_concealed leakage control for completed workflow reproduction")
        elif leakage_controls.get("task_directories_model_visible") is not False:
            errors.append(f"workflow session {sid} task directories must not be model-visible")
        if not isinstance(leakage_controls, dict) or leakage_controls.get("seed_patches_model_visible") is not False:
            errors.append(f"workflow session {sid} seed patches must not be model-visible")
        if not isinstance(leakage_controls, dict) or not (
            leakage_controls.get("git_baseline_true_root_per_task") is True
            or leakage_controls.get("git_baseline_true_root_at_lane_start") is True
        ):
            errors.append(f"workflow session {sid} must use a verified true-root Git baseline")
        if not isinstance(leakage_controls, dict) or leakage_controls.get("fixed_snapshot_objects_model_visible") is not False or leakage_controls.get("pre_seed_reflog_entries_visible") is not False:
            errors.append(f"workflow session {sid} fixed snapshot objects and pre-seed reflogs must not be model-visible")
        if not isinstance(leakage_controls, dict) or leakage_controls.get("concealment_verification_passed") is not True:
            errors.append(f"workflow session {sid} must pass seed concealment verification")
        if not isinstance(leakage_controls, dict) or leakage_controls.get("verifier_assets_model_visible") is not False:
            errors.append(f"workflow session {sid} verifier assets must not be model-visible")
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
        if (
            not isinstance(token_usage, dict)
            or token_usage.get("measurement_source") != "codex-jsonl-usage-events"
            or not isinstance(token_usage.get("total_provider_tokens"), int)
            or token_usage.get("total_provider_tokens", 0) <= 0
        ):
            errors.append(f"workflow session {sid} objective acceptance requires positive provider-reported total tokens")
        critical_failures = quality.get("critical_failures", []) if isinstance(quality, dict) else []
        prompt_delivery = sequence.get("prompt_delivery", {}) if isinstance(sequence, dict) else {}
        leakage_controls = sequence.get("leakage_controls", {}) if isinstance(sequence, dict) else {}
        legacy_seed_delivery = (
            prompt_delivery.get("seed_delivery_mode") == "lazy-one-task-at-a-time"
            and prompt_delivery.get("future_seed_regressions_visible") is False
            and leakage_controls.get("git_baseline_true_root_per_task") is True
        )
        warm_seed_delivery = (
            prompt_delivery.get("seed_delivery_mode") == "preseeded-composite"
            and prompt_delivery.get("future_seed_regressions_visible") is True
            and prompt_delivery.get("controller_verification") == "final-only"
            and leakage_controls.get("git_baseline_true_root_at_lane_start") is True
        )
        structurally_isolated = (
            prompt_delivery.get("future_tasks_visible") is False
            and prompt_delivery.get("future_prompts_materialized_lazily") is True
            and (legacy_seed_delivery or warm_seed_delivery)
            and leakage_controls.get("task_directories_model_visible") is False
            and leakage_controls.get("verifier_assets_model_visible") is False
            and leakage_controls.get("verifier_integrity_passed") is True
            and leakage_controls.get("seed_patches_model_visible") is False
            and leakage_controls.get("fixed_snapshot_objects_model_visible") is False
            and leakage_controls.get("pre_seed_reflog_entries_visible") is False
            and leakage_controls.get("concealment_verification_passed") is True
        )
        if (
            session.get("status") != "completed"
            or interpretation.get("accepted_for_execution") is not True
            or quality.get("functional_verifier_passed") is not True
            or not structurally_isolated
        ):
            errors.append(
                f"workflow session {sid} objective acceptance requires a completed, execution-accepted, functionally verified, and structurally isolated run"
            )
        if session.get("schema_version") == 2:
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
        if review_status != "reviewed" or not isinstance(quality_score, int) or quality_score < 4 or critical_failures:
            errors.append(f"workflow session {sid} objective acceptance requires a reviewed quality result with score >= 4 and no critical failures")


def validate_workflow_sessions(session_doc: dict, sequence_ids: set[str], fixture_doc: dict, profiles_by_id: dict[str, dict], runtime_ids: set[str], model_condition_ids: set[str], errors: list[str]) -> None:
    if session_doc.get("schema_version") != 1:
        errors.append("data/workflow-sessions.json must use schema_version 1")
    if session_doc.get("primary_metric") != "cumulative provider-reported workflow tokens":
        errors.append("data/workflow-sessions.json primary_metric must be cumulative provider-reported workflow tokens")
    sessions = session_doc.get("sessions")
    if not isinstance(sessions, list):
        errors.append("data/workflow-sessions.json must contain a sessions list")
        return
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
        validate_workflow_session_contract(session, canonical_profile, errors)
        comparison_id = session.get("interpretation", {}).get("comparison_baseline_session_id") if isinstance(session.get("interpretation"), dict) else None
        if comparison_id:
            baseline = sessions_by_id.get(comparison_id)
            if baseline is None:
                errors.append(f"workflow session {sid} references missing comparison baseline {comparison_id}")
            elif (
                baseline.get("replicate_index") != session.get("replicate_index")
                or baseline.get("baseline_pool", {}).get("protocol_fingerprint")
                != session.get("baseline_pool", {}).get("protocol_fingerprint")
            ):
                errors.append(f"workflow session {sid} comparison baseline {comparison_id} is not pool- and replicate-matched")
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
            required = {"run_record", "final_diff", "evidence_bundle", "manifest"}
            missing = sorted(required - set(artifacts))
            if missing:
                errors.append(f"workflow session {sid} compact artifacts missing keys: {', '.join(missing)}")
            artifact_paths = []
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
                if not full.exists():
                    errors.append(f"workflow session {sid} compact artifact {key} does not exist: {value}")
            roots = {path.parent for path in artifact_paths}
            if len(roots) == 1:
                root = next(iter(roots))
                allowed_names = {"run.json", "changes.diff", "evidence.jsonl.gz", "manifest.sha256"}
                actual_names = {path.name for path in root.iterdir() if path.is_file()}
                if actual_names != allowed_names:
                    errors.append(f"workflow session {sid} compact artifact directory must contain exactly {sorted(allowed_names)}; found {sorted(actual_names)}")
                validate_compact_manifest(root, sid, errors)
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
    try:
        from scripts import run_codex_workflow_evaluation as runner
    except Exception as exc:
        errors.append(f"cannot import workflow runner for protocol binding validation: {exc}")
        runner = None
    current_sequence_bindings: set[str] = set()
    for path in (ROOT / "sources/evaluations/protocols").glob("*.json"):
        protocol = json.loads(path.read_text())
        if protocol.get("status") == "frozen-ready-not-run" and "gpt-5.5" in json.dumps(protocol):
            errors.append(f"frozen protocol {path.name} uses historical-inactive gpt-5.5")
        if protocol.get("status") != "frozen-ready-not-run":
            continue
        fixture = protocol.get("task_fixture", {})
        qualification_rel = fixture.get("qualification_path")
        qualification_path = ROOT / str(qualification_rel or "")
        if not qualification_rel or not qualification_path.is_file():
            errors.append(f"frozen protocol {path.name} is missing qualification evidence")
            continue
        actual = __import__("hashlib").sha256(qualification_path.read_bytes()).hexdigest()
        if fixture.get("qualification_sha256") != actual:
            errors.append(f"frozen protocol {path.name} has a stale qualification hash")
        if runner is not None:
            try:
                seq = runner.load_sequence(str(fixture.get("sequence_id")))
                if seq.get("status") != "active":
                    # Retired sequences retain immutable historical protocols whose
                    # descriptors intentionally bind the pre-retirement contract.
                    continue
                if qualification_rel != seq.get("qualification_path"):
                    # Immutable protocols bound to earlier qualification paths are
                    # historical contracts; current binding checks apply only to
                    # the qualification path selected by the active sequence.
                    continue
                expected_fingerprint = runner.baseline_protocol_fingerprint(seq)
            except Exception as exc:
                errors.append(f"frozen protocol {path.name} cannot compute current runner fingerprint: {exc}")
            else:
                actual_fingerprint = protocol.get("baseline_pool", {}).get("protocol_fingerprint")
                if actual_fingerprint != expected_fingerprint:
                    # Frozen protocols are immutable historical contracts. Multiple
                    # generations may share the active qualification path while
                    # binding older runner/image bytes; only the exact current
                    # fingerprint is eligible as the live binding.
                    continue
                selected = protocol.get("selected_execution", {})
                selected_descriptor = selected.get("descriptor", {})
                selected_profile = selected_descriptor.get("selected_profile", {}).get("profile_id")
                try:
                    runner.assert_profile_runnable(str(selected_profile or "baseline-bare-codex"))
                except ValueError:
                    # Historical and blocked treatment profiles retain immutable
                    # unrun protocol generations as provenance, not live bindings.
                    continue
                descriptor = protocol.get("baseline_pool", {}).get("descriptor")
                if descriptor != runner.baseline_protocol_descriptor(seq):
                    # Referenced and superseded protocols remain immutable provenance.
                    # They are not current bindings after behavior-bearing runner drift.
                    continue
                docker_image = selected_descriptor.get("runtime", {}).get("docker_image")
                timeout_for_execution = int(fixture.get("timeout_seconds_per_task", 3600))
                expected_execution = runner.execution_condition_descriptor(
                    seq,
                    str(selected_profile or "baseline-bare-codex"),
                    timeout_seconds_per_task=timeout_for_execution,
                    docker_image=str(docker_image or runner.DEFAULT_DOCKER_IMAGE),
                )
                if selected.get("descriptor") != expected_execution or selected.get("descriptor_sha256") != runner._json_hash(expected_execution):
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
            errors.append(f"active workflow sequences missing current frozen protocol bindings: {', '.join(missing)}")


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
    validate_fixture_sequence_status_consistency(workflow_sequences_doc, fixtures_doc, large_candidates_doc, medium_candidates_doc, errors)
    validate_workflow_sessions(workflow_sessions_doc, workflow_sequence_ids, fixtures_doc, profiles_by_id, runtime_ids, model_condition_ids, errors)
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
        ROOT / "docs/reports/phase-1-compatibility-safe-token-saving-stacks.md",
        ROOT / "docs/evaluations/evaluation-framework.md",
        ROOT / "docs/evaluations/repository-fixture-framework.md",
        ROOT / "docs/evaluations/cumulative-result-schema.md",
        ROOT / "docs/evaluations/fixtures/README.md",
        ROOT / "docs/evaluations/token-usage-and-quality-standards.md",
        ROOT / "docs/evaluations/phase-2-benchmark-plan.md",
        ROOT / "docs/evaluations/continuous-workflow-simulation.md",
        ROOT / "docs/evaluations/workflow-evaluation-runbook.md",
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
