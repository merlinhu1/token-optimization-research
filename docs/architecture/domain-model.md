# Domain Model

## Entity graph

```text
Source
  └─ reviewed_by → SourceReview
Artifact
  ├─ has_source_review → SourceReview
  ├─ makes → Claim
  ├─ implements → Technique
  └─ bundles → Artifact
Technique
  ├─ belongs_to → CompatibilityGroup
  ├─ conflicts_with → Technique
  ├─ stacks_with → Technique
  └─ evaluated_by → EvaluationProtocol / EvaluationRun
EvaluationRun
  ├─ tests → Technique
  ├─ uses → Workload
  ├─ measures → MetricSet
  └─ produces → Finding
Finding
  └─ supports → PaperSection / Standard / Prompt
```

## Entities

### Source

A concrete URL, file, paper, transcript, or imported seed document.

Fields:

- `id`
- `url_or_path`
- `source_type`
- `retrieved_at`
- `hash` when local or stable artifact exists

### SourceReview

A review event that records how deeply a source was inspected.

Fields:

- `source_id`
- `reviewed_at`
- `review_depth`: `surface | moderate | deep | reproduced`
- `reviewer`
- `notes`

### Artifact

A repository, benchmark, paper, bundle, primitive, or adjacent product.

Stored initially in `data/repositories.json` for repo-like artifacts. Later this can split into `data/artifacts.json` if papers and products need one registry.

Key fields:

- `id`
- `kind`
- `url`
- `summary`
- `mechanism`
- `sources`
- `reviewed_at`
- `review_depth`

### Claim

A scoped assertion made by an artifact.

Claims should eventually move into `data/claims.json` rather than being embedded only as prose in repository records.

Key fields:

- `id`
- `artifact_id`
- `claim_text`
- `metric_scope`: `operation | request | session | provider_billed | output_only | quality_gated | other`
- `evidence_label`
- `source_ids`
- `caveat_ids`

### Technique

An atomic token-saving intervention.

A technique is defined by:

- intervention surface;
- transformation mechanism;
- raw fallback requirement;
- quality risk;
- compatibility group.

A technique is **not** defined by a repository name.

### CompatibilityGroup

A set of techniques that compete for the same surface or authority. Groups are not just topical categories; they encode likely non-compatibility.

Examples:

- terminal stdout owner;
- code retrieval authority;
- MCP response schema owner;
- memory authority;
- model-routing authority.

### CompatibilityEdge

A relationship between two techniques or a technique and a group.

Types:

- `conflicts_with`
- `stacks_with`
- `depends_on`
- `subsumes`
- `requires_ordering`
- `unknown`

Edges require rationale and evidence level.

### EvaluationProtocol

A reusable experiment design for a technique category.

### EvaluationRun

A concrete execution of a protocol.

### Finding

A conclusion from one or more evaluation runs. Findings can be positive, negative, null, or methodological.

## Identity rules

- Artifact ID: `owner__repo` for GitHub repositories.
- Technique ID: `TNN-short-name`.
- Claim ID: `claim-artifact-short-hash-or-sequence`.
- Evaluation ID: `eval-YYYYMMDD-technique-workload`.
- Finding ID: `finding-YYYYMMDD-short-name`.

## Future data split

Current bootstrap keeps claims inside repository records for speed. When the catalog grows, split into:

- `data/artifacts.json`
- `data/sources.json`
- `data/source-reviews.json`
- `data/claims.json`
- `data/techniques.json`
- `data/compatibility-edges.json`
- `data/evaluations.json`
- `data/findings.json`
