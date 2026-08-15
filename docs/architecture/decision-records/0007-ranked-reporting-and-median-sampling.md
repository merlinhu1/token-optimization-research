# ADR 0007: Publish Scoped Rankings From Pre-Registered Median Samples

## Status

Accepted. Supersedes the first-valid-sample rule in
[`0005-token-accounting-and-protocol-identity.md`](0005-token-accounting-and-protocol-identity.md)
and the no-ranking position in
[`0003-methodology-and-reporting.md`](0003-methodology-and-reporting.md).

## Context

Two earlier positions were wrong in ways that made the work less useful without making it more
honest.

**Refusing to rank.** The stated reason was that two fixtures and three runtimes cannot support
a general recommendation. That is true and irrelevant: it disqualifies every benchmark that has
ever been published, including SPEC, MLPerf, and SWE-bench, none of which decline to order their
results. A ranking whose scope is stated is the honest form. Withholding the ordering does not
transfer uncertainty to the reader, it transfers the judgement while pretending not to have one
— and the repository was already making that judgement implicitly by publishing per-tool deltas
that any reader would sort.

**Retaining only the first valid sample.** This existed to prevent rerunning until a favourable
number appeared, which is a real hazard worth defending against. But a single observation cannot
distinguish a tool effect from run-to-run variance, so every result carried a `screening` label
that the evidence could never shed. The control was protecting integrity by making the
measurement permanently inconclusive.

Median-of-N replaces it and is strictly better, **provided N is fixed before execution**. Without
pre-registration, "run three, dislike the median, run two more" is cherry-picking with extra
steps, and the new rule would be weaker than the one it replaces rather than stronger.

## Decision

- Decision (2026-08-15): Publish rankings. A published ranking must state its workload set, model
  conditions, sample size, and observed dispersion. Scope is carried by the statement, not by
  refusing to make it.
- Decision (2026-08-15): Tools whose sample ranges overlap at the reported N are reported as
  indistinguishable at that N rather than ordered against each other. Ranking does not mean
  manufacturing precision the samples do not support.
- Decision (2026-08-15): The point estimate for a protocol is the **median** of total
  provider-reported tokens across a pre-registered set of N replicates, N odd and at least 3.
- Decision (2026-08-15): N and the protocol identity are registered before the first provider call.
  All N retained replicates are published, including verifier failures and low-quality outputs.
- Decision (2026-08-15): A replicate that fails before the provider boundary produced no
  measurement and is replaced, with its zero-spend receipt retained. A replicate whose agent
  performed badly produced a real token count and counts toward the median.
- Decision (2026-08-15): Extending a sample after seeing results requires a new registration, and
  both the original and extended estimates are reported.

## Consequences

- Provider cost rises by roughly N× per condition. This is the price of an estimate that can
  support an ordering, and it is the main reason to keep N at 3 unless a comparison is close.
- Results stop being permanently labelled screening. A pre-registered median across N replicates
  with published dispersion is a scoped estimate.
- Dispersion becomes a first-class output. Reporting the spread is what allows an honest
  "indistinguishable" verdict instead of a spurious ordering.
- The registry must express which sample plan a session belongs to, so the schema carries
  `sample_plan` and validation rejects a retained set larger than its registered N.
- Nothing changes about comparability: a median is only computed within one frozen protocol and
  model condition, and only compared against a matched baseline sample.

## Provenance

Recorded 2026-08-15 at the experiment owner's direction. Adopted while the active registry was
empty following the 2026-08-13 task-family correction, so no existing corpus required migration
and the first corrected-contract campaign runs under this policy from the start.
