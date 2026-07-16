# Cumulative result schema

## Purpose

Primary evidence is stored as append-only workflow-session records, with compact decision fields in `data/workflow-sessions.json` and recoverable evidence under `sources/evaluations/workflow-sessions/<session-id>/`.

The primary metric is cumulative provider-reported token use across a persistent software-engineering workflow. Monetary cost is out of scope.

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

A replicate is one complete execution of an ordered workflow sequence. A workflow with three tasks has three structured task outcomes but remains one replicate.

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

## Required decision fields

Each new workflow record uses session `schema_version: 2` and contains:

1. **Identity and scope** — session, study, sequence, profile, model condition, replicate, evidence stage, and frozen protocol.
2. **Token use** — provider source, exposed token components, total provider tokens, reconstruction basis, and tokens per accepted task.
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

Treatment estimands must be explicit. Lifecycle-v0 production profiles use availability/natural use with the product's normal integration and no evaluator-authored invocation steering. Prompted preferred direct use and mandatory policy remain historical taxonomy only; they are not runnable production remedies for low or unobserved explicit invocation. Historical protocol semantics are never silently rewritten to a newer profile definition. Explicit command absence is not interpreted as integration inactivity unless the frozen mechanism contract makes that observation complete.

## Directory convention

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json
  changes.diff
  evidence.jsonl.gz        # includes final-verifier-results.json
  manifest.sha256
```

Historical bundles without the new structured result object remain valid under their frozen runner contract; their reviewed task outcomes stay in the compact registry and reports.
