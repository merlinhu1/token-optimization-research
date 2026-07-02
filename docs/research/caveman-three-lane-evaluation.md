# Caveman three-lane evaluation

Date: 2026-07-14
Evidence stage: reproduction
Treatment profile: `behavior-caveman`
Model condition: Codex CLI, GPT-5.6 Luna, xhigh reasoning

## Scope

This evaluation covers the Caveman **behavior-policy-only** arm. The pinned full-mode Caveman skill was rendered into the first model-facing prompt and remained active in one persistent thread. MCP-description compression, plugin hooks, global instructions, and persistent mode state were disabled. Zero Caveman shell-command invocations are expected for this arm because treatment exposure is instruction-layer policy injection, not a command-line tool.

The three canonical warm-state sequences ran concurrently with final-only concealed verification:

- Fastify: five tasks
- Terraform: three tasks
- Beets: three tasks

Provider-billed token volume is the primary token metric. Correctness and independent production-quality review gate all effectiveness claims.

## Results

| Lane | Baseline correctness / quality | Caveman correctness / quality | Baseline provider tokens | Caveman provider tokens | Delta | Disposition |
|---|---:|---:|---:|---:|---:|---|
| Fastify | 5/5 prompt-aligned, 3/5 | 5/5 prompt-aligned, 3/5 | 71,683,046 | 63,220,716 | -8,462,330 (-11.81%) | Hard-lane screening only; both runs quality-rejected |
| Terraform | 1/3, 2/5 | 2/3, 2/5 | 13,639,315 | 14,896,581 | +1,257,266 (+9.22%) | Treatment rejected; correctness improved by one task but remains under-solved |
| Beets | 2/3, 2/5 | 3/3, 4/5 | 8,068,385 | 11,653,177 | +3,584,792 (+44.43%) | Accepted correctness-improving treatment; not token savings |

Raw three-lane totals were 93,390,746 baseline tokens and 89,770,474 Caveman tokens, a raw decrease of 3,620,272 (-3.88%). This aggregate is **not an effectiveness claim**: correctness and acceptance differ by lane, and the quality-rejected Fastify hard lane dominates the token volume.

## Lane review

### Fastify

The original final verifier stopped in task 4 because the implementation emitted `Server is closing` while the concealed script used the case-sensitive regex `/server is closing/`. The public prompt requires a message identifying that the server is closing but does not prescribe capitalization. Independent review classified this as a verifier-contract false negative.

The preserved final cumulative patch was reconstructed from the pinned Fastify snapshot and composite seed. With only that unsupported regex made case-insensitive, the remainder of task 4 and all of task 5 passed. Prompt-aligned behavior is therefore 5/5.

Independent source review nevertheless found two merge-blocking production defects shared with the matching baseline:

1. `lib/symbols.js` does not restore `kLogController`. Controller state is stored under the ordinary public property `"undefined"`, allowing collisions and runtime logging failures.
2. `lib/request.js` returns `{ ...this.raw.headers }` when no additional headers exist, breaking `request.headers === request.raw.headers` identity and established compatibility behavior.

Caveman used 11.81% fewer provider tokens at equal prompt-aligned task count and equal rejected quality. This is useful hard-lane screening evidence, not an accepted production-objective win.

### Terraform

The aggregate concealed verifier was green, but independent final-tree review found only 2/3 disclosed objectives correct:

- tracing context propagation: pass;
- client-capability propagation: fail;
- strict versus const-only variable parsing phases: pass.

`BuiltinEvalContext.ConfigureProvider` reconstructs a partial capability literal rather than forwarding `ctx.ClientCapabilities()`, and `MockEvalContext.ClientCapabilities()` also omits `StorePlannedPrivate`. The verifier checks the new computed-block capability but under-covers preservation of existing capabilities at these boundaries.

Caveman improved correctness from 1/3 to 2/3 but increased provider tokens by 9.22% and remained quality-rejected.

### Beets

Independent reconstruction and semantic probes accepted all three objectives at quality 4/5:

- path-format inheritance and legacy-key translation;
- multivalue genre handling, including semicolon-delimited list flattening;
- complete Tidal popularity, artwork, pagination, token-loading, and required-typing behavior.

Correctness improved from the matching hard baseline's 2/3 to 3/3. Provider tokens increased by 44.43%, so this is accepted correctness-improvement evidence rather than token-savings evidence.

A canonical hard-baseline comparison is recorded at:

`sources/evaluations/workflow-sessions/baseline-beets-20260714-vs-caveman-p-ca2e2a06cba6-r0.json`

## Behavioral exposure

The pinned Caveman skill was present in each model-facing treatment condition, while overlapping output controllers and tool surfaces were disabled.

Observable final-response text was shorter than the matching baseline in every lane:

| Lane | Baseline final-message characters | Caveman final-message characters | Delta |
|---|---:|---:|---:|
| Fastify | 2,789 | 2,304 | -17.39% |
| Terraform | 1,316 | 1,269 | -3.57% |
| Beets | 1,391 | 1,190 | -14.45% |

This confirms observable concise-output behavior, but final-message length is not provider-token efficiency. Provider output tokens increased on Fastify, while total provider tokens increased on Terraform and Beets because cached and fresh input volume dominated.

## Integrity and limitations

- All three compact treatment manifests passed SHA-256 verification.
- Treatment artifacts were preserved despite one lane's original verifier exit.
- Repository validation, Truthmark check/index, and `git diff --check` passed after the matrix merge.
- Embedded Codex streams contain recoverable stderr lines interleaved with JSON in some runs; accounting records preserve the parsing warnings.
- Each comparison currently has one complete multi-task workflow execution per arm (`replicate_count = 1`). This means one workflow replicate—not one task; Fastify still contains five task outcomes and Terraform/Beets three each.
- The Fastify casing assertion should be corrected in the next canonical verifier refresh; the prompt-aligned replay is explicitly distinguished from the original verifier exit.
- The evaluation applies only to Caveman's instruction-layer behavioral policy, not its MCP-description compression or host-hook integrations.

## Conclusion

Caveman reliably produced shorter final reports, but it did **not** establish broad provider-token savings at accepted software quality.

- Beets is an accepted correctness improvement bought with 44.43% more provider tokens.
- Terraform improves one objective but remains under-solved and uses 9.22% more tokens.
- Fastify uses 11.81% fewer tokens at equal prompt-aligned correctness, but both baseline and treatment remain below the production-quality threshold.

The evidence supports Caveman as a concise-output behavior policy, not as a generally validated provider-token optimization across these three software-maintenance lanes.
