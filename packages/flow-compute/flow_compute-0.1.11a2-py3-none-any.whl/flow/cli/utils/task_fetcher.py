"""Centralized task fetching for the CLI.

Provides task fetching without caching - makes direct API calls.
Optimized to minimize redundant API calls by relying on HTTP layer caching.
"""

import logging
import os

import flow.sdk.factory as sdk_factory
from flow.errors import AuthenticationError
from flow.sdk.client import Flow
from flow.sdk.models import Task, TaskStatus


class TaskFetcher:
    """Centralized service for fetching tasks."""

    def __init__(self, flow_client: Flow | None = None):
        """Initialize with optional Flow client.

        Args:
            flow_client: Optional Flow client instance. Creates one if not provided.
        """
        self.flow_client = flow_client or sdk_factory.create_client(auto_init=True)

    def _dbg(self, msg: str) -> None:
        try:
            if os.environ.get("FLOW_STATUS_DEBUG"):
                logging.getLogger("flow.status.fetcher").info(msg)
        except Exception:  # noqa: BLE001
            pass

    def fetch_all_tasks(
        self,
        limit: int = 1000,
        prioritize_active: bool = True,
        status_filter: TaskStatus | None = None,
    ) -> list[Task]:
        """Fetch tasks directly from API.

        Simplified to make 1-2 API calls maximum, relying on HTTP caching.

        Args:
            limit: Maximum number of tasks to return
            prioritize_active: Whether to prioritize active tasks in results
            status_filter: Optional status filter for tasks

        Returns:
            List of tasks with active tasks prioritized if requested
        """
        # If filtering by specific status, just fetch those
        if status_filter:
            tasks = self.flow_client.list_tasks(status=status_filter, limit=limit)
            self._dbg(
                f"fetch_all: fetched {len(tasks) if tasks else 0} for status={getattr(status_filter, 'value', status_filter)}"
            )
            return sorted(tasks, key=lambda t: t.created_at, reverse=True)

        if not prioritize_active:
            # Simple case: just fetch all tasks
            tasks = self.flow_client.list_tasks(limit=limit)
            self._dbg(f"fetch_all(no prioritization): fetched {len(tasks)} tasks")
            return sorted(tasks, key=lambda t: t.created_at, reverse=True)

        # Prioritize active: fetch active first, then general if needed
        tasks_by_id: dict[str, Task] = {}

        try:
            # Single batched call for active tasks (RUNNING + PENDING)
            # This is cached at HTTP layer
            active = self.flow_client.list_tasks(
                status=[TaskStatus.RUNNING, TaskStatus.PENDING],
                limit=min(200, max(100, limit)),
            )
            self._dbg(f"fetch_all(active): fetched {len(active)} active tasks")
            for task in active:
                tasks_by_id[task.task_id] = task
        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            self._dbg(f"fetch_all(active): error: {e}")

        # If we need more tasks, fetch general list
        if len(tasks_by_id) < limit:
            try:
                remaining = limit - len(tasks_by_id)
                general = self.flow_client.list_tasks(limit=remaining)
                self._dbg(f"fetch_all(general): fetched {len(general)} additional tasks")
                for task in general:
                    if task.task_id not in tasks_by_id:
                        tasks_by_id[task.task_id] = task
            except Exception as e:
                if isinstance(e, AuthenticationError):
                    raise
                self._dbg(f"fetch_all(general): error: {e}")

        # Convert to sorted list: most recent first
        all_tasks = sorted(tasks_by_id.values(), key=lambda t: t.created_at, reverse=True)
        return all_tasks[:limit]

    def fetch_for_display(
        self, show_all: bool = False, status_filter: str | None = None, limit: int = 100
    ) -> list[Task]:
        """Fetch tasks for display commands (status, list).

        Args:
            show_all: Whether to show all tasks or apply time filtering
            status_filter: Optional status string to filter by
            limit: Maximum number of tasks to return

        Returns:
            List of tasks ready for display
        """
        self._dbg(
            f"fetch_for_display: show_all={show_all} status_filter={status_filter} limit={limit}"
        )

        if status_filter:
            try:
                status_enum = (
                    TaskStatus(status_filter) if isinstance(status_filter, str) else status_filter
                )
                tasks = self.flow_client.list_tasks(status=status_enum, limit=limit)
                self._dbg(
                    f"fetch_for_display: fetched {len(tasks)} tasks for status={status_filter}"
                )
                return sorted(tasks, key=lambda t: t.created_at, reverse=True)
            except AuthenticationError:
                raise
            except Exception as e:  # noqa: BLE001
                self._dbg(f"fetch_for_display: error fetching status={status_filter}: {e}")
                return []

        if show_all:
            try:
                tasks = self.flow_client.list_tasks(limit=limit)
                self._dbg(f"fetch_for_display(--all): fetched {len(tasks)} tasks")
                return sorted(tasks, key=lambda t: t.created_at, reverse=True)
            except Exception as e:
                if isinstance(e, AuthenticationError):
                    raise
                self._dbg(f"fetch_for_display(--all): error: {e}")
                return []

        # Default: prioritize active tasks
        try:
            active_tasks = self.flow_client.list_tasks(
                status=[TaskStatus.RUNNING, TaskStatus.PENDING],
                limit=max(100, limit),
            )
            self._dbg(f"fetch_for_display(active): fetched {len(active_tasks)} tasks")

            if active_tasks:
                sorted_tasks = sorted(active_tasks, key=lambda t: t.created_at, reverse=True)
                return sorted_tasks[:limit]

            # No active tasks, fetch recent
            self._dbg("fetch_for_display: no active tasks, fetching recent")
            recent_tasks = self.flow_client.list_tasks(limit=limit)
            self._dbg(f"fetch_for_display(recent): fetched {len(recent_tasks)} tasks")
            return sorted(recent_tasks, key=lambda t: t.created_at, reverse=True)

        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            self._dbg(f"fetch_for_display: error: {e}")
            return []

    def fetch_for_resolution(self, limit: int = 1000) -> list[Task]:
        """Fetch tasks for name/ID resolution (cancel, ssh, logs).

        This method prioritizes active tasks since those are most likely
        to be the target of user actions.

        Args:
            limit: Maximum number of tasks to fetch

        Returns:
            List of tasks with active tasks prioritized
        """
        return self.fetch_all_tasks(limit=limit, prioritize_active=True, status_filter=None)
