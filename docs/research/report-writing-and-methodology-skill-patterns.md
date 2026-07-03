# Report-writing and research-methodology skill patterns

## Purpose

This note extracts reusable patterns from external research-skill repositories and adapts them to this repository's practical software-evaluation context. The goal is better report quality, stronger research methodology, and immediately usable Phase 2 benchmark flows without turning the project into a citation-heavy literature review.

External repositories inspected:

- `assafelovic/gpt-researcher`
- `orchestra-research/AI-research-SKILLs`
- `Master-cai/Research-Paper-Writing-Skills`

The patterns below are used as methodology inspiration. Claims in this repository should continue to be grounded primarily in inspected source code, runnable benchmarks, provider-reported token usage, verifier outputs, and software-quality review.

## Selected skill patterns to adapt

| Pattern | Source skill or prompt | What to adapt here | What not to copy |
|---|---|---|---|
| Recursive research decomposition | GPT Researcher deep-research mode | Break broad questions into bounded subquestions with explicit breadth/depth, then synthesize branch findings. Useful for benchmark-audit passes across surfaces. | Do not use generic web-summary depth as evidence when source code or benchmark artifacts are required. |
| Source curation before report writing | GPT Researcher source curation and report prompts | Separate evidence collection from report drafting; prioritize relevance, reliability, recency, and quantitative detail. | Do not force many citations into practical software reports; use citations only for external methods, benchmark provenance, or prior-art positioning. |
| Subtopic uniqueness and anti-duplication | GPT Researcher subtopic report prompts | Prevent repeated stack archetypes and repeated report sections; each section should add a distinct mechanism, workload, or evidence class. | Do not generate long sections merely to satisfy word count. |
| Two-loop research cycle | Orchestra `autoresearch` | Use an inner loop for fast benchmark runs and an outer loop for synthesis, pattern detection, pivots, and updated hypotheses. | Do not run indefinite autonomous loops in this repo without explicit scheduling and run-budget controls. |
| Protocol-before-result discipline | Orchestra `autoresearch` | Write the task protocol, hypothesis, metric, baseline, and falsification condition before running an evaluation. This prevents metric gaming. | Do not over-formalize one-off source inspections; use it for benchmark-audit and reproduction. |
| Research state and findings memory | Orchestra `autoresearch` templates | Maintain compact run state, trajectory, evidence gaps, and current understanding for Phase 2 evaluations. | Do not create sprawling logs that duplicate raw transcripts already stored under `sources/evaluations/`. |
| Narrative principle | Orchestra `ml-paper-writing` | Every report needs a one-sentence technical claim: what is being evaluated, why it matters, and what evidence currently supports it. | Do not claim novelty or broad superiority without reproduction evidence. |
| Systems-paper thesis formula | Orchestra `systems-paper-writing` | Use `X is better for Y in Z` as a benchmark hypothesis template: a stack/profile X should improve metric Y under workload/environment Z. | Do not write venue-style academic framing when a concise technical report is sufficient. |
| Design alternatives and ablations | Orchestra `systems-paper-writing` | For each stack, name alternatives and ablations: remove memory, replace retriever, disable behavior controller, or use a lower-intervention baseline. | Do not present multi-component gains without isolating components in Phase 2. |
| Epistemic rigor review | Orchestra `ara-rigor-reviewer` | Review reports across evidence relevance, falsifiability, scope calibration, argument coherence, exploration integrity, and methodological rigor. | Do not require the full ARA directory structure unless this repo later adopts it. |
| Paragraph-level clarity and reverse outlining | Master-cai `research-paper-writing` | One paragraph, one message. Use reverse outlines to check section flow and claim-evidence mapping. | Do not apply academic prose templates mechanically to operational benchmark reports. |
| Challenge-insight-contribution structure | Master-cai abstract/introduction guides | For executive summaries, state task/challenge, insight, candidate profile, and evidence status. | Do not overstate a contribution as solved before reproduction. |
| Claim-evidence hard constraint | Master-cai paper-review | Every major claim in abstract/executive summary and conclusion must map to an evidence artifact or be weakened. | Do not leave unsupported claims as prose because they sound plausible. |
| Experiment triad | Master-cai experiments guide | Phase 2 must include strong baselines, ablations/design-choice isolation, and harder or out-of-distribution cases. | Do not count command-level token reduction as task-level success. |
| Standard benchmark configuration capture | BigCode/lm-evaluation harness skills | Record model, task, sampling/generation settings, execution permissions, saved samples, and metric output paths for every evaluation. | Do not import generic model benchmarks as direct evidence for coding-agent stack savings. |
| Figure/table planning | Orchestra `academic-plotting` | Use one figure/table per message: compatibility surface map, benchmark result table, ablation chart, or run trajectory. | Do not use decorative visuals without measurement or decision value. |

## Recommended internal skills for this repository

These are not necessarily standalone Hermes skills yet; they are reusable roles or checklists that should shape prompts, templates, and Phase 2 workflows.

### 1. Claim-evidence auditor

Use before publishing any report section.

Checklist:

1. Extract every major claim from the executive summary, findings, and selection guidance.
2. Classify the claim as mechanism, compatibility, benchmark, reproduction, or recommendation.
3. Map the claim to source-logic dossier, benchmark-audit record, reproduction run, or explicit limitation.
4. Weaken or remove claims with no evidence path.
5. Add falsification or downgrade conditions for retained claims.

### 2. Benchmark protocol writer

Use before running Phase 2 tasks.

Checklist:

1. Define hypothesis using `X improves Y for workload Z`.
2. Freeze repository fixture, prompt, baseline, treatment profile, and model/provider.
3. Declare the complete provider-token accounting boundary, execution-integrity conditions, and separate model-behavior diagnostics.
4. Declare fixture/contract invalidity and operational exclusion rules before running.
5. Freeze the lifecycle protocol under `sources/evaluations/protocols/`; current execution state and compact evidence are indexed by `data/workflow-sessions.json`.

### 3. Stack ablation planner

Use for every multi-component stack.

Checklist:

1. Identify each owned surface in the full profile.
2. Create ablations that remove or replace one component at a time when feasible.
3. Include a lower-intervention baseline.
4. Treat installer/orchestrator behavior separately from reducer behavior.
5. Report component interactions instead of attributing all gains to the full bundle.

### 4. Scientific report reviewer

Use after drafting.

Dimensions:

1. Evidence relevance: does each cited artifact support the claim?
2. Falsifiability: can the claim be disproven by a concrete run?
3. Scope calibration: does the wording match the inspected workload and evidence stage?
4. Argument coherence: does the report move from problem to hypothesis to evidence to limits?
5. Exploration integrity: are negative findings, exclusions, and pivots recorded?
6. Methodological rigor: are baselines, ablations, metric definitions, and reproducibility details adequate?

### 5. Practical software-quality reviewer

Use after each reproduction run.

Checklist:

1. Did the verifier pass?
2. Did the treatment preserve key diagnostics and raw-output recovery?
3. Is the final diff minimal, maintainable, and convention-preserving?
4. Were safety, permissions, generated config, and reset paths reviewed?
5. Did token savings come from real efficiency rather than under-solving or skipping work?

### 6. Citation-light prior-art mapper

Use when writing reports for this repo.

Rules:

1. Prefer direct software evidence over broad literature citation.
2. Cite or link only when identifying external benchmark provenance, prior-art categories, or method lineage.
3. Do not cite every tool README in the report body; keep raw provenance in dossiers and data records.
4. Use grouped related-work framing by mechanism or surface, not one paragraph per repository.
5. Keep the report readable as a technical decision artifact.

### 7. Figure/table planner

Use when turning Phase 2 results into reports.

Recommended visuals:

- surface ownership matrix;
- baseline versus treatment provider-reported workflow tokens;
- structured per-task correctness and independent quality table;
- treatment installation/configuration and isolation summary, with observed use included only as optional descriptive telemetry;
- ablation chart by component;
- run trajectory for iterative benchmark development;
- installer profile diff for Tokless-generated configuration.

## Integration into existing repository artifacts

| Existing artifact | Improvement from these skills |
|---|---|
| `docs/reports/phase-1-compatibility-safe-token-saving-stacks.md` | Add claim-evidence and falsification discipline; keep stack hypotheses evidence-stage calibrated and not deployment-grade. |
| `docs/evaluations/phase-2-benchmark-plan.md` | Use protocol-before-result, ablation planning, and benchmark configuration capture. |
| `docs/evaluations/token-usage-and-quality-standards.md` | Keep provider-reported workflow-token eligibility separate from model-behavior diagnostics. |
| `docs/evaluations/immediately-usable-flows.md` | Convert methodology into lifecycle-v0 execution flows with compact artifacts and operational validity checks. |
| `data/workflow-sessions.json` | Store the compact index of operational provider runs and their separate quality diagnostics. |
| `prompts/paper-writer.md` | Enforce narrative, reverse outline, claim-evidence map, and citation-light prior-art rules. |
| `prompts/evaluator.md` | Enforce protocol-before-result, baseline compatibility, token-first comparison, and post-run document synchronization. |

## Current operating recommendation

For lifecycle-v0 research:

1. Reuse the retained operational baseline for each active sequence; do not rerun it for a better diagnostic outcome.
2. Freeze a compatible treatment protocol and verify tool identity, isolation, and fixture qualification before provider use.
3. Run one treatment through `scripts/run_sequential_workflow_matrix.py` and retain the first operationally valid sample.
4. Compare cumulative provider-reported tokens as the primary outcome; report verifier and optional source-review outcomes separately.
5. Update `data/workflow-sessions.json`, fixture state, generated runbook, current findings, and any active prompt or method surface affected by the run.
6. Delete superseded workflow guidance instead of maintaining two architectures.

The Phase 2 report should be concise and evidence-forward: fewer citations, more protocol, compact raw artifacts, provider-reported token usage, verifier diagnostics, optional review context, ablations, and negative findings.
## Installed repo-local skills

The recommended internal skills are installed as repo-local prompt files under `.agents/skills/` and surfaced through `AGENTS.md`:

- `.agents/skills/benchmark-protocol-writer.md`
- `.agents/skills/claim-evidence-auditor.md`
- `.agents/skills/stack-ablation-planner.md`
- `.agents/skills/practical-software-quality-reviewer.md`
- `.agents/skills/scientific-report-reviewer.md`
- `.agents/skills/citation-light-prior-art-mapper.md`
- `.agents/skills/figure-table-planner.md`

These files are intentionally repo-local rather than global Hermes skills so the research workflow travels with the repository and does not depend on the active user profile.

## Truthmark research-truth layer

Truthmark is installed as a repo-local research-truth workflow layer.

Durable methodology, evidence-stage, token-accounting, quality-diagnostic, stack-compatibility, current-finding, and agent-workflow claims live under `docs/truthmark/engineering/research/`.

Raw `sources/**` artifacts remain evidence archives, not canonical truth docs.
