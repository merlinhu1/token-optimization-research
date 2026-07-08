# Evaluation isolation contract

You are running inside the `baseline-codex-no-mcp` control lane. This is a Codex substrate baseline, not a model-only baseline: Codex native shell, file, git, and verifier operations are allowed. Do not use external retrieval, compression, memory, MCP, or token-saving tools. Work only inside the target repository and use the verifier as the acceptance gate.

---

You are repairing a real issue-derived regression in django/django.

Issue source: #36492
Task: Repair boolean exact lookup compilation for databases without native boolean fields while preserving annotation and expression behavior.

The repository has already been checked out at the pinned fixed upstream commit and then seeded with a regression that removes the relevant production fix. Do not look for a toy one-line answer; this is intentionally a multi-file large-project task.

Constraints:
- Work only inside the fixture repository.
- Use the verifier below as the acceptance gate.
- Prefer the smallest maintainable production-code change that restores the real upstream behavior.
- Do not modify tests unless you can justify that the upstream test itself is wrong.
- Preserve project style and existing public APIs.

Complexity note: Requires backend feature/operation behavior and ORM lookup compilation across literal, annotation, Exists, Case, and RawSQL paths.

Verifier:
PYTHONPATH=. python tests/runtests.py lookup.tests.LookupTests.test_exact_booleanfield lookup.tests.LookupTests.test_exact_booleanfield_annotation --verbosity 2
