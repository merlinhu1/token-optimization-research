#!/usr/bin/env python3
"""Generate one cumulative, registry-derived evaluation panel audit."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SEQUENCES = (
    "fastify-lifecycle-sequence-v0",
    "beets-lifecycle-sequence-v0",
    "terraform-lifecycle-sequence-v0",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def weighted_tokens(usage: dict[str, int]) -> float:
    return round(
        usage["fresh_input_tokens"]
        + 0.1 * usage["cached_input_tokens"]
        + 6 * usage["output_tokens"],
        1,
    )


def summed_usage(sessions: list[dict[str, Any]]) -> dict[str, int | float]:
    totals = {
        key: sum(int(session["cumulative_token_usage"][key]) for session in sessions)
        for key in (
            "fresh_input_tokens",
            "cached_input_tokens",
            "output_tokens",
            "reasoning_tokens",
            "total_provider_tokens",
        )
    }
    return {
        "fresh_input_tokens": totals["fresh_input_tokens"],
        "cached_input_tokens": totals["cached_input_tokens"],
        "output_tokens": totals["output_tokens"],
        "reasoning_tokens": totals["reasoning_tokens"],
        "raw_provider_tokens": totals["total_provider_tokens"],
        "weighted_tokens": weighted_tokens(totals),
    }


def pct_delta(value: int | float, baseline: int | float) -> float:
    return round((value / baseline - 1) * 100, 2)


def build_panel(
    root: Path,
    *,
    model_condition_id: str,
    replicate_index: int,
    date: str,
) -> dict[str, Any]:
    registry_path = root / "data/workflow-sessions.json"
    profile_path = root / "data/evaluation-profiles.json"
    sessions = json.loads(registry_path.read_text())["sessions"]
    profiles = {
        profile["id"]: profile
        for profile in json.loads(profile_path.read_text())["profiles"]
    }
    treatments: dict[str, list[dict[str, Any]]] = defaultdict(list)
    sessions_by_id = {session["session_id"]: session for session in sessions}
    for session in sessions:
        if (
            session.get("agent", {}).get("model_condition_id") == model_condition_id
            and session.get("replicate_index") == replicate_index
            and session.get("profile", {}).get("profile_id") != "baseline-bare-codex"
            and session.get("status") == "completed"
            and session.get("interpretation", {}).get("accepted_for_objective") is True
        ):
            treatments[session["profile"]["profile_id"]].append(session)

    rows: list[dict[str, Any]] = []
    baseline_ids: set[str] = set()
    for profile_id, profile_sessions in treatments.items():
        by_sequence = {
            session["task_sequence"]["sequence_id"]: session
            for session in profile_sessions
        }
        if set(by_sequence) != set(SEQUENCES) or len(profile_sessions) != len(SEQUENCES):
            continue
        ordered = [by_sequence[sequence] for sequence in SEQUENCES]
        usage = summed_usage(ordered)
        cited_baselines = {
            session["interpretation"]["comparison_baseline_session_id"]
            for session in ordered
        }
        if len(cited_baselines) != len(SEQUENCES):
            raise ValueError(f"{profile_id} does not cite one baseline per sequence")
        baseline_ids.update(cited_baselines)
        profile = profiles[profile_id]
        slug = profile.get("artifact_slug")
        if not isinstance(slug, str) or not slug:
            raise ValueError(f"{profile_id} is missing artifact_slug")
        rows.append(
            {
                "profile_id": profile_id,
                "artifact_slug": slug,
                "session_ids": [session["session_id"] for session in ordered],
                "workflow_count": len(ordered),
                "accepted_task_count": sum(
                    int(session["software_quality"]["tasks_passed"])
                    for session in ordered
                ),
                "usage": usage,
            }
        )

    if not rows:
        raise ValueError("no complete accepted treatment profiles matched the requested panel")
    baseline_sessions = [sessions_by_id[session_id] for session_id in sorted(baseline_ids)]
    baseline_by_sequence = {
        session["task_sequence"]["sequence_id"]: session
        for session in baseline_sessions
    }
    if set(baseline_by_sequence) != set(SEQUENCES) or len(baseline_sessions) != len(SEQUENCES):
        raise ValueError("panel does not resolve to one shared baseline per workflow")
    ordered_baselines = [baseline_by_sequence[sequence] for sequence in SEQUENCES]
    baseline_usage = summed_usage(ordered_baselines)

    rows.sort(key=lambda row: (row["usage"]["raw_provider_tokens"], row["profile_id"]))
    for rank, row in enumerate(rows, start=1):
        row["raw_delta_vs_baseline_percent"] = pct_delta(
            row["usage"]["raw_provider_tokens"],
            baseline_usage["raw_provider_tokens"],
        )
        row["weighted_delta_vs_baseline_percent"] = pct_delta(
            row["usage"]["weighted_tokens"],
            baseline_usage["weighted_tokens"],
        )
        row["raw_rank"] = rank

    panel_raw = sum(int(row["usage"]["raw_provider_tokens"]) for row in rows)
    panel_weighted = round(sum(float(row["usage"]["weighted_tokens"]) for row in rows), 1)
    repeated_baseline_raw = int(baseline_usage["raw_provider_tokens"]) * len(rows)
    repeated_baseline_weighted = round(float(baseline_usage["weighted_tokens"]) * len(rows), 1)
    compact_date = date.replace("-", "")
    audit_id = f"{model_condition_id}-r{replicate_index}-panel-results-{compact_date}"
    first = rows[0]
    first_session = sessions_by_id[first["session_ids"][0]]
    agent = first_session["agent"]
    return {
        "schema_version": 1,
        "audit_id": audit_id,
        "date": date,
        "source_registry": {
            "path": "data/workflow-sessions.json",
            "sha256": sha256(registry_path),
        },
        "condition": {
            "runtime_id": agent["runtime_id"],
            "model_condition_id": model_condition_id,
            "provider": agent["provider"],
            "model": agent["model"],
            "reasoning_effort": agent["reasoning_effort"],
            "replicate_index": replicate_index,
            "workflows": list(SEQUENCES),
            "primary_metric": "raw_provider_tokens",
            "secondary_metric": "weighted_tokens = fresh input + 0.1 * cached input + 6 * output",
        },
        "profile_count": len(rows),
        "workflow_session_count": len(rows) * len(SEQUENCES),
        "accepted_task_count": sum(int(row["accepted_task_count"]) for row in rows),
        "baseline": {
            "profile_id": "baseline-bare-codex",
            "session_ids": [session["session_id"] for session in ordered_baselines],
            "usage": baseline_usage,
        },
        "results_ranked_by_primary_metric": rows,
        "descriptive_panel_aggregate": {
            "treatment_raw_provider_tokens": panel_raw,
            "repeated_baseline_raw_provider_tokens": repeated_baseline_raw,
            "raw_delta_percent": pct_delta(panel_raw, repeated_baseline_raw),
            "treatment_weighted_tokens": panel_weighted,
            "repeated_baseline_weighted_tokens": repeated_baseline_weighted,
            "weighted_delta_percent": pct_delta(panel_weighted, repeated_baseline_weighted),
            "independence_note": "The same three baseline sessions are repeated for every profile; this aggregate is descriptive, not a panel of independent controls.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-condition-id", required=True)
    parser.add_argument("--replicate-index", type=int, required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    panel = build_panel(
        ROOT,
        model_condition_id=args.model_condition_id,
        replicate_index=args.replicate_index,
        date=args.date,
    )
    output = args.output or ROOT / "sources/evaluations/audits" / f"{panel['audit_id']}.json"
    output.write_text(json.dumps(panel, indent=2) + "\n")
    print(output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
