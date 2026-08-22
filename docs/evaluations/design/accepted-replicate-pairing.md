# Accepted-replicate pairing

## Read this before comparing results across runtimes

The worked example below is drawn from a retired generation whose evidence has been deleted. The
rule it illustrates is generation-independent and still in force.

`rN` in a workflow session ID is a **runtime-local immutable attempt label**. It is not, by itself, a cross-runtime comparison label.

Lifecycle V1 has two accepted bare-Codex control replicates (`r0`, `r1`) and two accepted bare-OpenCode treatment replicates (`r1`, `r2`). OpenCode `r0` reached provider execution but was rejected before objective acceptance because strict evidence ingress could not retain the required last-message artifact. It is not an accepted treatment replicate.

The canonical comparisons therefore use **accepted-replicate ordinal**, not matching raw `rN` text.

| Canonical pair | Accepted ordinal | bare Codex control | bare OpenCode treatment | Canonical panel |
|---|---:|---|---|---|
| `lifecycle-v1-sol-high-accepted-pair-01` | 1 | Codex r0 | OpenCode r1 | [`opencode-openai-gpt-5-6-sol-high-accepted-pair-01-panel-results-20260802.json`](../../../sources/evaluations/archive/lifecycle-v1-pre-corrected-prompts-20260813/audits/opencode-openai-gpt-5-6-sol-high-accepted-pair-01-panel-results-20260802.json) |
| `lifecycle-v1-sol-high-accepted-pair-02` | 2 | Codex r1 | OpenCode r2 | [`opencode-openai-gpt-5-6-sol-high-accepted-pair-02-panel-results-20260802.json`](../../../sources/evaluations/archive/lifecycle-v1-pre-corrected-prompts-20260813/audits/opencode-openai-gpt-5-6-sol-high-accepted-pair-02-panel-results-20260802.json) |

Each row covers the two persistent V1 workflows, Fastify and Beets. The registry binds every accepted OpenCode lane directly to its baseline through `interpretation.comparison_baseline_session_id` and records the visible pair name in `interpretation.comparison_pair`.

## Pairing contract

An accepted-order pair is valid only when both lanes retain the same:

- fixture and baseline-pool fingerprint;
- Lifecycle V1 sequence and task order;
- rendered model-facing prompt hashes;
- provider model (`gpt-5.6-sol`) and reasoning effort (`high`);
- accepted objective status and compact-artifact integrity.

The intentional experimental variable is the replacement runtime: bare Codex versus bare OpenCode. The raw runtime-local labels remain in session IDs and frozen evidence for traceability; they are not renamed.

The r2 OpenCode record includes later controller/adapter provenance for the evidence-ingress repair. That does not alter the model-facing task contract, but it remains a disclosed runtime-revision caveat in the frozen protocol and the r2 completion audit.

## Reporting rule

Use `accepted-pair-01` and `accepted-pair-02` in human-facing comparison text and panel filenames. Do **not** describe OpenCode r2 as unpaired merely because there is no bare-Codex r2, and do **not** compare OpenCode r1 with Codex r1 solely because the local labels match.
