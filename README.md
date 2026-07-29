# Token Optimization Research

Research infrastructure for measuring provider-reported token usage and software quality in realistic coding-agent workflows.

## Current evaluation portfolio

The repository retains operationally valid Fastify, Beets, and Terraform provider-token evidence; verifier and review outcomes remain diagnostic for completed sessions. The active low-complexity portfolio is mixed-generation: Fastify retains its passing **Baseline V3** contract, while Beets and Terraform each have a paid and independently audited **Baseline V4** control. Each routine task supplies one exact mechanical edit command, changes one or two production files, exposes focused validation, and forbids discovery and broad suites. The lifecycle portfolio remains:

| Sequence | Fixture | Ordered stages |
|---|---|---|
| `fastify-lifecycle-sequence-v0` | Fastify | feature → behavior-preserving refactor → code review |
| `beets-lifecycle-sequence-v0` | Beets | feature → behavior-preserving refactor → code review |
| `terraform-lifecycle-sequence-v0` | Terraform | feature → behavior-preserving refactor → code review |

Every lane uses one pinned repository snapshot and one persistent model session. The controller applies all three independently qualified start conditions and their focused model-visible acceptance tests before prompt 1, discloses prompts in order, and preserves model/tool state. The explicitly authorized Baseline V3 pilot on 2026-07-22 retained three first-valid provider-backed controls totaling 236,151 provider tokens: Fastify 76,623, Beets 73,584, and Terraform 85,944. All nine literal model commands exited zero and produced the prescribed narrow diffs. Fastify's repeated final verifier passed 3/3; Beets and Terraform each reported 0/3 only because the final-verifier wrapper failed to export `WORKFLOW_REPO`, despite the same focused commands passing inside all six model turns. The matrix's first publication transaction also rolled back when two post-publication contract assertions incorrectly treated a historical accounting audit as open-ended and baseline presence as sufficient to expose treatment commands. Those assertions were corrected and the immutable compact bundles were recovered without provider reruns. The three V3 pilot identities remain occupied. Treatment eligibility is determined per sequence by the independent zero-incident audit; no failed lane may be rerun for a favorable result.

Baseline V4 corrects only the Beets and Terraform verifier-environment contract under new task, qualification, pool, protocol, audit, and attempt identities. It keeps task difficulty and prescribed edits unchanged. The authorized 2026-07-28 pilots retained Beets at 88,200 provider tokens and Terraform at 87,811; GPT-5.6 Sol/`high` executed all six prescribed commands once, all task and final verifiers passed, and independent trajectory audits recorded strict integer zero in all eight incident categories for both sequences. Separate stale post-publication state tests initially rolled each registry transaction back; both exact compact bundles were recovered transactionally without another provider call. Both r0 identities are occupied and non-rerunnable, and both sequences are eligible for provider-free treatment-protocol freeze.

A 2026-07-18 official-integration audit and follow-up runtime review found that 48 of 54 historical treatment sessions could not support product-effect claims. At the experiment owner's direction, invalid sessions, comparisons, compact bundles, and occupied protocols were deleted from the active corpus rather than relabelled as baseline. The same policy later removed six incomplete Cartog direct-MCP sessions. Deletion receipts preserve each adjudication; the six retained original historical records are the Headroom default-wrapper and proxy-only conditions, and the prior TokenJuice+jcodemunch stack decision remains withdrawn.

Sixteen eligible historical treatment conditions contribute 66 accepted provider-backed sessions alongside 35 controls. After withdrawing twelve invalid or unproven OpenCode treatment sessions, the active registry contains 155 accepted sessions: 35 baselines, 3 replacement-runtime OpenCode controls, and 117 individual-tool treatments. The current treatment-compatible low-complexity controls—Fastify V3, Beets V4, and Terraform V4—now contain three valid runs per lane: 783,883 provider tokens and 322,096.0 weighted token-cost units under `fresh + 0.1×cached + 6×output`; the machine-readable report is `sources/evaluations/audits/current-low-complexity-control-token-cost-20260728.json`. Fastify r2 retained 90,420 tokens and Terraform r2 retained 87,784; all six prescribed commands and final task verifiers passed, and independent trajectory review recorded zero incidents in every required category. Beets r2 failed before the provider boundary when lane scratch disappeared during checkout materialization. Its immutable receipt remains an occupied zero-spend controller failure—not a session or token result. The distinct owner-authorized Beets r3 replacement retained 87,370 provider tokens (43,130.2 weighted units), with 3/3 commands and verifiers passing, one persistent thread, and zero retries; its compact session was recovered provider-free after stale receipt-state tests rolled back publication. The Phase 2 synthesis reports 551,060,181 treatment tokens against 509,861,580 repeated matched-baseline tokens (+8.08%) with 141/144 task verifiers. A prospective r3 screen used 216,039,299 tokens against 202,598,376 repeated fresh-baseline tokens (+6.63%) with 53/54 task verifiers; four of six aggregate directions changed. The assisted-v1 Sol/`high` baseline retained 7,718,469 tokens and 9/9 verifier passes, but trajectory review found substantive corrections and one surviving hidden-contract regression. It remains immutable historical evidence and is not a Baseline V3 or V4 comparison control.

Bare OpenCode 1.18.9 with GPT-5.6 Sol/`high` retained 122,368 provider tokens across the three lifecycle-v0 workflows. A stricter installation audit withdrew the TokenJuice, Snip, Cartog, and Headroom generations; only Serena's three original sessions remain active while fresh successor profiles await paid execution. The deletion and recovery boundary is recorded in `sources/evaluations/audits/invalid-opencode-treatment-result-deletions-20260729.json`.

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
- `docs/papers/luna-xhigh-r3-natural-use-replication-screen.md` — prospective six-profile eligible natural-use replication screen.

## Validation

```bash
python3 scripts/validate_repository.py
python3 scripts/test_workflow_evaluation_contract.py
```

Fixture qualification evidence is executable and generated by:

```bash
python3 scripts/generate_workflow_qualification.py fastify-lifecycle-sequence-v0 sources/evaluations/fixtures/medium/fastify-fastify/repo
python3 scripts/generate_workflow_qualification.py beets-lifecycle-sequence-v0 sources/evaluations/fixtures/medium/beetbox-beets/repo
python3 scripts/generate_workflow_qualification.py terraform-lifecycle-sequence-v0 sources/evaluations/fixtures/large/hashicorp-terraform/repo
```

Executed provider-free integration matrices are published with `scripts/publish_integration_qualification.py`; the publisher rejects nonzero lanes, provider-backed session creation, failed preparation, failed host integration, failed warmup, or failed MCP handshakes.

See `AGENTS.md` before changing evaluation contracts.
