"""Canonical token metric for every evaluation and report."""
from __future__ import annotations

from typing import Any, Mapping

WEIGHTED_TOKEN_COST_FORMULA = (
    "fresh_input_tokens + 0.1 * cached_input_tokens + 6 * output_tokens"
)


def weighted_token_cost(usage: Mapping[str, Any]) -> float | None:
    """Return the canonical weighted cost, or None for incomplete telemetry."""
    values = [usage.get(key) for key in ("fresh_input_tokens", "cached_input_tokens", "output_tokens")]
    if any(type(value) is not int or value < 0 for value in values):
        return None
    fresh, cached, output = values
    return (fresh * 10 + cached + output * 60) / 10


AGENT_STEP_DEFINITION = (
    "count of completed agent items (agent_message, command_execution, file_change, todo_list)"
)


def weighted_token_cost_per_step(usage: Mapping[str, Any]) -> float | None:
    """Decompose the canonical metric as weighted cost per agent step.

    Weighted token cost stays the sole reported metric; this factors it so the two
    sources of run-to-run movement can be told apart. Context carried per step is
    near-reproducible across replicates, while step count is where trajectory
    nondeterminism lands, so a tool that compresses context and a tool that shortens
    the search are distinguishable at a sample size the budget can reach.
    """
    total = weighted_token_cost(usage)
    steps = usage.get("agent_steps")
    if total is None or type(steps) is not int or steps <= 0:
        return None
    return round(total / steps, 1)
