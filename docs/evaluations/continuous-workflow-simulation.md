# Continuous workflow simulation

## Purpose

Continuous workflow simulation is the primary Phase 2 evidence path for token-optimization claims. It measures cumulative provider-billed token usage across a realistic persistent project session.

The goal is to determine whether a baseline or treatment profile gets an ordered sequence of repository tasks to green with fewer provider-billed tokens while preserving task success and final repository quality.

## Core rule

Reset before the session, not between tasks. Feed one prompt and inject one regression at a time.

A valid workflow session preserves these across the ordered task sequence:

- repository source working tree; model-facing Git metadata may be re-rooted by the controller before each task to conceal seed provenance;
- tool indexes and caches;
- generated profile files;
- agent home and runtime config;
- memory/state stores enabled by the active profile;
- accumulated task artifacts unless the protocol explicitly models cleanup.

The agent must not see future task prompts, future regressions, future verifier commands, or future task identifiers before the current task verifier has passed. Enforce this structurally: materialize only the current prompt; inject only the current regression; keep task fixtures and acceptance verifiers in controller-only storage; mount only the target repository plus an isolated output directory into the model runtime; hash verifier assets before execution; and verify those hashes before every acceptance step. A valid runner starts or resumes the same agent session for task 1, runs the hidden task 1 verifier, then injects task 2 and resumes that same session only after task 1 passes. Prompt-only instructions or metadata such as `future_tasks_visible: false` do not prove isolation.

## Leakage controls

Issue-derived regression fixtures must not expose the answer path as a visible git diff, parent commit, reflog entry, reachable object, public issue lookup key, or future seeded defect. Before every task, the controller must replace model-facing Git metadata, commit the current broken state as a parentless root, verify that the fixed snapshot and prior roots are inaccessible, and keep seed patches plus controller reference objects outside the model mount. Use neutral task aliases and sanitize prompts so they do not mention fixed upstream commits, public issue numbers, or production-code reverse patches.

Behavioral acceptance is mandatory. Unrelated sentinel edits and exact-source restoration guards are not legitimate ways to reach a production-file complexity floor; every seeded change must be causally connected to the stated task and accepted through behavior or a documented source-identity contract.

The stronger fixture design is to build tasks from pre-fix bases plus hidden behavioral tests instead of production-code reverse patches. Until then, lazy seed delivery and verified true-root concealment are required for objective workflow runs.

## Primary metric

The primary metric is cumulative provider-billed workflow usage:

```text
workflow_session_total = sum(provider-billed usage for all model-visible work in the session)
```

Record fresh input, cached input, cache-write, output, reasoning when available, total provider tokens, and cost. Report tokens per accepted task as a derived metric.

## Quality constraint

A treatment only supports a positive claim when it reduces cumulative provider-billed workflow tokens or cost and preserves quality.

Quality requires:

- per-task verifier success where available;
- final repository verifier success where available;
- no critical safety, diagnostic, stale-context, or reversibility failure;
- final diff/status and transcript reviewability.

Deterministic verifier success is a functional execution gate, not an automatic ordinal quality score. Leave `quality_score` null and `accepted_for_objective` false until a recorded software-quality review evaluates the documented quality dimensions.

## Workflow session contract

A workflow session binds:

- `session_id`;
- `experiment_group_id`;
- repository fixture and initial snapshot;
- task sequence ID;
- profile ID;
- runtime/model condition;
- state policy;
- per-task results;
- cumulative token usage;
- final software-quality result;
- operational reproducibility evidence.

Baseline and treatment sessions are directly comparable only when they use the same repository fixture, initial snapshot, task sequence, runtime, provider, model, model condition, and quality gates.

## Evidence boundaries

| Evidence type | Role |
|---|---|
| `workflow-simulation` | Primary evidence for tool or stack ranking. |
| `workflow-ablation` | Attribution evidence after a full/default profile has workflow evidence. |
| `sanity-check` | Install, profile-isolation, usage-capture, diagnostic-preservation, and runner checks only. |

Sanity checks do not rank tools.

## Artifact layout

Completed workflow-session runs keep a compact evidence bundle instead of a materialized checkout or split task-log tree:

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json
  changes.diff
  evidence.jsonl.gz
  manifest.sha256
```

`changes.diff` concatenates ordered task deltas; each section is relative to the parentless baseline created for that task. This preserves review evidence across Git re-rooting without requiring all independent seed patches to coexist in one synthetic broken tree.

`evidence.jsonl.gz` preserves recoverable raw streams such as prompts, Codex events, setup logs, seed-delivery and concealment reports, per-task deltas, verifier output, provider usage extraction, and tool-isolation audit output. Do not commit generated checkouts, virtualenvs, Codex homes, caches, controller Git objects, or split per-task transcript directories.

## Activation sequence

Provider-backed execution requires an active sequence and a frozen protocol. Fastify, Terraform, and Beets satisfy the readiness gate, but fixture qualification and prepare-only validation do not themselves authorize or constitute a paid run.

After one medium-project candidate has causally related behavior and passes fixture, lazy-seed, concealment, verifier-integrity, isolation, and quality preflights:

1. run `baseline-bare-codex` on the full persistent sequence;
2. stop if the baseline fails any frozen gate;
3. run one treatment profile on the same sequence and model condition;
4. compare cumulative provider tokens, tokens per accepted task, pass rate, correction turns, repeated reads, stale-context incidents, and final quality;
5. expand only after the record shape, artifacts, and validation remain reliable.

Candidate first treatments:

- LeanCTX as the broad/persistent-context candidate;
- CodeGraph or Serena as narrower retrieval comparators;
- Headroom default Codex integration as a broad compression/proxy candidate.
