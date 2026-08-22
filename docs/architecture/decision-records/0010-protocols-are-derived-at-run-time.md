# ADR 0010: Derive Protocols At Run Time And Enforce Comparability At Comparison Time

## Status

Accepted (2026-08-22). Amends the operational contract around protocol identity in
[`0005-token-accounting-and-protocol-identity.md`](0005-token-accounting-and-protocol-identity.md).
The identity rules themselves — what a protocol descriptor contains, and that a model or effort
change mints a new identity — are unchanged and remain in force.

## Context

A run could not start until an operator had minted a frozen protocol for that exact
sequence/profile/model-condition, and the runner refused outright without one:

```
expected exactly one current frozen protocol for <sequence>/<profile>; exact=[] compatible=[]
--protocol is required before any workflow setup
```

The stated purpose was comparability: a baseline and a treatment must be produced by the same
measurement apparatus, or the difference between their numbers is not the treatment.

That purpose is sound. The mechanism served it poorly.

**It gated the wrong event.** Comparability can only be violated when two runs are compared, but
the check fired when one was started. Nothing in the frozen protocol was unavailable at
comparison time — every session already records its full `selected_execution.descriptor` and the
`descriptor_sha256` of those bytes.

**It did not actually protect the comparison it claimed to.** A frozen protocol binds the
treatment to the apparatus blessed when it was minted. It says nothing about whether the
*baseline* ran under that same apparatus; a baseline's recorded runner hash is a legacy constant
rather than the file's bytes. The comparison this repository publishes was never the thing being
checked.

**Its failure mode was silence.** `CLAUDE.md` documented the ordering as a trap: mint after every
script edit is final, because editing a pinned script afterwards stops the protocol matching, and
the symptom is a refusal that looks like a missing file rather than a stale one. A control whose
misuse is invisible is a hazard, not a safeguard.

**It taxed the cheapest work in the repository.** Provider-free readiness checks produce no
measurement and so have no comparability to protect, yet the gate refused them too. During the
2026-08-22 lane readiness work this forced a separate smoke harness to be written rather than
using the matrix that already existed.

This is the same critique ADR 0009 applied to `sample_plan`: friction carrying the *form* of
pre-registration without the deliberation that gives pre-registration its force. `refresh_workflow_contracts.py`
was a command run because the runner demanded it, not a moment where anyone decided anything.

## Decision

- Decision (2026-08-22): **Comparability is enforced when two runs are compared, not when one is
  started.** Repository validation rejects any comparison whose baseline and treatment disagree on
  the apparatus-relevant fields of their recorded execution descriptors, naming the fields that
  diverged. This applies to every retained session, because each already records its descriptor.
- Decision (2026-08-22): The apparatus-relevant fields are the descriptor's `version`,
  `sequence_id`, `model_facing_prompts`, `agent_condition`, `dependencies`, `isolation`, and the
  reproducibility members of `runtime`. `selected_profile`, `execution_role` and `tool_adapter` are
  excluded: those are what a treatment changes. `runtime.fixture_runner_sha256` is excluded because
  it carries the per-profile tool manifest rather than the runner's own bytes.
- Decision (2026-08-22): **A protocol is derived at run time when one does not already exist.**
  Protocol identity is content-addressed from the causal descriptor bytes, so the same apparatus
  always resolves to the same protocol and a changed apparatus resolves to a new one. Minting at
  run time cannot produce a protocol that disagrees with the run it describes, which removes the
  ordering trap rather than documenting it.
- Decision (2026-08-22): **Provider-free runs require no protocol.** A run that never reaches the
  provider produces no measurement for a protocol to make comparable.
- Decision (2026-08-22): `frozen_protocol` is optional on a session record. The configuration a run
  executed under is recorded inline as `selected_execution.descriptor` — a self-contained receipt
  rather than a pointer to a separate file. Records that carry a protocol are still checked against
  its bytes in full.
- Decision (2026-08-22): The launch path **warns** when no current protocol matches and proceeds.
  A missing protocol usually does mean the apparatus moved since the baseline, and knowing that
  before spending is worth more than being stopped by it.
- Decision (2026-08-22): Minted protocols remain immutable evidence, retained and committed
  alongside the sessions that reference them. Nothing about protocol *content* changes.

## Consequences

The guarantee gets stronger and the ceremony disappears. Comparability is now checked against the
actual pair being compared rather than against a file blessed in advance, and it is checked for
every retained session rather than only for runs that happened to be launched through the gate.

You can now spend money on a run that later proves non-comparable, where previously the gate would
have refused to start it. That is the deliberate trade: the launch-time warning names the
divergence, and the comparison-time check makes the bad comparison impossible to publish. A wasted
run is recoverable; a silently incomparable published result is not.

Operators no longer run `refresh_workflow_contracts.py` before a run. It remains available for
deliberately minting a protocol ahead of time — reserving an identity a parent lane will hold a
child to still requires one — but it is no longer on the path to starting work.
