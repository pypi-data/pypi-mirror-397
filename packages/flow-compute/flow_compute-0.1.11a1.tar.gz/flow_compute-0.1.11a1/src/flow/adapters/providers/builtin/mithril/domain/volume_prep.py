"""Volume preparation service.

Resolves/creates volumes declared in TaskConfig and returns updated specs and
resolved IDs. Centralizes logic used by submission/storage flows to keep them
thin and DRY, and to enable consistent validation behavior.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.domain.volumes import VolumeService
    from flow.sdk.models import TaskConfig


class VolumePreparationService:
    """Resolves and ensures volumes exist before bidding.

    Responsibilities:
    - Resolve by ID or name (exact match in region)
    - Create when unresolved, using unique suffix on name conflicts
    - Return updated TaskConfig volume specs and list of resolved IDs
    """

    @staticmethod
    def resolve_and_ensure_volumes(
        volumes: VolumeService,
        config: TaskConfig,
        *,
        region: str,
        project_id: str,
    ) -> tuple[list[Any], list[str]]:
        """Resolve or create volumes declared in the config.

        Args:
            config: TaskConfig containing `volumes` specs
            region: Target region for volumes
            project_id: Project identifier

        Returns:
            (updated_volume_specs, resolved_volume_ids)
        """
        resolved_ids: list[str] = []
        updated_specs = config.volumes

        if not updated_specs:
            return updated_specs, resolved_ids

        existing = volumes.list_volumes(project_id=project_id, region=region, limit=1000)

        for spec in updated_specs:
            vol_id = spec.volume_id
            vol_name = spec.name

            if not vol_id and vol_name and existing:
                matches = [v for v in existing if v.name == vol_name]
                if len(matches) == 1:
                    vol_id = matches[0].id
                else:
                    raise ValueError(f"Resolved multiple volumes: {matches}")

            if not vol_id:
                raise ValueError(f"Failed to resolve volume: {vol_name}")

        return updated_specs, resolved_ids
