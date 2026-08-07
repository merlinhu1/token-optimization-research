# OpenCode four-tool Lifecycle V1 screen — 2026-08-08

## Scope

This is a single-replicate, provider-backed OpenCode screening run across the active Lifecycle V1 Fastify and Beets workflows. Cartog was explicitly excluded before provider execution because its pinned native binary could not reproduce the frozen artifact identity; it has no result in this screen.

The selected model condition was OpenAI `gpt-5.6-sol` with `high` reasoning through OpenCode 1.18.9. The four executed product profiles were Graphify, LeanCTX, Snip, and CodeScope. Each profile ran once on each workflow, serially, from the clean published protocol commit `3b16bbbb15f6e8b2af87a51cebdc58803294d94f`.

## Outcome

All eight lanes were accepted. Each lane completed all three ordered tasks, passed controller verification, retained provider usage, and had a valid three-file manifest. That is 24/24 accepted task outcomes and 8/8 accepted lanes. Correctness, review, and maintainability fields remain diagnostics; they did not trigger reruns or token-sample selection.

The matched bare-OpenCode comparison samples are protocol-bound and shared by product treatments at each sequence/fingerprint/replicate. The comparison records therefore support descriptive single-run observations only. They are marked `claim_status: single-run-screening` and `eligible_for_ranking: false`; this table must not be read as a stable product ranking or population estimate.

| Profile | Fastify raw / weighted | Beets raw / weighted | Two-sequence raw delta | Two-sequence weighted delta |
|---|---:|---:|---:|---:|
| Matched bare OpenCode | 1,805,580 / 356,056.6 | 2,072,332 / 374,997.0 | baseline | baseline |
| Graphify | 1,383,348 / 279,138.6 | 1,871,489 / 360,614.0 | -16.07% | -12.49% |
| LeanCTX | 2,112,834 / 403,076.8 | 2,435,719 / 447,362.6 | +17.29% | +16.33% |
| Snip | 797,433 / 190,354.2 | 1,856,762 / 346,146.0 | -31.56% | -26.61% |
| CodeScope | 1,867,698 / 376,865.6 | 1,957,342 / 350,351.6 | -1.36% | -0.52% |

The weighted metric is `fresh input + 0.1 × cached input + 6 × output`. Reasoning tokens are retained as a provider-reported output subset and are not added again.

## Lane evidence

| Profile | Fastify run | Beets run | Protocols |
|---|---|---|---|
| Graphify | [`graphify-opencode-v1-fastify-20260808-p-72ac148f730b-r1`](../../sources/evaluations/workflow-sessions/graphify-opencode-v1-fastify-20260808-p-72ac148f730b-r1/run.json) | [`graphify-opencode-v1-beets-20260808-p-d8cfc5066f76-r1`](../../sources/evaluations/workflow-sessions/graphify-opencode-v1-beets-20260808-p-d8cfc5066f76-r1/run.json) | `1946cfbaf5a9`, `c338fb74ff7c` |
| LeanCTX | [`leanctx-opencode-v2-fastify-20260808-p-72ac148f730b-r1`](../../sources/evaluations/workflow-sessions/leanctx-opencode-v2-fastify-20260808-p-72ac148f730b-r1/run.json) | [`leanctx-opencode-v2-beets-20260808-p-d8cfc5066f76-r1`](../../sources/evaluations/workflow-sessions/leanctx-opencode-v2-beets-20260808-p-d8cfc5066f76-r1/run.json) | `0202e15b5a3d`, `09c5749d5fe7` |
| Snip | [`snip-opencode-v2-fastify-20260808-p-72ac148f730b-r1`](../../sources/evaluations/workflow-sessions/snip-opencode-v2-fastify-20260808-p-72ac148f730b-r1/run.json) | [`snip-opencode-v2-beets-20260808-p-d8cfc5066f76-r1`](../../sources/evaluations/workflow-sessions/snip-opencode-v2-beets-20260808-p-d8cfc5066f76-r1/run.json) | `00fb94ae1c82`, `81aebd7c2ba2` |
| CodeScope | [`codescope-opencode-v1-fastify-20260808-p-72ac148f730b-r1`](../../sources/evaluations/workflow-sessions/codescope-opencode-v1-fastify-20260808-p-72ac148f730b-r1/run.json) | [`codescope-opencode-v1-beets-20260808-p-d8cfc5066f76-r1`](../../sources/evaluations/workflow-sessions/codescope-opencode-v1-beets-20260808-p-d8cfc5066f76-r1/run.json) | `635fa0901238`, `e2dfa444cd6d` |

The runner also emitted one comparison record per lane under `sources/evaluations/workflow-sessions/baseline-{sequence}-20260808-vs-{profile}-p-{fingerprint}-r1.json`. Those records retain baseline IDs, raw-token deltas, task counts, acceptance, and the single-run interpretation boundary.

## Interpretation boundary

This screen establishes accepted artifacts and descriptive token observations for these exact runtime, model, profile, protocol, fixture, and replicate identities. It does not establish a durable product ranking, causal tool effect, general model efficiency, or quality equivalence. No pass-selected reruns were performed. Future work must use new explicitly authorized identities rather than rerunning these occupied samples.
