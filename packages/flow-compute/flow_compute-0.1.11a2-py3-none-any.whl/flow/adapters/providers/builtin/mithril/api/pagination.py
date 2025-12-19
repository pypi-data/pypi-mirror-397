"""Reusable pagination utilities for Mithril API."""

from collections.abc import Callable, Iterator
from typing import Any, TypeVar

T = TypeVar("T")


def paginate(
    api_call: Callable[[dict[str, Any]], dict[str, Any]],
    params: dict[str, Any],
    *,
    max_pages: int = 20,
    data_key: str = "data",
    cursor_key: str = "next_cursor",
    cursor_param: str = "next_cursor",
) -> Iterator[T]:
    """Paginate through an API endpoint that uses cursor-based pagination.

    Yields items from each page until no more pages are available or max_pages is reached.
    This is a generator that can be used with islice() to limit total results.

    Args:
        api_call: The API method to call (e.g., self._api.list_instances)
        params: Initial parameters for the API call (will be copied for each page)
        max_pages: Maximum number of pages to fetch (safety limit)
        data_key: Key in response dict containing the list of items (default: "data")
        cursor_key: Key in response dict containing the next cursor (default: "next_cursor")
        cursor_param: Parameter name to pass cursor in next request (default: "next_cursor")

    Yields:
        Individual items from each page's data list

    Example:
        # Fetch all instances with automatic pagination
        instances = list(paginate(api.list_instances, {"project": "proj_123", "limit": 100}))

        # Limit to first 1000 items across all pages
        from itertools import islice
        instances = list(islice(paginate(api.list_instances, params), 1000))

        # Process items as they come (memory efficient)
        for instance in paginate(api.list_instances, params):
            process(instance)
    """
    next_cursor = None
    page_count = 0

    while page_count < max_pages:
        # Copy params and add cursor if we have one
        page_params = params.copy()
        if next_cursor:
            page_params[cursor_param] = next_cursor

        page_count += 1
        response = api_call(page_params)

        # Extract items and next cursor
        items = response.get(data_key, [])
        next_cursor = response.get(cursor_key)

        # Yield all items from this page
        if not items:
            break

        yield from items

        # Stop if no more pages
        if not next_cursor:
            break
