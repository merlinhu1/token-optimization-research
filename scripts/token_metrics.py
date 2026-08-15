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
