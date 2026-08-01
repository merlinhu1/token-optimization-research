# Baseline V5 compile-only code-review correction task

The affected component contains a partial code-review correction change that no longer compiles. A proposed change is already present in the working tree; correct it rather than merely describing the problem.

Find the affected production code, inspect relevant definitions and usages, and restore compilation. Search and inspect the repository as needed. Choose the smallest reasonable repair, but do not assume an exact source shape is required. Do not modify tests, generated files, dependency locks, or evaluation controls.

Compilation is the only acceptance gate. Unit-test results, style, behavioral fidelity, and source-review quality are diagnostics only and do not determine pass/fail.

Use this command to check the affected component:

```bash
node --check fastify.js && node --check lib/errors.js
```

Stop when the command exits 0. Do not run network-dependent commands.
