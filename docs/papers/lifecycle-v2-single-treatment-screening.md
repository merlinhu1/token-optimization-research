# Lifecycle V2: single-treatment screening of token-saving integrations across three coding-agent runtimes

> **Metric authority.** Every token value in this report is **weighted token cost**
> (`fresh input + 0.1 × cached input + 6 × output`). No raw-token result or secondary token
> metric is used, shown, compared, or ranked. Weighted cost is reported with its two factors —
> agent steps and weighted cost per step — wherever the decomposition carries the finding
> ([ADR 0008](../architecture/decision-records/0008-bounded-task-family-and-cost-decomposition.md)).

> **Evidence status (2026-09-21).** Current. Every number here is reproducible from
> `data/workflow-sessions.json` and the retained artifacts in
> `sources/evaluations/workflow-sessions/`. This report supersedes
> [Phase 2 Lifecycle V1 natural-use screening](phase-2-natural-use-screening.md), whose corpus was
> deleted when V1 was retired and which must not be read as a current finding.

> **Evidence stage:** `reproduction` for every result below. Each is a provider-backed run under a
> content-addressed protocol with retained artifacts.

## Executive summary

- **Scope.** 15 token-saving products measured as single treatments against matched, runtime-native
  controls on two fixtures, under the Lifecycle V2 bounded-defect-repair contract.
- **Coverage is deliberately uneven and is stated everywhere it matters.** Codex carries 15
  products, Claude Code 13, and OpenCode only 3 of its 16 runnable profiles. The Codex and Claude
  Code arms are the result. **The OpenCode arm is a preliminary screen and is labelled as such
  throughout.**
- **The runtime changes the sign of the effect, not merely its size.** In **12 of 26** product-lane
  comparisons measured on more than one runtime, the direction of the effect differs between
  runtimes. A product that reduces weighted token cost on one agent can increase it on another.
- **The fixture changes the sign too.** In **9 of 31** product-runtime pairs, the direction differs
  between the two fixtures of the same runtime.
- **Claude Code is where these products work.** 10 of 13 reduce weighted token cost on both lanes.
  On Codex only 5 of 15 do.
- **Correctness was not traded away in aggregate.** 693 of 726 recorded task outcomes passed their
  controller verifiers. Exceptions are individually attributed rather than averaged away.
- **No universal ranking is established, and none is offered.** Most cells hold a single replicate,
  which is a screen and not an effect estimate.

## What this report does not establish

Read this section before the tables.

- **It is not a leaderboard.** Most product-runtime-lane cells hold **one replicate**. Under
  [ADR 0009](../architecture/decision-records/0009-replicate-counts-are-chosen-not-registered.md) a
  single replicate can support "not worth carrying forward"; it cannot support a ranked effect size.
- **Replicate depth is allocated by result direction, so the deeper arms are a selected sample.**
  Products that screened well were resampled; products that screened badly were not. A deeper arm is
  **not** evidence of a better product.
- **Where ranges overlap at the counts held, the products are indistinguishable** and are reported
  that way rather than ordered ([ADR 0007](../architecture/decision-records/0007-ranked-reporting-and-median-sampling.md)).
- **Mechanism is not isolated.** Interception, retrieval depth, persistent instructions, tool
  schemas and trajectory length are all plausible contributors. This design does not separate them.
- **Cross-runtime effect sizes do not transfer.** The same product measured on two runtimes produces
  two different numbers, and sometimes two different signs. A Claude Code figure is not an estimate
  of the same product's Codex or OpenCode figure.

## Method

- **Task family.** Lifecycle V2: a series of bounded defect repairs, each restoring one named
  behaviour that a specific upstream test already decides, so every task has a closed stopping
  condition and no single task dominates session cost.
- **Fixtures.** Fastify (JavaScript) and Beets (Python), each pinned to an upstream commit and to a
  reproducible prepared-base commit.
- **Sessions.** One persistent agent session per condition carries state across every task. All task
  verifiers and the project-wide compile verifier run once after the final prompt, so hidden gates
  cannot truncate the measured workflow.
- **Prompts.** Compatible baseline and treatment sessions receive identical prompt bytes. Prompts
  state the observable symptom without naming the file, function or test, and never disclose
  controller commands or acceptance policy. Solution-directed task assistance is forbidden.
- **Installation.** Every product is installed through its own author-recommended integration
  surface. Evaluator-authored steering, quotas and forced tool calls are forbidden; product-authored
  guidance is preserved. Natural use only: zero model-issued tool calls is a valid observed outcome.
- **Controls.** Each runtime is measured against its own bare control on the same fixture, prompts,
  model and reasoning effort. Agent runtimes are pinned to a frozen build and hash-verified before
  every spending launch.

### Controls

| Runtime | Control profile | Fastify median | Beets median |
|---|---|---:|---:|
| Codex CLI | `baseline-bare-codex` | 756,956 (n=3) | 589,696 (n=3) |
| Claude Code | `baseline-claude-code-no-mcp` | 640,241 (n=5) | 434,661 (n=6) |
| OpenCode CLI | `runtime-opencode-codex-product-v1` | 1,076,737 (n=2) | 558,808 (n=2) |

The four OpenCode control sessions predating the 2026-09-16 adapter re-pin are **excluded** from
every figure in this report. That re-pin created a new apparatus, and its receipt bars pooling
across it.

## Results

Change in weighted token cost against the matched runtime control on the same fixture. Negative is
cheaper than the control. `n` is the number of retained replicates in that cell.

| Product | Codex Fastify | Codex Beets | Claude Code Fastify | Claude Code Beets | OpenCode Fastify | OpenCode Beets |
|---|---:|---:|---:|---:|---:|---:|
| Cartog | -26.1% (n=1) | +1.4% (n=1) | -14.7% (n=1) | -13.0% (n=1) | — | — |
| Caveman | +9.7% (n=1) | +20.6% (n=1) | -25.0% (n=2) | -32.1% (n=2) | +1.3% (n=1) | +1.3% (n=1) |
| CodeGraph | +3.6% (n=1) | +72.4% (n=1) | +1.1% (n=1) | +3.4% (n=1) | — | — |
| CodeScope | -4.0% (n=1) | -3.1% (n=1) | — | — | — | — |
| Graphify | -26.5% (n=1) | +4.3% (n=1) | -12.8% (n=2) | -29.7% (n=2) | — | — |
| LeanCTX | -24.7% (n=2) | -1.0% (n=2) | -35.4% (n=2) | -39.7% (n=2) | -62.2% (n=2) | -14.2% (n=2) |
| Ponytail | -2.2% (n=1) | +7.6% (n=1) | -23.4% (n=2) | -32.3% (n=2) | -20.7% (n=1) | +13.4% (n=1) |
| RTK | -9.2% (n=1) | -12.7% (n=1) | -14.2% (n=2) | -24.2% (n=2) | — | — |
| RepoWise | -8.4% (n=1) | -0.7% (n=1) | — | — | — | — |
| Serena | +0.8% (n=1) | +19.9% (n=1) | -24.4% (n=2) | -25.8% (n=2) | — | — |
| SigMap | -0.2% (n=1) | +17.9% (n=1) | -18.6% (n=1) | +51.8% (n=1) | — | — |
| Snip | -22.0% (n=1) | -3.7% (n=1) | -21.7% (n=1) | -23.1% (n=1) | — | — |
| Token Savior | -16.8% (n=1) | +3.3% (n=1) | -25.6% (n=2) | -48.1% (n=2) | — | — |
| TokenJuice | -18.6% (n=1) | +0.6% (n=1) | +6.1% (n=1) | -28.9% (n=1) | — | — |
| jCodeMunch | +11.3% (n=1) | +43.0% (n=1) | -11.0% (n=1) | -14.9% (n=1) | — | — |

## Findings

### The runtime decides the direction

Twelve of the twenty-six product-lane comparisons that exist on more than one runtime **change sign**
between runtimes. Caveman costs 9.7% and 20.6% more on Codex, saves 25.0% and 32.1% on Claude Code,
and is indistinguishable from the control on OpenCode. Serena costs more on both Codex lanes and
saves roughly a quarter on both Claude Code lanes. jCodeMunch costs 11.3% and 43.0% more on Codex
and saves 11.0% and 14.9% on Claude Code.

This is the central result, and it is the reason a single-runtime product recommendation is not
supportable from this corpus. The interaction between the integration and the host agent is as large
as the integration itself.

### The fixture decides the direction too

Nine of thirty-one product-runtime pairs change sign **between the two fixtures**, holding the
runtime constant. SigMap on Claude Code saves 18.6% on Fastify and costs 51.8% more on Beets.
TokenJuice on Claude Code costs 6.1% more on Fastify and saves 28.9% on Beets. A product evaluated
on one repository has not been evaluated.

### Claude Code is the runtime where these products pay

Ten of thirteen products reduce weighted token cost on both Claude Code lanes. On Codex only five of
fifteen do — RTK, Snip, LeanCTX, CodeScope and RepoWise — and several products are substantially more
expensive there, CodeGraph reaching +72.4% on Beets.

### LeanCTX is the only product measured on all three runtimes

It reduces cost on every runtime, and by an amount that varies more than threefold: −24.7% and −1.0%
on Codex, −35.4% and −39.7% on Claude Code, −62.2% and −14.2% on OpenCode. Its OpenCode arm carries
the corpus's clearest cost decomposition: weighted cost per step falls far below the control on both
lanes with no overlap, while step count rises, so it buys a cheaper trajectory at the price of a
longer one. How that nets out depends on how expensive the lane's steps were to begin with.

### A measured quality cost, on one runtime only

LeanCTX's OpenCode integration denies the agent's native file tools — its installer reports
`Shadow mode: native tools denied` — and routes all retrieval through its own compressed surface. On
Beets, both replicates lost the same task by making the same wrong edit at the same line, against a
control that passes that task in all four of its replicates. The same product on Codex and Claude
Code, where its integration is additive rather than exclusive, shows no such loss.

This is reported as a reproducible association and **not** as a demonstrated mechanism. A
specification-exposure explanation was examined and does not survive the cross-runtime data. The
measurement that would settle it is a declared ablation: LeanCTX on OpenCode with the native tools
restored.

## The OpenCode arm is preliminary

Three of sixteen runnable OpenCode profiles have been measured: LeanCTX, Ponytail and Caveman.
Thirteen remain unrun, including Serena, CodeGraph, SigMap, Cartog, RepoWise and jCodeMunch. Two of
the strongest products by measured effect elsewhere, Snip and Token Savior, have **no runnable
OpenCode profile at all**, so this arm cannot mirror the Codex sweep even with unlimited budget.

Until those cells exist, no aggregate OpenCode claim should be drawn from this report beyond the
three products named, and the three carry one or two replicates each.

An earlier attempt at the LeanCTX OpenCode cell was invalidated as an apparatus defect: a runner bug
registered the agent runtime itself as the product's MCP server, so the model ran with its native
tools denied and no replacement, and its 1,735,070.4 weighted tokens bought no measurement. It is
disclosed in full and occupies no replicate slot. The bug affected nine tool configurations and is
fixed, which is why the OpenCode arm is young rather than merely small.

## Threats to validity

| Threat | Control |
|---|---|
| Prompt differences between arms | Identical prompt bytes; no requirement or preference for treatment-tool use |
| Telling the agent where to look | Solution-directed assistance forbidden; this retired an earlier task family |
| A model or effort change reusing an incomparable control | Model/effort changes mint new protocol identities |
| Environmental noise charged to the treatment | Fixtures exit zero on a clean prepared base |
| One task dominating session cost | Bounded tasks with closed stopping conditions |
| Rerunning until the number looks right | First valid sample retained; acceptance never gates retention |
| Reduced tool setups flattering a product | Faithful installation of every author-recommended surface |
| An agent CLI auto-updating mid-study | Runtimes pinned to a frozen build, hash-verified before every spending launch |
| An apparatus defect producing a plausible number | Treatment presence established from the model's own tool stream, not a preflight |

## Data availability

- Machine authority: [`data/workflow-sessions.json`](../../data/workflow-sessions.json),
  [`data/evaluation-profiles.json`](../../data/evaluation-profiles.json).
- Retained artifacts, one directory per session: `sources/evaluations/workflow-sessions/`.
- Protocols, content-addressed from the causal descriptor: `sources/evaluations/protocols/`.
- Receipts for invalidations, exclusions and disclosed spend: `sources/evaluations/audits/`.
- Current interpretation and open questions: [research roadmap](../research/roadmap.md).
