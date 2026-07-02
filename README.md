# Token Optimization Research

A research workspace for determining which tools, policies, and compatibility-safe stacks reduce **cumulative provider-reported token use** in AI-assisted software-engineering workflows without reducing correctness or final software quality.

The project does **not** estimate monetary cost. Fresh input, cached input, cache-write, output, reasoning, and total provider tokens are recorded when the provider exposes them; total workflow token use is the primary metric.

## Grand objective

Produce practical, reproducible guidance for common AI-assisted software-engineering work:

> Identify interventions that reduce cumulative token use per correctness-accepted workflow while preserving software quality, diagnostic fidelity, and a normal-user treatment configuration.

The primary practical workflow is a compact lifecycle sequence rather than a language matrix:

1. one feature implementation;
2. one behavior-preserving refactor;
3. one code-review task, including correction of any acceptance-critical defect found.

Maintenance regression repair, diagnosis, migration, documentation, and other task types remain useful optional lanes. Existing Fastify, Terraform, and Beets maintenance runs remain valid evidence for their frozen maintenance scope; later lifecycle runs add evidence rather than replacing them.

## Research system

This repository is not a list of tips. It:

- collects implementations and claims with pinned provenance;
- decomposes products into atomic techniques and owned surfaces;
- inspects source logic before using a tool in evaluation decisions;
- models compatibility and conflicts between techniques;
- evaluates treatments in persistent multi-task workflows;
- records provider token use, structured per-task verifier outcomes, independent software-quality review, treatment installation/configuration, isolation, optional use telemetry, and recoverable artifacts;
- retains negative, failed, and zero-use findings;
- synthesizes evidence into scoped practitioner guidance.

## Evaluation principles

- **One replicate means one complete multi-task workflow execution, not one task.**
- A single replicate is a screening observation. Additional same-contract replicates accumulate confidence as token budget permits.
- New runs are additional evidence. They are not “replacement runs” unless an earlier run is explicitly invalidated by a demonstrated contract, isolation, or artifact defect.
- Frozen protocol evidence remains valid within its recorded scope. Reporting-only runner or schema improvements do not split a comparison pool; changes to prompts, task seeds, acceptance verifiers, model-visible treatment, runtime, or isolation do.
- Every concealed task verifier runs even when an earlier verifier fails. Structured per-task outcomes determine `tasks_passed`.
- Lower token use is not a positive result when correctness or independent quality is worse.
- Treatment lanes represent the declared normal-user configuration. Treatment availability, mandatory policy, and integrated-owner profiles are distinct estimands and must be labeled explicitly.
- Candidate expansion is paused. The first lifecycle screen is reduced to one atomic treatment, `retrieval-codegraph`; all other unexecuted candidates are deferred until that screen or a concrete mechanism gap justifies reconsideration.

## Lean decision metrics

Required canonical metrics are limited to evidence that directly supports the token-versus-correctness conclusion:

- provider-reported token components and workflow total;
- operational completion and agent-declared completion per task;
- structured concealed-verifier result per task;
- final independent software-quality score and critical failures;
- documented treatment installation/configuration plus isolation result; observed use is optional descriptive telemetry, not an acceptance gate;
- immutable protocol and compact-artifact integrity.

Money estimates, latency, setup/index timing, broad behavior telemetry, and manually scored stale-context observations are not required decision metrics. Existing raw event evidence may support targeted diagnostics without expanding every canonical record.

## Evidence stages

- `lead` — discovery/backlog only;
- `source-logic` — implementation mechanism and compatibility inspected;
- `benchmark-audit` — external benchmark harness and scoring inspected;
- `reproduction` — controlled persistent workflow with provider token accounting and software-quality gates.

## Start here

- Architecture: [`docs/architecture/README.md`](docs/architecture/README.md)
- Evaluation framework: [`docs/evaluations/evaluation-framework.md`](docs/evaluations/evaluation-framework.md)
- Workflow runbook: [`docs/evaluations/workflow-evaluation-runbook.md`](docs/evaluations/workflow-evaluation-runbook.md)
- Token and quality standard: [`docs/evaluations/token-usage-and-quality-standards.md`](docs/evaluations/token-usage-and-quality-standards.md)
- Cumulative result schema: [`docs/evaluations/cumulative-result-schema.md`](docs/evaluations/cumulative-result-schema.md)
- Research roadmap: [`docs/research/roadmap.md`](docs/research/roadmap.md)
- Current findings: [`docs/truthmark/engineering/research/current-findings.md`](docs/truthmark/engineering/research/current-findings.md)
- Phase 1 report: [`docs/reports/phase-1-compatibility-safe-token-saving-stacks.md`](docs/reports/phase-1-compatibility-safe-token-saving-stacks.md)

## Validate the workspace

```bash
truthmark check --json
truthmark index --json
python3 -m unittest scripts.test_workflow_evaluation_contract
python3 scripts/validate_repository.py
git diff --check
```
