---
name: stack-ablation-planner
description: Use when evaluating a multi-component token-saving stack to isolate surface ownership, component contributions, interactions, and lower-intervention comparators.
---
# Stack Ablation Planner

## Purpose

Prevent multi-tool bundle claims from hiding which component actually helped or harmed. Compatibility-safe stacks must show non-overlapping surface ownership and component-level contribution where feasible.

## When to Use

Use for any stack with two or more components, and for any installer/orchestrator profile that enables multiple tools.

## Procedure

1. List each component and its owned surface:
   - terminal/tool-output compaction;
   - retrieval/context;
   - memory/reinjection;
   - broad compression/proxy;
   - execution offload;
   - behavioral output style;
   - artifact/code minimization;
   - repository packing;
   - replacement runtime;
   - installer/orchestrator.
2. Identify overlap risks:
   - two tools rewriting shell output;
   - two tools auto-injecting memory;
   - broad owner plus narrow add-on fighting over context;
   - replacement runtime combined with add-on assumptions.
3. Define ablations:
   - full stack;
   - baseline;
   - lower-intervention comparator;
   - remove one component at a time when feasible;
   - replace one component with a simpler alternative when feasible.
4. Define interaction checks:
   - does component A hide diagnostics needed by component B?
   - does retrieval reduce broad reads or add tool-call overhead?
   - does memory reduce rediscovery or inject stale state?
   - does behavior control improve brevity or cause under-solving?
5. Treat installer/orchestrator tools separately from reducers.

## Output

Use a table:

| Variant | Components enabled | Owned surfaces | Expected benefit | Expected failure mode | Required metric |
|---|---|---|---|---|---|

## Common Pitfalls

- Calling an installer/orchestrator a token reducer.
- Attributing full-stack savings to every component.
- Combining replacement-agent runtimes with add-on stacks in the same lane.
- Ignoring lower-intervention baselines such as `RTK + CodeGraph`.
