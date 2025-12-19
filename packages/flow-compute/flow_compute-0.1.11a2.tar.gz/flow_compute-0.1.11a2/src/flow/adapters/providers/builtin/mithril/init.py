"""Mithril provider initialization and configuration implementation."""

import time

from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.protocols.http import HttpClientProtocol
from flow.protocols.provider_init import ProviderInitProtocol as IProviderInit


class MithrilInit(IProviderInit):
    """Mithril provider initialization interface implementation.

    Handles configuration gathering and validation for the
    Mithril provider.
    """

    def __init__(self, http_client: HttpClientProtocol):
        """Initialize with HTTP client for API calls.

        Args:
            http_client: Authenticated HTTP client instance
        """
        self.http = http_client
        self.api = MithrilApiClient(http_client)
        # Lightweight TTL caches to keep init flows snappy without repeated API calls
        self._cache_ttl_seconds: float = 300.0
        self._projects_cache: tuple[list[dict[str, str]], float] | None = None
        # SSH keys cache keyed by project_id (None = unscoped)
        self._ssh_keys_cache: dict[str, tuple[list[dict[str, str]], float]] = {}
        # Subscribe to key-change events to invalidate local key cache
        try:
            from flow.core.events.key_events import SSH_KEYS_CHANGED, KeyEventBus

            def _on_keys_changed(_payload):
                try:
                    self._ssh_keys_cache.clear()
                except Exception:  # noqa: BLE001
                    pass

            KeyEventBus.subscribe(SSH_KEYS_CHANGED, _on_keys_changed)
        except Exception:  # noqa: BLE001
            pass

    def list_projects(self) -> list[dict[str, str]]:
        """List available projects for the authenticated user.

        Fetches projects dynamically from the API to ensure
        current list based on user permissions.

        Returns:
            List of project dictionaries with id and name

        Raises:
            AuthenticationError: If API key is invalid
            ProviderError: If API request fails
        """
        # Check cache first
        try:
            if self._projects_cache is not None:
                cached_value, ts = self._projects_cache
                if time.time() - ts < self._cache_ttl_seconds:
                    return cached_value
        except Exception:  # noqa: BLE001
            pass

        response = self.api.list_projects()
        projects = []

        for project in response:
            # Extract relevant fields, handling potential API response variations
            project_id = project.get("id") or project.get("fid") or project.get("project_id")
            project_name = (
                project.get("name") or project.get("display_name") or project.get("project_name")
            )

            projects.append(
                {
                    "id": project_id if project_id is not None else "",
                    "name": project_name if project_name is not None else "",
                }
            )

        # Store in cache
        try:
            self._projects_cache = (projects, time.time())
        except Exception:  # noqa: BLE001
            pass

        return projects

    def list_ssh_keys(self, project_id: str | None = None) -> list[dict[str, str]]:
        """List SSH keys available in the account/project.

        Args:
            project_id: Optional project filter for multi-project setups

        Returns:
            List of SSH key dictionaries with id and name

        Raises:
            AuthenticationError: If API key is invalid
            ProviderError: If API request fails
        """
        params = {}
        if project_id:
            params["project"] = project_id

        # Cache key by project scope
        cache_key = project_id or "__all__"
        try:
            cached = self._ssh_keys_cache.get(cache_key)
            if cached:
                value, ts = cached
                if time.time() - ts < self._cache_ttl_seconds:
                    return value
        except Exception:  # noqa: BLE001
            pass

        response = self.api.list_ssh_keys(params)
        ssh_keys = []

        for key in response:
            # Handle potential variations in API response structure
            key_id = key.get("id")
            key_name = key.get("name") or key.get("display_name")
            fingerprint = key.get("fingerprint")
            entry = {
                "id": key_id if key_id is not None else "",
                "name": key_name if key_name is not None else "",
                "fingerprint": fingerprint if fingerprint is not None else "",
            }
            # Include required only when True to avoid leaky defaults
            required = key.get("required") if "required" in key else key.get("is_required")
            if bool(required):
                entry["required"] = True
            ssh_keys.append(entry)

        # Store in cache by scope
        try:
            self._ssh_keys_cache[cache_key] = (ssh_keys, time.time())
        except Exception:  # noqa: BLE001
            pass

        return ssh_keys

    def list_tasks_by_ssh_key(self, key_id: str, limit: int = 100) -> list[dict[str, str]]:
        """List recent tasks launched with a given SSH key.

        Uses Mithril's spot bids endpoint as the source of truth. This returns
        entries even if Task objects do not preserve the full launch specification.

        Args:
            key_id: SSH key platform ID (e.g., sshkey_abc123)
            limit: Maximum number of results (default: 100)

        Returns:
            List of minimal task dictionaries compatible with CLI expectations.
        """
        try:
            # Project scope if supported
            params = {"limit": limit}
            # Include project if discoverable via auth context
            try:
                # Best-effort project inference via separate endpoint in future
                pass
            except Exception:  # noqa: BLE001
                pass

            response = self.api.list_bids(params)
            bids = response.get("data", response) if isinstance(response, dict) else response
            results: list[dict[str, str]] = []
            for bid in bids:
                launch_spec = bid.get("launch_specification", {}) if isinstance(bid, dict) else {}
                task_ssh_keys = launch_spec.get("ssh_keys", [])
                if key_id in task_ssh_keys:
                    task_id = bid.get("fid") or bid.get("id") or ""
                    results.append(
                        {
                            "task_id": task_id,
                            "name": bid.get("name") or f"task-{task_id[:8]}",
                            "status": bid.get("status", "unknown"),
                            "instance_type": bid.get("instance_type", "N/A"),
                            "created_at": bid.get("created_at"),
                            "region": bid.get("region", "unknown"),
                        }
                    )
            return results[:limit]
        except Exception:  # noqa: BLE001
            return []
