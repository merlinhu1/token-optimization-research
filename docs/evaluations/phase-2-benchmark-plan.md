# Phase 2 benchmark and evaluation plan

## Objective

Phase 2 converts Phase 1 source-logic candidates into benchmark-audited and partially reproduced evidence. The goal is not to discover more tools. The goal is to determine which compatibility-safe stacks produce provider-billed savings while preserving software quality on defined task classes.

## Inputs from Phase 1

- 29 source-logic tool dossiers.
- No remaining lead-only backlog entries.
- Compatibility-safe surface model.
- Phase 1 candidate stacks and replacement-agent lane.
- Existing benchmark examples in cited repositories, including tokbench, agentic-token-bench, CodeGraph benchmarks, Token Savior tsbench, Caveman Code MicroBench, Ponytail task benchmark, Headroom/Tokbench pilot results, and terminal-output reducer examples.

## Phase 2 tracks

| Track | Output | Promotion target |
|---|---|---|
| Benchmark-audit | Inspect existing harnesses, tasks, scoring, token accounting, raw outputs, and failure semantics. | Promote selected dossiers to `benchmark-audit`. |
| Evaluation harness | Define tasks, fixtures, run records, usage schema, and quality rubric. | Create immediately usable reproduction flows. |
| Stack reproduction | Run baseline and selected treatments on the same tasks with provider-billed accounting. | Promote validated stack evidence toward `reproduction`. |

## Prioritized components for benchmark-audit

| Surface | Components | Audit focus |
|---|---|---|
| Terminal/tool-output compaction | RTK, Lowfat, Snip, TokenJuice, xcsift, Headroom terminal modes | command coverage, raw fallback, failing-output fidelity, operation-to-task translation. |
| Retrieval/context | Serena, SigMap, CodeGraph, jcodemunch MCP, Claude Context, LeanCTX retrieval, CocoIndex Code | query quality, freshness, index cost, tool-call overhead, edit-target success. |
| Memory/reinjection | Cavemem, Claude Mem, MEX, Token Savior memory, LeanCTX memory | rediscovery reduction, stale-context rate, project/session scoping, reset path. |
| Broad compression/proxy | Headroom, Claw Compactor, LeanCTX, Token Savior, Kompact-style references | schema/code fidelity, raw recovery, request versus task billing, turn inflation. |
| Replacement runtime | ClawCodex, Caveman Code | agent loop, routing defaults, memory/compression defaults, benchmark harness validity, baseline parity. |
| Installer/orchestrator | Tokless | profile reproducibility, non-overlap enforcement, disable/reset behavior, generated config audit. |

## Initial stack reproduction portfolio

Run baselines plus a small set of treatments before expanding.

| Profile ID | Stack/profile | Reason |
|---|---|---|
| `baseline-native-agent` | Native Claude/Codex-style workflow without token-saving add-ons | Required comparator. |
| `baseline-rtk-codegraph` | RTK + CodeGraph | Lower-intervention legacy baseline. |
| `balanced-addon` | Lowfat + SigMap + MEX + Ponytail | General multi-surface candidate. |
| `light-hook-memory` | Snip + Serena + Cavemem | Lightweight existing-agent candidate. |
| `broad-context-owner` | LeanCTX alone, then LeanCTX + Ponytail | Single broad owner hypothesis. |
| `integrated-mcp-owner` | Token Savior MCP profile | Single integrated MCP owner hypothesis. |
| `replacement-clawcodex` | ClawCodex | Replacement-agent lane. |
| `replacement-caveman-code` | Caveman Code | Replacement-agent lane. |
| `tokless-profile` | Tokless-installed selected non-overlapping profile | Installer reproducibility test, not extra reduction layer. |

## Task classes

| Task class | Token-waste target | Minimum verifier |
|---|---|---|
| Noisy test failure repair | Long failing test logs and repeated reruns. | The failing test passes; no unrelated tests regress. |
| Build/typecheck repair | Compiler/typechecker output and code navigation. | Build/typecheck passes. |
| Large-codebase navigation | Avoid broad file reads while locating relevant symbols. | Correct file/function identified and task-specific question answered. |
| Multi-file refactor | Retrieval precision and edit quality. | Tests pass and diff matches required behavior. |
| Memory rediscovery | Reuse project conventions across repeated tasks. | Correct convention applied without re-reading full docs. |
| MCP/tool-heavy workflow | Large intermediate tool traces and offloaded execution. | Final answer or generated artifact passes verifier; intermediate trace stays outside main context. |
| Apple build repair | xcodebuild/SPM output compaction. | Build/test issue is correctly localized; fix passes where environment permits. |
| Replacement-agent coding task | Runtime-level token/cost/quality trade-off. | Same verifier across baseline and replacement agents. |

## Run design

1. Freeze repository fixture and task prompt.
2. Run native baseline with usage capture enabled.
3. Reset repository and tool state.
4. Install or activate one treatment profile.
5. Run the same task with the same model/provider where possible.
6. Capture transcript, usage, tool logs, raw artifacts, transformed artifacts, and verifier output.
7. Score software quality using the standard rubric.
8. Record result in `data/evaluations.json` and store raw artifacts under `sources/evaluations/<evaluation-id>/`.

## Minimum acceptance criteria for a stack to advance

A stack can be described as Phase 2 positive only if:

- provider-billed task tokens or cost improve versus baseline, or the report explains a non-cost benefit such as quality or latency;
- deterministic verifier passes or quality score is at least 3;
- turn count and tool-call count do not erase the operation-level savings without explanation;
- no overlapping surface owner is active unintentionally;
- install, disable, and reset paths are documented;
- negative or failed runs are retained in the evidence record.

## Immediate first experiments

1. Audit and reproduce one terminal-output compactor on a noisy failing-test fixture.
2. Audit and reproduce one retrieval stack on a large-codebase navigation fixture.
3. Run `baseline-native-agent`, `balanced-addon`, and `light-hook-memory` on the same small coding task.
4. Run ClawCodex and Caveman Code on a separate replacement-agent fixture using the same verifier.
5. Test one Tokless-installed non-overlapping profile and compare generated config to the manually specified profile.
