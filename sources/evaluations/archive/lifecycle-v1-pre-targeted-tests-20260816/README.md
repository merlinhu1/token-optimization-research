# Archived pre-targeted-tests Lifecycle V1 baselines

These four bare-Codex baselines executed under prompts whose only sanctioned test invocation was
a single capped full-suite run as the final verification step. Permitting targeted test runs
during investigation on 2026-08-16 changed model-facing prompt bytes, which mints new
qualification and protocol identities (ADR 0005), so they are historical evidence for the prompt
bytes they actually ran against and are not controls for the current contract.

- Archived sessions: 4 (`baseline-beets-20260816-p-bc3a19a3954d-r0`/`-r1`,
  `baseline-fastify-20260816-p-ffc865cb74af-r0`/`-r1`)
- Weighted token cost: Beets 292,473.2 and 298,045.8; Fastify 471,318.0 and 386,611.2
- Every task verifier and every final project-wide verifier exited 0 in all four runs.

## Why they were superseded

They are the measurement that identified the defect in their own contract. Decomposing weighted
cost into agent steps and context per step showed that capping suite output did exactly what it
was designed to do to the second factor and destabilised the first:

| contract | replicate | steps | input per step |
|---|---|---:|---:|
| pre-cap Beets | r0 / r1 | 33 / 35 | 58,920 / 63,632 |
| capped Beets | r0 / r1 | 40 / 47 | 34,786 / 34,759 |
| capped Fastify | r0 / r1 | 42 / 37 | 55,646 / 56,839 |

Context per step became almost perfectly reproducible — 0.1% apart on Beets — while step count
variance rose from 6.1% to 17.5%. Normalised to a common cache hit rate, weighted-cost spread was
worse than the pre-cap pair it replaced (15.6% against 12.7%).

The mechanism was measured offline rather than inferred. Under `--tb=no` the Beets suite emits
15,312 characters naming 39 failed tests and nothing else, while `--tb=line` emits 1,710,421 —
99.7% of full tracebacks, because 39 failures expand to roughly 6,800 subtest failure lines. No
traceback verbosity setting exists between those two points. Fastify's `--reporter=dot` retains
file, line, and assertion values within 17,653 characters, so the two fixtures were nominally
symmetric in size but not in information, and Beets was the more variable of the two.

Targeted reruns of a failing area cost roughly 3,300 characters. The diagnostic information was
never expensive; only the undirected dump was. The superseding contract therefore permits
targeted test runs during investigation and keeps the capped full-suite call as the final step.

Frozen protocols move with these sessions; they are not active contracts.
