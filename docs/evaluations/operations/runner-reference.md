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
6. after every prompt completes, run the complete controller verifier suite once against the cumulative final repository; active Lifecycle V1 executes three controller-only affected-component compile commands and then one frozen project-wide compile command, while historical V2/V3/V4 protocols retain their frozen acceptance contracts;
7. extract cumulative provider tokens and retain the ordered checkpoints plus final diff.

Future prompts remain controller-only until their turn. Future regression code is present from lane start. The model container does not mount task fixtures, seed patches, controller Git objects, or verifier scripts. Controller verifier hashes are checked during the lane, but functional verification provides no intermediate feedback and never truncates a lane.

Executed Baseline V3/V4 wrappers, qualifications, protocols, and provider evidence are immutable historical records and must not be rewritten for the new task contract. Lifecycle V1 gives Fastify and Beets active task directories, qualifications, pool fingerprints, and protocols; Terraform V1 is rejected historical evidence with no current launch path. Each active task seeds an authentic semantic regression from completed upstream behavior and gives the agent a normal software-engineering objective that expects correct implementation through repository discovery and related-code inspection. Controller scoring and compile commands are not model-facing, and no acceptance tests are injected. Provider-free qualification must prove clean standalone seed/fix round-trips, conflict-free composite seeding, controller compilation on seeded and repaired states, aggregate verifier execution, and the fully repaired project's final compile command before a pilot can be authorized.

The matrix takes a global production lock before provider-capable planning and passes the locked file descriptor to its isolated lane runners. Immediately before an authorized current-generation baseline matrix launches provider-capable jobs, it atomically creates immutable generation-specific per-sequence attempt receipts in the controller authority; direct runners reserve the same identity after all preflights and before the first provider task. Both planning paths reject any existing receipt, so strict-ingress rejection or process interruption cannot reopen a paid slot for pass-selection. Direct provider runners acquire the same global lock before checking slot availability and hold it through compact-artifact publication and the atomic registry slot recheck. Accepted treatments resolve their comparison ID only to an error-free canonical schema-v2 baseline with exact protocol, selected-execution, provider-usage, and compact-evidence identity. Matrix publication binds each returned record to its planned sequence/profile/replicate/protocol/pool/selected-execution tuple, verifies its exact compact bundle before copying, immediately tracks every copied artifact, registry replacement attempt, and comparison path, rereads the registry under the lock, rejects full-slot collisions across retained and batch records, and uses durable same-directory atomic publication. Any publication interruption—including `KeyboardInterrupt` or `SystemExit`—or post-publication validation failure, including a failure in the repository contract suite, triggers best-effort restoration of the prior registry and generated authorities and removal of every tracked artifact/comparison. This prevents concurrent or misclassified session IDs from consuming a sample slot. Rejected compact evidence is copied into a unique sibling temporary directory, fsynced, and atomically renamed before cleanup. If preservation cannot complete, a durable sentinel suppresses checkout cleanup so the complete source remains recoverable. Disposable lane checkouts are otherwise removed unless `--keep-lanes` is set.

## Activation and prerequisites

Fastify and Beets are the active primary sequences under Lifecycle V1. Their provider-free qualifications passed and their GPT-5.6 Sol/high r0 pilots are retained; treatment remains blocked pending the required pilot audit. Terraform's incomplete V1 r0 is rejected historical evidence and cannot be rerun or used for treatment. Unit tests, behavior, style, and source-review findings do not gate treatment launch.

An active sequence must have:

- authentic semantic regression tasks with one or two production targets;
- clean standalone seed/fix round-trips with seeded compiler outcomes limited to 0 or 1 and fixed compilation succeeding;
- a deterministic conflict-free composite semantic seed;
- evidence that every composite seeded compiler outcome is 0 or 1 and every repaired compile verifier exits zero;
- model-facing prompts that state complete software objectives without scoring-policy or compile-command disclosure;
- clean model-facing prompt sequencing and verifier isolation.

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
- qualification proves composite semantic seed application, records seeded controller compiler outcomes, and verifies full-fixed cumulative/project-wide success;
- the current agent prompt contains no controller compile command or internal scoring-policy disclosure.

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

Lifecycle V1 component compile-verifier outcomes determine per-task pass/fail; the final project-wide compile outcome determines workflow pass/fail and whether the baseline pilot can unlock treatments. Broader tests, behavior, style, maintainability, and source-quality reviews remain diagnostic evidence about sampled model behavior and do **not** gate token accounting. Baseline reuse additionally requires every compile task to pass, canonical execution identity, complete provider-usage shape and arithmetic, and an exact four-file compact bundle whose run record and manifest are bound to the session. Keep the first operationally valid sample for each frozen protocol and replicate; never rerun merely because diagnostic quality is imperfect. Rerun only when the fixture/contract was invalid or the provider execution was operationally incomplete. Every planned non-prepare lane must emit exactly one strict-valid authoritative session before the matrix can pass or publish comparisons; exit code zero without that session is a failed matrix. Matrix publication validates produced sessions independently: strict-valid siblings are retained even when another lane exits nonzero or emits no valid session. Before checkout cleanup, each bounded rejected compact root is copied byte-for-byte to `<lane>/rejected-evidence/<session-id>/` with a separate `rejection.json`; that copy is diagnostic, is listed in `failure_evidence`, and can never enter the accepted registry. Oversized, symlinked, directory-bearing, or otherwise unbounded roots remain rejected without unsafe recursive copying. Copied accepted and rejected artifact files and their destination and parent directories are fsynced before the registry is durably replaced. The outer publication transaction exclusively owns rollback so the initiating failure is preserved and cleanup failures are aggregated rather than masking it.

## Compact artifacts

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json              # protocol identity, total usage, operational checkpoints, final verifier result
  changes.diff          # ordered cumulative checkpoints plus final cumulative diff
  evidence.jsonl.gz     # prompts, provider events, setup, composite seed, integrity, final verifier, audit
  manifest.sha256       # hashes for the other three files
```

The session directory must contain exactly these four nonsymlink regular files at `sources/evaluations/workflow-sessions/<session_id>`—no relocated roots, directory aliases, additional files, directories, or symlinks. The manifest covers exactly the first three; `evidence.jsonl.gz` must be a nonempty, total- and per-record-bounded, valid gzip stream of unique canonical relative-path JSONL evidence objects with no duplicate JSON members; and `run.json` must match the registry session’s protocol, pool, selected execution, complete provider usage, acceptance, ordered task outcomes, verifier integrity, Docker/tool identities, and runtime/provider/model/model-condition/reasoning tuple. Immutable historical records may retain a null cache-write measurement, but that compatibility representation is not reusable at current runtime ingress. Three immutable Ponytail r2 records retain their original `run.json` rejection bit alongside the later zero-provider registry re-audit that accepted their accounting evidence; this compatibility exception is ID-bounded and cannot apply to current records.

Direct and matrix publication both apply this same strict validator before registry mutation. After dependency validation and before lock acquisition or run-root creation, the matrix creates/validates the configured lane-base path one component at a time with `lstat` semantics; any alias or non-directory ancestor aborts planning. Immediately before each provider-capable child starts, the matrix writes and fsyncs a lane-local cleanup-prohibition sentinel and records the prohibition in memory. The guard remains through child exit, registry/artifact discovery, merge, downstream validation, and transaction commit. Any rejected or interrupted paid lane is routed through the atomic rejected-evidence copier: a lock-protected, reference-counted run sentinel covers parallel lane copies; unique same-directory temporary names prevent thread collisions; every lexical ancestor from the filesystem root through the trusted run root, lane, checkout, artifact root, and session directory must be a real directory; and the lane/rejected-evidence destination root is created without following aliases, opened with `O_NOFOLLOW`, identity-checked against the unresolved trusted run root, and rechecked before copying and atomic publication. Copied evidence is bounded and nonsymlinked, and the temporary tree is fsynced before atomic rename. Existing preservation destinations are fail-closed collisions, including a retry after post-rename fsync failure. Only a newly completed and parent-fsynced bundle permits checkout cleanup. Ambiguous, missing, regular-file, symlinked source or destination root/ancestor, escaped, or otherwise unsafe output keeps the whole checkout without writing through the alias. A sentinel-write failure also retains the in-memory cleanup prohibition, so an occupied identity never loses its sole source checkout.

Baseline V3 dependency bootstrap uses non-login `bash -c` with `/opt/data/bin` and `/opt/data/opt/go/bin` explicitly prepended. Beets uses `uv sync --group test --frozen`; Beets `uv.lock` and Terraform `go.sum` hashes are protocol-bound. The nine provider-free production-container literal-command and controller-verifier outputs are immutable, hash-checked receipts under `sources/evaluations/audits/baseline-v3-literal-command-receipts-20260722/`; receipt task order, provider counts, provider tokens, and bootstrap/command/verifier exit codes must be strict non-boolean integers. Every numeric qualification exit/count and every decision-bearing Baseline V3 audit count/order must likewise use a real JSON integer, never a boolean lookalike. These receipts are qualification evidence only, not paid-run evidence.

Baseline V4 retains the same pinned dependency contracts. Its six literal-command receipts live under `sources/evaluations/audits/baseline-v4-literal-command-receipts-20260722/`; the task-family audit additionally binds each qualification's aggregate-wrapper exit and exactly three task exits plus the two-lane prepare-only manifest. All provider counts and tokens are strict integer zero. These artifacts do not occupy a pilot identity.

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
