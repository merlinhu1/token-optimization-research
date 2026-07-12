# Warm-state workflow lane runner

This page documents runner details. The maintained operator runbook is `docs/evaluations/operations/runbook.md`, rendered from the active workflow registries.

## What this runner does

`scripts/run_codex_workflow_evaluation.py` runs one profile on one active multi-task sequence from `data/workflow-task-sequences.json`.

The primary lane measures cumulative provider usage after model and tool state warm up:

1. merge every qualified regression against the same pinned fixed snapshot before provider execution;
2. conceal the fixed snapshot and commit the composite broken tree as one parentless model-facing root;
3. materialize and send task 1 only;
4. capture its provider events and cumulative source checkpoint without running a controller verifier;
5. resume the same Codex thread with each later prompt while preserving source, tool, index, cache, profile, and agent state;
6. after every prompt completes, run the complete controller verifier suite once against the cumulative final repository; for Baseline V2, compare every declared model-visible focused test byte-for-byte with its integrity-bound controller-owned canonical copy, then execute the unchanged model-visible test path;
7. extract cumulative provider tokens and retain the ordered checkpoints plus final diff.

Future prompts remain controller-only until their turn. Future regression code is present from lane start. The model container does not mount task fixtures, seed patches, controller Git objects, or verifier scripts. Controller verifier hashes are checked during the lane, but functional verification provides no intermediate feedback and never truncates a lane.

The matrix takes a global production lock before provider-capable planning and passes the locked file descriptor to its isolated lane runners. Direct provider runners acquire that same lock before checking slot availability and hold it through compact-artifact publication and the atomic registry slot recheck. Accepted treatments resolve their comparison ID only to an error-free canonical schema-v2 baseline with exact protocol, selected-execution, provider-usage, and compact-evidence identity. Matrix publication binds each returned record to its planned sequence/profile/replicate/protocol/pool/selected-execution tuple, verifies its exact compact bundle before copying, immediately tracks every copied artifact, registry replacement attempt, and comparison path, rereads the registry under the lock, rejects full-slot collisions across retained and batch records, and uses durable same-directory atomic publication. Any publication interruption—including `KeyboardInterrupt` or `SystemExit`—or post-publication validation failure, including a failure in the repository contract suite, triggers best-effort restoration of the prior registry and generated authorities and removal of every tracked artifact/comparison. This prevents concurrent or misclassified session IDs from consuming a sample slot. The matrix retains only bounded compact failure evidence and removes disposable lane checkouts unless `--keep-lanes` is set.

## Activation and prerequisites

Fastify, Terraform, and Beets are the active primary sequences after behavioral fixture qualification. Provider-backed execution requires an explicit frozen protocol and operator authorization; Baseline V2 additionally requires the one canonical protocol ID/path for the configured model condition. A direct treatment run must find a reusable canonical baseline for the same sequence, pool, and replicate before any setup or provider spend. That baseline must be top-level and selected-execution baseline evidence under `baseline-bare-codex`; every accepted treatment record must carry its resolved baseline-session binding. Fixture validation uses `--prepare-only`.

An active sequence must have:

- causally related behavioral tasks;
- standalone seeded-fail/fixed-pass evidence for every task;
- a deterministic conflict-free composite seed;
- evidence that every task verifier fails against the composite broken start;
- evidence that every verifier passes against the fixed snapshot;
- clean model-facing concealment and verifier isolation.

For an activated sequence, verify the runner and container from the repository root:

```bash
python3 scripts/run_codex_workflow_evaluation.py --list-sequences
docker image inspect token-eval-codex:latest >/dev/null
```

Frozen protocols bind qualification bytes, execution-harness hashes, Dockerfile hash, inspected image identity, and task-directory bytes. Runtime setup rejects stale bindings before provider spend. `scripts/refresh_workflow_contracts.py` validates qualification evidence and never invents qualification results.

## No-model prepare gate

Run `--prepare-only` after any fixture, verifier, prompt, runner, or isolation change. `prepare-verification.json` must prove:

- every declared regression was merged into the composite broken start;
- only `task-prompts/task-01.md` was materialized;
- task fixtures, seed patches, and verifier scripts remain controller-only;
- the model-facing Git repository has one clean parentless commit and no remote;
- the fixed snapshot object is absent from the model-facing object database and reflog;
- qualification proves composite-seeded failure and full-fixed cumulative success.

Preparation does not call the model and does not authorize a paid run.

## Runtime acceptance

There are no per-task hidden functional gates. Between prompts, the controller stops only for operational invalidity such as a nonzero Codex process exit, missing thread identity, verifier-integrity corruption, isolation failure, or unrecoverable runtime failure.

A provider-backed lane is eligible for the token-usage objective when:

- every scheduled prompt completed in the same thread;
- provider usage is complete and warning-free;
- verifier integrity and tool isolation pass;
- compact evidence is recoverable.

Usage extraction is thread-aware. Codex `turn.completed.usage` carries cumulative `ThreadTokenUsage.total`; `scripts/extract_codex_usage.py` schema v2 selects the final snapshot per distinct thread and derives per-task increments by differencing snapshots. A decreasing cumulative counter is an accounting-integrity failure. OpenAI Codex reports cache reads but no cache-write category, so the extractor records the unsupported `cache_write_tokens` component as exact integer zero. Every initial, resumed, and operational-retry event stream must independently contain exactly one unique `thread.started` identity; resumed/retry identities must equal the first task's persistent thread, and any mismatch is an operational continuity failure that blocks acceptance. Historical schema-v1 summaries remain immutable and require the retained correction audit.

A production workflow must use a controller Python that can import the repository validation dependencies, including `jsonschema`. The matrix probes this before creating or starting any lane and fails before provider spend if no prepared interpreter is available. Set `WORKFLOW_VALIDATION_PYTHON` explicitly when the launching interpreter lacks those dependencies.

Concealed verifier outcomes and source-quality reviews remain diagnostic evidence about the sampled model behavior. They do **not** gate token accounting or baseline reuse. Reuse still requires the canonical execution identity, complete provider-usage shape and arithmetic, and an exact four-file compact bundle whose run record and manifest are bound to the session. Keep the first operationally valid sample for each frozen protocol and replicate; never rerun merely because the model produced imperfect code or received a sub-perfect review score. Rerun only when the fixture/contract was invalid or the provider execution was operationally incomplete. Every planned non-prepare lane must emit exactly one strict-valid authoritative session before the matrix can pass or publish comparisons; exit code zero without that session is a failed matrix. Matrix publication validates produced sessions independently: strict-valid siblings are retained even when another lane exits nonzero or emits no valid session, while rejected lane artifacts remain only as bounded diagnostic evidence under the matrix run root. Copied artifact files and their destination and parent directories are fsynced before the registry is durably replaced. The outer publication transaction exclusively owns rollback so the initiating failure is preserved and cleanup failures are aggregated rather than masking it.

## Compact artifacts

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json              # protocol identity, total usage, operational checkpoints, final verifier result
  changes.diff          # ordered cumulative checkpoints plus final cumulative diff
  evidence.jsonl.gz     # prompts, provider events, setup, composite seed, integrity, final verifier, audit
  manifest.sha256       # hashes for the other three files
```

The session directory must contain exactly these four nonsymlink regular files at `sources/evaluations/workflow-sessions/<session_id>`—no relocated roots, directory aliases, additional files, directories, or symlinks. The manifest covers exactly the first three; `evidence.jsonl.gz` must be a nonempty, total- and per-record-bounded, valid gzip stream of unique canonical relative-path JSONL evidence objects with no duplicate JSON members; and `run.json` must match the registry session’s protocol, pool, selected execution, complete provider usage, acceptance, ordered task outcomes, verifier integrity, Docker/tool identities, and runtime/provider/model/model-condition/reasoning tuple. Immutable historical records may retain a null cache-write measurement, but that compatibility representation is not reusable at current runtime ingress. Three immutable Ponytail r2 records retain their original `run.json` rejection bit alongside the later zero-provider registry re-audit that accepted their accounting evidence; this compatibility exception is ID-bounded and cannot apply to current records.

Do not publish materialized checkouts, virtual environments, Codex homes, caches, controller Git objects, or split logs.

## Common problems

### Stale protocol

After any bound runner, prompt, verifier, qualification, schema, runtime, or task-directory change:

```bash
python3 scripts/refresh_workflow_contracts.py
```

Refresh only after qualification has been regenerated from a clean pinned checkout.

### Composite seed conflict

A conflict means two independently-authored regressions cannot coexist unambiguously. Repair or replace the fixture tasks and regenerate qualification. Do not fall back to injecting a patch over model-authored work.

### Missing Codex authentication or image

Use lane preflight output. Do not publish copied Codex homes. Build the standard image with the documented fixture Dockerfile when its pinned identity is intentionally changed.

## Validation

```bash
python3 scripts/test_workflow_evaluation_contract.py
python3 scripts/validate_repository.py
git diff --check
truthmark check --json
truthmark index --json
```

A current record uses sequential prompt disclosure, `preseeded-composite` seed delivery, `final-only` controller verification, one true-root baseline at lane start, and persistent repository/tool/agent state through the complete lane.
