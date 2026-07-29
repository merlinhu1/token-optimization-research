# Baseline V5 compile-only behavior-preserving refactor task

The affected component contains a partial behavior-preserving refactor change that no longer compiles.

Find the affected production code, inspect relevant definitions and usages, and restore compilation. Search and inspect the repository as needed. Choose the smallest reasonable repair, but do not assume an exact source shape is required. Do not modify tests, generated files, dependency locks, or evaluation controls.

Compilation is the only acceptance gate. Unit-test results, style, behavioral fidelity, and source-review quality are diagnostics only and do not determine pass/fail.

Use this command to check the affected component:

```bash
uv run --offline --frozen python -m py_compile beets/dbcore/db.py beets/dbcore/query.py
```

Stop when the command exits 0. Do not run network-dependent commands.
