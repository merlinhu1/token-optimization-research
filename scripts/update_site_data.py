#!/usr/bin/env python3
"""Render the public site's measurements from the session registry.

`docs/index.html` draws every chart from one JSON block:

    <!-- generated:site-data -->
    <script type="application/json" id="site-data">...</script>
    <!-- /generated:site-data -->

Hand-typed figures on the site went stale twice, so this generator owns them and `--check`
fails when the checked-in block differs from what the registry implies.

A cell is one product under one agent on one codebase. Its change is the median weighted token
cost of its accepted runs against the median of the same agent's no-add-on control pool. It is
confirmed when it holds at least two runs and the change exceeds that pool's run-to-run band
(max / min - 1), the bar the screening paper applies.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/workflow-sessions.json"
TARGET = ROOT / "docs/index.html"
BLOCK = "site-data"

CONTROL_ROLES = ("baseline", "replacement_runtime")
AGENTS = {
    "claude-code": "Claude Code",
    "codex-cli": "Codex CLI",
    "opencode-cli": "OpenCode",
}
MODELS = {"claude-opus-5": "Claude Opus 5", "gpt-5.6-sol": "GPT-5.6 Sol"}
CODEBASES = {
    "fastify": {"name": "Fastify", "language": "JavaScript"},
    "beets": {"name": "Beets", "language": "Python"},
}
# Profile ids carry the product slug; longer slugs first so "tokenjuice" never matches "token".
PRODUCTS = {
    "token-savior": "Token Savior",
    "tokenjuice": "TokenJuice",
    "jcodemunch": "jCodeMunch",
    "codegraph": "CodeGraph",
    "codescope": "CodeScope",
    "repowise": "RepoWise",
    "graphify": "Graphify",
    "ponytail": "Ponytail",
    "caveman": "Caveman",
    "leanctx": "LeanCTX",
    "cartog": "Cartog",
    "serena": "Serena",
    "sigmap": "SigMap",
    "snip": "Snip",
    "rtk": "RTK",
}


def product_of(profile_id: str) -> str:
    for slug, name in PRODUCTS.items():
        if re.search(rf"(^|-){re.escape(slug)}-", profile_id):
            return name
    raise SystemExit(f"no product name registered for profile {profile_id}")


def pct(value: float, base: float) -> float:
    return round((value / base - 1) * 100, 1)


def band(values: list[float]) -> float | None:
    return round((max(values) / min(values) - 1) * 100, 1) if len(values) >= 2 else None


def median(values: list[float | None]) -> float | None:
    present = [v for v in values if v is not None]
    return statistics.median(present) if present else None


def build() -> dict:
    sessions = json.loads(REGISTRY.read_text())["sessions"]
    usable = [
        s for s in sessions
        if s["interpretation"].get("usable_for_primary_objective_token_comparison") is True
    ]

    def key(s: dict) -> tuple[str, str, str]:
        return (
            s["agent"]["runtime_id"],
            s["task_sequence"]["sequence_id"].split("-")[0],
            s["baseline_pool"]["protocol_fingerprint"],
        )

    controls: dict[tuple, list[dict]] = collections.defaultdict(list)
    treatments: dict[tuple, list[dict]] = collections.defaultdict(list)
    models: dict[str, set[str]] = collections.defaultdict(set)
    for s in usable:
        models[s["agent"]["runtime_id"]].add(
            f"{MODELS.get(s['agent']['model'], s['agent']['model'])} · {s['agent']['reasoning_effort']}"
        )
        if s["session_role"] in CONTROL_ROLES:
            controls[key(s)].append(s["cumulative_token_usage"])
        else:
            treatments[key(s) + (product_of(s["profile"]["profile_id"]),)].append(
                s["cumulative_token_usage"]
            )

    cells = []
    pools_used = set()
    for (agent, codebase, pool, product), runs in sorted(treatments.items()):
        control = controls.get((agent, codebase, pool))
        if not control:
            raise SystemExit(f"{product} on {agent}/{codebase} has no control pool {pool}")
        pools_used.add((agent, codebase, pool))
        c_cost = statistics.median(u["weighted_token_cost"] for u in control)
        c_steps = median([u.get("agent_steps") for u in control])
        c_cps = median([u.get("weighted_token_cost_per_step") for u in control])
        cost_band = band([u["weighted_token_cost"] for u in control])
        steps = median([u.get("agent_steps") for u in runs])
        cps = median([u.get("weighted_token_cost_per_step") for u in runs])
        change = pct(statistics.median(u["weighted_token_cost"] for u in runs), c_cost)
        cells.append({
            "product": product,
            "agent": agent,
            "codebase": codebase,
            "runs": len(runs),
            "change_pct": change,
            "run_change_pct": sorted(pct(u["weighted_token_cost"], c_cost) for u in runs),
            "steps_pct": pct(steps, c_steps) if steps and c_steps else None,
            "cost_per_step_pct": pct(cps, c_cps) if cps and c_cps else None,
            "steps": [c_steps, steps],
            "cost_per_step": [round(c_cps) if c_cps else None, round(cps) if cps else None],
            "confirmed": len(runs) >= 2 and cost_band is not None and abs(change) > cost_band,
        })

    pools = []
    for agent, codebase, pool in sorted(pools_used):
        control = controls[(agent, codebase, pool)]
        costs = [u["weighted_token_cost"] for u in control]
        mid = statistics.median(costs)
        pools.append({
            "agent": agent,
            "codebase": codebase,
            "runs": len(control),
            "band_pct": band(costs),
            "run_offset_pct": sorted(pct(c, mid) for c in costs),
            "steps_band_pct": band([u["agent_steps"] for u in control if u.get("agent_steps")]),
            "cost_per_step_band_pct": band(
                [u["weighted_token_cost_per_step"] for u in control if u.get("weighted_token_cost_per_step")]
            ),
        })

    if len(pools) != len({(p["agent"], p["codebase"]) for p in pools}):
        raise SystemExit("two control pools serve one agent and codebase; the site assumes one")

    tasks_attempted = sum(s["software_quality"]["tasks_attempted"] for s in sessions)
    tasks_passed = sum(s["software_quality"]["tasks_passed"] for s in sessions)
    return {
        "metric": "fresh_input_tokens + 0.1 * cached_input_tokens + 6 * output_tokens",
        "as_of": max(s["date"] for s in usable),
        "agents": [
            {"id": rid, "name": AGENTS[rid], "model": " / ".join(sorted(models[rid]))}
            for rid in AGENTS if rid in models
        ],
        "codebases": [{"id": cid, **meta} for cid, meta in CODEBASES.items()],
        "products": sorted({c["product"] for c in cells}, key=str.lower),
        "pools": pools,
        "cells": cells,
        "totals": {
            "cells": len(cells),
            "confirmed": sum(c["confirmed"] for c in cells),
            "single_run_cells": sum(c["runs"] == 1 for c in cells),
            "treatment_runs": sum(c["runs"] for c in cells),
            "control_runs": sum(p["runs"] for p in pools),
            "tasks_attempted": tasks_attempted,
            "tasks_passed": tasks_passed,
        },
    }


def render() -> str:
    payload = json.dumps(build(), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return f'<script type="application/json" id="site-data">{payload}</script>'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the checked-in block is stale")
    args = parser.parse_args(argv)

    pattern = re.compile(
        rf"(<!-- generated:{BLOCK} -->\n).*?(\n<!-- /generated:{BLOCK} -->)", re.DOTALL
    )
    current = TARGET.read_text()
    if not pattern.search(current):
        raise SystemExit(f"missing <!-- generated:{BLOCK} --> block in {TARGET.relative_to(ROOT)}")
    body = render()
    updated = pattern.sub(lambda m: f"{m.group(1)}{body}{m.group(2)}", current)
    if current == updated:
        return 0
    if args.check:
        print(
            f"{TARGET.relative_to(ROOT)} site data is stale; run scripts/update_site_data.py",
            file=sys.stderr,
        )
        return 1
    TARGET.write_text(updated)
    print(f"updated {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
