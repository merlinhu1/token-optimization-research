# First Round Experiment Runbook

## Scope

Round 1 uses the active large-project Django and Terraform task set under this directory.

The treatment framework is tool-agnostic: each additive Codex lane declares one active token-saving tool, a `tool_state`, and a `tool_use_policy`. The runner maps the declared tool to its MCP config, isolated data directory, prompt guidance, optional warmup hook, and isolation audit allowances.

## Required lanes

For every task, run these primary lanes as separate planned records or explicit CLI overrides:

1. `baseline-codex-no-mcp` — Codex substrate, no MCP/retrieval/token-saving tools.
2. One primary treatment lane for the active tool, normally `tool_state = cold` and `tool_use_policy = optional`.

Warm-state optional variants are calibration lanes. Mark them with `evaluation_protocol.calibration_only = true`; the batch runner skips them unless `--include-calibration` is passed.

## Run order

Use paired task order, but complete a trusted baseline before treatment comparisons:

1. Containerized baselines for all tasks.
2. Containerized primary treatment lane for all tasks.
3. Calibration lanes only on a capped sentinel subset, for example:

```bash
python3 scripts/run_codex_evaluation_batch.py \
  --include-calibration \
  --calibration-limit-per-profile 2 \
  --execution-backend docker \
  --docker-image token-eval-codex:latest
```

Do not compare warm treatment results against a stale or host-only baseline. If the baseline was not containerized, rerun it before reporting container-grade conclusions.

## Container requirement

Codex reproduction runs require the Docker backend by default:

```bash
docker build \
  -f sources/evaluations/large-projects/container/Dockerfile \
  -t token-eval-codex:latest \
  .

python3 scripts/run_codex_evaluation_batch.py \
  --glob 'sources/evaluations/large-projects/*/runs/planned/*baseline-codex-no-mcp-r0.json' \
  --output sources/evaluations/large-projects/baseline-codex-no-mcp-container-summary.json \
  --execution-backend docker \
  --docker-image token-eval-codex:latest \
  --build-docker-image \
  --timeout 2700 \
  --no-skip-accepted
```

Host execution requires `--execution-backend host --allow-host-eval` and must be labeled diagnostic-only.

## Warm-state commands

Warm planned records carry `evaluation_protocol.tool_state = warm-index`. The runner performs the active tool's configured warmup hook after task setup and before Codex. Examples include `lean-ctx index build <target repo>` for LeanCTX and `codegraph init <target repo>` for CodeGraph.

The runner records:

- `evaluation-protocol.json`
- `<tool>-warmup-output.txt`
- `<tool>-warmup-metadata.json`
- `tool-warmup-metadata.json`

Warmup wall time, exit code, and output are setup metrics. They are not provider-token usage unless Codex later sees returned tool output in `codex-events.jsonl`.

## Preflight before each run

- Bind exact agent name, version, model, provider, temperature/determinism setting, max turns, and time budget in the run record.
- Confirm at least 5 GB free under `/opt/data` or set the fixture checkout and dependency caches to a larger external workspace.
- Run the selected planned run through `scripts/run_codex_fixture_evaluation.py <planned-run.json>` for Codex-based execution.
- The runner creates a fresh lane-specific `CODEX_HOME`, isolates agent `HOME`, `PYTHONUSERBASE`, XDG directories, `TMPDIR`, Go caches, and tool data under it, writes the profile-specific Codex config, and captures container/Codex preflight artifacts before the model starts.
- Confirm the baseline or treatment tool manifest matches the active profile; the baseline is Codex no-MCP, not model-only.
- Do not reuse memory, indexes, transcripts, generated profiles, global Codex instructions, hooks, skills, plugins, or MCP config from another run unless the active profile explicitly allows and rebuilds that warm state as part of the run.

## Artifact capture

Create `sources/evaluations/large-projects/<project-id>/runs/<evaluation-id>/` and save:

- `run-record-input.json`
- `evaluation-protocol.json`
- `container-preflight.json`
- `docker-build-output.txt` when `--build-docker-image` is used
- `docker-smoke-output.txt`
- `codex-events.jsonl`
- `codex-last-message.txt`
- `provider-usage.json`
- `provider-usage-extract.txt`
- `setup-output.txt`
- `verifier-output.txt`
- `final.diff`
- `git-status.txt`
- `codex-doctor.txt`
- `codex-mcp-list.txt`
- `codex-effective-config.toml`
- `codex-home-manifest.json`
- `tool-isolation-audit.json`
- `tool-isolation-audit.txt`
- warm/index artifacts when applicable
- `quality-review.md`

Only after these files exist should a compact record be appended to `data/evaluations.json`.

## Acceptance gates

- Container preflight passes for reproduction evidence.
- Verifier exits 0.
- Diff is minimal and fixes the seeded regression only.
- Provider-billed usage is captured when the agent/provider exposes it.
- Tool-isolation audit passes.
- Raw artifacts are recoverable.
- Failed or excluded runs are still recorded with an exclusion reason.

## Known execution caveats

If Docker daemon access is unavailable, the runner now fails before model execution rather than silently falling back to host isolation. Use host mode only for harness debugging, not final comparisons.
