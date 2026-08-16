#!/usr/bin/env python3
"""Render registry-derived prose into marked blocks in human-facing documents.

Registry facts -- how many sessions are retained, in what roles, under which sequences and
runtimes -- were previously restated by hand in several documents. That reconciliation was
mandated by AGENTS.md and drifted every time the corpus changed: a corrected task family or a
retired generation silently falsified a paragraph in four places at once, and nothing detected
it.

This generator owns those paragraphs. Each target file marks a region:

    <!-- generated:corpus-summary -->
    ...rendered text...
    <!-- /generated:corpus-summary -->

`--check` fails when a checked-in block differs from what the registries currently imply, so
stale prose is a gate failure rather than something a reader has to notice.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/workflow-sessions.json"
ARCHIVE_ROOT = ROOT / "sources/evaluations/archive"

BLOCK = "corpus-summary"
TARGETS = ("README.md", "sources/evaluations/README.md")

RUNTIME_LABELS = {
    "codex-cli": "Codex CLI",
    "opencode-cli": "OpenCode CLI",
    "claude-code": "Claude Code",
}


def _plural(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def archived_generations() -> list[tuple[str, int]]:
    """Archived generation directories with their retained session counts, oldest first."""
    generations: list[tuple[str, int]] = []
    if not ARCHIVE_ROOT.is_dir():
        return generations
    for path in sorted(ARCHIVE_ROOT.iterdir()):
        registry = path / "workflow-sessions-registry.json"
        if not registry.is_file():
            continue
        try:
            sessions = json.loads(registry.read_text()).get("sessions") or []
        except (OSError, json.JSONDecodeError):
            continue
        generations.append((path.name, len(sessions)))
    return generations


def _spread(values: list[float]) -> float | None:
    """Spread of a sample as a percentage of its smallest member."""
    if len(values) < 2 or min(values) <= 0:
        return None
    return (max(values) - min(values)) / min(values) * 100


def render_decomposition(sessions: list[dict]) -> str:
    """Report weighted cost as steps x cost per step, per sample plan.

    Weighted token cost remains the reported metric. Publishing its two factors is what
    lets a reader see whether a difference came from carrying less context per step or
    from taking fewer steps, and which of the two a given sample is precise enough to
    resolve: per-step cost reproduces closely across replicates, step count does not.
    """
    plans: dict[str, list[dict]] = collections.defaultdict(list)
    for session in sessions:
        usage = session.get("cumulative_token_usage") or {}
        plan = (session.get("sample_plan") or {}).get("plan_id")
        if plan and isinstance(usage.get("agent_steps"), int):
            plans[plan].append(usage)
    if not plans:
        return ""
    parts: list[str] = []
    for plan_id, usages in sorted(plans.items()):
        steps = [float(u["agent_steps"]) for u in usages]
        per_step = [float(u["weighted_token_cost_per_step"]) for u in usages if u.get("weighted_token_cost_per_step")]
        fragment = (
            f"`{plan_id}` holds {_plural(len(usages), 'replicate')} "
            f"({', '.join(str(int(s)) for s in steps)} agent steps"
        )
        step_spread = _spread(steps)
        cost_spread = _spread(per_step) if len(per_step) == len(usages) else None
        if step_spread is not None:
            fragment += f", spread {step_spread:.1f}%"
        fragment += ")"
        if cost_spread is not None:
            fragment += f"; weighted cost per step spread {cost_spread:.1f}%"
        parts.append(fragment)
    return (
        "Weighted token cost decomposes as agent steps times weighted cost per step. "
        + "; ".join(parts)
        + "."
    )


def render_summary() -> str:
    doc = json.loads(REGISTRY.read_text())
    sessions = doc.get("sessions") or []
    archives = archived_generations()

    if not sessions:
        lines = [
            "The active registry holds no provider-backed sessions. A corrected task family "
            "mints new qualification and protocol identities, so the prior corpus is archived "
            "and fresh execution is required before any result claim."
        ]
        if archives:
            detail = "; ".join(
                f"`{name}` ({_plural(count, 'session')})" for name, count in archives
            )
            lines.append(f"Archived generations: {detail}.")
        return "\n\n".join(lines)

    roles = collections.Counter(s.get("session_role") for s in sessions)
    seqs = collections.Counter(s.get("task_sequence", {}).get("sequence_id") for s in sessions)
    runtimes = collections.Counter(s.get("agent", {}).get("runtime_id") for s in sessions)

    role_text = ", ".join(
        f"{count} {label}"
        for label, count in (
            ("baselines", roles.get("baseline", 0)),
            ("replacement-runtime controls", roles.get("replacement_runtime", 0)),
            ("individual-tool treatments", roles.get("individual_tool_treatment", 0)),
            ("stack treatments", roles.get("stack_treatment", 0)),
            ("ablations", roles.get("ablation", 0)),
        )
        if count
    )
    seq_text = ", ".join(f"{count} `{sid}`" for sid, count in sorted(seqs.items()))
    runtime_text = ", ".join(
        f"{RUNTIME_LABELS.get(rid, rid)} {count}" for rid, count in sorted(runtimes.items())
    )

    lines = [
        f"The active registry contains {_plural(len(sessions), 'accepted provider-backed session')}: "
        f"{role_text}. By sequence: {seq_text}. By runtime: {runtime_text}."
    ]
    decomposition = render_decomposition(sessions)
    if decomposition:
        lines.append(decomposition)
    if archives:
        detail = "; ".join(
            f"`{name}` ({_plural(count, 'session')})" for name, count in archives
        )
        lines.append(f"Archived generations: {detail}.")
    return "\n\n".join(lines)


def apply_block(text: str, body: str) -> str:
    pattern = re.compile(
        rf"(<!-- generated:{BLOCK} -->\n).*?(\n<!-- /generated:{BLOCK} -->)",
        re.DOTALL,
    )
    if not pattern.search(text):
        raise SystemExit(f"missing <!-- generated:{BLOCK} --> block")
    return pattern.sub(lambda m: f"{m.group(1)}{body}{m.group(2)}", text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if a checked-in block is stale")
    args = parser.parse_args(argv)

    body = render_summary()
    stale: list[str] = []
    for relative in TARGETS:
        path = ROOT / relative
        current = path.read_text()
        updated = apply_block(current, body)
        if current == updated:
            continue
        if args.check:
            stale.append(relative)
        else:
            path.write_text(updated)
            print(f"updated {relative}")
    if stale:
        joined = ", ".join(stale)
        print(
            f"registry summary is stale in {joined}; run python3 scripts/update_registry_summaries.py",
            file=sys.stderr,
        )
        return 1
    if not args.check:
        print("registry summaries current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
