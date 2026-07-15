# Lowfat three-lane evaluation

Date: 2026-07-13
Contract audit corrected: 2026-07-14

## Corrected result

The historical Lowfat arm was intentionally frozen as:

> Baseline Codex versus Lowfat v0.8.0 cold CLI, with prompted/preferred documented direct use and at least one model-initiated invocation.

That is a legitimate treatment estimand. Lowfat documents direct usage by prefixing commands with `lowfat`; the evaluator did not invent the interface. The later natural-use principle defines a different future estimand and does not retroactively invalidate the frozen prompted/direct-use arm.

The run-level conclusions are:

| Lane | Recorded provider-token delta | Correct disposition |
|---|---:|---|
| Fastify | +25.92% | Causally ineligible because only the treatment used external retrieval; independently quality-rejected at 3/5. |
| Terraform | +17.47% | Causally ineligible because only the treatment used external retrieval; quality itself was accepted. |
| Beets | +42.25% | Valid one-replicate screening evidence for the historical preferred-direct-use estimand; baseline and treatment quality accepted. |

The Beets result supports a narrow conclusion: under this prompted direct-use policy, Lowfat used 42.25% more provider-reported tokens than its matched baseline in one complete three-task workflow replicate. It is not evidence about Lowfat's native automatic shell integration and is not a general ranking.

## Frozen treatment guidance

All three treatment lanes received this same evaluator-authored first-prompt paragraph:

> You are running inside the terminal-lowfat treatment lane for Lowfat. Tool-state condition: cold-cli. Tool-use policy: preferred. Lowfat is available as a terminal/tool-output compaction proxy. Prefix eligible shell commands with lowfat (for example lowfat git status, lowfat git diff, lowfat npm test) unless full raw output is required for diagnosis; use raw commands when compaction would hide necessary detail. Do not use other retrieval, compression, memory, or token-saving tools. Work only inside the target repository. The controller runs concealed verification after the full task lane; do not inspect or modify evaluation harness files.

Commit `744d8d1` changed the arm from optional to preferred before execution, required at least one model-initiated invocation, and excluded zero-use sessions from that intended arm. The exact prompt bytes remain recoverable from each session's compressed evidence bundle. This means the measured intervention was the entire evaluator-authored preferred-direct-use policy, including unsupported-command pass-through—not native shell integration and not only the compression effect of supported filters.

## Native integration boundary

Pinned Lowfat v0.8.0 exposes two relevant modes:

- **Direct use:** `lowfat git status`, `lowfat ls -la`, and similar prefixes.
- **Automatic shell integration:** `eval "$(lowfat shell-init bash)"` or the corresponding shell, which defines wrappers for commands with configured filters inside recognized agent environments.

The historical lane mounted the binary on `PATH` and prompted direct use. It did not install shell-init or hook integration. Therefore it is valid only for the preferred-direct-use estimand.

A future natural-use Lowfat evaluation must first install and verify the native automatic shell integration. Binary availability alone is not that treatment.

## External-retrieval audit

Treatment-only external retrieval independently invalidates causal comparison in two lanes:

| Lane | Treatment retrieval | Matched baseline retrieval | Disposition |
|---|---:|---:|---|
| Fastify | 4 completed Codex web-search events and 32 completed shell commands containing `curl`, including upstream source/PR retrieval | 0 | Excluded from causal treatment comparison. |
| Terraform | 6 completed Codex web-search events for upstream symbols/PR material | 0 | Excluded from causal treatment comparison. |
| Beets | 0 web-search events and 0 network-client commands | 0 | Isolation-clean. |

This exclusion is independent of prompted/direct-use validity. Archived event streams preserve the evidence.

The legacy `tool_isolation_audit.passed` field covered only its forbidden-command list; it did not audit Codex web retrieval. The canonical registry now labels that narrow scope and records `external_retrieval_audit_passed: false` plus `overall_treatment_isolation_passed: false` for Fastify and Terraform. Frozen run bundles remain unchanged.

## Command coverage

The pinned binary bundles filters for `docker`, `find`, `git`, `grep`, `ls`, and `tree`. Unknown commands pass through.

| Lane | Lowfat prefixes | Covered by bundled filters | Pass-through |
|---|---:|---:|---:|
| Fastify | 406 | 50 | 356 (87.7%) |
| Terraform | 115 | 27 | 88 (76.5%) |
| Beets | 134 | 34 | 100 (74.6%) |
| **Total** | **655** | **111 (16.9%)** | **544 (83.1%)** |

The high pass-through rate limits mechanism attribution but does not invalidate the preferred-direct-use treatment. It shows that the complete prompted policy had little command-family coverage for these workflows.

## Token interpretation

Provider totals were dominated by cached input. Fastify and Terraform used less fresh-input-plus-output than baseline while reporting more total provider tokens because their persistent threads replayed larger context. Beets used more fresh-input-plus-output after additional commands and a large failed test.

These observations explain the recorded totals; they do not repair the retrieval confound in Fastify or Terraform.

## Future contract

Before another Lowfat natural-use run:

1. install native `lowfat shell-init` integration rather than only mounting the binary;
2. verify in the actual model shell that supported commands resolve to Lowfat wrappers;
3. keep Codex web search disabled and model shell networking denied in both arms;
4. fail isolation audit on treatment-only external retrieval;
5. do not add evaluator-authored direct-use guidance to the natural-use arm;
6. retain zero use as a valid natural-use observation;
7. preserve the historical prompted/direct-use protocols unchanged.

The current runs remain evidence under their exact frozen scopes. Later compatible runs add evidence; they are not replacement runs.
