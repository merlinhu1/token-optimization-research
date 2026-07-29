# Baseline V5 compile-only feature implementation task

The affected component contains a partial feature implementation change that no longer compiles.

Find the affected production code, inspect relevant definitions and usages, and restore compilation. Search and inspect the repository as needed. Choose the smallest reasonable repair, but do not assume an exact source shape is required. Do not modify tests, generated files, dependency locks, or evaluation controls.

Compilation is the only acceptance gate. Unit-test results, style, behavioral fidelity, and source-review quality are diagnostics only and do not determine pass/fail.

Use this command to check the affected component:

```bash
export PATH=/opt/data/bin:/opt/data/opt/go/bin:$PATH; GOTOOLCHAIN=auto go test -run '^$' ./internal/policy/callback
```

Stop when the command exits 0. Do not run network-dependent commands.
