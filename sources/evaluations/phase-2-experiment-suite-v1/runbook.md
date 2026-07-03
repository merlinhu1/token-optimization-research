# Runbook

## One-time materialization

```bash
python3 sources/evaluations/fixture-corpus/v1/materialize.py all
```

## Per-fixture baseline run

1. Reset the fixture with the registry `reset.command`.
2. Start a native-agent run with the exact text in `tasks/<fixture-id>/agent-prompt.txt`.
3. Capture transcript, provider usage, verifier output, final diff, and environment metadata under `runs/<evaluation-id>/`.
4. Score software quality with the 0-5 rubric.
5. Record the compact run in `data/evaluations.json` only after raw artifacts exist.

## Per-treatment run

1. Reset repository and tool state.
2. Activate exactly one treatment profile from `profile-matrix.md`.
3. Confirm disabled overlapping surfaces before the task starts.
4. Use the same agent prompt, model/provider family, maximum turns, and verifier as the baseline.
5. Preserve failures and negative operational evidence.

## Codex container rerun checklist for non-MCP terminal tools

Use this checklist before rerunning terminal-binary lanes such as `terminal-rtk`.

1. Restore or build the pinned tool binary at the path declared by the runner.
2. Confirm the host shell does not expose the treatment tool globally unless the protocol explicitly allows it.
3. Mount the pinned binary path for provenance and also mount the binary into a stable login-shell path such as `/usr/local/bin/<tool>` inside the solve container.
4. Probe the exact Docker login-shell surface before model execution; runner preflight PATH alone is not sufficient because Codex-launched shells may reset PATH.
5. Mount the run artifact directory writable into the solve container when invoking `codex exec --output-last-message`.
6. Remove stale lane eval homes before a protocol-changing rerun, then run the batch with `--no-skip-accepted`.
7. If a batch reveals a harness or isolation defect, kill that batch and rerun from the start after the fix; do not merge partial pre-fix and post-fix results in one summary.
8. After completion, confirm no `run_codex_evaluation_batch`, `run_codex_fixture_evaluation`, or `codex exec --json` processes remain.

For the RTK lane, the expected active binary is `/opt/data/tool-candidates/rtk/target/release/rtk`, and the solve container must also see it as `/usr/local/bin/rtk`.

Non-JSON lines in `codex-events.jsonl` require inspection, not automatic exclusion. Codex stderr diagnostics such as failed `apply_patch` attempts can appear outside JSON while a valid `turn.completed.usage` block, verifier pass, and isolation audit still make the run usable.

## Smoke checks for fixture readiness

Initial acceptance verifiers are expected to fail for coding-repair fixtures before the agent fixes them. The verifier command is still concrete and ready to run. Non-coding fixtures with artifact-generation tasks fail until the required artifact is produced.

## Aggregate reporting rule

Do not publish a default-owner claim from a single fixture. Aggregate by stratum, report confidence separately for terminal, retrieval, memory, broad-owner, installer, and replacement-runtime lanes, and include negative runs.
