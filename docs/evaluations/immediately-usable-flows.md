# Immediately usable evaluation flows

## Directory convention

Create one directory per evaluation run:

```text
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
```

Use `data/evaluations.json` for compact index records. Keep raw logs out of reports unless summarized.

## Flow 1: benchmark-audit an existing repository benchmark

Use this when a cited repository already contains a harness or published results.

1. Identify benchmark files, task definitions, result files, and scoring code.
2. Record whether token accounting is estimated, provider-reported, or product self-reported.
3. Inspect how failed, timed-out, or excluded runs are handled.
4. Inspect whether quality gates are deterministic or subjective.
5. Record baseline parity: same model, same prompt, same allowed tools, same max turns.
6. Decide whether the dossier can move from `source-logic` to `benchmark-audit`.

Output:

- updated dossier benchmark section;
- raw notes under `sources/evaluations/<evaluation-id>/benchmark-audit.md`;
- compact `data/evaluations.json` record with `evidence_stage: benchmark_audit`.

## Flow 2: run a terminal-output compactor micro benchmark

Use this for RTK, Lowfat, Snip, TokenJuice, xcsift, and related reducers.

1. Capture raw command output from a failing test/build fixture.
2. Run the compactor with the same raw output or command.
3. Count raw and transformed tokens with a fixed tokenizer.
4. Check required diagnostics:
   - command exit status;
   - failing file and line;
   - assertion or compiler error;
   - stack frame or diagnostic context;
   - raw-output recovery path.
5. Record artifact reduction and diagnostic preservation.

Minimum pass condition: transformed output reduces estimated artifact tokens and preserves all required diagnostics.

## Flow 3: run a retrieval benchmark

Use this for Serena, SigMap, CodeGraph, jcodemunch MCP, Claude Context, CocoIndex Code, and LeanCTX retrieval.

1. Freeze a repository snapshot.
2. Define navigation questions and edit targets with expected files/symbols.
3. Run each retrieval tool with the same query budget.
4. Record returned files, symbols, token counts, tool calls, latency, and whether the expected target appeared.
5. Score usefulness before any agent sees the result.
6. Run an agent task only after retrieval quality is known.

Minimum pass condition: expected target is returned within the token/tool-call budget and does not require broad full-repository packing.

## Flow 4: run a full stack reproduction

Use this for compatibility-safe stack candidates.

1. Create `profile.md` listing each component, enabled surfaces, disabled overlapping surfaces, install commands, reset commands, and expected generated files.
2. Run the relevant substrate baseline on the task, such as `baseline-codex-no-mcp` for additive Codex treatment experiments.
3. Reset repository and agent state.
4. Activate treatment profile.
5. Run treatment with the same task prompt, model/provider, and turn budget.
6. Capture provider usage, transcript, tool calls, verifier output, and final diff.
7. Apply the quality rubric.
8. Compare provider-billed task totals, turns, tool calls, latency, verifier result, and quality score.

Minimum pass condition: verifier passes and treatment improves at least one primary metric without critical regression.

## Flow 5: run a replacement-agent comparison

Use this for ClawCodex and Caveman Code.

1. Do not install hook-layer token-saving stacks in the replacement-agent lane.
2. Use the same repository fixture and task verifier as the baseline agent.
3. Record runtime defaults: compression, memory, repository map, model routing, caps, and tool execution mode.
4. Run baseline and replacement agents separately from clean state.
5. Compare provider-billed task tokens, pass rate, turns, latency, cost, final diff quality, and failure modes.

Minimum pass condition: replacement runtime passes the same verifier and improves cost, latency, or quality enough to justify the larger trust boundary.

## Flow 6: test a Tokless-installed profile

Use this for installer/orchestrator validation.

1. Define the intended non-overlapping profile before running Tokless.
2. Run Tokless in a disposable agent home or container.
3. Capture generated config, hooks, MCP entries, permissions, plugins, binaries, indexes, and logs.
4. Verify only intended surfaces are enabled.
5. Run the selected profile's smoke test.
6. Run Tokless disable/unwire path and verify cleanup.
7. Compare generated config to the manually specified profile.

Minimum pass condition: Tokless reproduces the selected profile without enabling extra overlapping owners and cleanup leaves no stale hooks or broad permissions.
