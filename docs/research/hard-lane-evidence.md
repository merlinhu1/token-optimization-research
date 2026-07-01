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

The previous 0/5 versus 0/5 condition comparison is withdrawn. The failed process exit reflected verifier-contract errors rather than five implementation failures. Current prompt-aligned fingerprints are `a9c642bc016a` for GPT-5.6 Luna xhigh and `109705c35eff` for GPT-5.5 high. Treatments must pair against a run from the same corrected frozen model condition and protocol fingerprint.
