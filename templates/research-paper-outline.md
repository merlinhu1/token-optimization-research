# Research Paper Outline

## Working title

Compatibility-Aware Evaluation of Token-Saving Techniques for AI Coding Agents

## Abstract placeholder

AI coding agents increasingly use context-management middleware, output compactors, repository maps, memory systems, and terse prompting to reduce token usage. Reported savings are difficult to compare because they operate on different buffers and often measure operation-level reductions rather than provider-billed task totals. This paper proposes a compatibility-aware taxonomy and technique-level evaluation framework.

## Outline

1. Introduction
   - Motivation: token limits, cost, latency, and context pollution.
   - Problem: claims are not comparable across scopes.
2. Background
   - AI coding-agent context flows.
   - Token accounting and provider billing.
3. Taxonomy
   - Compatibility-based categories.
   - Bundles vs atomic techniques.
4. Evaluation framework
   - Metrics, controls, quality retention, billing.
5. Catalog study
   - Repository discovery and evidence labels.
6. Technique evaluations
   - Individual experiments by category.
7. Discussion
   - Stackability, hidden overhead, prompt-cache effects, quality failures.
8. Standards and recommendations
   - Reporting checklist for token-saving tools.
9. Limitations
10. Conclusion

## Research assets to cite from this repo

- `data/repositories.json`
- `data/techniques.json`
- `docs/reference/compatibility-taxonomy.md`
- `docs/evaluations/design/framework.md`
