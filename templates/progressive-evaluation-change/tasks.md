# Tasks: <change-id>

Keep each task small enough to run in a later low-context session.

## Gate 0: Register

- [ ] Fill `proposal.md` summary, scope, prior evidence, and non-goals.
- [ ] Set `status.json` to `in_progress` with `current_gate: 0`.
- [ ] Record the next task in `status.json`.

## Gate 1: Freeze protocol

- [ ] Fill hypothesis and target evidence stage in `protocol.md`.
- [ ] Fill task fixture, baseline, treatment, metrics, quality gates, and failure rules.
- [ ] Verify baseline and treatment do not change the prompt, fixture, verifier, or model/provider unless explicitly justified.
- [ ] Update `status.json` with protocol completion and next task.

## Gate 2: Benchmark-audit evidence, if applicable

- [ ] Identify harness files, task definitions, scoring code, raw outputs, and token accounting files.
- [ ] Write raw audit notes under `sources/evaluations/<evaluation-id>/benchmark-audit.md`.
- [ ] Decide whether the benchmark evidence supports `benchmark-audit`, downgrade, or blocked status.
- [ ] Update `results.md` or `status.json` with the audit conclusion.

## Gate 3: Reproduction fixture, if applicable

- [ ] Create `sources/evaluations/<evaluation-id>/task.md` from `templates/evaluation-task.md`.
- [ ] Record fixture commit, prompt hash, verifier command, and reset procedure.
- [ ] Create `sources/evaluations/<evaluation-id>/profile.md` for baseline and treatment profiles.
- [ ] Update `status.json` with the exact baseline-run command or flow.

## Gate 4: Baseline run

- [ ] Run baseline from clean state.
- [ ] Save transcript, provider usage, environment metadata, and verifier output.
- [ ] Record baseline status and any exclusion reason.
- [ ] Update `status.json` with the exact treatment-run command or flow.

## Gate 5: Treatment run

- [ ] Reset repository and agent/tool state.
- [ ] Activate treatment profile.
- [ ] Run treatment with the frozen prompt, fixture, verifier, and model/provider where possible.
- [ ] Save transcript, provider usage, environment metadata, verifier output, and raw/transformed artifacts.
- [ ] Record treatment status and any exclusion reason.

## Gate 6: Quality and ablation review

- [ ] Write `quality-review.md` under `sources/evaluations/<evaluation-id>/`.
- [ ] If multiple components are active, fill an ablation table with owned surfaces, expected benefit, failure mode, and required metric.
- [ ] Check diagnostic preservation, reset path, safety, and reviewability.
- [ ] Update `status.json` to `needs_review` or ready for synthesis.

## Gate 7: Synthesis and index

- [ ] Complete `results.md` with accepted result, uncertainty, downgrade conditions, and evidence paths.
- [ ] Add or update the compact record in `data/evaluations.json`.
- [ ] Update any dossier or report only to the evidence stage reached.
- [ ] Mark `status.json` as `done`, `downgraded`, `blocked`, or `superseded`.
- [ ] Run repository validation commands.
