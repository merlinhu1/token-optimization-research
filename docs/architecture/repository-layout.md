# Repository Layout Architecture

The repository is a research production system. Top-level folders are organized by ownership, not by project phase.

## Top-level responsibilities

| Path | Role | Should contain | Should not contain |
|---|---|---|---|
| `data/` | Canonical structured records | JSON registries used by validation, runbooks, and synthesis | Free-form notes without schema |
| `sources/` | Raw/source material and evidence bundles | Discovery artifacts, fixture source material, archived run evidence | Canonical conclusions or active docs |
| `docs/` | Human-facing documentation | Architecture, methodology, evaluation protocols, reports, Truthmark docs | Raw transcripts, generated checkouts, local runtime state |
| `schemas/` | Machine-readable record contracts | JSON Schema files for evaluation/session records | Example records or run outputs |
| `templates/` | Reusable record and report templates | Blank templates for dossiers, records, reports, and evaluation changes | Filled canonical records |
| `scripts/` | Deterministic tools | Validators, runbook generators, runners, usage extractors | Research conclusions |
| `prompts/` | Agent prompts | Researcher, evaluator, and writer prompts | Source evidence or generated run output |
| `.agents/` | Repo-local agent skills | Skills required by this repository's research workflow | Host-level agent configuration |
| `.truthmark/` | Truthmark configuration | Truthmark config only | Truth docs or generated run artifacts |

## Documentation layout

| Path | Responsibility |
|---|---|
| `docs/README.md` | Human-facing documentation index and placement rules |
| `docs/architecture/` | System design, domain model, compatibility model, and decision records |
| `docs/evaluations/design/` | Evaluation estimand, workflow, fixture, result, accounting, and isolation contracts |
| `docs/evaluations/operations/` | Generated runbook, runner reference, workflow guide, and fixture guide |
| `docs/evaluations/plans/` | Historical phase plans retained for context |
| `docs/methodology/` | Durable research methods, discovery, provenance, reporting patterns, and case studies |
| `docs/papers/` | Completed research papers and phase reports |
| `docs/reference/` | Literature, taxonomy, and research standards |
| `docs/research/` | Active roadmap and tool-research direction |
| `templates/` | Repository-wide blank paper, evaluation, record, and fixture templates |
| `docs/tool-dossiers/` | Persistent source-logic or better tool dossiers |
| `docs/truthmark/` | Maintainer-facing routes and durable repository-truth claims |

The root `README.md` is a storefront and navigation page. It should not duplicate detailed methodology or evaluation procedure.

## Evaluation source layout

Active workflow fixtures and archived evidence are separated under `sources/evaluations/`:

```text
sources/evaluations/
  README.md
  fixtures/
    container/Dockerfile
    large/<project-id>/
      setup.sh
      reset.sh
      verify-smoke.sh
      tasks/<task-id>/
        agent-prompt.txt
        seed-regression.patch
        setup.sh
        reset.sh
        verify.sh
    medium/<project-id>/
      ...same contract...
  workflow-sessions/<session-id>/
    run.json
    changes.diff
    evidence.jsonl.gz
    manifest.sha256
  archive/
    historical-fixtures/<project-id>/
    single-task-reruns/<group>/
```

`data/workflow-task-sequences.json` is the canonical active sequence registry.

`data/repository-fixtures.json` is the canonical fixture-readiness registry.

`docs/evaluations/operations/runbook.md` is generated from the registries by `scripts/update_workflow_runbook.py`.

## Archive policy

Archived fixture/run evidence is retained for traceability, negative findings, and historical comparisons.

Archived evidence does not define active workflow architecture.

Do not present archived single-task evidence as positive `reproduction` evidence unless it is requalified through the active workflow-session protocol.

## Local/generated state policy

Generated fixture checkouts are local runtime state and are ignored:

```text
sources/evaluations/fixtures/large/*/repo/
sources/evaluations/fixtures/medium/*/repo/
```

Workflow sessions may keep only compact evidence bundles in git. Do not commit materialized `project/`, `codex-homes/`, `.venv/`, `__pycache__/`, split transcripts, or split setup/verifier logs.

## Scaled data directory direction

Current canonical registries are intentionally compact:

```text
data/repositories.json
data/techniques.json
data/compatibility-edges.json
data/literature.json
data/evaluations.json
data/repository-fixtures.json
data/workflow-task-sequences.json
data/workflow-sessions.json
```

Split into claim/source/finding-level registries only when repository records become too large or paper writing needs stable claim-level citation IDs.
