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

## Fastify primary-objective hard baselines

Frozen sequence: `fastify-maintenance-sequence-v1`

Qualified task count: five sequential warm-state repairs

| Model condition | Session | Operational turns | Agent-declared complete | Verified task surfaces | Provider tokens | Evidence status |
|---|---|---:|---:|---:|---:|---|
| GPT-5.6 Luna, xhigh | `baseline-fastify-20260713-p-57a82a0dca61-r0` | 5/5 | 5/5 | 0/5 | 92,627,212 | Primary-objective hard baseline for fingerprint `57a82a0dca61` |
| GPT-5.5, high | `baseline-fastify-20260713-p-d8a06f2ef78f-r0` | 5/5 | 5/5 | 0/5 | 50,112,674 | Primary-objective hard baseline for fingerprint `d8a06f2ef78f` |

The older GPT-5.6 session `baseline-fastify-20260713-p-292cc70dff18-r0` used a superseded verifier contract and remains difficulty evidence in Git commit `e4be0b3` rather than a comparison anchor.

### Model-condition observation

Against GPT-5.6 Luna xhigh, GPT-5.5 high used **42,514,538 fewer provider tokens (-45.90%)** with the same observed hard-lane outcome: 5/5 operational turns, 5/5 agent-declared completions, and 0/5 verified task surfaces. Under the hard-lane rule, GPT-5.5 high is more token-efficient for this run.

This is a condition-level comparison, not a causal model-family ablation: both the routed model (`gpt-5.5` versus `gpt-5.6-luna`) and reasoning effort (`high` versus `xhigh`) differ. Tool treatments must pair against the baseline with the same frozen model condition and protocol fingerprint.
