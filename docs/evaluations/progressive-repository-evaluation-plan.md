# Progressive repository-level evaluation plan

## Purpose

This plan defines a progressive evaluation workflow for token-optimization research. It is inspired by OpenSpec's separation of proposal, design/specification, tasks, status, and archival evidence, but it does not import OpenSpec's product-change lifecycle or archive/apply semantics.

The goal is to let an operator stop after any bounded work unit, commit the intermediate artifact, and resume later when token budget is available. No stack or tool should be promoted from `source-logic` to `benchmark-audit` or `reproduction` in one unbounded pass.

## Core idea

Treat each evaluation as an `evaluation change`: a small, versioned repository record with a frozen scope, protocol, task checklist, status file, raw evidence paths, and final interpretation.

An evaluation change can represent one of these units:

- benchmark-audit of one existing repository benchmark;
- operation-level micro benchmark for one reducer or fixture;
- retrieval benchmark for one repository snapshot and question set;
- one baseline/treatment reproduction pair;
- one compatibility-safe stack ablation lane;
- one replacement-agent comparison;
- one installer/orchestrator reproducibility test.

Each change advances through explicit gates. A later session can inspect the status file and continue from the next unchecked task without rereading all prior evidence.

## Directory model

Use lightweight OpenSpec-style planning files under `docs/evaluations/changes/` and raw evidence under `sources/evaluations/`.

```text
docs/evaluations/changes/<change-id>/
  proposal.md       # why this evaluation exists, scope, non-goals, target evidence stage
  protocol.md       # frozen hypothesis, fixtures, baselines, treatments, metrics, gates
  tasks.md          # checkbox task list, ordered for small token-budget sessions
  status.json       # machine-readable current state and next resumable task
  results.md        # interpretation after evidence is collected

sources/evaluations/<evaluation-id>/
  task.md
  profile.md
  environment.json
  baseline-transcript.jsonl
  treatment-transcript.jsonl
  provider-usage.json
  verifier-output.txt
  quality-review.md
  artifacts/

data/evaluations.json
  # compact index of completed, failed, negative, and excluded evaluation records
```

Use `templates/progressive-evaluation-change/` as the starting point for new changes.

## Identifiers

Use stable, descriptive IDs that make partial work easy to find.

- Change ID: `YYYY-MM-DD-<lane>-<target>`.
- Evaluation ID: `<change-id>-<run-role>-rNN` for run evidence.
- Task ID: `<task-class>-<short-fixture>-vNN`.
- Profile ID: use existing Phase 2 profile IDs when possible, such as `baseline-native-agent`, `sigmap-governance-artifact`, or `replacement-caveman-code`.

Examples:

- `2026-06-28-benchmark-audit-tokbench`
- `2026-06-28-terminal-micro-rtk-noisy-pytest`
- `2026-06-28-stack-ablation-sigmap-governance-artifact`

## Progressive gates

### Gate 0: Register the evaluation change

Token budget: low.

Required artifacts:

- `proposal.md`
- initial `tasks.md`
- initial `status.json`

Required decisions:

- target evidence stage: `benchmark-audit` or `reproduction`;
- evaluation lane;
- target tool, stack, benchmark, or profile;
- non-goals for this change.

Exit rule: the next task is clear and does not require rereading broad repository context.

### Gate 1: Freeze the protocol before results

Token budget: low to medium.

Required artifacts:

- completed `protocol.md`
- fixture path or planned fixture source;
- baseline and treatment definitions;
- metric boundaries;
- quality gates;
- failure, exclusion, and falsification rules.

Exit rule: another operator can run the baseline or audit without changing prompts, fixtures, metrics, or scoring rules.

### Gate 2: Collect or audit existing benchmark evidence

Token budget: medium.

Use this gate for `benchmark-audit` changes.

Required artifacts:

- raw notes under `sources/evaluations/<evaluation-id>/benchmark-audit.md`;
- harness file paths, task definitions, scoring code, token accounting method, raw-output availability, and failure semantics;
- updated `status.json` with inspected paths and unresolved questions.

Exit rule: the evidence can support a `benchmark-audit` promotion, downgrade, or explicit limitation without running a local reproduction.

### Gate 3: Prepare runnable reproduction fixture

Token budget: medium.

Use this gate for reproduction changes.

Required artifacts:

- `sources/evaluations/<evaluation-id>/task.md` from `templates/evaluation-task.md`;
- fixture repository path, commit, dirty-state policy, reset command, and verifier command;
- prompt hash and fixture hash when available;
- treatment install, disable, and reset path.

Exit rule: baseline and treatment runs can start from clean state with the same prompt and verifier.

### Gate 4: Run baseline only

Token budget: medium to high.

Required artifacts:

- baseline transcript;
- baseline provider usage or measurement source note;
- verifier output;
- baseline environment metadata;
- baseline compact record staged for `data/evaluations.json` only after quality review.

Exit rule: baseline result is preserved even if treatment must wait for another session.

### Gate 5: Run one treatment only

Token budget: medium to high.

Required artifacts:

- treatment transcript;
- treatment provider usage or measurement source note;
- verifier output;
- raw and transformed artifacts where relevant;
- treatment environment metadata.

Exit rule: treatment evidence is comparable to the frozen baseline, or the status file records why it is excluded.

### Gate 6: Review quality and ablations

Token budget: medium.

Required artifacts:

- `quality-review.md` using the software-quality gates;
- ablation table when two or more components are active;
- surface ownership and overlap check;
- downgrade conditions for under-solving, diagnostic loss, unsafe state, or unresettable configuration.

Exit rule: token savings cannot be interpreted without the quality result.

### Gate 7: Synthesize and index

Token budget: low to medium.

Required artifacts:

- completed `results.md`;
- compact `data/evaluations.json` record;
- dossier or report update only when evidence stage permits it;
- `status.json` marked `done`, `blocked`, `downgraded`, or `superseded`.

Exit rule: the repository records the result, including negative and failed results, without requiring transcript rereads.

## Status states

Use these states in `status.json`:

- `not_started` — artifact exists but no substantive work has started.
- `in_progress` — current gate has started and can be resumed.
- `blocked` — missing credential, fixture, dependency, provider usage record, or verifier.
- `needs_review` — evidence exists but quality or claim-evidence review is not done.
- `done` — final interpretation and index record are complete.
- `downgraded` — evidence failed promotion criteria but remains useful as a negative finding.
- `superseded` — a newer change replaces this one.

Every status update should include:

- `current_gate`;
- `next_task`;
- `resume_context` in three to six bullets;
- paths to the latest artifacts;
- blockers or required external inputs.

## Token-budget sizing

Use this sizing to choose the next task.

| Size | Typical work | Stop artifact |
|---|---|---|
| S | Register change, read one benchmark file, fill one protocol section, update status. | Updated markdown section or `status.json`. |
| M | Audit one harness, freeze one task fixture, run one operation-level micro benchmark, complete quality review. | Raw notes plus status update. |
| L | Run one full baseline or one full treatment with provider usage capture. | Transcript, usage, verifier output, and environment record. |

Do not combine two L-sized tasks in one session unless the operator explicitly confirms enough token and provider budget.

## Claim and promotion rules

- A `source-logic` candidate can be selected for evaluation, but cannot be described as measured.
- A `benchmark-audit` result requires inspected harness, tasks, scoring, token accounting, raw outputs, and failure semantics.
- A `reproduction` result requires independent target-workload runs with provider-billed accounting where available, pass/fail or quality score, turns, tool calls, latency, and reset evidence.
- A treatment that reduces tokens while failing the verifier is a quality regression.
- A treatment with overlapping surface owners is invalid unless overlap was disabled and verified before the run.
- Negative, null, blocked, and excluded results remain first-class repository evidence.

## OpenSpec-inspired boundaries

Borrow these OpenSpec-style practices:

- separate why (`proposal.md`), what must be true (`protocol.md`), execution checklist (`tasks.md`), and current state (`status.json`);
- validate scope before running expensive work;
- make each change reviewable in Git;
- keep historical changes instead of overwriting conclusions.

Do not borrow these OpenSpec practices for this repository-level evaluation workflow:

- no spec archive/apply step that mutates canonical product specs;
- no requirement that every evaluation becomes a long-lived product capability;
- no automatic promotion from completed tasks to claims;
- no task status as evidence without raw artifacts and quality gates.

## Review checklist before starting a new run

- The protocol was written before results.
- Baseline and treatment use the same task prompt, fixture, verifier, and model/provider where possible.
- Provider-billed task usage is the primary metric when available.
- Cache fields are recorded separately from fresh input tokens.
- Raw output is recoverable when compaction is tested.
- Quality gates are defined before interpreting token savings.
- Reset and disable paths are documented.
- `status.json` names the next resumable task.

## Validation commands

After adding or updating evaluation-change artifacts, run:

```bash
truthmark check --json
truthmark index --json
python3 scripts/validate_repository.py
git diff --check
```

For Go-based Tokless verification, run `go test ./...` from the Tokless clone or fixture with the Go path described in `AGENTS.md`, not from this repository root.
