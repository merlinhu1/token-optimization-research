# Beets task qualification backlog

Fixture ID: `medium-beetbox-beets`
Upstream: `beetbox/beets`
Pinned qualification commit: `8ddae794d30e9984be904f80459614155c6592d9`
Language/runtime: Python

This directory is intentionally a qualification backlog, not an active reproduction sequence yet.
Create five task subdirectories only after each task has:

1. a real upstream maintenance/regression source or clearly documented synthetic seed rationale;
2. a seed-regression patch against the pinned qualification commit;
3. a sanitized model-facing prompt that does not reveal issue IDs, fixed commits, or answer paths;
4. `setup.sh`, `reset.sh`, and `verify.sh` that pass standalone and in the ordered persistent workflow;
5. verifier output showing the seeded start state fails and the fixed state passes.

Planned coverage slots:

- task-01: core behavior regression
- task-02: extension/plugin/module behavior regression
- task-03: configuration/schema/validation regression
- task-04: CLI/server/request workflow regression
- task-05: state/cache/lifecycle regression
