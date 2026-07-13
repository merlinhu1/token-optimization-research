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

## Fastify primary-objective hard baseline

Frozen sequence: `fastify-maintenance-sequence-v1`

Model condition: GPT-5.6 Luna, xhigh reasoning

Qualified task count: five sequential warm-state repairs

| Session | Operational turns | Agent-declared complete | Deterministic result | Provider tokens | Evidence status |
|---|---:|---:|---|---:|---|
| `baseline-fastify-20260713-p-292cc70dff18-r0` | 5/5 | 5/5 | Original verifier green; rejected at independent quality review (2/5) | 90,553,295 | Superseded difficulty evidence; archived in `e4be0b3` |
| `baseline-fastify-20260713-p-57a82a0dca61-r0` | 5/5 | 5/5 | Strengthened final verifier failed all five task surfaces | 92,627,212 | **Current primary-objective hard baseline**; archived in `d210f18` |

The current comparison anchor is the strengthened run because it matches the active verifier contract. Its measured baseline is **92,627,212 provider tokens**, or **18,525,442.4 provider tokens per agent-declared task completion**. Treatment results must use the same frozen protocol and report both correctness and provider-token deltas against this anchor.
