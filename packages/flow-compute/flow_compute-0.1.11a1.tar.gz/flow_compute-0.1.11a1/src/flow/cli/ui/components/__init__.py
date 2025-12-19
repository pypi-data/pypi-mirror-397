"""Interactive selection components for Flow CLI.

This package provides reusable components for interactive resource selection
with proper separation of concerns between models, rendering, state management,
and keyboard interaction.
"""

from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.sdk.models import Task, Volume

from flow.cli.ui.components.formatters.task_formatter import TaskFormatter
from flow.cli.ui.components.formatters.volume_formatter import VolumeFormatter
from flow.cli.ui.components.models import SelectionItem
from flow.cli.ui.components.renderer import map_rich_to_prompt_toolkit_color
from flow.cli.ui.components.selector import InteractiveSelector
from flow.cli.ui.components.selector_api import Selector


def select_task(tasks: Iterable["Task"], title: str = "Select a task"):
    items = [TaskFormatter.to_selection_item(t) for t in tasks]
    return Selector.select_one(items, title=title)


def select_volume(volumes: Iterable["Volume"], multiselect: bool = False, title: str | None = None):
    items = [VolumeFormatter.to_selection_item(v) for v in volumes]

    if multiselect:
        title = title or "Select volumes"
        return Selector.select_many(items, title=title)

    title = title or "Select a volume"
    return Selector.select_one(items, title=title)


__all__ = [
    "InteractiveSelector",
    "SelectionItem",
    "map_rich_to_prompt_toolkit_color",
    "select_task",
    "select_volume",
]
