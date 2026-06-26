# Experiment Tool Isolation Policy

## Purpose

Installed or ambient tools must not affect a run unless the active evaluation profile explicitly enables them. This is especially important for host-installed retrieval, compression, memory, and MCP tools.

## Control rule

A run is accepted only if all controls agree:

1. The run record names the active `profile_id` and enabled surfaces.
2. The task directory contains a tool manifest for that profile.
3. The evaluated agent is launched under a lane-specific runtime home/config, not the controller's ambient tool configuration.
4. Preflight artifacts prove that only the lane's allowed tools are visible before the model starts.
5. The transcript and preflight audit finds no forbidden tool calls, MCP servers, hooks, caches, indexes, or memory injections.

## Baseline profile

`baseline-bare-codex` is the current Codex/OpenAI substrate baseline. This baseline is not model-only or tool-free: Codex native shell, plain file operations, git, edits, and verifier commands are allowed. It forbids MCP servers, retrieval/compression/memory/token-saving owners, global Codex instructions, hooks, skills/plugins, and warm indexes.

Agent runtime and model choice are a separate dimension from the tool profile. Current accepted automation is `agent.runtime_id = codex-cli` with OpenAI/Codex usage extraction. A future Claude Opus lane must use its own runtime/model condition, for example `agent.runtime_id = claude-code` plus an Anthropic model condition in `data/evaluation-agent-runtimes.json`; it must not be executed through the Codex runner or merged into Codex/OpenAI tool-effect aggregates.

## Treatment profile

A treatment profile is an additive lane on the same Codex substrate. It enables exactly the named tool or stack from `profile.component_ids` and `setup.tool_permissions.allowed_token_saving_tools`. Individual-tool lanes expose one treatment tool; stack profiles must list each enabled component and owned surface.

## Ambient installed tools

Installed tools do not contaminate a run merely by existing on disk. They contaminate a run if they are exposed to the evaluated agent, called in the transcript, pre-seed indexes or memory, alter shell output, or change setup/reset/verifier behavior.

For Codex-based runs, do not uninstall global tools to create a baseline. Instead launch Codex with a fresh lane-specific `CODEX_HOME`:

- `baseline-bare-codex`: minimal config, no MCP servers, no global `AGENTS.md`, no hooks, no skills/plugins, auth symlink only.
- Treatment lanes: generated config intentionally enables only the MCP/tool server declared by the active tool config, with run-local data/cache/index state.

Current concrete tool configs include LeanCTX and CodeGraph; adding another tool requires a new tool-config entry with command, allowed audit terms, optional env/mounts, prompt guidance, and optional warmup hook.

The controller session may have ambient tools installed, but the evaluated Codex process must not inherit the controller's Codex home, global instructions, MCP config, hooks, skills, plugins, warm indexes, `HOME`, Python user site, XDG directories, or temp directory unless the active profile explicitly enables them. Agent subprocess `HOME`, `PYTHONUSERBASE`, `XDG_CACHE_HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, and `TMPDIR` must live under the fresh lane-specific Codex home.

## Non-MCP terminal-binary lanes

Terminal-binary treatments such as RTK are not MCP lanes. They must use an empty MCP config and expose only the active binary through lane-specific PATH, environment, and Docker mounts.

The preflight PATH and the actual Codex solve shell are separate isolation surfaces. A runner preflight can find a binary while `codex exec` launches commands through a login shell that cannot find it. Container preflight must therefore include a Docker/login-shell probe for the active tool, not only a runner-environment probe.

For Docker-backed Codex solves, mount the pinned treatment binary at its provenance path and also bind the binary into a stable default shell path such as `/usr/local/bin/<tool>`. RTK reruns use `/opt/data/tool-candidates/rtk/target/release/rtk` for provenance and `/usr/local/bin/rtk` for solve-shell availability.

When Codex is invoked with artifact-output flags, the run artifact directory must be mounted writable into the solve container. For example, `codex exec --output-last-message <run_dir>/codex-last-message.txt` is not valid unless `<run_dir>` exists inside the solve container.

Protocol-changing reruns must remove stale lane eval homes and use `--no-skip-accepted`. If a batch is killed because of a harness or isolation defect, its partial output is retained as negative operational evidence but excluded from the final summary; rerun the full planned set after the fix.

## Required run procedure

1. Reset the repository checkout with the task setup/reset script.
2. For Codex-based runs, use `scripts/run_codex_fixture_evaluation.py <planned-run.json>` or produce equivalent artifacts.
3. Create a fresh lane-specific `CODEX_HOME` before each run and do not copy global Codex instructions, hooks, skills, plugins, MCP config, `HOME`, Python user site, XDG directories, temp directories, or package caches except those explicitly allowed by the profile.
4. Save preflight artifacts: `codex-doctor.txt`, `codex-mcp-list.txt`, `codex-effective-config.toml`, and `codex-home-manifest.json`.
5. Save the full agent event stream and final response.
6. Save verifier output, final diff, and git status.
7. Run `python3 scripts/audit_tool_isolation.py <run-record.json> <events.jsonl> <codex-mcp-list.txt> <codex-effective-config.toml> <prompt.md>` before accepting the run.

## Exclusion rule

If a Codex no-MCP baseline transcript or preflight artifact contains `lean-ctx`, `mcp_lean_ctx`, `ctx_read`, `ctx_search`, `ctx_shell`, `codegraph`, `serena`, or another forbidden treatment surface, the run is marked `excluded`. Do not try to repair it by editing the transcript. Rerun under a fresh lane-specific runtime home instead.
