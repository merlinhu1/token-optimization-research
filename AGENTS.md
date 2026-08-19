# Repository guidance

This file is the instruction authority for this repository. `CLAUDE.md` is a symlink to it.

## What this repository is

Research infrastructure for measuring **weighted token cost** and software quality in realistic
coding-agent workflows. It holds evaluation contracts, pinned fixtures, generated qualification
evidence, frozen execution protocols, and the reports built from them. It is a research-evidence
repository first: most files are either machine authority, generated output, or immutable
evidence, and each kind has different editing rules. Read [Editing rules by file kind](#editing-rules-by-file-kind)
before your first write.

The measurement is a comparison. Every rule below exists because something can make a baseline and
a treatment differ for a reason that is not the treatment. When a rule seems inconvenient, that is
usually what it is protecting.

## Precedence

1. **Registries decide state.** `data/*.json` says what is active, pinned, registered, or retired.
   Where this file and a registry disagree about state, the registry is right and this file is
   stale — fix it.
2. **This file decides policy**, and the [ADRs](docs/architecture/decision-records/) record why the
   policy exists. Do not work around a rule you disagree with; raise it.
3. **Frozen evidence decides history.** It is never edited to agree with either.

If you cannot satisfy a rule, stop and say so. A silent workaround in this repository does not
produce a slightly worse result, it produces evidence that looks valid and is not.

## Non-negotiables

1. **Run `make check` before finishing any change to evaluation state.** Nothing runs it
   automatically: this repository has no CI, and an unrun gate is the same as no gate.
2. **Weighted token cost is the sole token metric**, reported from a pre-registered median sample.
   See [Measurement and inference](#measurement-and-inference).
3. **Never hand-edit generated or frozen files.** Regenerate the first; leave the second alone.
4. **An action that changes research state updates every active surface that reports it, in the
   same change.** See [Documentation lifecycle](#documentation-lifecycle).
5. **Solution-directed task assistance is forbidden** in model-facing prompts. See
   [Fixture design](#fixture-design).
6. **Never select, drop, or rerun a sample because of the number it produced.** See
   [Threats to validity](#threats-to-validity).

## Setup

`make check` fails closed without `jsonschema`, so create the virtualenv the `Makefile` prefers:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
```

The `Makefile` uses `.venv/bin/python3` when it exists and falls back to bare `python3`. Bare
`python3` on a machine without `jsonschema` installed globally will fail, so **invoke scripts
through `make`, or with `.venv/bin/python3` explicitly** — not with bare `python3`.

Fixture work additionally needs `node`/`npm` (Fastify) and `uv` (Beets). Fixture checkouts under
`sources/evaluations/fixtures/*/*/repo/` are gitignored and materialized locally by each
fixture's `setup.sh`.

## Measurement and inference

### The metric

The repository's sole token evaluation metric is **weighted token cost**:

`fresh_input_tokens + 0.1 * cached_input_tokens + 6 * output_tokens`

Every token result, comparison, delta, median, ranking, chart, and narrative claim must use this
metric and name it explicitly. Reasoning tokens are already included in output tokens and must not
be added again. Provider token counters and reconstructed raw totals may be retained only as
internal telemetry needed to calculate or audit weighted token cost; never present, compare, rank,
or interpret them as an evaluation result. Do not introduce a secondary raw-token metric.

Publish weighted cost as its two factors — **agent steps times weighted cost per step** — with the
spread of each factor, not as a single number ([ADR 0008](docs/architecture/decision-records/0008-bounded-task-family-and-cost-decomposition.md)).
The factors move independently, and a total alone hides which one a tool actually changed.

### The estimator

A single run is not a result. The point estimate for a protocol is the **median weighted token
cost across a pre-registered set of N replicates, N odd and at least 3**
([ADR 0007](docs/architecture/decision-records/0007-ranked-reporting-and-median-sampling.md)).

- **Register before spending.** N and the protocol identity are fixed before the first provider
  call. Every session record carries a schema-required `sample_plan`; `validate_repository` enforces
  N odd and ≥ 3. Registration is what stops a median from being assembled by rerunning until the
  number is favourable.
- **Replicates accumulate additively across sessions as budget allows.** N fixes how many the sample
  holds, never when they run.
- **Publish all N**, including verifier failures and low-quality outputs. A replicate whose agent
  performed badly produced a real token count and counts toward the median. Only a replicate that
  failed *before* the provider boundary produced no measurement; replace it and retain its
  zero-spend receipt.
- **Extending a sample after seeing results requires a new registration**, and both the original and
  extended estimates are reported.
- **Report the median with its observed spread.** A ranking states its workload set, model
  conditions, N, and dispersion; tools whose ranges overlap at the reported N are reported as
  indistinguishable at that N rather than ordered.

### Grading a claim

Every claim carries an evidence stage — `lead`, `source-logic`, `benchmark-audit`, or `reproduction`
([ADR 0002](docs/architecture/decision-records/0002-evidence-stages.md)). Source-logic is
decision-bearing only for prioritization and stack-hypothesis formation; benchmark and reproduction
wording requires benchmark or reproduction artifacts.

`evidence_stage` is schema-required on session and run records, and those schemas admit only
`benchmark_audit` and `reproduction` — a lead or a source-logic reading can never be recorded as
execution evidence. Do not infer a token result from qualification readiness either: a passing
qualification proves preparation, not effect.

## Threats to validity

Each control below exists because the corresponding failure has already happened here or was found
before it could. Removing a control silently is how a study stops measuring what it claims to.

| Threat | Control |
|---|---|
| Prompt differences between arms confound the comparison | Compatible baseline and treatment sessions receive identical prompt bytes, and must not require or prefer treatment-tool invocation |
| Telling the agent where to look suppresses the retrieval that context tools act on | Solution-directed task assistance forbidden; this retired Lifecycle V0 ([ADR 0005](docs/architecture/decision-records/0005-token-accounting-and-protocol-identity.md)) |
| A model or effort change silently reuses an incomparable control | Model/effort changes mint new protocol identities; a baseline cannot cross conditions |
| Environmental noise in a fixture is charged to the treatment | A fixture must exit zero on a clean prepared base — see [Fixture design](#fixture-design) |
| An unbounded task lets one task dominate and swamp the effect | Bounded tasks with closed stopping conditions ([ADR 0008](docs/architecture/decision-records/0008-bounded-task-family-and-cost-decomposition.md)) |
| Rerunning until the number looks right | Pre-registered N; first valid sample retained; acceptance never gates sample retention |
| Reduced tool setups flatter or penalize a product | Faithful installation of every author-recommended surface; reduced setups are declared ablations |

## Evaluation contract

The active task family, its sequences, its ordered task IDs, and their counts live in
`data/workflow-task-sequences.json`; the current generation is
`validate_repository.CURRENT_TASK_FAMILY_GENERATION`. Read them there rather than restating them
here — a restated count is what goes stale.

The active framework is **Lifecycle V2**: a series of bounded defect repairs, each restoring one
named behavior that a specific upstream test already decides, so every task has a closed stopping
condition and no single task dominates session cost. Lifecycle V1 was superseded on 2026-08-16.
Lifecycle V0 was retired on 2026-08-14 under
`sources/evaluations/audits/lifecycle-v0-framework-retired-20260814.json` and no longer exists in
the corpus.

Every active sequence, task ID, qualification file, and current execution contract must belong to
the active generation. Do not reintroduce a V0 or other compatibility lane. Accepted production
records are immutable historical evidence. Rejected or excluded records may be deleted only by
explicit experiment-owner direction, together with their artifact roots and unreferenced protocols.

New runs use the model conditions registered as active in `data/evaluation-agent-runtimes.json` —
that registry is the authority for runtime, model, and reasoning effort. Conditions marked
`historical-inactive` are historical only: do not prepare or execute a new protocol under them.
Model or effort changes mint new protocol identities and cannot reuse a baseline from another
condition.

## Fixture design

- Pin the upstream repository commit.
- Build authentic tasks from upstream code/history.
- Start patches must be independently applicable and compose without overlap.
- **A fixture must exit zero on a clean prepared base.** Tests that fail on a clean tree show the
  agent failures it did not cause and cannot fix, and whether it investigates them is variance
  charged to the measurement. Diagnose the cause before excluding anything: exclude only what the
  pin does not own — environment-dependent failures — never a genuine upstream defect, and record
  the finding. A fixture may then declare `initial_snapshot.prepared_removals`; the controller
  removes those paths and commits the removal with a fixed identity and date, so the prepared base
  is a reproducible commit pinned alongside the upstream commit. Everything deciding that hash lives
  in the sequence, so the evaluation checkout and the local fixture cannot build different bases.
  Verify afterwards that the seeded regressions still fail: an exclusion that blinds the oracle is
  worse than the noise it removed.
- Active tasks seed authentic semantic regressions from completed upstream behavior in one or two
  production files. Seed patches must apply independently and compose cleanly; standalone and
  composite seeded verifier outcomes may be either 0 or 1 but must be recorded without
  infrastructure failure. Every cumulative repaired state must pass its retained task verifiers, and
  the fully repaired project-wide snapshot must compile.
- Model-facing prompts state the observable symptom and expected behavior without naming the file,
  function, or test, permit normal repository search and related-code inspection, expect a complete
  correct implementation, and forbid changes to tests, generated files, dependency locks, or
  evaluation controls. They must not disclose controller compile commands, evaluator scoring, or the
  internal acceptance policy.
- Internally, every task must pass affected-component compilation and the final workflow must pass
  project-wide compilation. Every task also receives exactly one narrow, implementation-independent
  essential-behavior smoke check. The smoke check should reject a missing or seriously flawed
  implementation while admitting coherent alternatives — it must not compare exact source, prescribe
  the repair, or expand into a broad suite. All broader tests, behavioral fidelity, style,
  maintainability, exact source shape, and source review remain diagnostic only. This distinction
  belongs in controller metadata and documentation, never in the agent instruction.
- **Solution-directed task assistance** is forbidden. Prescribing target files, symbols,
  implementation steps, or validation commands suppresses the search and exploration that
  context-reduction tools act on, which is why Lifecycle V0 was retired; see
  [ADR 0005](docs/architecture/decision-records/0005-token-accounting-and-protocol-identity.md).
  Compatible baseline and treatment sessions must receive identical prompt bytes and must not
  require or prefer treatment-tool invocation.
- Run all task verifiers and the project-wide compile verifier after the final prompt in one
  persistent workflow.

## Evidence and execution

Qualification JSON is generated executable evidence; never hand-edit it. Production runs require
provider-reported cumulative token telemetry sufficient to calculate weighted token cost and
isolated baseline/treatment conditions. Task verifiers and final project compilation gate
task/workflow acceptance and treatment unlock, but **do not gate weighted-token sample retention**.
Broader tests and source-review outcomes are diagnostic and must not trigger pass-selection reruns.

Treatment execution is availability/natural-use only after faithful product installation:

- Install every tool-author-recommended normal integration surface — its own hooks, wrappers,
  proxies, MCP exposure, product-authored instructions, rules, or skills.
- Evaluator-authored steering, quotas, and forced calls are forbidden, but evaluator neutrality must
  never remove or contradict the product's own guidance.
- Server-only, guidance-free, or otherwise reduced setups are explicit ablations rather than
  canonical product treatments.
- Zero explicit model-issued tool commands after faithful installation remains a valid observed
  outcome, because the intervention may operate below or around the model-visible command surface.
- Preserve the first valid assignment sample, and interpret mechanism evidence only from
  instrumentation appropriate to the declared integration.

## Editing rules by file kind

| Kind | Examples | Rule |
|---|---|---|
| Machine authority | `data/*.json` | Edit directly; it is the source the rest derives from. |
| Generated | `docs/evaluations/operations/runbook.md`, `generated:corpus-summary` blocks, `qualification-*.json`, `sources/evaluations/audits/lifecycle-v2-task-entries.json` | Never hand-edit. Change the generator, then regenerate. |
| Frozen evidence | `sources/evaluations/protocols/*`, `sources/evaluations/archive/**`, executed audits and session records | Never rewrite in place. Supersede and archive instead. |
| Narrative | `README.md`, `docs/**` | Hand-maintained; must be reconciled whenever the state it describes changes. |
| Fixture checkouts | `sources/evaluations/fixtures/*/*/repo/` | Gitignored, disposable, rebuilt by `setup.sh`. |

## Changing a task contract

Run these in order. Getting the order wrong wastes a full qualification run.

1. Edit the generator, not the generated task directories:
   `.venv/bin/python3 scripts/generate_lifecycle_v2_tasks.py`
2. Rebuild the fixture checkout: `sources/evaluations/fixtures/medium/<fixture>/setup.sh`
   (`setup-deps.sh` reinstalls dependencies; `reset.sh` restores the prepared base).
3. Regenerate qualification evidence — it executes the verifiers, so it is slow:
   `.venv/bin/python3 scripts/generate_workflow_qualification.py <sequence-id> <checkout>`
4. Archive the superseded protocol, then mint the new one **last**:
   `.venv/bin/python3 scripts/refresh_workflow_contracts.py --sequence-id <id> --profile-id <id>
   --workflow-model-condition-id <id> --workflow-model <model> --workflow-reasoning-effort <effort>`
5. Regenerate derived surfaces and reconcile narrative — see [Documentation lifecycle](#documentation-lifecycle).
6. `make check`.

When task contracts change, regenerate the affected `qualification-lifecycle-v2-*.json`, regenerate
the runbook and registry summaries, and refresh only current execution contracts. A model-facing
prompt change mints new qualification and protocol identities and archives the prior corpus.
Qualification filenames are `qualification-<generation>-<YYYYMMDD>.json`; each fixture qualifies on
its own schedule, so requalifying one does not force the other.

### Protocol-minting traps

- **Mint protocols after every script edit is final.** The protocol descriptor pins
  `validator_sha256`, the runner hash, and the qualification-generator hash. Editing any of those
  scripts afterwards silently stops the protocol from matching, and the runner reports
  `expected exactly one current designated baseline protocol ... found 0`.
- **Pass the model-condition flags** to `refresh_workflow_contracts.py`. Without them the descriptor
  records a null `model_condition_override` and will not match the active gate.
- **`refresh_workflow_contracts.py` refuses to overwrite an existing protocol file.** Archive or
  remove the superseded one first.
- **`make check` requires the current branch to have an upstream.** One contract test resolves
  `git rev-parse @{upstream}`, which fails on a fresh branch with no tracking ref.

## Documentation lifecycle

An action that changes research state must update every active surface that reports that state in
the same change. This includes an evaluation run, qualification or protocol refresh, fixture
promotion or retirement, session merge or deletion, treatment comparison, evidence-stage promotion,
and a change to eligibility or interpretation policy.

After such an action:

1. Update the machine authority first: `data/workflow-sessions.json`, `data/repository-fixtures.json`,
   and any affected sequence/profile registry.
2. Regenerate the derived surfaces; never hand-edit generated content:
   - `.venv/bin/python3 scripts/update_workflow_runbook.py` for `docs/evaluations/operations/runbook.md`;
   - `.venv/bin/python3 scripts/update_registry_summaries.py` for the `generated:corpus-summary`
     blocks in `README.md` and `sources/evaluations/README.md`.

   `make check` fails when either is stale, so do not restate corpus counts, role splits, or runtime
   splits in prose by hand — put them in a generated block instead.
3. Reconcile the narrative that generation cannot own: `docs/evaluations/README.md`,
   `docs/research/roadmap.md`, and any interpretation claim that depends on the changed state.
4. Reconcile active prompts, templates, repo-local skills, schemas, and architecture decision records
   when the contract changes. Search for the retired status, path, policy phrase, protocol/session
   ID, and lifecycle term.
5. If a document or template has no distinct maintained authority or current consumer, delete it and
   remove its references instead of leaving a second stale workflow.
6. Preserve frozen evidence bytes. Describe current execution state in registries and generated views
   rather than rewriting an executed protocol in place.
7. Run the required checks and inspect `git status` afterward. A green run is invalid if it deleted a
   required test or left new evidence untracked.

Do not finish an evaluation run with stale `ready-not-run`, `no production result`, empty-registry,
mandatory-quality-review, or baseline-rerun guidance in active surfaces.

**Do not pin a generation name, task count, dated filename, or model ID into a check or a document
that is not about that specific thing.** All of these have gone stale here: a contract test asserted
the literal string `Lifecycle V1`, identifiers carried a `lifecycle_v1_` prefix while operating on
whatever generation was active, and this file restated task counts and model IDs the registries
already owned. Read state from the registry; assert policy, not wording.

## Required checks

```bash
make check
```

`make check` is the executable definition of this gate. It runs, in order: the runbook and
registry-summary drift checks, both contract test suites, repository validation, `git diff --check`,
and a working-tree comparison that fails if the checks themselves changed tracked or untracked
state. Read the `Makefile` for the exact commands — it is the authority, and a second copy of the
list here would drift from it.

Repository validation gates every registry record on `schemas/workflow-session-record.schema.json`
and fails closed when `jsonschema` is absent. When a record shape legitimately changes, update the
schema in the same change: it is enforced against all retained sessions, not just new ones.

## Local skills

Load only the skill that matches the current work:

- `.agents/skills/benchmark-protocol-writer.md` before preparing or running an evaluation;
- `.agents/skills/claim-evidence-auditor.md` before publishing research claims;
- `.agents/skills/practical-software-quality-reviewer.md` only when an optional diagnostic review of
  model-produced changes is requested or useful.
