# Phase 1 report: compatibility-safe token-saving stack hypotheses for AI coding agents

> Historical report. This preserves the Phase 1 state and terminology at publication time. Current lifecycle-v0 execution, token eligibility, and artifact contracts are owned by `AGENTS.md`, `data/workflow-sessions.json`, and `docs/evaluations/evaluation-framework.md`; quality review is now diagnostic rather than a token-sample gate. The current measured synthesis is the [Phase 2 lifecycle-v0 natural-use screening report](phase-2-lifecycle-v0-natural-use-screening.md); the Phase 2 routing and priority lists below are historical planning rather than the active evaluation roadmap.

**Date:** 2026-06-29
**Repository:** `token-optimization-research`
**Review status:** source-logic compatibility report; benchmark-audit and reproduction pending
**Evidence base:** 42 source-logic tool dossiers: 29 original dossiers plus 13 corrective-audit graph/RAG and memory dossiers promoted on 2026-06-29
**Claim boundary:** stack findings are source-logic hypotheses for Phase 2 evaluation. They are not deployment-grade recommendations, measured provider-billed savings claims, procurement recommendations, or proof of quality preservation.

## Executive summary

This report identifies compatibility-safe stack hypotheses for AI coding agents from 42 source-logic tool dossiers. A compatibility-safe stack assigns clear ownership for token-relevant surfaces: terminal and tool-output compaction, retrieval and context selection, durable memory, broad compression or proxy control, execution offload, behavioral output style, artifact minimization, repository packing, installer/orchestrator behavior, and replacement-agent runtime behavior.

The central Phase 1 finding is not that a single stack should be treated as the default. The stronger result is a research portfolio: a set of non-overlapping stack hypotheses and comparators that can be carried into Phase 2 benchmark-audit and reproduction. The portfolio deliberately includes narrow lower-intervention comparators, graph/RAG retrieval candidates, memory-heavy candidates, broad-owner candidates, Apple/platform-specific candidates, installer/orchestrator reproducibility candidates, and replacement-agent lanes.

The expanded source-logic set materially changes the retrieval and memory portions of the research space. Graphify, Understand-Anything, Cartog, Codescope, SwarmVault, Total Agent Memory, Dragon-Brain, Memex, CognitX CodeGraph, and related graph/RAG or memory tools are now source-logic candidates rather than discovery-only records. They can therefore participate in source-logic stack hypotheses, but they still require benchmark-audit and reproduction before any measured effectiveness claim.

The most important methodological constraint remains unchanged: source inspection can support mechanism and compatibility hypotheses, but it cannot establish provider-token savings or correctness/quality preservation. Phase 2 must evaluate each candidate against a baseline with provider-reported workflow token accounting, structured task verifier results, independent quality review, treatment isolation, and recoverable artifacts. Monetary cost, latency, and broad behavior telemetry are not project decision metrics.

## Scope

Included:

- Tools with persistent source-logic dossiers or equivalent source-logic records in the repository.
- Compatibility-safe stack hypotheses where each component owns a distinct token-relevant surface.
- Single-owner stacks where one tool deliberately combines multiple surfaces and should be evaluated as an integrated owner.
- Workload-specific hypotheses, including graph/RAG onboarding, repeated-memory tasks, code review, Apple/Xcode repair, MCP-heavy offload, and replacement-agent comparisons.
- Phase 2 benchmark-audit and reproduction routing.

Excluded:

- Deployment-grade recommendations.
- Claims of measured savings, pass-rate preservation, or cost reduction.
- Tool popularity as a primary stack-selection criterion.
- Loose bundles without explicit surface ownership.
- Multi-tool stacks that double-own retrieval, memory, shell-output compaction, broad proxy compression, execution offload, or runtime control unless the overlap is itself the ablation under test.

## Evidence-stage boundaries

The repository uses four evidence stages:

| Stage | Meaning in this report | Permitted use |
|---|---|---|
| `lead` | Discovery/backlog evidence only | Candidate discovery and future triage only |
| `source-logic` | Representative implementation files inspected for mechanism, runtime behavior, state, failure modes, and compatibility implications | Stack hypothesis formation and Phase 2 prioritization |
| `benchmark-audit` | Benchmark harness, tasks, scoring, token accounting, raw outputs, and exclusion/failure semantics inspected | Evidence-weighted ranking and benchmark-informed selection |
| `reproduction` | Local or independent target-workload reproduction with provider-billed accounting and software-quality gates | Deployment-grade recommendation consideration |

All stack candidates in this report are `source-logic` hypotheses. A Phase 2 profile can be called a coverage probe or comparator, but that is a research role rather than an evidence stage.

## Methodology

### Source-logic review

The report uses persistent dossiers in `docs/tool-dossiers/` as the primary evidence layer. Each dossier records repository identity, inspected source paths, installation and integration behavior, runtime behavior, token-saving mechanism, compatibility notes, failure modes, and next review tasks.

### Corrective coverage audit

A corrective discovery audit on 2026-06-28 found missing graph/RAG and memory candidates. The 13 corrective-audit records were promoted to source-logic dossiers on 2026-06-29. The raw source-inspection artifacts remain in the repository provenance layer rather than in the report body.

### Compatibility-surface analysis

Stack construction uses surface ownership rather than repository popularity. A stack is compatibility-safe when each component has a distinct role, or when one integrated component is intentionally treated as the sole owner for overlapping surfaces.

### Phase 2 readiness

The report prioritizes candidates that can be ablated cleanly: baseline, single-surface owner, full stack, remove-one variants, lower-intervention comparator, broad-owner comparator, and replacement-runtime comparator where appropriate.

## Evaluation criteria

| Criterion | Definition | Priority |
|---|---|---|
| Surface compatibility | Components avoid competing hooks, context surfaces, retrieval authority, memory authority, compression/proxy ownership, output channels, and state boundaries | Highest |
| Evidence stage | Source-logic evidence is required for stack hypotheses; benchmark-audit and reproduction are required for stronger claims | Highest |
| Workload fit | The stack targets a specific token-waste pattern such as terminal noise, broad file reads, rediscovery, large logs, offload traces, or artifact bloat | High |
| Ablation clarity | Phase 2 can isolate each component's contribution | High |
| Diagnostic preservation | The stack has a plausible raw-output or error-fidelity path | High |
| Operational complexity | Install, state, cache, hook, service, and reset behavior are bounded enough for controlled reproduction | Medium |
| Adoption signal | Stars, forks, and visibility can guide audit order but do not substitute for source or benchmark evidence | Low |

## Surface ownership model

| Surface | Candidate owners | Stack rule |
|---|---|---|
| Terminal/tool-output compaction | RTK, Lowfat, Snip, TokenJuice, xcsift, LeanCTX shell compression, Token Savior Bash compaction | Use one general owner. Use xcsift as a specialized Apple/Xcode owner only when a general shell compactor is not also filtering the same output. |
| Code retrieval and indexing | CodeGraph, Cartog, Graphify, Understand-Anything, Serena, SigMap, jcodemunch MCP, CocoIndex Code, Code Review Graph, CognitX CodeGraph, Codescope, SwarmVault, Memex, LeanCTX retrieval, Token Savior retrieval | Use one primary current-source retrieval authority unless an explicit retrieval bakeoff is being run. |
| Memory and reinjection | Claude Mem, Cavemem, MEX, Total Agent Memory, Dragon-Brain, Memex, Token Savior memory, LeanCTX memory, SwarmVault memory | Use one automatic memory or reinjection authority. MEX can be used as a scaffold/governance layer only if it is not also acting as automatic memory reinjection. |
| Broad context compression/proxy | Headroom, Claw Compactor, LeanCTX, Token Savior, Codescope, Memex | Evaluate broad owners alone or with non-overlapping policy layers. Do not combine broad compressors or broad context owners without disabled surfaces and raw-recovery checks. |
| Execution offload/result selection | Context-Mode, pctx, Headroom proxy modes, Maestro Flow orchestration | Use one offload or orchestration owner per run. |
| Behavioral output style | Caveman | Use one behavior/output-style controller. |
| Artifact/code minimization | Ponytail | Use one artifact-policy layer. |
| Repository packing/digests | Repomix, Gitingest | Use for snapshots and handoffs, not as a default companion to targeted retrieval. |
| Replacement runtime | ClawCodex, Caveman Code | Evaluate as alternative runtimes rather than add-ons to an existing hook stack. |
| Installer/orchestrator | Tokless, Maestro Flow, Grace Marketplace | Evaluate setup/reproducibility separately from token-reduction mechanisms unless the orchestrator itself owns a measured surface. |

## Source-logic stack hypotheses

### Hypothesis 1: Lower-intervention terminal plus graph retrieval comparator

**Components:** `RTK + CodeGraph`

**Target workload:** general coding tasks where noisy terminal output and broad code search are the expected token sinks.

**Owned surfaces:** RTK owns terminal/tool-output compaction. CodeGraph owns current-source retrieval.

**Compatibility rationale:** the components occupy distinct surfaces and provide a low-complexity comparator for broader graph/RAG and memory stacks.

**Primary risks:** terminal compaction may hide diagnostics; graph retrieval may add tool-call overhead or suffer stale indexing.

**Phase 2 ablation:** baseline, RTK-only, CodeGraph-only, RTK+CodeGraph.

**Downgrade criteria:** no provider-billed task reduction after turn count and cache effects are included; failed target localization; diagnostic loss in failing-command output.

### Hypothesis 2: Cartog-centered local graph/RAG stack

**Components:** `Lowfat + Cartog + Total Agent Memory`

**Target workload:** implementation tasks requiring current-source graph navigation plus durable project/history memory.

**Owned surfaces:** Lowfat owns terminal compaction. Cartog owns current-source graph/RAG retrieval. Total Agent Memory owns durable memory and prior-decision recall.

**Compatibility rationale:** current source and durable memory are separate authorities, making the stack suitable for memory ablation.

**Primary risks:** Cartog index freshness, memory staleness, and combined install/hook state.

**Phase 2 ablation:** Cartog-only, Cartog+Total Agent Memory, Lowfat+Cartog+Total Agent Memory.

**Downgrade criteria:** memory injection increases stale context; graph context does not reduce broad reads; terminal compaction loses failing-line diagnostics.

### Hypothesis 3: Graphify-centered graph retrieval stack

**Components:** `Graphify + MEX + Snip`

**Target workload:** project onboarding, architecture questions, and code/document graph lookup in existing Claude/Codex-like workflows.

**Owned surfaces:** Graphify owns graph generation and graph query/MCP retrieval. MEX acts as memory scaffold and drift-governance layer. Snip owns shell-output filtering.

**Compatibility rationale:** the graph, scaffold, and shell-output surfaces are separable if MEX is not configured as a second automatic memory injector.

**Primary risks:** graph freshness, extractor coverage, host skill installation side effects, and shell filter coverage.

**Phase 2 ablation:** Graphify alone, Graphify+Snip, Graphify+MEX+Snip.

**Downgrade criteria:** graph lookup causes additional correction turns, graph rebuild overhead dominates, or retrieved graph context does not locate the relevant files/symbols.

### Hypothesis 4: Understand-Anything onboarding and graph-context stack

**Components:** `Understand-Anything + Cavemem + Snip`

**Target workload:** unfamiliar-repository onboarding and explanation tasks where graph context and prior observations may replace broad source reads.

**Owned surfaces:** Understand-Anything owns project graph and onboarding context. Cavemem owns compressed memory. Snip owns shell-output filtering.

**Compatibility rationale:** the first benchmark pass can disable memory to isolate graph value, then add Cavemem to test repeated-task rediscovery.

**Primary risks:** generated graph context may be too coarse for edits; Cavemem may duplicate current-source context; graph generation cost may offset savings.

**Phase 2 ablation:** Understand-Anything without memory, then Understand-Anything+Cavemem on repeated tasks.

**Downgrade criteria:** graph context requires follow-up broad reads; memory increases stale recall; verifier quality drops.

### Hypothesis 5: Integrated MCP owner stack

**Components:** `Token Savior MCP profile`

**Target workload:** MCP-compatible agents where one integrated owner is preferable to composing retrieval, memory, and Bash compaction tools.

**Owned surfaces:** Token Savior owns retrieval, project indexing, compact worktree summaries, memory, and optional Bash compaction.

**Compatibility rationale:** this is a single-owner hypothesis. It should not be combined with separate retrieval, memory, or Bash compaction tools unless those surfaces are explicitly disabled.

**Primary risks:** broad ownership makes attribution difficult; profile boundaries and memory retention need audit; partial adoption may create hidden overlap.

**Phase 2 ablation:** profile-level surface disabling if supported; otherwise Token Savior alone against baseline and lower-intervention comparator.

**Downgrade criteria:** broad ownership increases correction turns, profile boundaries are unclear, or raw diagnostics are not recoverable.

### Hypothesis 6: Broad context-owner comparator

**Components:** `LeanCTX`, optionally `+ Ponytail`

**Target workload:** teams willing to let one local context layer own read/search/shell/memory/graph/MCP surfaces, with a separate artifact-minimization policy layer.

**Owned surfaces:** LeanCTX owns broad context access and compression surfaces. Ponytail owns artifact/code minimization only.

**Compatibility rationale:** LeanCTX should be evaluated as a broad owner, not casually stacked with narrow retrieval, memory, or shell compaction tools.

**Primary risks:** cache freshness, daemon behavior, broad-surface overlap, and under-building from artifact minimization.

**Phase 2 ablation:** baseline, LeanCTX alone, LeanCTX+Ponytail.

**Downgrade criteria:** broad ownership adds overhead, loses source fidelity, or Ponytail causes under-solved tasks.

### Hypothesis 7: Code review graph stack

**Components:** `Code Review Graph + Claude Mem + Lowfat`

**Target workload:** code review, PR repair, and change-impact tasks.

**Owned surfaces:** Code Review Graph owns review/diff-oriented retrieval. Claude Mem owns summarized prior-session recall. Lowfat owns terminal output.

**Compatibility rationale:** the stack is workload-specific and should be tested against review-quality gates rather than general coding tasks first.

**Primary risks:** review-oriented graph context may not generalize; memory summaries can be stale or privacy-sensitive; terminal compaction can hide diagnostics.

**Phase 2 ablation:** Code Review Graph alone, Code Review Graph+Claude Mem on repeated review tasks, full stack with Lowfat.

**Downgrade criteria:** increased false positives, missed review defects, or no reduction in repeated review context.

### Hypothesis 8: MCP-heavy retrieval and execution-offload stack

**Components:** `jcodemunch MCP + pctx + Caveman`

**Target workload:** MCP-heavy workflows where intermediate traces and execution steps should stay outside the main model context.

**Owned surfaces:** jcodemunch owns compact code retrieval. pctx owns execution offload/code-mode runtime. Caveman owns terse output style.

**Compatibility rationale:** retrieval, execution offload, and behavior style are distinct surfaces, but runtime trust and result-selection boundaries are more complex than lower-intervention stacks.

**Primary risks:** pctx session trust boundary, generated execution state, broad MCP tool surface, and terse output increasing correction turns.

**Phase 2 ablation:** jcodemunch-only retrieval, pctx-only offload where feasible, full stack.

**Downgrade criteria:** hidden execution traces impede diagnosis, terse output under-explains decisions, or external offload does not reduce billed task context.

### Hypothesis 9: SwarmVault wiki and graph owner

**Components:** `SwarmVault`, optionally `+ Lowfat`

**Target workload:** documentation-heavy repositories, generated wiki/page retrieval, and project onboarding.

**Owned surfaces:** SwarmVault owns vault/wiki generation, retrieval, graph traversal, and memory-like project context. Lowfat can own terminal compaction only when SwarmVault output compaction is not used.

**Compatibility rationale:** SwarmVault should be evaluated as a broad graph/wiki owner before adding other graph or memory systems.

**Primary risks:** generated summaries can omit edit-critical detail; compile/search/query steps may add cost; broad graph/wiki/memory ownership overlaps Graphify, Memex, Maestro Flow, Codescope, and LeanCTX.

**Phase 2 ablation:** SwarmVault alone against graph retrieval comparators; optional Lowfat only in terminal-heavy tasks.

**Downgrade criteria:** generated wiki context requires broad source rereads, retrieval lacks citations or provenance, or stale artifacts mislead edits.

### Hypothesis 10: Heavy architecture graph plus durable memory stack

**Components:** `CognitX CodeGraph + Dragon-Brain`

**Target workload:** architecture tasks in TypeScript/Nest/React-style repositories where current architecture and durable decisions both matter.

**Owned surfaces:** CognitX CodeGraph owns current-source architecture graph retrieval. Dragon-Brain owns durable agent memory and temporal recall.

**Compatibility rationale:** the stack is valid only if CognitX remains the current-source graph authority and Dragon-Brain remains durable memory authority.

**Primary risks:** multiple graph backends, service operational complexity, memory deletion/retention governance, and setup overhead.

**Phase 2 ablation:** CognitX alone, Dragon-Brain memory-only on repeated tasks, combined stack.

**Downgrade criteria:** graph/memory boundaries blur, services are not reproducible, or memory recall introduces stale decisions.

### Hypothesis 11: Broad code-intelligence owner comparator

**Components:** `Codescope` alone

**Target workload:** large repositories where a Rust-native graph/search/context owner might replace several narrower tools.

**Owned surfaces:** Codescope owns graph/search/context, output archiving, and related code-intelligence surfaces.

**Compatibility rationale:** Codescope is a broad-owner comparator and should not be combined with separate graph retrieval, memory, or output-compaction tools until disabled-surface behavior is mapped.

**Primary risks:** daemon/service state, broad overlap, output archiving fidelity, and difficulty attributing benefits.

**Phase 2 ablation:** Codescope alone against RTK+CodeGraph, RTK+Cartog, and Graphify-centered stacks.

**Downgrade criteria:** broad owner overhead exceeds savings, archiving loses diagnostics, or retrieval does not improve target localization.

### Hypothesis 12: Apple platform build-repair stack

**Components:** `xcsift + Serena + MEX`

**Target workload:** Swift, iOS, macOS, and Xcode-heavy build/test repair.

**Owned surfaces:** xcsift owns Xcode/SPM output parsing. Serena owns code retrieval and editing. MEX owns project convention scaffolding and drift governance.

**Compatibility rationale:** the stack uses one specialized terminal owner, one retrieval/editing owner, and one non-automatic governance/memory scaffold.

**Primary risks:** xcsift is domain-specific; general terminal compactors must not also filter `xcodebuild`; memory governance may not help one-off repair tasks.

**Phase 2 ablation:** xcsift-only, xcsift+Serena, xcsift+Serena+MEX.

**Downgrade criteria:** xcsift misses compiler/test diagnostics, Serena duplicates broad reads, or MEX adds irrelevant context.

### Hypothesis 13: Broad compression-owner comparator

**Components:** `Headroom` or `Claw Compactor` as single broad compression owner

**Target workload:** large logs, large tool results, long histories, or proxy-mediated sessions where broad compression might reduce request size.

**Owned surfaces:** Headroom or Claw Compactor owns broad compression/proxy behavior. Only one should be active in a run.

**Compatibility rationale:** broad compression owners must be tested separately from narrow terminal compactors and retrieval tools because they can alter multiple context surfaces.

**Primary risks:** lost schema/code fidelity, raw recovery dependence, additional correction turns, and proxy overhead.

**Phase 2 ablation:** broad owner alone against terminal-only compactor and baseline.

**Downgrade criteria:** compression savings disappear at task level, raw recovery is unreliable, or correction turns offset request-level compression.

### Hypothesis 14: SigMap governance and artifact-minimization stack

**Components:** `Lowfat + SigMap + MEX + Ponytail`

**Target workload:** general coding sessions where terminal noise, targeted source navigation, project-context discipline, and artifact bloat are all expected to matter.

**Owned surfaces:** Lowfat owns terminal compaction. SigMap owns targeted source/context retrieval. MEX owns project-context governance and drift discipline. Ponytail owns artifact/code minimization.

**Compatibility rationale:** the stack is a multi-surface add-on hypothesis with one owner per surface and explicit ablations for memory/governance and artifact policy.

**Primary risks:** MEX and Ponytail benefits may depend on agent compliance rather than automatic runtime behavior; artifact minimization can under-build; SigMap must not be combined with another retrieval authority in the same run.

**Phase 2 ablation:** Lowfat+SigMap, Lowfat+SigMap+MEX, Lowfat+SigMap+MEX+Ponytail.

**Downgrade criteria:** MEX does not reduce rediscovery, Ponytail causes under-solved tasks, or SigMap does not reduce broad reads.

### Hypothesis 15: Lightweight hook and memory stack

**Components:** `Snip + Serena + Cavemem`

**Target workload:** existing Claude/Codex-like workflows that need shell-output filtering, language-server-backed source intelligence, and compressed memory without broad proxy ownership.

**Owned surfaces:** Snip owns shell-output filtering. Serena owns code retrieval and editing through language-server-backed tools. Cavemem owns compressed memory.

**Compatibility rationale:** the stack keeps intervention narrow and avoids broad context/proxy ownership, making it a useful comparator for heavier graph and memory systems.

**Primary risks:** language-server setup and project support can vary; Cavemem may inject stale observations; Snip can miss unsupported command forms.

**Phase 2 ablation:** Serena-only, Snip+Serena, Snip+Serena+Cavemem on repeated tasks.

**Downgrade criteria:** retrieval setup is unreliable, memory increases stale context, or shell filtering loses failing diagnostics.

### Hypothesis 16: Replacement-agent evaluation lane

**Components:** `ClawCodex` or `Caveman Code` as replacement runtimes

**Target workload:** cases where replacing the coding agent is acceptable.

**Owned surfaces:** the replacement runtime owns agent loop, tool execution, memory/context, compression/routing, and cost behavior.

**Compatibility rationale:** replacement agents should be evaluated as alternative runtimes, not add-ons to hook stacks.

**Primary risks:** runtime differences confound stack effects; quality may fall if savings come from under-solving; benchmark settings may not generalize.

**Phase 2 ablation:** Codex no-MCP baseline, ClawCodex alone, Caveman Code alone on identical tasks.

**Downgrade criteria:** verifier failure, lower quality score, more correction turns, or savings only from omitted work.

### Hypothesis 17: Installer/orchestrator reproducibility lane

**Components:** `Tokless`, `Maestro Flow`, or `Grace Marketplace`, evaluated in constrained profiles

**Target workload:** reproducible installation, orchestration, workflow state, or governance-specific projects.

**Owned surfaces:** Tokless owns installation/profile wiring; Maestro Flow owns orchestration/context workflow; Grace Marketplace owns GRACE-specific project artifact and verification surfaces.

**Compatibility rationale:** installer/orchestrator tools should not be counted as independent token reducers unless their owned runtime surface is explicitly evaluated.

**Primary risks:** over-installation, hidden hook overlap, workflow overhead, project-specific constraints, and unclear disable/reset behavior.

**Phase 2 ablation:** manual profile versus orchestrated profile with the same selected reducers; orchestration-only tasks for Maestro; GRACE-governed fixtures for Grace Marketplace.

**Downgrade criteria:** generated profiles activate overlapping owners, disable/reset paths fail, or orchestration adds more overhead than it removes.

## Baselines and comparators for Phase 2

| Variant | Components enabled | Purpose | Required metric |
|---|---|---|---|
| `baseline-codex-no-mcp` | Codex CLI workflow with native shell/edit/file operations and no MCP/token-saving add-ons | Establish the practical-agent workflow baseline | Provider token components/total, structured task outcomes, independent quality, isolation |
| `terminal-only` | One of RTK, Lowfat, Snip, TokenJuice, or xcsift for Apple logs | Select the terminal owner before multi-tool stacks | Compact/raw token delta, diagnostic fidelity, raw recovery |
| `retrieval-only` | One of CodeGraph, Cartog, Graphify, Understand-Anything, Serena, SigMap, jcodemunch, CocoIndex Code, Code Review Graph, CognitX CodeGraph, Codescope, or SwarmVault | Isolate retrieval benefit and index overhead | Target localization, follow-up broad reads, billed tokens, index time |
| `memory-only repeated-task` | One of Cavemem, Claude Mem, Total Agent Memory, Dragon-Brain, Memex, Token Savior memory, or LeanCTX memory | Test rediscovery reduction | Stale-context rate, repeated-task token delta, correctness |
| `lower-intervention comparator` | RTK + CodeGraph or RTK + Cartog | Compare simple non-overlapping stacks against broader owners | Same metrics as baseline plus component attribution |
| `graph bakeoff` | Fixed terminal owner plus exactly one retrieval authority | Compare graph/RAG candidates without retrieval overlap | File/symbol hit rate, broad-read reduction, billed tokens |
| `broad-owner comparator` | LeanCTX, Token Savior, Headroom, Claw Compactor, Codescope, SwarmVault, or Memex alone | Test whether single broad ownership beats narrow composition | Task-level savings, raw recovery, reset behavior |
| `installer parity` | Manual profile versus Tokless-installed equivalent profile | Test setup reproducibility rather than token reduction | Generated config diff, install/disable/reset, same task metrics |
| `replacement runtime` | Codex no-MCP baseline versus ClawCodex versus Caveman Code | Test alternative agent runtime trade-offs | Provider token use, structured task outcomes, independent quality |
| `Apple specialized` | xcsift alone, general compactor alone, xcsift+Serena | Test specialized versus general terminal compaction | Diagnostic fidelity, repair success, billed tokens |

## Compatibility exclusions

| Exclusion | Reason |
|---|---|
| Multiple primary retrieval engines in one default run | Duplicate context, stale-index disagreement, and poor attribution |
| LeanCTX plus separate retrieval, memory, and terminal compaction tools without disabled surfaces | LeanCTX can already own broad context surfaces |
| Token Savior plus separate retrieval/memory/Bash compaction tools without profile restrictions | Token Savior is an integrated owner across those surfaces |
| SwarmVault plus Graphify, Memex, Maestro Flow, Codescope, or LeanCTX as unconstrained default | Broad graph/wiki/retrieval/memory/context ownership overlaps |
| Cavemem plus Claude Mem plus Total Agent Memory plus Dragon-Brain plus Memex | Multiple durable-memory authorities create stale and duplicate recall risk |
| RTK plus Lowfat plus Snip plus TokenJuice | Multiple shell compactors can hide diagnostics or break command expectations |
| xcsift plus a general shell compactor on `xcodebuild` output | Apple build output should have one parser/filter owner |
| Headroom plus Claw Compactor or LeanCTX compression | Broad compression owners need separate raw-recovery and task-level validation |
| Context-Mode plus pctx | Both own execution offload/result selection |
| Repomix or Gitingest as default continuous retrieval companion | Repository packing is better suited for snapshots and handoffs than targeted retrieval loops |
| Context Engine as a runtime retrieval owner | Its inspected repository contains skill/static-site code rather than a runtime MCP/indexer implementation |
| Tokless as a token-saving component by itself | Its source-logic dossier supports installer/orchestrator behavior, not an independent reduction runtime |
| Replacement agents plus hook-layer add-on stacks | Replacement runtimes own the agent loop and should be evaluated separately |

## Phase 2 evaluation routing

| Situation | Source-logic hypothesis to evaluate first | Comparator |
|---|---|---|
| General coding with noisy terminal output and code search | RTK + CodeGraph, then RTK + Cartog | Native baseline; terminal-only; retrieval-only |
| Graph/RAG onboarding or architecture questions | Graphify stack, Understand-Anything stack, Cartog stack, SwarmVault owner | Fixed terminal owner plus one retrieval authority |
| Repeated tasks with project memory needs | Cartog + Total Agent Memory; Understand-Anything + Cavemem; Code Review Graph + Claude Mem | Same retrieval stack without memory |
| Broad context ownership | LeanCTX alone; Token Savior alone; Codescope alone; Memex alone | Lower-intervention comparator |
| Broad compression/proxy experiments | Headroom alone; Claw Compactor alone | Terminal-only compactor and Codex no-MCP baseline |
| MCP-heavy tool execution | jcodemunch MCP + pctx + Caveman | jcodemunch-only and pctx-only variants |
| Code review and PR repair | Code Review Graph + Claude Mem + Lowfat | Code Review Graph alone; Codex no-MCP review baseline |
| Apple/Xcode repair | xcsift + Serena + MEX | xcsift-only; general terminal compactor; xcsift+Serena |
| Installer reproducibility | Tokless manual-parity profile; Maestro Flow orchestration profile | Equivalent manual configuration |
| Replacement-agent trade-off | ClawCodex alone; Caveman Code alone | Native baseline with no add-ons |

## Limitations

- All retained stack candidates are source-logic hypotheses, not benchmark-audit or reproduction findings.
- Provider-reported input, output, cache, and total-token effects have not been measured for these stacks.
- Pass-rate preservation, edit quality, review quality, diagnostic fidelity, and latency have not been reproduced on frozen target workloads.
- The report does not rank tools by stars or popularity. Adoption signals are used only as weak discovery and prioritization inputs.
- Some broad-owner tools may require services, daemons, local databases, or host-specific hooks; Phase 2 must evaluate reset and uninstall behavior.
- Memory tools require stale-context, deletion, privacy, and namespace-isolation checks before any deployment-grade recommendation.
- Retrieval tools require freshness, index cost, and target-localization checks before any claim that they reduce broad reads.
- Terminal compactors require raw-output recovery and failing-diagnostic fidelity checks before any task-level savings claim.
- Replacement agents must be evaluated as full alternative runtimes, not as interchangeable add-ons.

## Next review priorities

1. Run a terminal-owner bakeoff across RTK, Lowfat, Snip, TokenJuice, and xcsift on fixed noisy-output fixtures.
2. Run a retrieval bakeoff with one fixed terminal owner and exactly one retrieval authority per run: CodeGraph, Cartog, Graphify, Understand-Anything, Serena, SigMap, jcodemunch, CocoIndex Code, Code Review Graph, CognitX CodeGraph, Codescope, and SwarmVault where workload-appropriate.
3. Run repeated-task memory ablations for Cavemem, Claude Mem, Total Agent Memory, Dragon-Brain, Memex, Token Savior memory, and LeanCTX memory.
4. Evaluate broad-owner candidates alone before composing them with narrow tools: LeanCTX, Token Savior, Headroom, Claw Compactor, Codescope, SwarmVault, and Memex.
5. Evaluate installer/orchestrator tools for reproducible setup and surface discipline: Tokless, Maestro Flow, and Grace Marketplace.
6. Evaluate replacement-agent runtimes separately from add-on stacks: ClawCodex and Caveman Code.
7. Promote only candidates with inspected harnesses, token accounting, raw outputs, and failure semantics to `benchmark-audit`.
8. Promote only candidates with independent target-workload runs, provider-billed accounting, and software-quality gates to `reproduction`.
