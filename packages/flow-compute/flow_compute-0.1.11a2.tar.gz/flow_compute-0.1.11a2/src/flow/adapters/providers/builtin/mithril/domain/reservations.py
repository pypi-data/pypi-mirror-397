"""Reservation management service."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

from flow.adapters.providers.builtin.mithril.core.constants import (
    RESERVATION_STATUS_MAPPINGS,
)
from flow.sdk.models import Reservation, ReservationSpec
from flow.sdk.models.enums import ReservationStatus

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient


class ReservationsService:
    """Service for managing reservations."""

    def __init__(self, api: MithrilApiClient) -> None:
        """Initialize reservation service.

        Args:
            api: Mithril API client for reservation operations
        """
        self._api = api

    def create(self, spec: ReservationSpec) -> Reservation:
        """Create a new reservation.

        Args:
            spec: Reservation specification with all required parameters

        Returns:
            Created reservation

        Raises:
            MithrilAPIError: If reservation creation fails
        """
        launch_spec: dict[str, Any] = {
            "volumes": list(spec.volumes),
            "ssh_keys": list(spec.ssh_keys),
        }
        if spec.startup_script:
            launch_spec["startup_script"] = spec.startup_script

        payload: dict[str, Any] = {
            "project": spec.project_id,
            "instance_type": spec.instance_type,
            "region": spec.region,
            "start_time": self._datetime_to_iso_z(spec.start_time_utc),
            "end_time": self._compute_end_time(spec.start_time_utc, spec.duration_hours),
            "instance_quantity": spec.quantity,
            "name": spec.name or f"reservation-{spec.instance_type}",
            "launch_specification": launch_spec,
        }

        response = self._api.create_reservation(payload)
        return self._response_to_reservation(response)

    def list(self, params: dict[str, Any] | None = None) -> list[Reservation]:
        """List reservations."""
        params = params or {}
        response = self._api.list_reservations(params)

        if isinstance(response, dict):
            data = response.get("data", response.get("reservations", []))
        else:
            data = response

        if not isinstance(data, list):
            data = [data] if data else []

        return [self._response_to_reservation(r) for r in data]

    def get(self, reservation_id: str) -> Reservation:
        """Get a specific reservation.

        Args:
            reservation_id: ID of reservation to retrieve

        Returns:
            Reservation details

        Raises:
            MithrilAPIError: If reservation not found
        """
        response = self._api.get_reservation(reservation_id)
        return self._response_to_reservation(response)

    def extend(self, reservation_id: str, new_end_time: str) -> Reservation:
        """Extend a reservation to a new end time.

        Args:
            reservation_id: ID of reservation to extend
            new_end_time: New end time in ISO format (UTC with Z suffix)

        Returns:
            Updated reservation

        Raises:
            MithrilAPIError: If extension fails
        """
        payload = {"end_time": new_end_time}
        response = self._api.extend_reservation(reservation_id, payload)
        return self._response_to_reservation(response)

    def get_extension_availability(self, reservation_id: str) -> dict[str, Any]:
        """Get extension availability for a reservation.

        Args:
            reservation_id: ID of reservation to check

        Returns:
            Extension availability info with latest_extension_time and available flag
        """
        return self._api.get_extension_availability(reservation_id)

    def get_availability(
        self,
        *,
        project_id: str,
        instance_type: str,
        region: str,
        mode: str = "latest_end_time",
        start_time: str | None = None,
        end_time: str | None = None,
        earliest_start_time: str | None = None,
        latest_end_time: str | None = None,
        quantity: int | None = None,
    ) -> Any:
        """Get availability per OpenAPI modes: slots, latest_end_time, check.

        Args:
            project_id: Project FID
            instance_type: Instance type FID
            region: Region name
            mode: Query mode - "slots", "latest_end_time", or "check"
            start_time: Start time for latest_end_time/check modes
            end_time: End time for check mode
            earliest_start_time: Start of range for slots mode
            latest_end_time: End of range for slots mode
            quantity: Number of instances needed

        Returns:
            Mode-dependent response (slots list, latest_end_time response, or check response)
        """
        params: dict[str, Any] = {
            "project": project_id,
            "instance_type": instance_type,
            "region": region,
            "mode": mode,
        }

        if mode == "latest_end_time":
            if start_time:
                params["start_time"] = start_time
            if quantity:
                params["quantity"] = quantity
        elif mode == "slots":
            if earliest_start_time:
                params["earliest_start_time"] = earliest_start_time
            if latest_end_time:
                params["latest_end_time"] = latest_end_time
        elif mode == "check":
            if start_time:
                params["start_time"] = start_time
            if end_time:
                params["end_time"] = end_time
            if quantity:
                params["quantity"] = quantity

        return self._api.get_reservation_availability(params)

    def _response_to_reservation(self, resp: dict[str, Any]) -> Reservation:
        """Map API response to SDK Reservation."""
        status_raw = str(resp.get("status", "pending")).lower()
        status_mapped = RESERVATION_STATUS_MAPPINGS.get(status_raw, "PENDING")

        return Reservation(
            reservation_id=resp["fid"],
            name=resp.get("name"),
            status=ReservationStatus[status_mapped],
            instance_type=resp["instance_type"],
            region=resp.get("region", ""),
            quantity=resp["instance_quantity"],
            start_time_utc=self._parse_datetime(resp["start_time"]),
            end_time_utc=self._parse_datetime(resp.get("end_time")),
            price_total_usd=self._parse_price(resp.get("total_price")),
            provider_metadata={
                "fid": resp["fid"],
                "project": resp.get("project"),
                "created_by": resp.get("created_by"),
                "created_at": resp.get("created_at"),
                "unit_price": resp.get("unit_price"),
                "instances": resp.get("instances", []),
                "launch_specification": resp.get("launch_specification"),
                "deactivated_at": resp.get("deactivated_at"),
            },
        )

    @staticmethod
    def _compute_end_time(start: datetime, duration_hours: int) -> str:
        end = start + timedelta(hours=duration_hours)
        return ReservationsService._datetime_to_iso_z(end)

    @staticmethod
    def _datetime_to_iso_z(dt: datetime) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def _parse_price(price_str: str | None) -> float | None:
        if not price_str:
            return None
        try:
            return float(str(price_str).replace("$", "").replace(",", ""))
        except (ValueError, AttributeError):
            return None
