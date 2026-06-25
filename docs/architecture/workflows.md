# Research Workflows

## Workflow 1: Repository discovery to normalized record

```text
candidate URL
  → source review
  → artifact record
  → claims extracted
  → technique mapping
  → caveats and evidence labels
  → evaluation backlog item
```

Checklist:

1. Inspect README and docs.
2. Record source URLs and review depth.
3. Classify artifact kind.
4. Extract mechanism and scoped claims.
5. Decide whether it is an implementation, bundle, benchmark, measurement tool, primitive, research prototype, or adjacent project.
6. Map implementations to existing technique IDs or propose a new technique.
7. Add caveats and compatibility notes.

## Workflow 2: Technique definition

```text
repeated mechanisms across artifacts
  → proposed atomic technique
  → intervention surface
  → compatibility group
  → quality risks
  → evaluation protocol
```

A new technique is justified only if it has a distinct intervention surface or mechanism. A new bundle is not a new technique.

## Workflow 3: Literature review to evaluation method

```text
paper/framework
  → literature record
  → metrics extracted
  → applicability notes
  → evaluation framework update
```

Literature review is not just summarization. Its output should improve experimental design.

## Workflow 4: Technique evaluation

```text
technique ID
  → protocol
  → workload selection
  → baseline/treatment artifacts
  → run
  → metric record
  → finding
  → taxonomy or paper update
```

Evaluation should preserve both reduced and raw artifacts when possible.

## Workflow 5: Paper section generation

```text
question
  → relevant technique IDs
  → repository/claim IDs
  → evaluation/finding IDs
  → section draft
  → citation/provenance audit
```

Paper prose must be traceable back to internal records.

## Backlog flow

```text
candidate → triaged → reviewed → normalized → needs-evaluation → evaluated → synthesized
```

Do not let `reviewed` masquerade as `evaluated`. A reviewed README claim is not an experimental finding.
