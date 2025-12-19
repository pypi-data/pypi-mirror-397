"""Reservations facet: capacity reservation lifecycle."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ReservationsProtocol(Protocol):
    """Reservation creation, inspection, and extension."""

    def create_reservation(
        self,
        instance_type: str,
        config: Any,
        volume_ids: list[str] | None = None,
    ) -> Any: ...

    def list_reservations(self, params: dict[str, Any] | None = None) -> list[Any]: ...

    def get_reservation(self, reservation_id: str) -> Any: ...

    def get_reservation_availability(
        self,
        instance_type: str,
        num_nodes: int,
        duration_hours: float,
        *,
        region: str | None = None,
        earliest_start_time: str | None = None,
        latest_end_time: str | None = None,
        mode: str | None = None,
    ) -> list[dict[str, Any]]: ...

    def extend_reservation(self, reservation_id: str, new_end_time: str) -> Any: ...

    def get_extension_availability(self, reservation_id: str) -> dict[str, Any]: ...
