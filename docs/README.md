# Documentation

Use this page as the entry point for human-facing documentation.

## Start here

- **Read the finished research:** [`papers/`](papers/README.md)
- **Run or understand an evaluation:** [`evaluations/`](evaluations/README.md)
- **See the current research direction:** [`research/`](research/README.md)
- **Inspect a tool:** [`tool-dossiers/`](tool-dossiers/README.md)

## Directory map

| Directory | What belongs here |
|---|---|
| [`architecture/`](architecture/README.md) | Repository design, domain model, compatibility model, workflows, and decision records |
| [`evaluations/`](evaluations/README.md) | Evaluation design contracts, operator guides, and historical plans |
| [`methodology/`](methodology/README.md) | Research methods, discovery rules, provenance, reporting patterns, and methodology case studies |
| [`papers/`](papers/README.md) | Finished research papers and published phase reports |
| [`reference/`](reference/README.md) | Supporting literature, taxonomies, and standards |
| [`research/`](research/README.md) | Active roadmap and tool-research direction |
| [`../templates/`](../templates/README.md) | Repository-wide blank outlines and reusable record templates |
| [`tool-dossiers/`](tool-dossiers/README.md) | Tool index and source-inspection dossiers |

## Placement rules

- Put a completed synthesis in `docs/papers/`, never in `templates/`.
- Put a blank outline or reusable starting document in the repository-root `templates/`, never in `docs/papers/`.
- Put runnable procedures in `evaluations/operations/` and evaluation contracts in `evaluations/design/`.
- Put ongoing priorities in `research/`; put durable research methods in `methodology/`.
- Put raw evidence and machine-readable records under `sources/` and `data/`, not under `docs/`.
