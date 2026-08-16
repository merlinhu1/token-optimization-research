# ADR 0008: Size Tasks For Variance, And Publish The Metric's Two Factors

## Status

Accepted. Supersedes the Lifecycle V1 task family described in
[`0005-token-accounting-and-protocol-identity.md`](0005-token-accounting-and-protocol-identity.md);
the weighted-token-cost definition and protocol-identity minting in that record are unchanged.

## Context

Weighted token cost was reproducing badly enough to threaten the point of the study. Two
Beets replicates of one frozen protocol landed 1.9% apart and two Fastify replicates 21.9%
apart, and a tool effect smaller than the baseline's own spread cannot be resolved at any
sample size the budget can reach.

Factoring the metric located the problem. Weighted cost is the product of how many steps
the agent takes and what each step costs, and the two behave differently:

| contract | replicate | steps | input per step |
|---|---|---:|---:|
| pre-cap Beets | r0 / r1 | 33 / 35 | 58,920 / 63,632 |
| capped Beets | r0 / r1 | 40 / 47 | 34,786 / 34,759 |
| capped Fastify | r0 / r1 | 42 / 37 | 55,646 / 56,839 |

Capping test-suite output made context per step almost perfectly reproducible — 0.1% apart
on Beets — and destabilised step count, from 6.1% spread to 17.5%. The 1.9% total was two
large movements cancelling, not stability. Normalised to a common cache hit rate the capped
pair was *more* dispersed than the uncapped pair it replaced, 15.6% against 12.7%.

Two causes were found by measurement rather than argument.

**Unbounded tasks.** Per-task step counts showed the variance was not spread across the
sequence. Beets task 1 ran 17 steps in both replicates and Fastify task 1 ran 16 and 15,
while the review task ran 11 against 16 and 13 against 10. The review task also carried
roughly 45% of session cost. Its instruction was to "identify any defect that would be
unacceptable to ship", which has no terminal condition: the agent stops when it judges
itself finished, and that judgement is close to a coin flip. Aggregate variance was
therefore mostly one task's variance, and one task's variance cannot be averaged away by
replicating the sequence.

**A red fixture.** The pinned Fastify checkout fails seven tests on a clean tree in the
sandboxed lane, all of them opening real sockets. Every Fastify run has shown the agent
seven failures it did not cause and cannot fix, and whether it investigates them is
another coin flip charged to the measurement.

## Decision

- Decision (2026-08-16): The reported metric remains weighted token cost. It is additionally
  published as **agent steps times weighted cost per step**, with the spread of each factor.
  This is a decomposition, not a second metric, and no raw-token figure is reported.
- Decision (2026-08-16): Every task must have a closed stopping condition — a named behaviour
  that a specific upstream test decides. Task instructions that ask the agent to judge its own
  thoroughness are not permitted, because the stopping point becomes a sampled quantity.
- Decision (2026-08-16): Task families are sized so that no single task dominates. Lifecycle V2
  is a series of bounded defect repairs of comparable size — seven on Beets, six on Fastify —
  replacing three unbounded tasks. The validator enforces at least four tasks, all of one class,
  for this contract.
- Decision (2026-08-16): Prompts state the observable symptom and never name the file, function,
  or test. Locating the defect is the work that retrieval tools are meant to make cheaper, and
  26 of 84 active treatment profiles are retrieval tools; disclosing the location would make the
  study insensitive to its largest category by construction.
- Decision (2026-08-16): A seed enters the registry only after execution proves it — the seeded
  state must fail the covering upstream tests and the repaired state must pass them.
- Decision (2026-08-16): A fixture whose suite is red before the agent starts is defective. Tests
  that fail on a clean pinned checkout are excluded from the suite command, and the exclusion must
  be shown to leave the seeded regressions still failing.
- Decision (2026-08-16): Supported task-family generations are declared in one table that the
  validator and the qualification generator both read, so a new family is registered rather than
  hardcoded.

## Consequences

- Provider cost per run rises. Thirteen bounded tasks are not cheaper than three unbounded ones,
  and this buys variance reduction with money rather than for free. The prior estimate that it
  would cost about the same was wrong.
- Whether variance actually falls is unmeasured. The argument for this family is structural — no
  dominating term, closed stopping conditions, a green baseline — and only a fresh sample settles
  it. Nothing here should be reported as a variance improvement until it is measured.
- Weighted cost per step is not the near-deterministic quantity an earlier draft of this reasoning
  claimed. Input tokens per step reproduce to 0.1%; weighted cost per step moved 15.3%, because
  the fresh-to-cached split varies. The decomposition earns its place as a diagnostic, not as a
  way to detect effects at small N.
- All Lifecycle V1 evidence is archived, not deleted. Retired sequences stay registered so the
  contract their sessions executed against remains readable.
- The gate no longer encodes one family's shape, which is what made this change expensive: the
  first attempt failed on roughly a dozen assertions that hardcoded three tasks, a
  feature/refactor/review ordering, task-id suffixes, and a qualification filename.

## Provenance

Recorded 2026-08-16 at the experiment owner's direction, after the owner rejected an attributed
cause — cross-run provider cache warming — that the archived pre-cap pair refutes: those two
replicates ran back to back and show no such asymmetry. The owner's attribution to task and prompt
design is what the per-task step data supports.
