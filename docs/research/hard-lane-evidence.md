# Hard-lane evidence policy

## Purpose

A hard lane is a qualified workflow whose composite broken state, prompts, concealment controls, and fixed-state verifiers are sound, but whose evaluated agent condition does not produce an objective-accepted solve. Hard-lane runs remain useful diagnostic evidence when their claims are labeled precisely.

## Evidence labels

A model turn may have three distinct outcomes:

1. **Operationally completed** — the provider turn exited successfully and produced an artifact.
2. **Agent-declared complete** — the final agent message states that the requested repair was implemented.
3. **Verifier-confirmed** — the concealed behavioral/type acceptance gate passed on the final cumulative repository.

These labels must never be collapsed. Agent-declared completion is evidence about agent behavior and confidence, not task correctness.

## Allowed claims

Hard-lane records may support claims about:

- operational completion rate;
- agent-declared completion rate;
- provider-token demand;
- failure localization and recurring under-solving patterns;
- workload difficulty for a frozen model/runtime condition;
- correctness-aware treatment comparisons.

## Disallowed claims

Hard-lane records do not establish:

- verified task completion;
- an objective-accepted baseline;
- successful token savings;
- software-quality preservation;
- treatment causality from token volume alone.

## Comparison rule

Report correctness and token usage jointly. A treatment is favorable on a hard lane only when it improves verifier-confirmed behavior, or when it uses fewer tokens with no worse verified-correctness vector. If baseline and treatment both fail, describe the result as **hard-lane attempt efficiency**, not successful token savings.

A hard-lane result cannot replace an accepted production comparison. Terraform and Beets remain the production objective pair.

## Fastify hard-lane observation

Frozen sequence: `fastify-maintenance-sequence-v1`

Model condition: GPT-5.6 Luna, xhigh reasoning

Qualified task count: five sequential warm-state repairs

| Session | Operational turns | Agent-declared complete | Deterministic result | Provider tokens | Evidence status |
|---|---:|---:|---|---:|---|
| `baseline-fastify-20260713-p-292cc70dff18-r0` | 5/5 | 5/5 | Original verifier green; rejected at independent quality review (2/5) | 90,553,295 | Hard-lane diagnostic; archived in `e4be0b3` |
| `baseline-fastify-20260713-p-57a82a0dca61-r0` | 5/5 | 5/5 | Strengthened final verifier failed all five task surfaces | 92,627,212 | Hard-lane diagnostic; archived in `d210f18` |
| **Aggregate** | **10/10** | **10/10** | **0 objective-accepted runs** | **183,180,507** | **Hard-lane difficulty evidence** |

The two runs establish that the model consistently reached and claimed completion for every prompt while failing acceptance-critical behavior. This is positive evidence that the lane is hard for this model condition and useful for stress calibration. It is not evidence that the ten task attempts were correct.
