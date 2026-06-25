# Protocol: <change-id>

Write this before collecting results.

## Hypothesis

`<profile or tool>` improves `<metric>` for `<workload>` while preserving `<quality gate>`.

## Evidence stage target

- Target stage: benchmark-audit | reproduction
- Promotion rule:
- Falsification or downgrade rule:

## Task fixture

- Task ID:
- Task class:
- Repository/path:
- Commit or snapshot:
- Dirty-state policy:
- Task prompt path:
- Prompt hash:
- Allowed tools:
- Maximum turns/time:

## Baseline

- Baseline profile ID:
- Agent/model/provider:
- Command or flow:
- Enabled surfaces:
- Reset command:

## Treatment

- Treatment profile ID:
- Components enabled:
- Owned surfaces:
- Disabled overlapping surfaces:
- Install or activation command:
- Disable/reset command:

## Metrics

### Token accounting boundary

Primary boundary: artifact_estimated | request_estimated | provider_billed_request | provider_billed_task | session_total

Required fields:

- fresh input tokens:
- cached input tokens:
- cache-write tokens:
- output tokens:
- reasoning tokens:
- total provider tokens:
- estimated cost:
- measurement source:

### Agent behavior

- turns:
- tool calls:
- correction turns:
- latency:
- raw-output recovery used:

### Software-quality gates

- verifier command:
- expected verifier result:
- diagnostic facts to preserve:
- diff quality rule:
- safety/reversibility checks:
- quality scoring rubric additions:

## Failure and exclusion rules

A run is excluded only when:

-

A run is a valid negative finding when:

-

A run falsifies the hypothesis when:

-

## Raw artifact paths

- Task record:
- Profile record:
- Environment record:
- Transcript:
- Provider usage:
- Verifier output:
- Quality review:
- Raw/transformed artifacts:
