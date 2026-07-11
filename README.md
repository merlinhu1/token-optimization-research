# Token Optimization Research

Research infrastructure for measuring provider-reported token usage and software quality in realistic coding-agent workflows.

## Current evaluation portfolio

The repository retains operationally valid Fastify, Beets, and Terraform provider-token baseline samples; their verifier and review outcomes are diagnostics, not selection gates. Invalid fixture runs and stale protocols were removed at the experiment owner's direction. Terraform's current verifier exercises pagination through rendered output instead of requiring one canonical private helper name. The only runnable task contracts remain:

| Sequence | Fixture | Ordered stages |
|---|---|---|
| `fastify-lifecycle-sequence-v0` | Fastify | feature → behavior-preserving refactor → code review |
| `beets-lifecycle-sequence-v0` | Beets | feature → behavior-preserving refactor → code review |
| `terraform-lifecycle-sequence-v0` | Terraform | feature → behavior-preserving refactor → code review |

Every lane uses one pinned repository snapshot and one persistent model session. The controller applies all three independently qualified start conditions before prompt 1, discloses prompts in order, preserves model/tool state, and runs all concealed verifiers after prompt 3.

A 2026-07-18 official-integration audit and follow-up runtime review found that 48 of 54 historical treatment sessions could not support product-effect claims. At the experiment owner's direction, invalid sessions, comparisons, compact bundles, and occupied protocols were deleted from the active corpus rather than relabelled as baseline. Deletion receipts preserve each adjudication; the six retained historical records are the Headroom default-wrapper and proxy-only conditions, and the prior TokenJuice+jcodemunch stack decision remains withdrawn.

Seventeen canonical treatment conditions contribute 72 accepted provider-backed sessions alongside 21 controls. Every profile passed protocol-bound provider-free setup and assignment gates before its first valid run. The Phase 2 synthesis reports 582,180,587 treatment tokens against 541,295,326 repeated matched-baseline tokens (+7.55%) with 150/153 task verifiers. A prospective r3 screen of seven profiles used 257,591,572 tokens against 236,364,772 repeated fresh-baseline tokens (+8.98%) with 62/63 treatment verifiers; five of seven aggregate directions changed from the preceding screen. These are descriptive observations, not stable rankings.

## Documentation

Start with [`docs/README.md`](docs/README.md). The main destinations are:

- [`docs/papers/`](docs/papers/README.md) — completed research papers and phase reports;
- [`docs/evaluations/`](docs/evaluations/README.md) — evaluation design and operator guidance;
- [`docs/research/`](docs/research/README.md) — current roadmap and research direction;
- [`docs/tool-dossiers/`](docs/tool-dossiers/README.md) — tool index and source-inspection dossiers;
- [`templates/`](templates/README.md) — blank outlines and reusable templates.

## Source of truth

- `data/workflow-task-sequences.json` — lifecycle v0 contracts.
- `data/repository-fixtures.json` — pinned fixture readiness.
- `sources/evaluations/fixtures/` — task prompts, start patches, controller acceptance, and generated v0 qualification evidence.
- `data/workflow-sessions.json` — active retained provider-backed controls and objective-eligible treatment samples; corrupted treatments are represented only by deletion receipts.
- `docs/evaluations/operations/runbook.md` — generated operator runbook.
- `docs/papers/official-integration-parity-audit.md` — current treatment-validity and disposition authority.
- `docs/papers/phase-2-lifecycle-v0-natural-use-screening.md` — corrected first natural-use screen.
- `docs/papers/luna-xhigh-r3-natural-use-replication-screen.md` — prospective seven-profile natural-use replication screen.

## Validation

```bash
python3 scripts/validate_repository.py
python3 scripts/test_workflow_evaluation_contract.py
```

Qualification evidence is executable and generated only by:

```bash
python3 scripts/generate_workflow_qualification.py fastify-lifecycle-sequence-v0 sources/evaluations/fixtures/medium/fastify-fastify/repo
python3 scripts/generate_workflow_qualification.py beets-lifecycle-sequence-v0 sources/evaluations/fixtures/medium/beetbox-beets/repo
python3 scripts/generate_workflow_qualification.py terraform-lifecycle-sequence-v0 sources/evaluations/fixtures/large/hashicorp-terraform/repo
```

See `AGENTS.md` before changing evaluation contracts.
