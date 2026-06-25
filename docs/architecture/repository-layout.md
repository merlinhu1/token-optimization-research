# Repository Layout Architecture

## Top-level responsibilities

| Path | Role | Should contain | Should not contain |
|---|---|---|---|
| `data/` | Canonical structured records | JSON registries used by validation and synthesis | Free-form notes without schema |
| `sources/` | Imported raw or seed material | Seed catalogs, snapshots, raw source notes | Canonical conclusions |
| `docs/architecture/` | Research-system design | Domain model, workflows, compatibility model | Tool marketing summaries |
| `docs/methodology/` | How research is conducted | Discovery, evidence, provenance, measurement rules | Individual repo reviews |
| `docs/taxonomy/` | Human-readable taxonomy | Category definitions and rationale | Raw data records |
| `docs/evaluations/` | Evaluation protocols and framework | Protocols, metrics, analysis templates | Unscoped benchmark claims |
| `docs/literature/` | Literature synthesis | Paper clusters and method extraction | Unreviewed paper dumps |
| `docs/paper/` | Manuscript staging | Outlines, sections, figures | Canonical source data |
| `docs/standards/` | Reporting standards | Naming, evidence labels, checklists | One-off notes |
| `templates/` | Entry templates | Repository, technique, claim, evaluation templates | Filled canonical records |
| `prompts/` | Agent prompts | Researcher/evaluator/writer prompts | Source evidence |
| `scripts/` | Validation and utility scripts | Deterministic checks and transforms | Research conclusions |

## Data directory evolution

Bootstrap state:

```text
data/
  repositories.json
  techniques.json
  compatibility-edges.json
  literature.json
  evaluations.json
```

Scaled state:

```text
data/
  artifacts.json
  sources.json
  source-reviews.json
  claims.json
  techniques.json
  compatibility-edges.json
  protocols.json
  evaluations.json
  findings.json
```

The scaled split should happen when repository records become too large or when paper writing needs claim-level citation IDs.
