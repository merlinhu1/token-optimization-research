# Cumulative result schema

## Purpose

Primary evidence is stored as append-only workflow-session records, with compact decision fields in `data/workflow-sessions.json` and recoverable evidence under `sources/evaluations/workflow-sessions/<session-id>/`.

The sole token metric is weighted token cost across a persistent software-engineering workflow: `fresh input + 0.1 × cached input + 6 × output`. Raw provider counters are calculation/audit telemetry, never result metrics. Monetary cost is out of scope.

## Core entities

| Entity | File | Role |
|---|---|---|
| Repository fixture | `data/repository-fixtures.json` | Frozen target, snapshot, setup/reset policy, and scale. |
| Workflow task sequence | `data/workflow-task-sequences.json` | Ordered tasks and persistence policy. |
| Evaluation profile | `data/evaluation-profiles.json` | Baseline or declared treatment configuration. |
| Agent/model registry | `data/evaluation-agent-runtimes.json` | Runtime/provider/model condition, independent of the tool profile. |
| Workflow session | `data/workflow-sessions.json` plus session directory | One complete baseline or treatment workflow replicate. |
| JSON schema | `schemas/workflow-session-record.schema.json` | Machine validation for compact records. |

## Replicate semantics

A replicate is one complete execution of an ordered workflow sequence. A workflow with three tasks has three structured task outcomes but remains one replicate. Its `replicate_index` is an immutable **runtime-local attempt label**; do not assume the same `rN` across different runtimes denotes a comparison pair.

Replicates are cumulative evidence:

- add one record per executed session;
- never overwrite raw metrics or compact evidence;
- do not call a later compatible execution a replacement run;
- exclude an earlier session only when a recorded contract, isolation, accounting, or artifact defect makes the intended inference invalid;
- preserve valid earlier sessions under their frozen scope even when the framework later improves.

## Comparison identity

A comparison pool is defined by causal/model-visible inputs:

- fixture snapshot and seed state;
- task order, prompt bytes, and acceptance-verifier bytes;
- baseline substrate or treatment configuration;
- runtime image and model condition;
- prompt disclosure and isolation policy.

Full runner, validator, generator, and schema hashes remain in the frozen protocol for provenance. Reporting-only implementation changes do not split a comparison pool. A change to a causal/model-visible input produces a new comparison identity.

The active pools retain their existing fingerprints through guarded causal-identity aliases so accumulated runs remain pairable after framework-only repairs.

### Cross-runtime accepted-order pairing

When one runtime has an excluded attempt and the other does not, `replicate_index` cannot be used as the cross-runtime key. The accepted treatment record must instead carry both `interpretation.comparison_baseline_session_id` and `interpretation.comparison_pair`, which names an `accepted-replicate-ordinal` and the two runtime-local labels. The validator requires matching pool, sequence, model-facing prompt hashes, model, reasoning effort, and accepted compact evidence before accepting that cross-index binding. See [Lifecycle V1 accepted-replicate pairing](lifecycle-v1-accepted-replicate-pairing.md) for the current map.

## Required decision fields

Each new workflow record uses session `schema_version: 2` and contains:

1. **Identity and scope** — session, study, sequence, profile, model condition, replicate, evidence stage, and frozen protocol.
2. **Token use** — weighted token cost, provider source, canonical formula, and internal component telemetry sufficient to audit the calculation.
3. **Per-task outcomes** — task ID/order, operational exit, declared completion, retry count, structured verifier exit/pass, and accepted state.
4. **Software quality** — tasks attempted/completed/passed, final verifier state, independent review status, quality score, and critical failures.
5. **Execution integrity** — verifier-integrity result, treatment-isolation result, external-retrieval hits, and pass-through treatment-command hits.
6. **Artifacts** — compact run record, final diff, evidence bundle, manifest, and checksums.
7. **Interpretation** — objective eligibility, comparison baseline, exclusions, screening/ranking status, and limitations.

Broad `state_observations` and `operational_reproducibility` objects remain readable for historical records but are no longer required for new records. Their prior null or constant fields did not support the core token-versus-correctness decision.

Money estimates, latency, setup/index timing, turn count, tool-call count, and manually scored behavior observations are not canonical requirements. Raw events may be examined for targeted diagnostics. Immutable historical `run.json` bundles may retain obsolete null-only cost keys for checksum provenance; the canonical registry, schema, and new runner output do not publish them.

## Concealed verifier result artifact

Each completed eligible lane emits `final-verifier-results.json` with one result per task. The controller:

- runs all task verifiers without short-circuiting;
- rejects duplicate, missing, malformed, or unexpected outcomes;
- joins each result to its per-task checkpoint;
- requires exact ordered task coverage and explicit attempt/verifier fields in schema-v2 records;
- cross-checks `tasks_attempted`, `tasks_passed`, final-verifier state, and functional-verifier state against those outcomes;
- derives `tasks_passed` from `accepted: true` values.

If provider execution or verifier integrity prevents final verification, each task records `not-run` rather than being fabricated as a deterministic failure.

## Treatment profiles

Treatment estimands must be explicit. Lifecycle-v0 canonical product profiles use availability/natural use after faithful installation of every tool-author-recommended normal integration surface, including product-authored guidance, rules, skills, and hooks. The evaluator may not add steering or forced calls, but it also may not strip or contradict the product's own guidance. Server-only, guidance-free, and other reduced conditions are explicit ablations, never substitutes for the canonical product treatment. Prompted preferred direct use and mandatory policy remain historical taxonomy only; they are not runnable production remedies for low or unobserved explicit invocation. Historical protocol semantics are never silently rewritten to a newer profile definition. Explicit command absence is not interpreted as integration inactivity unless the frozen integration's mechanism instrumentation makes that observation complete.

## Directory convention

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json
  changes.diff
  evidence.jsonl.gz        # includes final-verifier-results.json
  manifest.sha256
```

Historical bundles without the new structured result object remain valid under their frozen runner contract; their reviewed task outcomes stay in the compact registry and reports.
