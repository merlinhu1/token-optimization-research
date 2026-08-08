#!/usr/bin/env python3
"""Generate the standalone Phase 2 Lifecycle V1 report and SVG figures."""
from __future__ import annotations

import hashlib
import html
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/workflow-sessions.json"
REPORT_PATH = ROOT / "docs/papers/phase-2-lifecycle-v1-natural-use-screening.md"
DATA_PATH = ROOT / "sources/evaluations/audits/phase-2-lifecycle-v1-report-data-20260808.json"
FIGURES = ROOT / "docs/papers/figures"

SEQUENCES = {
    "fastify": "fastify-lifecycle-sequence-v1",
    "beets": "beets-lifecycle-sequence-v1",
}
DISPLAY = {
    "terminal-rtk-codex-instructions-v1": "RTK",
    "terminal-rtk-opencode-plugin-v1": "RTK",
    "retrieval-serena-codex-mcp-v1": "Serena",
    "retrieval-serena-opencode-mcp-v1": "Serena",
    "terminal-tokenjuice-codex-hook-v1": "TokenJuice",
    "terminal-tokenjuice-opencode-plugin-v2": "TokenJuice",
    "artifact-ponytail-codex-plugin-v1": "Ponytail",
    "artifact-ponytail-opencode-plugin-v1": "Ponytail",
    "behavior-caveman-codex-skill-v1": "Caveman",
    "behavior-caveman-opencode-plugin-v1": "Caveman",
    "retrieval-jcodemunch-codex-mcp-v2": "jCodeMunch",
    "retrieval-jcodemunch-opencode-product-v1": "jCodeMunch",
    "retrieval-codegraph-codex-mcp-v1": "CodeGraph",
    "retrieval-codegraph-opencode-mcp-v1": "CodeGraph",
    "retrieval-sigmap-codex-live-v1": "SigMap",
    "retrieval-sigmap-opencode-product-v1": "SigMap",
    "terminal-lowfat-opencode-plugin-v1": "LowFat",
    "integrated-token-savior-codex-product-v2": "Token Savior",
    "retrieval-graphify-codex-skill-v1": "Graphify",
    "retrieval-graphify-opencode-product-v1": "Graphify",
    "integrated-leanctx-codex-hybrid-v1": "LeanCTX",
    "integrated-leanctx-opencode-hybrid-v2": "LeanCTX",
    "terminal-snip-codex-hook-v1": "Snip",
    "terminal-snip-opencode-plugin-v2": "Snip",
    "retrieval-cartog-codex-product-v2": "Cartog",
    "codescope-codex-product-v1": "CodeScope",
    "codescope-opencode-product-v1": "CodeScope",
}
TOOL_ORDER = [
    "RTK", "Serena", "TokenJuice", "Ponytail", "Caveman",
    "jCodeMunch", "CodeGraph", "SigMap", "LowFat", "Token Savior",
    "Graphify", "LeanCTX", "Snip", "Cartog", "CodeScope",
]
TOOL_DISCUSSION = {
    "RTK": (
        "[RTK](../tool-dossiers/rtk-ai-rtk.md) rewrites eligible shell commands through guarded, "
        "command-specific output filters. The runtime split is consistent with integration depth: OpenCode can "
        "apply its native plugin automatically, while the Codex arm depended on routing instructions and included "
        "unsupported `rtk rg` and `rtk sed` forms that passed through. This is a mechanism-consistent inference, "
        "not a causal attribution."
    ),
    "Serena": (
        "[Serena](../tool-dossiers/oraios-serena.md) uses language-server-style MCP tools to retrieve symbols instead "
        "of broad files. Its near-neutral Codex result suggests that retrieval savings approximately balanced the "
        "MCP and trajectory overhead there; the OpenCode reduction is consistent with more effective targeted "
        "retrieval, but the retained runs do not isolate tool uptake from runtime behavior."
    ),
    "TokenJuice": (
        "[TokenJuice](../tool-dossiers/vincentkoc-tokenjuice.md) applies rule-driven command-output reducers through "
        "host hooks or plugins. The OpenCode reduction is consistent with automatic interception reducing terminal "
        "context, while the Codex increase indicates that any filtered output was outweighed by hook, cache, or "
        "trajectory effects in that runtime."
    ),
    "Ponytail": (
        "[Ponytail](../tool-dossiers/dietrichgebert-ponytail.md) changes implementation policy toward smaller, simpler "
        "artifacts rather than compressing an input stream. That can reduce generated code or prose, but its persistent "
        "instructions can also change planning and tool trajectories. The opposite runtime directions therefore fit "
        "activation and trajectory differences better than a uniform compression effect."
    ),
    "Caveman": (
        "[Caveman](../tool-dossiers/juliusbrussee-caveman.md) primarily compresses assistant prose, not shell output or "
        "retrieved code. The Codex trace did not show clear behavioral activation, so fixed guidance and unchanged tool "
        "context could dominate there. The OpenCode reduction is compatible with terser responses or a shorter "
        "trajectory, but the run does not identify which mechanism produced it."
    ),
    "jCodeMunch": (
        "[jCodeMunch](../tool-dossiers/jgravelle-jcodemunch-mcp.md) offers token-budgeted symbol retrieval through a "
        "large MCP schema and installed guidance. The small OpenCode reduction and larger Codex increase are consistent "
        "with fixed schema/guidance overhead being repaid only when retrieval displaces enough native reading; these "
        "runs do not provide a no-guidance or tool-uptake ablation."
    ),
    "CodeGraph": (
        "[CodeGraph](../tool-dossiers/cognitx-leyton-codegraph.md) replaces broad source exploration with bounded graph "
        "queries over a prebuilt Neo4j index. The OpenCode reduction is consistent with focused queries displacing file "
        "reads, whereas the Codex increase suggests that graph instructions, returned context, or extra turns exceeded "
        "the avoided reads."
    ),
    "SigMap": (
        "[SigMap](../tool-dossiers/manojmallick-sigmap.md) exposes signatures, dependency maps, routing, and session "
        "memory. Neither runtime showed a meaningful reduction: the OpenCode result was close to neutral and Codex was "
        "higher. A plausible explanation is that these small tasks were already navigable with native search, leaving "
        "index, MCP, and returned-map overhead without enough displaced context."
    ),
    "LowFat": (
        "[LowFat](../tool-dossiers/zdk-lowfat.md) automatically filters supported command output and preserves raw "
        "failure logs. Its OpenCode reduction is consistent with a narrow automatic layer saving terminal context "
        "without requiring a model retrieval decision. Coverage is limited to supported commands, and no qualified "
        "Codex condition exists for a runtime comparison."
    ),
    "Token Savior": (
        "[Token Savior](../tool-dossiers/mibayy-token-savior.md) combines retrieval, indexing, memory, compact summaries, "
        "and optional Bash rewriting. Its large Codex increase is consistent with a broad multi-surface integration "
        "adding schemas, state, and tool turns faster than it removed context. Because the treatment is integrated, "
        "this screen cannot identify which component drove the increase."
    ),
    "Graphify": (
        "[Graphify](../tool-dossiers/safishamsi-graphify.md) supplies a warm graph plus host-specific skills, instructions, "
        "and plugins. OpenCode's always-on policy can place graph guidance directly on shell calls, which may help explain "
        "its reduction; the Codex increase is consistent with graph and guidance overhead without enough displaced "
        "reading. The cross-runtime contrast remains descriptive."
    ),
    "LeanCTX": (
        "[LeanCTX](../tool-dossiers/yvgude-lean-ctx.md) is a broad hybrid layer spanning MCP retrieval, compressed reads, "
        "search, shell output, memory, and a warm index. Both runtimes used more weighted tokens, consistent with its "
        "multi-surface context and extra interaction costs exceeding any local compression. A component ablation would "
        "be required to distinguish retrieval, shell, and guidance effects."
    ),
    "Snip": (
        "[Snip](../tool-dossiers/edouard-claude-snip.md) rewrites supported shell producers through command-specific "
        "filters. The OpenCode reduction is consistent with effective automatic interception, while the Codex increase "
        "suggests lower rewrite coverage, pass-throughs, or a longer recovery trajectory. The retained evidence does not "
        "separate those possibilities."
    ),
    "Cartog": (
        "[Cartog](../tool-dossiers/jrollin-cartog.md) provides indexed graph navigation and token-bounded task-context "
        "bundles. The Codex increase indicates that indexing guidance, query responses, or longer tool chains exceeded "
        "the broad reads they may have replaced. OpenCode was excluded before provider execution because the pinned "
        "binary failed artifact-identity verification, so that absence is not a performance result."
    ),
    "CodeScope": (
        "[CodeScope](../tool-dossiers/onur-gokyildiz-bhi-codescope.md) combines graph/search tools with large-output "
        "archiving and optional compaction. Its OpenCode result was effectively neutral and Codex was modestly higher, "
        "consistent with bounded retrieval roughly balancing setup, schema, and tool-call overhead in one runtime but "
        "not the other. A near-zero single-run delta should not be read as a stable win."
    ),
}
BASELINE_IDS = {
    ("codex-cli", "fastify"): "baseline-fastify-20260802-p-72ac148f730b-r0",
    ("codex-cli", "beets"): "baseline-beets-20260802-p-d8cfc5066f76-r0",
    ("opencode-cli", "fastify"): "opencode-fastify-20260802-p-72ac148f730b-r1",
    ("opencode-cli", "beets"): "opencode-beets-20260802-p-d8cfc5066f76-r1",
}
BLOCKED = [
    {
        "tool": "LowFat",
        "runtime": "Codex",
        "status": "blocked before provider execution",
        "reason": "No qualified native Codex integration; no PATH-only or generic adapter substitution.",
    },
    {
        "tool": "Token Savior",
        "runtime": "OpenCode",
        "status": "blocked before provider execution",
        "reason": "No qualified native OpenCode integration; no generic adapter substitution.",
    },
    {
        "tool": "Cartog",
        "runtime": "OpenCode",
        "status": "blocked before provider execution",
        "reason": "The pinned native binary did not reproduce the frozen artifact identity; no provider execution was attempted.",
    },
]


def usage(row: dict) -> dict[str, int]:
    source = row["cumulative_token_usage"]
    return {key: int(source.get(key) or 0) for key in (
        "fresh_input_tokens", "cached_input_tokens", "output_tokens",
        "reasoning_tokens", "total_provider_tokens",
    )}


def weighted(tokens: dict[str, int]) -> float:
    return tokens["fresh_input_tokens"] + 0.1 * tokens["cached_input_tokens"] + 6 * tokens["output_tokens"]


def runtime(row: dict) -> str:
    descriptor = row.get("selected_execution", {}).get("descriptor", {})
    return (
        descriptor.get("runtime", {}).get("agent_runtime_id")
        or descriptor.get("agent_condition", {}).get("runtime_id")
    )


def profile_id(row: dict) -> str:
    return row["selected_execution"]["descriptor"]["selected_profile"]["profile_id"]


def sequence_name(row: dict) -> str:
    sequence_id = row["task_sequence"]["sequence_id"]
    for name, value in SEQUENCES.items():
        if sequence_id == value:
            return name
    raise ValueError(f"unexpected sequence: {sequence_id}")


def passed_tasks(row: dict) -> int:
    return sum(1 for item in row.get("per_task_results", []) if item.get("verifier_passed") is True)


def pct(value: float) -> str:
    return f"{value:+.2f}%"


def integer(value: int | float) -> str:
    return f"{int(round(value)):,}"


def one_decimal(value: float) -> str:
    return f"{value:,.1f}"


def dominant_component(row: dict) -> str:
    treatment = row["components"]
    baseline = row["baseline_components"]
    deltas = {
        "fresh input": treatment["fresh_input_tokens"] - baseline["fresh_input_tokens"],
        "cached input × 0.1": 0.1 * (treatment["cached_input_tokens"] - baseline["cached_input_tokens"]),
        "output × 6": 6 * (treatment["output_tokens"] - baseline["output_tokens"]),
    }
    label, value = max(deltas.items(), key=lambda item: abs(item[1]))
    return f"largest component: {label} {value:+,.1f} units"


def tool_result_summary(tool: str, by_tool: dict[tuple[str, str], dict]) -> str:
    results = []
    for runtime_id, display in (("codex-cli", "Codex"), ("opencode-cli", "OpenCode")):
        row = by_tool.get((tool, runtime_id))
        if row:
            results.append(f"{display} {pct(row['weighted_delta_pct'])} ({dominant_component(row)})")
    return f"**Measured outcome:** {'; '.join(results)}."


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_text(x: float, y: float, text: str, size: int = 13, anchor: str = "start", fill: str = "#243447", weight: str = "400") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial,Helvetica,sans-serif" font-size="{size}px" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}">{esc(text)}</text>'


def write_runtime_chart(rows: list[dict]) -> None:
    selected = sorted(rows, key=lambda row: (0 if row["runtime"] == "codex-cli" else 1, TOOL_ORDER.index(row["tool"])))
    width = 1120
    left, right, top = 235, 900, 88
    row_height = 28
    height = top + len(selected) * row_height + 70
    x_min, x_max = -40, 95
    scale = (right - left) / (x_max - x_min)
    zero = left - x_min * scale
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    parts.append('<rect width="100%" height="100%" fill="white"/>')
    parts.append(svg_text(28, 34, "Weighted token-cost change versus matched runtime baseline", 20, weight="700"))
    parts.append(svg_text(28, 58, "Positive values indicate higher weighted usage; negative values indicate lower usage.", 13, fill="#536579"))
    for tick in range(-40, 101, 20):
        x = left + (tick - x_min) * scale
        parts.append(f'<line x1="{x:.1f}" y1="{top-18}" x2="{x:.1f}" y2="{top + len(selected)*row_height}" stroke="#dfe6ee" stroke-width="1"/>')
        parts.append(svg_text(x, top - 27, f"{tick:+d}%", 11, "middle", "#536579"))
    parts.append(f'<line x1="{zero:.1f}" y1="{top-18}" x2="{zero:.1f}" y2="{top + len(selected)*row_height}" stroke="#243447" stroke-width="2"/>')
    for index, row in enumerate(selected):
        y = top + index * row_height
        if index and row["runtime"] != selected[index - 1]["runtime"]:
            parts.append(f'<line x1="28" y1="{y-15}" x2="1060" y2="{y-15}" stroke="#8b98a8" stroke-width="2"/>')
        label = f"{('Codex' if row['runtime'] == 'codex-cli' else 'OpenCode')} · {row['tool']}"
        parts.append(svg_text(left - 12, y + 5, label, 12, "end"))
        value = row["weighted_delta_pct"]
        x_value = zero + value * scale
        x = min(zero, x_value)
        bar_width = abs(x_value - zero)
        fill = "#b94a48" if value >= 0 else "#16807a"
        parts.append(f'<rect x="{x:.1f}" y="{y-9}" width="{max(bar_width,1):.1f}" height="18" rx="3" fill="{fill}"/>')
        anchor = "start" if value >= 0 else "end"
        label_x = x_value + (7 if value >= 0 else -7)
        parts.append(svg_text(label_x, y + 5, pct(value), 12, anchor, fill, "700"))
    parts.append(svg_text(zero, top + len(selected)*row_height + 38, "Matched baseline", 12, "middle", "#536579"))
    parts.append('</svg>')
    (FIGURES / "phase-2-lifecycle-v1-runtime-contrast.svg").write_text("\n".join(parts), encoding="utf-8")


def write_heatmap(rows: list[dict]) -> None:
    by_key = {(row["tool"], row["runtime"]): row for row in rows}
    left, top, cell_w, cell_h = 255, 95, 170, 38
    width, height = 1060, top + len(TOOL_ORDER) * cell_h + 50
    cols = [("codex-cli", "fastify", "Codex\nFastify"), ("codex-cli", "beets", "Codex\nBeets"), ("opencode-cli", "fastify", "OpenCode\nFastify"), ("opencode-cli", "beets", "OpenCode\nBeets")]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    parts.append('<rect width="100%" height="100%" fill="white"/>')
    parts.append(svg_text(28, 34, "Sequence-level weighted token-cost change", 20, weight="700"))
    parts.append(svg_text(28, 58, "The two cells under each runtime show Fastify and Beets; color indicates direction, not statistical significance.", 13, fill="#536579"))
    for index, (_, _, label) in enumerate(cols):
        x = left + index * cell_w + cell_w / 2
        first, second = label.split("\n")
        parts.append(svg_text(x, top - 28, first, 12, "middle", "#243447", "700"))
        parts.append(svg_text(x, top - 12, second, 12, "middle", "#243447", "700"))
    for row_index, tool in enumerate(TOOL_ORDER):
        y = top + row_index * cell_h
        parts.append(svg_text(left - 14, y + 24, tool, 13, "end"))
        for col_index, (runtime, lane, _) in enumerate(cols):
            row = by_key.get((tool, runtime))
            x = left + col_index * cell_w
            if row is None:
                fill = "#eef2f5"
                label = "blocked"
            else:
                value = row["sequence_delta_pct"][lane]
                intensity = min(abs(value) / 70, 1)
                if value >= 0:
                    fill = f"rgb({190 + int(45*intensity)},{235 - int(115*intensity)},{228 - int(115*intensity)})"
                else:
                    fill = f"rgb({220 - int(80*intensity)},{242 - int(75*intensity)},{238 - int(60*intensity)})"
                label = pct(value)
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_w-6}" height="{cell_h-5}" rx="4" fill="{fill}" stroke="white"/>')
            parts.append(svg_text(x + (cell_w-6)/2, y + 23, label, 12, "middle", "#243447", "700"))
    parts.append(svg_text(28, height - 27, "Source: current accepted Lifecycle V1 registry; one treatment assignment per product/runtime and sequence.", 11, fill="#536579"))
    parts.append('</svg>')
    (FIGURES / "phase-2-lifecycle-v1-sequence-heatmap.svg").write_text("\n".join(parts), encoding="utf-8")


def write_component_chart(aggregates: dict[str, dict]) -> None:
    width, height = 1000, 420
    left, right, top, bottom = 105, 925, 88, 335
    y_min, y_max = -1_250_000, 1_750_000
    scale = (bottom - top) / (y_max - y_min)
    def y(value: float) -> float:
        return bottom - (value - y_min) * scale
    zero = y(0)
    categories = [("Fresh input", "fresh_delta", "#4f81bd"), ("Cached input × 0.1", "cached_weighted_delta", "#8064a2"), ("Output × 6", "output_weighted_delta", "#c0504d")]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    parts.append('<rect width="100%" height="100%" fill="white"/>')
    parts.append(svg_text(28, 34, "Weighted-cost component differences", 20, weight="700"))
    parts.append(svg_text(28, 58, "Each bar is treatment minus the repeated matched baseline; reasoning is not added separately.", 13, fill="#536579"))
    for tick in (-1_000_000, -500_000, 0, 500_000, 1_000_000, 1_500_000):
        yy = y(tick)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="#dfe6ee" stroke-width="1"/>')
        parts.append(svg_text(left - 10, yy + 4, f"{tick/1_000_000:+.1f}M", 11, "end", "#536579"))
    parts.append(f'<line x1="{left}" y1="{zero:.1f}" x2="{right}" y2="{zero:.1f}" stroke="#243447" stroke-width="2"/>')
    centers = [335, 685]
    for center, runtime_name, runtime_key in zip(centers, ("Codex", "OpenCode"), ("codex-cli", "opencode-cli")):
        parts.append(svg_text(center, bottom + 42, runtime_name, 14, "middle", "#243447", "700"))
        for offset, (label, key, fill) in zip((-72, 0, 72), categories):
            value = aggregates[runtime_key][key]
            x = center + offset - 24
            yy = y(value)
            top_y = min(yy, zero)
            h = abs(yy - zero)
            parts.append(f'<rect x="{x:.1f}" y="{top_y:.1f}" width="48" height="{max(h,1):.1f}" rx="3" fill="{fill}"/>')
            parts.append(svg_text(x + 24, top_y - 7 if value >= 0 else top_y + h + 16, f"{value/1_000_000:+.2f}M", 10, "middle", fill, "700"))
    legend_x = 760
    for i, (label, _, fill) in enumerate(categories):
        x = legend_x + i*75
        parts.append(f'<rect x="{x}" y="{height-30}" width="12" height="12" fill="{fill}"/>')
        parts.append(svg_text(x+16, height-20, label.split()[0], 10, fill="#536579"))
    parts.append('</svg>')
    (FIGURES / "phase-2-lifecycle-v1-component-deltas.svg").write_text("\n".join(parts), encoding="utf-8")


def build_dataset() -> dict:
    raw = REGISTRY_PATH.read_bytes()
    registry = json.loads(raw)
    rows = registry["sessions"]
    by_id = {row["session_id"]: row for row in rows}
    candidates = [
        row for row in rows
        if row.get("session_role") == "individual_tool_treatment"
        and row.get("task_sequence", {}).get("sequence_id") in SEQUENCES.values()
        and (row.get("interpretation", {}).get("usable_for_primary_objective_token_comparison", True))
    ]
    candidate_groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in candidates:
        candidate_groups[(runtime(row), profile_id(row))].append(row)
    paired_keys = {
        key for key, group in candidate_groups.items()
        if len(group) == len(SEQUENCES)
        and {sequence_name(row) for row in group} == set(SEQUENCES)
    }
    treatments = [
        row for row in candidates
        if (runtime(row), profile_id(row)) in paired_keys
    ]
    if len(treatments) % len(SEQUENCES) != 0:
        raise RuntimeError(f"paired V1 treatment selection is not sequence-complete: {len(treatments)} sessions")
    expected_tasks = len(treatments) * 3
    if sum(passed_tasks(row) for row in treatments) != expected_tasks:
        raise RuntimeError(f"V1 task acceptance count changed; expected {expected_tasks} accepted tasks")
    baselines = {
        key: by_id[session_id]
        for key, session_id in BASELINE_IDS.items()
    }
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in treatments:
        grouped[(runtime(row), DISPLAY[profile_id(row)])].append(row)

    condition_rows: list[dict] = []
    for (runtime_id, tool), group in sorted(grouped.items()):
        treatment_components = {key: sum(usage(row)[key] for row in group) for key in usage(group[0])}
        baseline_components = {key: sum(usage(baselines[(runtime_id, sequence_name(row))])[key] for row in group) for key in usage(group[0])}
        sequence_delta = {}
        for lane in SEQUENCES:
            treatment = next(row for row in group if sequence_name(row) == lane)
            baseline = baselines[(runtime_id, lane)]
            sequence_delta[lane] = round(100 * (weighted(usage(treatment)) / weighted(usage(baseline)) - 1), 2)
        treatment_weighted = weighted(treatment_components)
        baseline_weighted = weighted(baseline_components)
        condition_rows.append({
            "runtime": runtime_id,
            "runtime_display": "Codex" if runtime_id == "codex-cli" else "OpenCode",
            "tool": tool,
            "profile_ids": sorted({profile_id(row) for row in group}),
            "session_ids": [row["session_id"] for row in sorted(group, key=sequence_name)],
            "sessions": len(group),
            "accepted_tasks": sum(passed_tasks(row) for row in group),
            "raw_provider_tokens": treatment_components["total_provider_tokens"],
            "weighted_tokens": round(treatment_weighted, 1),
            "baseline_raw_provider_tokens": baseline_components["total_provider_tokens"],
            "baseline_weighted_tokens": round(baseline_weighted, 1),
            "raw_delta_pct": round(100 * (treatment_components["total_provider_tokens"] / baseline_components["total_provider_tokens"] - 1), 2),
            "weighted_delta_pct": round(100 * (treatment_weighted / baseline_weighted - 1), 2),
            "sequence_delta_pct": sequence_delta,
            "components": treatment_components,
            "baseline_components": baseline_components,
        })

    aggregate_rows = {}
    for runtime_id in ("codex-cli", "opencode-cli"):
        selected = [row for row in condition_rows if row["runtime"] == runtime_id]
        treatment = {key: sum(row["components"][key] for row in selected) for key in usage(treatments[0])}
        baseline = {key: sum(row["baseline_components"][key] for row in selected) for key in usage(treatments[0])}
        aggregate_rows[runtime_id] = {
            "runtime_display": "Codex" if runtime_id == "codex-cli" else "OpenCode",
            "conditions": len(selected),
            "sessions": sum(row["sessions"] for row in selected),
            "accepted_tasks": sum(row["accepted_tasks"] for row in selected),
            "treatment": treatment,
            "repeated_baseline": baseline,
            "treatment_weighted": round(weighted(treatment), 1),
            "baseline_weighted": round(weighted(baseline), 1),
            "raw_delta_pct": round(100 * (treatment["total_provider_tokens"] / baseline["total_provider_tokens"] - 1), 2),
            "weighted_delta_pct": round(100 * (weighted(treatment) / weighted(baseline) - 1), 2),
            "fresh_delta": treatment["fresh_input_tokens"] - baseline["fresh_input_tokens"],
            "cached_delta": treatment["cached_input_tokens"] - baseline["cached_input_tokens"],
            "cached_weighted_delta": round(0.1 * (treatment["cached_input_tokens"] - baseline["cached_input_tokens"]), 1),
            "output_delta": treatment["output_tokens"] - baseline["output_tokens"],
            "output_weighted_delta": 6 * (treatment["output_tokens"] - baseline["output_tokens"]),
            "reasoning_delta": treatment["reasoning_tokens"] - baseline["reasoning_tokens"],
        }
    dataset = {
        "schema_version": 1,
        "report_id": "phase-2-lifecycle-v1-natural-use-screening",
        "evidence_snapshot": "2026-08-08",
        "source_registry": {"path": "data/workflow-sessions.json", "sha256": hashlib.sha256(raw).hexdigest()},
        "model_condition": {
            "Codex": "codex-openai-gpt-5-6-sol-high",
            "OpenCode": "opencode-openai-gpt-5-6-sol-high",
        },
        "sequences": list(SEQUENCES),
        "usage_formula": "fresh input + 0.1 * cached input + 6 * output",
        "treatment_condition_count": len(condition_rows),
        "treatment_session_count": len(treatments),
        "accepted_task_count": sum(passed_tasks(row) for row in treatments),
        "conditions": condition_rows,
        "aggregates": aggregate_rows,
        "blocked": BLOCKED,
    }
    return dataset


def report_markdown(data: dict) -> str:
    conditions = data["conditions"]
    by_tool = {(row["tool"], row["runtime"]): row for row in conditions}
    codex = data["aggregates"]["codex-cli"]
    opencode = data["aggregates"]["opencode-cli"]
    codex_base = codex["repeated_baseline"]
    open_base = opencode["repeated_baseline"]
    blocked_lines = "\n".join(f"- **{item['tool']} / {item['runtime']}:** {item['reason']}" for item in BLOCKED)
    if set(TOOL_DISCUSSION) != set(TOOL_ORDER):
        raise RuntimeError("every reported tool must have exactly one discussion entry")
    discussion_lines = "\n\n".join(
        f"#### {tool}\n\n{tool_result_summary(tool, by_tool)} {TOOL_DISCUSSION[tool]}"
        for tool in TOOL_ORDER
    )
    table_lines = []
    for tool in TOOL_ORDER:
        c = by_tool.get((tool, "codex-cli"))
        o = by_tool.get((tool, "opencode-cli"))
        c_tasks = f"{c['accepted_tasks']}/6" if c else "blocked"
        o_tasks = f"{o['accepted_tasks']}/6" if o else "blocked"
        table_lines.append(f"| {tool} | {pct(c['weighted_delta_pct']) if c else '—'} | {pct(o['weighted_delta_pct']) if o else '—'} | {c_tasks} | {o_tasks} |")

    component_lines = []
    for runtime_id, aggregate in (("codex-cli", codex), ("opencode-cli", opencode)):
        treatment = aggregate["treatment"]
        baseline = aggregate["repeated_baseline"]
        treatment_components = {
            "fresh_input": treatment["fresh_input_tokens"],
            "cached_input": 0.1 * treatment["cached_input_tokens"],
            "output": 6 * treatment["output_tokens"],
        }
        baseline_components = {
            "fresh_input": baseline["fresh_input_tokens"],
            "cached_input": 0.1 * baseline["cached_input_tokens"],
            "output": 6 * baseline["output_tokens"],
        }
        component_lines.extend([
            f"| {aggregate['runtime_display']} | Fresh input | {one_decimal(treatment_components['fresh_input'])} | {one_decimal(baseline_components['fresh_input'])} | {one_decimal(treatment_components['fresh_input'] - baseline_components['fresh_input'])} |",
            f"| {aggregate['runtime_display']} | Cached input × 0.1 | {one_decimal(treatment_components['cached_input'])} | {one_decimal(baseline_components['cached_input'])} | {one_decimal(treatment_components['cached_input'] - baseline_components['cached_input'])} |",
            f"| {aggregate['runtime_display']} | Output × 6 | {one_decimal(treatment_components['output'])} | {one_decimal(baseline_components['output'])} | {one_decimal(treatment_components['output'] - baseline_components['output'])} |",
            f"| {aggregate['runtime_display']} | Weighted token cost | {one_decimal(aggregate['treatment_weighted'])} | {one_decimal(aggregate['baseline_weighted'])} | {one_decimal(aggregate['treatment_weighted'] - aggregate['baseline_weighted'])} |",
        ])

    codex_conditions = codex["conditions"]
    opencode_conditions = opencode["conditions"]
    codex_tasks = codex["accepted_tasks"]
    opencode_tasks = opencode["accepted_tasks"]
    codex_reduced = sum(row["runtime"] == "codex-cli" and row["weighted_delta_pct"] < 0 for row in conditions)
    opencode_reduced = sum(row["runtime"] == "opencode-cli" and row["weighted_delta_pct"] < 0 for row in conditions)
    return f"""# Phase 2: Lifecycle V1 natural-use screening of token-saving integrations

## Executive summary

- **Scope:** {data['treatment_condition_count']} matched product/runtime conditions, {data['treatment_session_count']} persistent workflow sessions, and {data['accepted_task_count']} accepted task outcomes across Fastify and Beets.
- **Codex:** {codex_conditions} product profiles used **{one_decimal(codex['treatment_weighted'])} weighted token-cost units**, versus **{one_decimal(codex['baseline_weighted'])}** for repeated bare-Codex baselines: **{pct(codex['weighted_delta_pct'])}**.
- **OpenCode:** {opencode_conditions} product profiles used **{one_decimal(opencode['treatment_weighted'])} weighted token-cost units**, versus **{one_decimal(opencode['baseline_weighted'])}** for the matched no-treatment OpenCode runtime control: **{pct(opencode['weighted_delta_pct'])}**.
- **Correctness:** all {data['accepted_task_count']} accepted V1 tasks passed the active compile-based acceptance checks. Quality and maintainability were diagnostic, not token-eligibility gates.
- **Conclusion:** the screen shows a strong runtime × integration interaction. It does **not** establish a universally effective token-saving product or a stable ranking.

![Weighted token-cost change by runtime and product](figures/phase-2-lifecycle-v1-runtime-contrast.svg)

## Research question

Does assigning a documented token-saving integration reduce **weighted token cost** in a realistic persistent coding workflow, relative to the matched no-treatment condition for the same runtime?

The estimand is assignment to the installed, native product surface under natural use. The evaluator did not require tool calls, minimum uptake, or a passing implementation to retain a token sample.

## Experimental design

| Item | Definition |
|---|---|
| Workflow | Fastify and Beets; feature implementation, behavior-preserving refactor, code review/correction |
| Session model | Three sequential tasks in one persistent agent session |
| Codex condition | Codex CLI, OpenAI GPT-5.6 Sol, `high` reasoning; bare-Codex matched baseline |
| OpenCode condition | OpenCode CLI 1.18.9, OpenAI GPT-5.6 Sol, `high` reasoning; native no-treatment runtime control |
| Treatment policy | Pinned native integration; natural use; no evaluator-forced invocation |
| Primary measure | Weighted token cost |
| Accounting | `fresh input + 0.1 × cached input + 6 × output`; reasoning is an output subset and is not added again |
| Evidence snapshot | {data['evidence_snapshot']}; registry SHA-256 `{data['source_registry']['sha256']}` |

The same two baseline sessions are repeated descriptively across conditions within each runtime. Repetition does not create independent controls. Codex and OpenCode are reported separately because their runtime surfaces, event schemas, and control conditions differ.

## Results

### Aggregate runtime results

| Runtime | Conditions | Treatment sessions | Tasks | Treatment weighted cost | Baseline weighted cost | Weighted change |
|---|---:|---:|---:|---:|---:|---:|
| Codex | {codex_conditions} | {codex['sessions']} | {codex_tasks}/{codex_tasks} | {one_decimal(codex['treatment_weighted'])} | {one_decimal(codex['baseline_weighted'])} | {pct(codex['weighted_delta_pct'])} |
| OpenCode | {opencode_conditions} | {opencode['sessions']} | {opencode_tasks}/{opencode_tasks} | {one_decimal(opencode['treatment_weighted'])} | {one_decimal(opencode['baseline_weighted'])} | {pct(opencode['weighted_delta_pct'])} |

### Product/runtime contrasts

| Product | Codex weighted Δ | OpenCode weighted Δ | Codex tasks | OpenCode tasks |
|---|---:|---:|---:|---:|
{chr(10).join(table_lines)}

Negative values indicate lower treatment usage. The table is descriptive; it is not a stable product ranking.

![Sequence-level weighted token-cost change](figures/phase-2-lifecycle-v1-sequence-heatmap.svg)

### Token accounting decomposition

| Runtime | Component | Treatment | Repeated baseline | Difference |
|---|---|---:|---:|---:|
{chr(10).join(component_lines)}

In Codex, the weighted increase is distributed across fresh input, cached input, and output. In OpenCode, all three components decrease in aggregate; the cached-input reduction contributes most of the weighted reduction.

![Weighted-cost component differences](figures/phase-2-lifecycle-v1-component-deltas.svg)

## Interpretation

### Codex

- {codex_reduced} of {codex_conditions} Codex profiles reduced weighted token cost in this screen.
- These Codex observations are descriptive screening evidence; they do not establish a stable product ranking.

### OpenCode

- {opencode_reduced} of {opencode_conditions} OpenCode profiles reduced weighted token cost in this screen.
- These are OpenCode-native integration observations. They should not be transferred to bare Codex, where the integration surface and trajectory differ.

### Runtime interaction

The Codex aggregate changed by {pct(codex['weighted_delta_pct'])} weighted, while the OpenCode aggregate changed by {pct(opencode['weighted_delta_pct'])}. This is evidence of runtime-specific behavior, not proof that one runtime or product caused the full difference. Prompt serialization, caching, tool routing, command trajectories, and runtime accounting semantics remain potential contributors.

### Per-tool discussion

The measured component differences below identify where weighted cost changed; they do not establish why it changed. Mechanism explanations are source- and trace-grounded hypotheses that would require targeted ablations or replication to become causal claims.

{discussion_lines}

## Blocked combinations

{blocked_lines}

These combinations produced no provider-backed treatment result and are excluded from the treatment totals.

## Limitations

- Each product/runtime condition has one treatment assignment per workflow; there is no within-condition replicate.
- Repeated baselines are descriptive and do not provide {codex_conditions + opencode_conditions} independent control pairs.
- The two workflows cover only TypeScript and Python projects; results may not generalize to other repositories or task families.
- Weighted token cost is the sole outcome reported here. It is a declared accounting convention, not monetary cost.
- The weighted account does not identify which exact prompt, cached context, tool result, or trajectory step produced a difference.
- Compile/verifier success does not establish equal maintainability, correctness outside the tested contracts, latency, CPU cost, memory cost, or operational cost.
- Cross-runtime contrasts are screening evidence. They are not a causal comparison of Codex versus OpenCode.

## Conclusion

Lifecycle V1 shows that token-saving integrations can reduce **weighted token cost** in one runtime and increase it in another. In this screen, {codex_reduced} of {codex_conditions} Codex treatment conditions and {opencode_reduced} of {opencode_conditions} OpenCode conditions were below the matched weighted baseline. The result supports runtime-specific replication and better trajectory instrumentation—not a universal token-saving claim or deployment recommendation.

## Data availability

- Authoritative registry: [`data/workflow-sessions.json`](../../data/workflow-sessions.json)
- Derived report dataset: [`phase-2-lifecycle-v1-report-data-20260808.json`](../../sources/evaluations/audits/phase-2-lifecycle-v1-report-data-20260808.json)
- Cumulative Codex usage audit: [`codex-cumulative-usage-accounting-20260718.json`](../../sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json)
- Compact workflow evidence: [`sources/evaluations/workflow-sessions/`](../../sources/evaluations/workflow-sessions/)
"""


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    data = build_dataset()
    DATA_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    write_runtime_chart(data["conditions"])
    write_heatmap(data["conditions"])
    write_component_chart(data["aggregates"])
    REPORT_PATH.write_text(report_markdown(data), encoding="utf-8")
    print(json.dumps({
        "report": str(REPORT_PATH.relative_to(ROOT)),
        "data": str(DATA_PATH.relative_to(ROOT)),
        "figures": sorted(str(path.relative_to(ROOT)) for path in FIGURES.glob("phase-2-lifecycle-v1-*.svg")),
        "conditions": data["treatment_condition_count"],
        "sessions": data["treatment_session_count"],
        "tasks": data["accepted_task_count"],
    }, indent=2))


if __name__ == "__main__":
    main()
