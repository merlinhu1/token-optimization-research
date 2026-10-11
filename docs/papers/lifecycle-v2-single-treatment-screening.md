# Lifecycle V2: what token-saving tools actually do to weighted token cost

> **Metric authority.** Every value is **weighted token cost**
> (`fresh input + 0.1 × cached input + 6 × output`). No raw-token result is used, shown, compared or
> ranked.

> **Evidence status (2026-10-11).** Final for this phase. Every number is reproducible from
> `data/workflow-sessions.json` and the retained artifacts under
> `sources/evaluations/workflow-sessions/`. Supersedes
> [Phase 2 Lifecycle V1 screening](phase-2-natural-use-screening.md), whose corpus was deleted when
> V1 was retired.

## The result

Fifteen products were measured as single treatments against matched, runtime-native controls on two
fixtures and three coding-agent runtimes: 79 product-fixture-runtime cells, 121 provider-backed
sessions.

**Nine of those 79 cells are supported by two or more replicates whose median clears the
replicate-to-replicate band of the control they are measured against.** Those nine are the result.

| Product | Runtime | Fixture | Change in weighted token cost | Replicates | Control band |
|---|---|---|---:|---:|---:|
| LeanCTX | OpenCode | Fastify | **-64.7%** | 2 | 23.6% |
| LeanCTX | Claude Code | Fastify | **-35.4%** | 2 | 13.7% |
| LeanCTX | Codex | Fastify | **-24.7%** | 2 | 13.0% |
| Token Savior | Claude Code | Fastify | **-25.6%** | 2 | 13.7% |
| Caveman | Claude Code | Fastify | **-25.0%** | 2 | 13.7% |
| Serena | Claude Code | Fastify | **-24.4%** | 2 | 13.7% |
| Cartog | Claude Code | Fastify | **-23.5%** | 2 | 13.7% |
| Ponytail | Claude Code | Fastify | **-23.4%** | 2 | 13.7% |
| RTK | Claude Code | Fastify | **-14.2%** | 2 | 13.7% |

Read plainly: **LeanCTX reduces weighted token cost on the Fastify fixture under all three agents.
Six further products reduce it on Fastify under Claude Code. Nothing is established on the Beets
fixture under any agent, and eight of the fifteen products have no supported cell anywhere.**

Products with no supported cell: CodeGraph, CodeScope, Graphify, RepoWise, SigMap, Snip, TokenJuice,
jCodeMunch. That is *unmeasured*, not *ineffective* — each has readings, none of which met the bar.

## What this does not establish

- **No ranking.** Six of the nine supported cells sit between -14.2% and -25.6% against the same
  control. Ordering products inside that range is not supported.
- **No claim about Beets.** Zero cells survive on either Beets lane. The corpus is single-fixture at
  the supported level, and the gap reflects where replicate depth was spent as much as anything
  about the fixture.
- **No cross-runtime generalisation except for LeanCTX**, which is the only product with supported
  cells on more than one runtime — and all three of those are Fastify.
- **No mechanism.** Interception, retrieval depth, persistent instructions and trajectory length are
  all plausible contributors; this design separates none of them. On OpenCode, several products
  moved cost substantially while the model never invoked them once, so whatever acts is frequently
  below the model-visible command surface.
- **"Runtime" is not an isolated variable.** Codex and OpenCode run gpt-5.6-sol; Claude Code runs
  claude-opus-5. Only the Codex-OpenCode contrast varies the agent alone.

## Why only nine of seventy-nine

Two independent constraints, and both were measured rather than assumed.

### Controls vary more than the effects attributed to products

| Runtime | Fixture | Control replicates | Replicate-to-replicate band |
|---|---|---:|---:|
| Claude Code | Beets | 7 | 54.5% |
| Claude Code | Fastify | 5 | 13.7% |
| Codex | Beets | 3 | 8.8% |
| Codex | Fastify | 3 | 13.0% |
| OpenCode | Beets | 3 | 14.5% |
| OpenCode | Fastify | 4 | 23.6% |

A reading smaller than its control's band cannot be distinguished from that control's own variation.
That disqualifies most of the corpus on its own.

Worse, **the band has widened every time it was tested.** OpenCode Fastify went 16.6% → 23.6% on a
third replicate; Claude Code Beets 44.7% → 54.5% on a seventh; OpenCode Beets 2.2% → 14.5% on a
third, demoting six cells including three that had been supported. The measure is min-to-max, which
is monotonic: adding data can only widen it. **A two-replicate band is not an estimate — it is the
distance between two draws, and it was optimistic in every case tested.** Three of the six control
pools still rest on three replicates or fewer.

### Single replicates do not survive, at any margin

Five of the thinnest single-replicate claims were selected purely by how narrowly they cleared their
control, then given a second replicate. **Four of the five did not survive.**

| Margin at n=1 | Product | Cell | n=1 | n=2 | Outcome |
|---:|---|---|---:|---:|---|
| 1.1x | Ponytail | OpenCode Fastify | -25.8% | -11.3% | **retracted** |
| 1.1x | Cartog | Claude Code Fastify | -14.7% | -23.5% | confirmed |
| 1.3x | Token Savior | Codex Fastify | -16.8% | -1.1% | **retracted** |
| 1.4x | SigMap | Claude Code Fastify | -18.6% | -9.1% | **retracted** |
| 1.6x | Snip | Claude Code Fastify | -21.7% | -12.8% | **retracted** |

The only survivor had the *thinnest* margin and the *widest* margin failed, so the ratio of effect to
control noise carried no predictive power across this range. **No reading resting on one replicate
should be treated as an established effect, at any margin.** 59 of 79 cells rest on one replicate.

Treatment stability is also unpredictable: across the 20 multi-replicate cells it ranges from 1.5%
to 49.0%, and in 9 of 20 the treatment is *less* stable than its own control. A replicate count
records how many draws were taken and never how much they agreed.

## Every reading

`†` marks a reading that does **not** clear its control's band, or rests on a single replicate.
Only unmarked readings are supported.

| Product | Codex Fastify | Codex Beets | Claude Code Fastify | Claude Code Beets | OpenCode Fastify | OpenCode Beets |
|---|---:|---:|---:|---:|---:|---:|
| Cartog | -26.1%† (n=1) | +1.4%† (n=1) | -23.5% (n=2) | -10.9%† (n=1) | -20.8%† (n=1) | +27.5%† (n=1) |
| Caveman | +9.7%† (n=1) | +20.6%† (n=1) | -25.0% (n=2) | -30.5%† (n=2) | -5.2%† (n=1) | +2.4%† (n=1) |
| CodeGraph | +3.6%† (n=1) | +72.4%† (n=1) | +1.1%† (n=1) | +5.9%† (n=1) | -15.1%† (n=1) | -0.9%† (n=1) |
| CodeScope | -4.0%† (n=1) | -3.1%† (n=1) | — | — | -18.4%† (n=1) | +4.9%† (n=1) |
| Graphify | -26.5%† (n=1) | +4.3%† (n=1) | -12.8%† (n=2) | -28.0%† (n=2) | +1.1%† (n=1) | +48.5%† (n=1) |
| LeanCTX | -24.7% (n=2) | -1.0%† (n=2) | -35.4% (n=2) | -38.3%† (n=2) | -64.7% (n=2) | -13.3%† (n=2) |
| Ponytail | -2.2%† (n=1) | +7.6%† (n=1) | -23.4% (n=2) | -30.7%† (n=2) | -11.3%† (n=2) | +13.3%† (n=2) |
| RTK | -9.2%† (n=1) | -12.7%† (n=1) | -14.2% (n=2) | -22.4%† (n=2) | — | +1.7%† (n=1) |
| RepoWise | -8.4%† (n=1) | -0.7%† (n=1) | — | — | — | — |
| Serena | +0.8%† (n=1) | +19.9%† (n=1) | -24.4% (n=2) | -24.1%† (n=2) | -19.0%† (n=1) | -7.8%† (n=1) |
| SigMap | -0.2%† (n=1) | +17.9%† (n=1) | -9.1%† (n=2) | +55.3%† (n=1) | -17.6%† (n=1) | +20.0%† (n=1) |
| Snip | -22.0%† (n=1) | -3.7%† (n=1) | -12.8%† (n=2) | -21.2%† (n=1) | — | — |
| Token Savior | -1.1%† (n=2) | +3.3%† (n=1) | -25.6% (n=2) | -46.8%† (n=2) | — | — |
| TokenJuice | -18.6%† (n=1) | +0.6%† (n=1) | +6.1%† (n=1) | -27.2%† (n=1) | -55.1%† (n=1) | -9.2%† (n=2) |
| jCodeMunch | +11.3%† (n=1) | +43.0%† (n=1) | -11.0%† (n=1) | -12.9%† (n=1) | -4.2%† (n=1) | +11.5%† (n=1) |

## Cost decomposition

[ADR 0008](../architecture/decision-records/0008-bounded-task-family-and-cost-decomposition.md)
requires weighted cost to be published as its two factors, **agent steps times weighted cost per
step**, because a total alone hides which factor a tool moved. For the nine supported cells:

| Product | Runtime | Total | Agent steps | Weighted cost per step | Saving carried by |
|---|---|---:|---:|---:|---|
| LeanCTX | Claude Code | -35.4% | **-14.5%** (69&nbsp;&rarr;&nbsp;59) | **-24.2%** (9,269&nbsp;&rarr;&nbsp;7,026) | both |
| LeanCTX | OpenCode | -64.7% | +4.7% † (139&nbsp;&rarr;&nbsp;146) | **-66.2%** (8,257&nbsp;&rarr;&nbsp;2,792) | cost per step |
| LeanCTX | Codex | -24.7% | **+10.3%** (73&nbsp;&rarr;&nbsp;80) | **-34.6%** (10,825&nbsp;&rarr;&nbsp;7,084) | cost per step (steps rose) |
| Token Savior | Claude Code | -25.6% | -0.7% † (69&nbsp;&rarr;&nbsp;68) | **-25.0%** (9,269&nbsp;&rarr;&nbsp;6,952) | cost per step |
| Caveman | Claude Code | -25.0% | **-25.4%** (69&nbsp;&rarr;&nbsp;52) | +0.4% † (9,269&nbsp;&rarr;&nbsp;9,310) | steps |
| Serena | Claude Code | -24.4% | -10.1% † (69&nbsp;&rarr;&nbsp;62) | **-15.6%** (9,269&nbsp;&rarr;&nbsp;7,821) | cost per step |
| Cartog | Claude Code | -23.5% | -2.9% † (69&nbsp;&rarr;&nbsp;67) | **-21.3%** (9,269&nbsp;&rarr;&nbsp;7,297) | cost per step |
| Ponytail | Claude Code | -23.4% | **-18.1%** (69&nbsp;&rarr;&nbsp;56) | -4.9% † (9,269&nbsp;&rarr;&nbsp;8,816) | steps |
| RTK | Claude Code | -14.2% | -4.3% † (69&nbsp;&rarr;&nbsp;66) | **-10.9%** (9,269&nbsp;&rarr;&nbsp;8,263) | cost per step |

All cells are Fastify. `†` marks a factor whose change does not exceed the control pool's own
replicate-to-replicate spread on that same factor, and which therefore carries no weight:

| Runtime | Control spread, steps | Control spread, cost per step |
|---|---:|---:|
| Claude Code (Fastify) | 10.9% | 5.5% |
| Codex (Fastify) | 10.1% | 10.0% |
| OpenCode (Fastify) | 12.4% | 10.6% |

The factors separate the corpus into two mechanisms. **Caveman and Ponytail save on step count**
and leave cost per step inside its control spread. **Token Savior, Serena, Cartog and RTK save on
cost per step** and leave step count inside its control spread. **LeanCTX under Claude Code is the
only cell that moves both factors.** Under Codex and OpenCode, LeanCTX spends *more* steps and still
wins on the total, because the per-step reduction is large enough to absorb the increase — on
OpenCode, 8,257 to 2,792 per step against a 4.7% rise in steps.

The two factors are medians taken independently, so they do not multiply back to the total exactly;
they are reported as two separate observed quantities, not as a factorisation of one. Four of 145
sessions carry no step telemetry, and both factor medians are computed over the replicates that do;
the totals elsewhere in this report use every retained replicate.

## Coverage

Codex holds 15 products, Claude Code 13, OpenCode 12 of 16 runnable profiles. Four OpenCode profiles
cannot run as declared: RepoWise has no adapter treatment, and LowFat, DCP and SDL-MCP are absent
from PROFILE_META with no matching tool configuration, so `screening-ablation` overstates their
readiness. Snip and Token Savior have no OpenCode profile at all. All four blockers were found at
zero provider spend.

## Task correctness

Task verifiers do not gate token-sample retention, so a replicate whose agent produced a bad repair
still contributes its weighted token cost. That makes correctness something to report rather than
something to filter on, and the distribution matters more than the headline rate.

861 of 894 task outcomes passed. The 33 failures do not spread evenly:

| Where | Failures |
|---|---|
| Claude Code, Beets | 30 |
| OpenCode, Beets | 2 |
| Claude Code, Fastify | 1 |
| Codex, either fixture | 0 |

Twenty of the thirty-three are one task, `beets-membership-query-hashable-v2`, which fails 20 of 35
Claude Code attempts and 0 of 39 Codex and OpenCode attempts. The Claude Code bare control fails it
too, so it is a property of that task under that agent rather than an effect of any product. The
remaining four Claude Code control failures and the two OpenCode Beets failures are likewise spread
across different tasks and different sessions.

The practical consequence is a confound confined to the Beets lanes: a Claude Code Beets replicate
that abandons this task early spends fewer tokens than one that keeps working on it, which inflates
the apparent variance of exactly the lane where nothing clears its control anyway. It is one more
reason the Beets result is reported as absent rather than as null.

## Threats to validity

| Threat | Control |
|---|---|
| Prompt differences between arms | Identical prompt bytes; no requirement or preference for treatment-tool use |
| Telling the agent where to look | Solution-directed assistance forbidden |
| Model or effort change reusing an incomparable control | Model/effort changes mint new protocol identities |
| Per-task budget differing between arms | Enforced at validation; one lane was rejected for it and is receipted |
| Environmental noise charged to the treatment | Fixtures exit zero on a clean prepared base |
| Rerunning until the number looks right | First valid sample retained; acceptance never gates retention |
| Reduced tool setups flattering a product | Faithful installation of every author-recommended surface |
| An agent CLI auto-updating mid-study | Runtimes pinned and hash-verified before every spending launch |
| An apparatus defect producing a plausible number | Treatment presence established from the model's own tool stream, not a preflight |
| Infrastructure faults read as provider behaviour | Host state measured at the time of failure, not inferred from earlier checks |

## Disclosed spend that bought no measurement

Quota exhaustion, provider slowness, a credential defect, an expired token materialised into a file
the runner never read, and a full disk each destroyed lanes during this phase. Every instance is
receipted in `sources/evaluations/audits/` with its spend quantified where telemetry survived and
marked unquantifiable where the kill left none. Two apparatus defects found here — an MCP server
registered as the agent runtime itself, and a one-way credential copy that lets only one lane
succeed per token expiry — invalidated or blocked work and are receipted with what they cost.

## Data availability

- Machine authority: [`data/workflow-sessions.json`](../../data/workflow-sessions.json),
  [`data/evaluation-profiles.json`](../../data/evaluation-profiles.json)
- Retained artifacts, one directory per session: `sources/evaluations/workflow-sessions/`
- Protocols, content-addressed from the causal descriptor: `sources/evaluations/protocols/`
- Receipts for invalidations, exclusions, corrections and disclosed spend: `sources/evaluations/audits/`
- Current interpretation and open questions: [research roadmap](../research/roadmap.md)
