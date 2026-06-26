# Researcher Prompt

Research token-saving tools for AI coding agents. README inspection is not sufficient for qualified claims. For each important candidate, inspect the README, relevant docs, installer/config/plugin files, hook/MCP/runtime source, tests, and benchmark harnesses as far as the session allows. Persist partial findings in a dossier under `docs/tool-dossiers/` and update `data/tool-analysis-backlog.json` when deeper review remains.

Extract mechanism, claimed savings, evidence type, caveats, compatible/conflicting techniques, review level, source files inspected, runtime behavior, failure modes, and source URLs. Do not treat bundled stacks as atomic techniques.

When constructing stacks, avoid duplicate or near-duplicate combinations split only by target agent name. Select distinct combinations by workload and surface ownership. Repository reputation and star count should have low weight at stack-construction time because reputation is already used during discovery and dossier prioritization; prefer compatibility, dossier review depth, mechanism fit, and operational boundaries.

Return a repository-entry draft matching `templates/repository-entry.md`, update or propose a dossier matching `templates/tool-dossier.md`, and suggest technique mappings from `data/techniques.json`.
