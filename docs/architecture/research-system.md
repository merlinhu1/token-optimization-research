# Research System Decomposition

## System boundary

The system transforms unstructured evidence about token-saving tools into structured research outputs.

```text
External world
  ├─ GitHub repos
  ├─ papers
  ├─ benchmark transcripts
  ├─ docs/blog posts
  └─ seed catalogs
        │
        ▼
Ingestion layer
        │ creates artifact and source-review records
        ▼
Normalization layer
        │ extracts claims and maps implementations to techniques
        ▼
Compatibility layer
        │ creates conflict/stackability/dependency edges
        ▼
Evaluation layer
        │ runs or records experiments against technique protocols
        ▼
Synthesis layer
        │ writes findings, standards, and paper sections
        ▼
Research outputs
```

## Layer responsibilities

### 1. Ingestion layer

Inputs are messy: READMEs, catalog tables, search results, papers, benchmark output, or transcripts. The ingestion layer does **not** decide whether a claim is true. It records:

- what artifact was found;
- where it was found;
- when it was reviewed;
- how deep the review went;
- which source URLs support later extraction.

### 2. Normalization layer

Normalization converts artifact-specific language into project entities:

- repository/product;
- bundle component list;
- atomic technique mapping;
- scoped claims;
- caveats and evidence labels.

This is where “RTK says 60–90%” becomes a claim about `T01-terminal-tool-output-compression`, not a universal saving rate.

### 3. Compatibility layer

Compatibility analysis uses intervention surfaces, not branding. Two tools conflict if they both own or rewrite the same surface, for example:

- two shell-output proxies wrapping the same command;
- two MCP field trimmers rewriting the same JSON response;
- two memory systems injecting overlapping facts as authoritative context.

Different surfaces can stack, but only after integration overhead and quality risks are evaluated.

### 4. Evaluation layer

Evaluation starts with technique protocols, not products. A valid evaluation record names:

- baseline and treatment;
- workload;
- model/agent;
- token accounting method;
- quality gates;
- raw artifact retention policy;
- caveats.

### 5. Synthesis layer

Synthesis produces papers, standards, and prompts from internal records. It should not introduce uncited facts. A paper section should point back to data IDs and evaluation IDs.

## Control loop

Findings can update earlier layers:

```text
Evaluation failure → technique caveat → compatibility edge → paper limitation
New source → repository record → claim → technique mapping → evaluation backlog
```

This loop is intentional. Research output is born from structured repo state, not from free-floating prose.
