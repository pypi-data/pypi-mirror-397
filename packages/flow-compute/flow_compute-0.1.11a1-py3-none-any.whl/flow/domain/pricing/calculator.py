"""Pricing helpers: merged pricing table and per-instance limit calculation.

This module centralizes simple pricing math for CLI/UI layers without
depending on provider internals. It uses assets defaults merged with any
user overrides from config.
"""

from __future__ import annotations

from flow.domain.parsers.instance_parser import extract_gpu_info

# Default, domain-local pricing table to keep this module pure.
_DEFAULT_TABLE = {"default": {"low": 2.0, "med": 4.0, "high": 8.0}}


def _merged_limit_prices() -> dict:
    """Return default limit prices (domain-local).

    Any environment or user overrides should be merged by the application layer
    and passed explicitly to callers of these helpers.
    """
    return dict(_DEFAULT_TABLE)


def get_pricing_table(
    overrides: dict[str, dict[str, float]] | None = None,
) -> dict[str, dict[str, float]]:
    """Expose pricing table (defaults + optional overrides provided by caller)."""
    table = _merged_limit_prices()
    if overrides:
        for gpu, tiers in overrides.items():
            base = table.get(gpu, {})
            table[gpu] = {**base, **tiers}
    return table


def calculate_instance_price(
    instance_type: str,
    *,
    priority: str = "med",
    pricing_table: dict[str, dict[str, float]] | None = None,
) -> float:
    """Return per-instance limit price from gpu-tier table and priority.

    Args:
        instance_type: e.g., "a100", "8xa100", "h100-80gb.sxm.8x"
        priority: one of low/med/high
        pricing_table: optional pre-merged table
    """
    table = pricing_table or get_pricing_table()
    gpu_type, gpu_count = extract_gpu_info(instance_type)
    fallback = table.get("default", {"med": 4.0})
    per_gpu = table.get(gpu_type, table.get("default", {})).get(priority, fallback.get("med", 4.0))
    try:
        return float(per_gpu) * max(1, int(gpu_count))
    except Exception:  # noqa: BLE001
        return float(fallback.get("med", 4.0))
