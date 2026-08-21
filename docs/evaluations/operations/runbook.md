# Workflow Evaluation Runbook

This generated runbook reflects current workflow-sequence readiness.

It is rendered from `data/workflow-task-sequences.json`, `data/repository-fixtures.json`, `data/evaluation-profiles.json`, `data/evaluation-agent-runtimes.json`, and `data/workflow-sessions.json` by `scripts/update_workflow_runbook.py`.

Do not hand-edit execution status here. Update the registries, then run:

```bash
python3 scripts/update_workflow_runbook.py
python3 scripts/validate_repository.py
```

## Evidence boundary

A valid active Lifecycle V2 workflow pre-seeds every authentic semantic regression from completed upstream behavior into one qualified composite start, then materializes one normal software-engineering prompt at a time. Each prompt states the observable symptom without naming the file, function, or test, permits repository search and related-code inspection, and expects a complete correct implementation without disclosing evaluator scoring or controller commands. Fastify and Beets use their frozen qualified environments; Terraform V1's owner-declared-invalid r0 was removed and has no current runbook entry. Seed patch files, controller scripts, fixed parents, task acceptance commands, and the final project-wide compile command remain outside the model-visible surface. Product-effect eligibility also requires parity with the pinned official integration and positive treatment-assignment evidence; configuration/listing alone is insufficient.

Internally, every active task requires affected-component compilation. Feature and refactor tasks add one narrow essential-behavior smoke; review tasks remain compile-only. Broader tests, behavioral fidelity, style, maintainability, and source review remain diagnostic and do not determine evaluator pass/fail. This internal policy must never be presented as an agent instruction.

## Claude Code direct-Anthropic preparation

_No direct-Anthropic Claude Code preparation authority is present._

## Active sequences

| Sequence | Fixture | Scale | Snapshot | Tasks |
|---|---|---|---|---:|
| `fastify-lifecycle-sequence-v2` | `medium-fastify-fastify` | medium-project | [`94bcbcc6e2ef`](https://github.com/fastify/fastify.git) | 6 |
| `beets-lifecycle-sequence-v2` | `medium-beetbox-beets` | medium-project | [`9acb1ecff6c7`](https://github.com/beetbox/beets.git) | 6 |

## Planned candidates and blockers

_None._

## Activation gate

Before changing a sequence to `active`, require:

- one or two semantic production targets per task, restored to completed upstream behavior;
- standalone seed application and repair round-trips, with seeded verifier outcomes limited to 0 or 1 and repaired task verification succeeding;
- a conflict-free composite semantic seed whose controller verifier outcomes are all 0 or 1 at lane start;
- one parentless model-facing Git baseline with the fixed commit inaccessible;
- prompts that state complete software objectives, permit repository discovery, and withhold controller scoring;
- no model-visible acceptance commands or injected acceptance-test assets;
- controller-only component compilation for every task, one essential smoke for feature/refactor tasks, compile-only review tasks, and one frozen project-wide compile command;
- controller-only seed patch files and fixed references;
- cumulative provider usage capture, verifier integrity, isolation, structured task outcomes, and optional quality diagnostics;
- a machine-validated acceptance-passing provider pilot before any treatment provider execution or treatment unlock; provider-free protocol preparation may be frozen while native integration qualification and owner authorization remain pending.

A no-model prepare for a frozen candidate is allowed:

```bash
SEQUENCE_ID=fastify-lifecycle-sequence-v2
python3 scripts/run_sequential_workflow_matrix.py "$SEQUENCE_ID" --max-parallel 1 --workflow-model-condition-id codex-openai-gpt-5-6-sol-medium --workflow-model gpt-5.6-sol --workflow-reasoning-effort medium --prepare-only
```

`prepare-verification.json` must show every task preseeded, only task 1's prompt materialized, a clean true-root Git baseline, no fixed commit object or prior reflog, current composite qualification including recorded seeded verifier outcomes and passing repaired/project-wide boundaries, no controller seed/verifier files in the model root, no injected acceptance-test assets, and no controller acceptance command or scoring-policy disclosure in the current task prompt.

## Paid execution

Current runnable treatment profiles: `artifact-ponytail-codex-plugin-v1`, `behavior-caveman-codex-skill-v1`, `codescope-codex-product-v1`, `headroom-default-codex`, `integrated-leanctx-codex-hybrid-v1`, `integrated-token-savior-codex-product-v2`, `retrieval-cartog-codex-product-v2`, `retrieval-codegraph-codex-mcp-v1`, `retrieval-graphify-codex-skill-v1`, `retrieval-jcodemunch-codex-mcp-v2`, `retrieval-repowise-codex-product-v2`, `retrieval-serena-codex-mcp-v1`, `retrieval-sigmap-codex-live-v1`, `swarmvault-codex-product-v1`, `terminal-rtk-claude-code-hook-v1`, `terminal-rtk-codex-instructions-v1`, `terminal-snip-codex-hook-v1`, `terminal-tokenjuice-codex-hook-v1`. Historical profiles marked `historical-profile` are occupied evidence identities and cannot be rerun in place.

Provider-free preparation remains available for lanes without a reusable operational baseline; paid commands are listed only for unoccupied pilot identities:

```bash
python3 scripts/run_sequential_workflow_matrix.py beets-lifecycle-sequence-v2 --max-parallel 1 --workflow-model-condition-id codex-openai-gpt-5-6-sol-medium --workflow-model gpt-5.6-sol --workflow-reasoning-effort medium --prepare-only
python3 scripts/run_sequential_workflow_matrix.py beets-lifecycle-sequence-v2 --max-parallel 1 --workflow-model-condition-id codex-openai-gpt-5-6-sol-medium --workflow-model gpt-5.6-sol --workflow-reasoning-effort medium
```

Owner-authorized current-control replication is serialized. Commands are listed only for unoccupied identities; each paid command reserves its immutable receipts before provider work:

```bash
python3 scripts/run_sequential_workflow_matrix.py fastify-lifecycle-sequence-v2 --replicate-index 1 --max-parallel 1 --workflow-model-condition-id codex-openai-gpt-5-6-sol-medium --workflow-model gpt-5.6-sol --workflow-reasoning-effort medium --prepare-only
python3 scripts/run_sequential_workflow_matrix.py fastify-lifecycle-sequence-v2 --replicate-index 1 --max-parallel 1 --workflow-model-condition-id codex-openai-gpt-5-6-sol-medium --workflow-model gpt-5.6-sol --workflow-reasoning-effort medium
python3 scripts/run_sequential_workflow_matrix.py fastify-lifecycle-sequence-v2 --replicate-index 2 --max-parallel 1 --workflow-model-condition-id codex-openai-gpt-5-6-sol-medium --workflow-model gpt-5.6-sol --workflow-reasoning-effort medium --prepare-only
python3 scripts/run_sequential_workflow_matrix.py fastify-lifecycle-sequence-v2 --replicate-index 2 --max-parallel 1 --workflow-model-condition-id codex-openai-gpt-5-6-sol-medium --workflow-model gpt-5.6-sol --workflow-reasoning-effort medium
python3 scripts/run_sequential_workflow_matrix.py fastify-lifecycle-sequence-v2 --replicate-index 3 --max-parallel 1 --workflow-model-condition-id codex-openai-gpt-5-6-sol-medium --workflow-model gpt-5.6-sol --workflow-reasoning-effort medium --prepare-only
python3 scripts/run_sequential_workflow_matrix.py fastify-lifecycle-sequence-v2 --replicate-index 3 --max-parallel 1 --workflow-model-condition-id codex-openai-gpt-5-6-sol-medium --workflow-model gpt-5.6-sol --workflow-reasoning-effort medium
```

Reusable, zero-incident-audited baselines exist for `fastify-lifecycle-sequence-v2` (r0). No current active-default treatment protocol is frozen, so no paid treatment command is published. Choose one compatible profile, freeze and validate its protocol provider-free, certify the resulting exact tree, and then execute the rendered dry-run verbatim before requesting paid execution:

```bash
SEQUENCE_ID=fastify-lifecycle-sequence-v2
PROFILE_ID=replace-with-compatible-profile-id
python3 scripts/refresh_workflow_contracts.py --sequence-id "$SEQUENCE_ID" --profile-id "$PROFILE_ID" --workflow-model-condition-id codex-openai-gpt-5-6-sol-medium --workflow-model gpt-5.6-sol --workflow-reasoning-effort medium
python3 scripts/validate_repository.py
python3 scripts/run_sequential_workflow_matrix.py "$SEQUENCE_ID" --treatment-profile "$PROFILE_ID" --max-parallel 1 --workflow-model-condition-id codex-openai-gpt-5-6-sol-medium --workflow-model gpt-5.6-sol --workflow-reasoning-effort medium --dry-run
```

Run as many replicates per protocol as the work warrants; there is no registered N. All retained replicates are published, and a single replicate is a screen rather than an effect estimate. The point estimate is the median weighted token cost with its observed spread; no raw-token result is reported. Replace only replicates that failed before the provider boundary; verifier and review outcomes are diagnostic and never a reason to drop a sample.

## Active sequence details

### `fastify-lifecycle-sequence-v2`

- Fixture: `medium-fastify-fastify`
- Primary metric: weighted_token_cost
- Reset policy: Each task reset reverses only its own semantic production regression. No acceptance tests are injected. Every task requires affected-component compilation plus one narrow essential-behavior smoke drawn from the upstream tests that cover the restored behavior. Controller acceptance details are not disclosed as the agent task objective.
- Final project compile: `find lib -type f -name '*.js' -print0 | sort -z | xargs -0 -n1 node --check && node --check fastify.js`

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `fastify-trailer-duplicate-callback-v2` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v2/fastify-trailer-duplicate-callback-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v2/fastify-trailer-duplicate-callback-v2/verify.sh` |
| 2 | `fastify-nested-prefix-join-v2` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v2/fastify-nested-prefix-join-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v2/fastify-nested-prefix-join-v2/verify.sh` |
| 3 | `fastify-serializer-compiler-flag-v2` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v2/fastify-serializer-compiler-flag-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v2/fastify-serializer-compiler-flag-v2/verify.sh` |
| 4 | `fastify-sync-validator-throw-v2` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v2/fastify-sync-validator-throw-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v2/fastify-sync-validator-throw-v2/verify.sh` |
| 5 | `fastify-duplicated-route-method-array-v2` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v2/fastify-duplicated-route-method-array-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v2/fastify-duplicated-route-method-array-v2/verify.sh` |
| 6 | `fastify-head-route-web-stream-v2` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v2/fastify-head-route-web-stream-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v2/fastify-head-route-web-stream-v2/verify.sh` |

### `beets-lifecycle-sequence-v2`

- Fixture: `medium-beetbox-beets`
- Primary metric: weighted_token_cost
- Reset policy: Each task reset reverses only its own semantic production regression. No acceptance tests are injected. Every task requires affected-component compilation plus one narrow essential-behavior smoke drawn from the upstream tests that cover the restored behavior. Controller acceptance details are not disclosed as the agent task objective.
- Final project compile: `uv run --offline --frozen python -c "import ast, pathlib; [ast.parse(p.read_text(), filename=str(p)) for root in ('beets', 'beetsplug') for p in pathlib.Path(root).rglob('*.py')]"`

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `beets-library-file-error-message-v2` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v2/beets-library-file-error-message-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v2/beets-library-file-error-message-v2/verify.sh` |
| 2 | `beets-migration-text-paths-v2` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v2/beets-migration-text-paths-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v2/beets-migration-text-paths-v2/verify.sh` |
| 3 | `beets-subcommand-help-alignment-v2` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v2/beets-subcommand-help-alignment-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v2/beets-subcommand-help-alignment-v2/verify.sh` |
| 4 | `beets-concurrent-plugin-dispatch-v2` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v2/beets-concurrent-plugin-dispatch-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v2/beets-concurrent-plugin-dispatch-v2/verify.sh` |
| 5 | `beets-cached-attribute-error-surface-v2` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v2/beets-cached-attribute-error-surface-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v2/beets-cached-attribute-error-surface-v2/verify.sh` |
| 6 | `beets-zero-penalty-display-v2` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v2/beets-zero-penalty-display-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v2/beets-zero-penalty-display-v2/verify.sh` |

## Artifact contract

Each completed session keeps exactly four files:

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json
  changes.diff
  evidence.jsonl.gz
  manifest.sha256
```

`run.json` contains metadata, frozen protocol path/id/SHA-256, baseline pool fingerprint, selected-execution descriptor and hash, immutable Docker image identity, treatment tool adapter identity when applicable, provider usage, composite-seed/concealment claims, operational task checkpoints, and the final verifier result.

`changes.diff` concatenates ordered cumulative source checkpoints and the final diff relative to the one composite broken-start root.

`evidence.jsonl.gz` contains prompts, Codex events, setup logs, cumulative checkpoints, composite-seed and concealment reports, final verifier output and integrity checks, provider-usage extraction, and tool-isolation audit output.

`manifest.sha256` hashes the other three files.

Controller Git objects, generated checkouts, dependency environments, Codex homes, caches, and split task artifacts are scratch state and must not remain beside the compact four files.

## Maintenance contract

- Session IDs and compact evidence are retained once a provider run is operationally valid.
- Deterministic verifier and source-review outcomes are diagnostic model-behavior evidence, not token-accounting gates.
- Reuse the first valid provider sample for each frozen protocol and replicate; never rerun to select for a pass.
- `python3 scripts/validate_repository.py` checks generated-runbook drift.
- Truth docs own durable claims; this runbook is generated operator procedure.
