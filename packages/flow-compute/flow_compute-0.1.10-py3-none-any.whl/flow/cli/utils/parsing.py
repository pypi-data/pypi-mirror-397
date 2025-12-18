"""CLI parsing utilities."""

from __future__ import annotations

from contextlib import suppress


def parse_price(value: str | float | int | None) -> float:
    """Parse a price string like "$1.50" to a float 1.5.

    Returns 0.0 on None or unparsable input.
    """
    if value is None:
        return 0.0
    if isinstance(value, int | float):
        return float(value)
    s = str(value).strip()
    with suppress(Exception):
        if s.startswith("$"):
            s = s[1:]
    with suppress(Exception):
        return float(s)
    return 0.0
