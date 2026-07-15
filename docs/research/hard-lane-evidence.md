# Primary-objective hard-lane evidence policy

## Purpose

A primary-objective hard lane is a qualified workflow whose composite broken state, prompts, concealment controls, and fixed-state verifiers are sound, but whose bare agent condition does not produce a verifier-confirmed solve. Its failed bare result remains the baseline for provider-token evaluation. Treatments are judged relative to that baseline rather than discarded solely because the baseline failed.

## Evidence labels

A model turn may have three distinct outcomes:

1. **Operationally completed** — the provider turn exited successfully and produced an artifact.
2. **Agent-declared complete** — the final agent message states that the requested repair was implemented.
3. **Verifier-confirmed** — the concealed behavioral/type acceptance gate passed on the final cumulative repository.

These labels must not be collapsed. Agent-declared completion is evidence about agent behavior and task-attempt completion, while verifier output records correctness.

## Primary-objective use

Hard-lane records support:

- primary-objective provider-token comparisons;
- operational and agent-declared completion rates;
- verifier-confirmed correctness comparisons;
- failure localization and recurring under-solving patterns;
- workload difficulty for a frozen model/runtime condition;
- comparative tool-effectiveness claims against the frozen bare baseline.

The baseline's verifier failure remains part of the result; it does not erase the measured token usage or the five agent-declared completions.

## Outperformance rule

Always report correctness and provider-token usage together.

A treatment outperforms the hard baseline when either:

- it improves verifier-confirmed correctness; or
- it achieves the same verifier-confirmed correctness with fewer provider tokens.

For a specifically **token-efficiency** claim, require no worse correctness and fewer provider tokens. If correctness improves while tokens increase, report a correctness-versus-token tradeoff rather than calling it token savings. Never infer verifier-confirmed correctness from an agent completion claim.

## Fastify verifier-contract correction

Frozen sequence: `fastify-maintenance-sequence-v1`

Qualified task count: five sequential warm-state repairs

The strengthened verifier snapshot used by fingerprints `57a82a0dca61` and `d8a06f2ef78f` was invalid for objective scoring. It introduced five requirements absent from, or contradictory to, the model-visible prompts:

- exact max-parameter error-message spelling;
- timeout message text containing duration and route;
- `request.headers === request.raw.headers` object identity;
- an internal `kLogController` symbol and an exact service-unavailable log message;
- Content-Type cache identity and exact quote/casing serialization, despite the prompt explicitly saying object identity was not required.

Post-hoc replay against prompt-aligned behavioral verifiers produced:

| Model condition | Superseded session | Operational turns | Agent-declared complete | Corrected verifier surfaces | Provider tokens | Disposition |
|---|---|---:|---:|---:|---:|---|
| GPT-5.6 Luna, xhigh | `baseline-fastify-20260713-p-57a82a0dca61-r0` | 5/5 | 5/5 | 4/5 | 92,627,212 | Invalid original protocol; archived in Git |
| GPT-5.5, high | `baseline-fastify-20260713-p-d8a06f2ef78f-r0` | 5/5 | 5/5 | **5/5** | 50,112,674 | Invalid original protocol, but implementation succeeds under corrected acceptance; archived in Git |

The previous 0/5 versus 0/5 condition comparison is withdrawn. The failed process exit reflected verifier-contract errors rather than five implementation failures. The intermediate prompt-aligned fingerprints were `a9c642bc016a` for GPT-5.6 Luna xhigh and `109705c35eff` for GPT-5.5 high; both are now superseded by the additional source-review findings below.

Independent source review then found that the `a9c642bc016a` GPT-5.6 run was still a verifier false negative despite its green aggregate gate: default max-parameter handling returned 404 instead of 414, and logger compatibility behavior was incomplete. It was rejected at quality review (2/5, 3/5 tasks) and removed from the live pool. The `109705c35eff` GPT-5.5 record and the accepted Beets pool were also retired because the prompt/verifier bytes changed.

Current prompt-aligned baseline state:

- Fastify GPT-5.6 Luna xhigh: `baseline-fastify-20260713-p-6a8afd4b63ca-r0`, 5/5 verified surfaces and 60,671,087 provider tokens, but rejected at independent quality review (3/5). Final-tree reconstruction showed `kLogController` remained undefined, so controller state used the collision-prone public string key `"undefined"`. It remains a primary-objective hard baseline, not an accepted baseline. The paired Lowfat run has the same quality defect, but its +25.92% token delta is forensic only because the treatment used prohibited external retrieval and pass-through commands.
- Beets GPT-5.6 Luna xhigh: `baseline-beets-20260713-p-7aaac4b8a309-r0`, 3/3 verified tasks, 6,400,224 provider tokens, accepted at 4/5 quality. The required `MediaAttributes.popularity` contract is explicitly verified.

The first Terraform and Beets `terminal-lowfat` treatment attempts completed their workflows and invoked Lowfat zero times. They remain valid zero-use observations for their availability arm: no use occurred and no use is attributed. The later prompted/preferred direct-use arm was independently predeclared and is a distinct valid estimand rather than a retroactive natural-use violation. Fastify and Terraform are causally excluded because only treatment used external retrieval; Beets remains valid one-replicate screening evidence for the narrow preferred-direct-use arm (+42.25% tokens, accepted quality). None estimates native automatic shell integration. Across that arm, 544 of 655 prefixes targeted Lowfat pass-through commands, which is descriptive coverage rather than an acceptance condition. Future natural-use execution is blocked until `lowfat shell-init` is installed and preflighted in the actual model shell; zero use will remain valid and external-retrieval events disqualifying.
