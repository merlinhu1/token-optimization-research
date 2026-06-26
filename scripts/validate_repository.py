#!/usr/bin/env python3
"""Lightweight structural validation for the token optimization research repository."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "README.md",
    "METHODOLOGY.md",
    "RESEARCH_ROADMAP.md",
    "data/repositories.json",
    "data/techniques.json",
    "data/compatibility-edges.json",
    "data/literature.json",
    "data/evaluations.json",
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
    "docs/literature/literature-review.md",
    "docs/paper/research-paper-outline.md",
    "docs/reports/phase-1-compatibility-safe-token-saving-stacks.md",
    "docs/standards/research-standards.md",
    "docs/research/tool-research-strategy.md",
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
    "templates/repository-entry.md",
    "templates/technique-entry.md",
    "templates/claim-entry.md",
    "templates/evaluation-record.md",
    "templates/report.md",
    "templates/tool-dossier.md",
    "prompts/researcher.md",
    "prompts/evaluator.md",
    "prompts/paper-writer.md",
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


def load_json(rel: str) -> dict:
    path = ROOT / rel
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"Invalid JSON in {rel}: {exc}") from exc


def main() -> int:
    errors: list[str] = []
    for rel in REQUIRED_PATHS:
        if not (ROOT / rel).exists():
            errors.append(f"missing required path: {rel}")

    techniques_doc = load_json("data/techniques.json")
    repositories_doc = load_json("data/repositories.json")
    compatibility_doc = load_json("data/compatibility-edges.json")
    literature_doc = load_json("data/literature.json")
    evaluations_doc = load_json("data/evaluations.json")

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

    for ev in evaluations_doc.get("evaluations", []):
        tid = ev.get("technique_id")
        if tid and tid not in technique_ids:
            errors.append(f"evaluation {ev.get('id')} references unknown technique {tid}")

    for lit in literature_doc.get("literature", []):
        if not lit.get("id") or not lit.get("sources"):
            errors.append("literature record missing id or sources")

    if errors:
        print("Validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Validation passed")
    print(f"- techniques: {len(techniques_doc.get('techniques', []))}")
    print(f"- repositories: {len(repositories_doc.get('repositories', []))}")
    print(f"- compatibility edges: {len(compatibility_doc.get('edges', []))}")
    print(f"- literature records: {len(literature_doc.get('literature', []))}")
    print(f"- evaluations: {len(evaluations_doc.get('evaluations', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
