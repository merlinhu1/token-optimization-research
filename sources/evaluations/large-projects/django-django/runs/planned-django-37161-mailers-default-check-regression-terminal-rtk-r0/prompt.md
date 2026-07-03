# Evaluation isolation contract

You are running inside the `terminal-rtk` treatment lane for RTK. Tool-state condition: `cold`. Tool-use policy: `optional`. RTK is available as an optional terminal/tool-output compaction proxy. Use `rtk <command>` for git, test, build, and search commands when it is likely to reduce terminal output without hiding required diagnostics; otherwise use Codex native shell commands. Do not use other retrieval, compression, memory, or token-saving tools. Work only inside the target repository and use the verifier as the acceptance gate.

---

You are repairing a real issue-derived regression in django/django.

Issue source: #37161
Task: Repair Django system checks so malformed MAILERS settings warn when the default mailer alias is absent.

The repository has already been checked out at the pinned fixed upstream commit and then seeded with a regression that removes the relevant production fix. Do not look for a toy one-line answer; this is intentionally a multi-file large-project task.

Constraints:
- Work only inside the fixture repository.
- Use the verifier below as the acceptance gate.
- Prefer the smallest maintainable production-code change that restores the real upstream behavior.
- Do not modify tests unless you can justify that the upstream test itself is wrong.
- Preserve project style and existing public APIs.

Complexity note: Requires wiring a new check through the checks package and registry rather than patching one validation function.

Verifier:
PYTHONPATH=. python tests/runtests.py check_framework.test_mail --verbosity 2
