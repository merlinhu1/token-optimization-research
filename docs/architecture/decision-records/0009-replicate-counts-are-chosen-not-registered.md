# ADR 0009: Choose Replicate Counts Per Protocol Instead Of Pre-Registering Them

## Status

Accepted (2026-08-19). Supersedes the pre-registration decisions in
[`0007-ranked-reporting-and-median-sampling.md`](0007-ranked-reporting-and-median-sampling.md).
ADR 0007's ranking and dispersion decisions are unchanged and remain in force.

## Context

ADR 0007 required every replicate to declare a `sample_plan` naming an N, odd and at least 3,
registered before the first provider call, with validation rejecting a retained set larger than
its registered N. The stated purpose was to stop a median being assembled by rerunning until the
number was favourable.

That control assumed every provider run is a confirmatory measurement. Most are not. The study
screens on the order of eighty treatment profiles, and a screen answers a different question than
an estimate: not *how large is this effect* but *is this worth measuring at all*. A treatment that
is obviously bad on its first replicate does not need two more to establish that it is bad. Under
the old rule the only compliant options were to spend twice more on a foregone conclusion or to
retain a plan whose declared N was never met.

The mechanism was also weaker than it appeared. `plan_id` was derived automatically from the
protocol fingerprint and N defaulted to 3 from an environment variable, so the "registration" was
a default nobody consciously chose. It carried the friction of pre-registration without the
deliberation that gives pre-registration its force. The amendment path it prescribed,
`supersedes_plan_id`, appeared in exactly one place in the codebase: the error message telling an
operator to use it.

## Decision

- Decision (2026-08-19): Replicate counts are chosen per protocol as the work warrants. There is
  no minimum, no parity requirement, and no cap on retained replicates.
- Decision (2026-08-19): A single replicate is a legitimate retained result. It is a **screen**,
  not an effect estimate, and must be described as one.
- Decision (2026-08-19): `sample_plan` is no longer required, emitted, or enforced. Records that
  already carry one keep it as historical metadata; the schema still permits the field.
- Decision (2026-08-19): `replicate_index` uniqueness within a sequence, profile, model condition
  and protocol pool remains enforced. That is data integrity — two runs must not be presented as
  the same attempt — and is unrelated to how many replicates a protocol accumulates.
- Decision (2026-08-19): Where several replicates exist, the point estimate remains the median
  weighted token cost reported with its observed spread, and the two-factor decomposition of
  ADR 0008 still applies. Dropping the registration does not change the estimator.
- Decision (2026-08-19): Retained replicates are still all published, including verifier failures
  and low-quality outputs. A replicate is never dropped because its number is inconvenient.

## Consequences

Optional stopping is no longer structurally prevented; it is managed by disclosure. A published
comparison states how many replicates each arm holds, so a reader can see directly when an
estimate rests on one run, and can discount it accordingly. This is weaker than a pre-registered
N and is accepted deliberately: the previous control was not obtaining the deliberation it
assumed, and it taxed screening work that never needed it.

The honesty requirement moves into the wording of claims. A one-replicate result may support
"this tool was not worth carrying forward"; it may not support a ranked effect size. Where a
comparison is close relative to the observed spread, ADR 0007's rule still governs: report the
tools as indistinguishable at that N rather than ordering them.
