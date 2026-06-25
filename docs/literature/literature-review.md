# Literature Review: Evaluation Techniques for Token Saving

This document tracks research relevant to evaluating token-saving techniques for AI coding agents.

## Review questions

1. How do prompt-compression methods measure semantic retention and downstream task quality?
2. How do retrieval and context-selection papers evaluate code understanding and repair tasks?
3. Which agentic coding benchmarks expose token, cost, latency, and quality trade-offs?
4. How should prompt caching and provider billing be included in evaluations?
5. What metrics detect hidden regressions from missing diagnostics, schemas, or code semantics?

## Initial literature clusters

- **Prompt compression:** LLMLingua, LongLLMLingua, learned prompt compressors, extractive vs abstractive compression.
- **Long-context and retrieval:** context selection, repo maps, RAG evaluation, chunking, reranking, code navigation.
- **Coding-agent benchmarks:** SWE-bench-style repair, CLI agent benchmarks, deterministic task validators.
- **Cost and token accounting:** provider-billed usage, prompt caching, session logs, cache alignment.
- **Quality retention:** semantic similarity, exact code preservation, structured-output validity, diagnostic completeness.

## Paper matrix

Populate `data/literature.json` first, then summarize mature clusters here.
