"""Mithril-specific instance type adapter with dynamic region overrides."""

from __future__ import annotations

import logging
import time
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flow.adapters.providers.builtin.mithril.core.constants import (
    INSTANCE_TYPE_NAMES,
    VALID_REGIONS,
)
from flow.domain.parsers.instance_parser import InstanceParser
from flow.errors import FlowError
from flow.protocols.instance_types import InstanceTypeResolverProtocol

if TYPE_CHECKING:  # pragma: no cover - import cycle guard for type checkers only
    from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient


logger = logging.getLogger(__name__)


class InstanceTypeResolver(InstanceTypeResolverProtocol):
    """Mithril-specific instance type resolver.

    Adapts domain InstanceTypeRegistry to work with Mithril's
    specific mappings and IDs.
    """

    def __init__(
        self,
        api: MithrilApiClient,
        *,
        ttl: float = 300.0,
    ):
        """Initialize resolver with dynamic hydration from API."""
        self._api = api
        self._ttl = float(ttl)
        self._regions: tuple[str, ...] = tuple(VALID_REGIONS)
        if not self._regions:
            raise ValueError("Mithril InstanceTypeResolver requires at least one valid region")

        # Dynamic mappings populated from API (alias -> instance_fid)
        self._map: dict[str, str] = {}
        # Reverse mapping for display names (instance_fid -> display_name)
        self._names: dict[str, str] = dict(INSTANCE_TYPE_NAMES)
        self._family_ids: dict[str, list[str]] = self._build_family_index(self._names)
        self._last_refresh: float | None = None

    def resolve(self, user_spec: str) -> str:
        """Resolve user-friendly spec (e.g., "a100", "4xa100") to a Mithril ID.

        Raises FlowError with helpful suggestions when resolution fails.
        """
        if not user_spec:
            raise FlowError("Instance type specification is required")

        normalized_spec = user_spec.lower().strip()

        # Direct ID passthrough does not need hydration.
        if normalized_spec.startswith("it_"):
            return user_spec.strip()

        self._ensure_region_overrides()

        for key in self._iter_lookup_keys(normalized_spec):
            mapped = self._map.get(key)
            if mapped:
                return mapped

        available_types = list(self._map.keys())
        raise FlowError(
            f"Unknown instance type: {user_spec}",
            suggestions=[
                f"Available: {', '.join(available_types[:5])}...",
                "Use 'flow pricing --list' to see all available instance types",
                "Examples: 'a100', '4xa100', '8xh100'",
            ],
        )

    def resolve_simple(self, spec: str) -> str:
        """Simple exact resolution using the static mapping (no canonicalization)."""
        normalized = spec.lower().strip()
        if normalized.startswith("it_"):
            return spec.strip()
        self._ensure_region_overrides()
        if normalized in self._map:
            return self._map[normalized]
        available = sorted(self._map.keys())
        raise ValueError(f"Unknown instance type: {spec}. Available: {', '.join(available)}")

    def candidate_ids(self, user_spec: str) -> list[str]:
        """Return candidate instance type IDs for a spec, covering variants.

        For H100, consider both SXM and PCIe 8x variants to allow region-specific
        availability differences.
        """
        candidates: list[str] = []
        primary = self.resolve(user_spec)
        candidates.append(primary)

        spec_lower = (user_spec or "").lower()
        if any(token in spec_lower for token in ("h100", "xh100")):
            for alt_id in self._family_ids.get("h100", []):
                if alt_id not in candidates:
                    candidates.append(alt_id)
        if spec_lower in {"a100", "1xa100"}:
            for alt in (
                "a100-80gb.sxm.1x",
                "a100-80gb.sxm.2x",
                "a100-80gb.sxm.4x",
                "a100-80gb.sxm.8x",
            ):
                try:
                    alt_id = self.resolve(alt)
                except FlowError:
                    continue
                if alt_id not in candidates:
                    candidates.append(alt_id)

        # Fallback to just returning any that resolved
        return candidates

    @staticmethod
    def _parse_key(user_spec: str) -> str:
        """Parse user spec into a normalized key present in mapping.

        Accepts inputs like "a100", "4xa100", "8xh100", or canonical long forms
        like "h100-80gb.sxm.8x" and returns the same when appropriate.
        """
        s = (user_spec or "").strip().lower()
        if not s:
            return s
        # If already in dotted long form, return as-is
        if "." in s and any(tok in s for tok in ("sxm", "pcie")):
            return s
        # If it looks like N x gpu
        if "x" in s:
            left, right = s.split("x", 1)
            try:
                _ = int(left)
                return f"{left}x{right}"
            except ValueError:
                return s
        return s

    def _ensure_region_overrides(self) -> None:
        """Load region overrides if configured."""
        now = time.monotonic()
        if self._last_refresh is not None and (now - self._last_refresh) < self._ttl:
            return
        self._hydrate_from_instance_types()
        self._hydrate_overrides()
        self._last_refresh = time.monotonic()

    def _hydrate_from_instance_types(self) -> None:
        """Fetch instance types from API to discover new SKUs dynamically."""
        response = self._api.list_instance_types({})

        # Unwrap {"data": [...]} format if needed
        if isinstance(response, dict) and "data" in response:
            instance_types = response["data"]
        elif isinstance(response, list):
            instance_types = response
        else:
            return

        if not isinstance(instance_types, list):
            return

        for item in instance_types:
            fid = item.get("fid")
            name = item.get("name")
            num_gpus = item.get("num_gpus")
            gpu_type = item.get("gpu_type")

            # Handle legacy "gpus" array format: {"gpus": [{"name": "L40S", "count": 2}]}
            if not num_gpus or not gpu_type:
                gpus = item.get("gpus")
                if isinstance(gpus, list) and gpus:
                    first_gpu = gpus[0]
                    if isinstance(first_gpu, dict):
                        gpu_type = gpu_type or first_gpu.get("name")
                        num_gpus = num_gpus or first_gpu.get("count")

            if not fid or not name:
                continue

            self._names[fid] = name
            aliases = self._derive_aliases(name)

            if num_gpus and gpu_type:
                gpu_lower = gpu_type.lower()
                if num_gpus > 1:
                    aliases.add(f"{num_gpus}x{gpu_lower}")
                aliases.add(gpu_lower)

            family = self._detect_family(name) or self._detect_family(gpu_type)
            if family:
                self._record_family_member(family, fid)

            for alias in aliases:
                if alias and alias not in self._map:
                    self._map[alias] = fid

    def _hydrate_overrides(self) -> None:
        """Fetch availability and merge instance mappings across all regions."""
        response = self._api.list_spot_availability({})

        # Unwrap {"auctions": [...]} or similar formats if needed
        if isinstance(response, dict):
            for key in ("auctions", "data", "availability"):
                if key in response and isinstance(response[key], list):
                    response = response[key]
                    break
            else:
                return  # Dict with no recognized wrapper - skip silently

        if not isinstance(response, Sequence):
            return  # Skip silently for unexpected formats

        overrides: set[str] = set()
        for payload in response:
            if not isinstance(payload, Mapping):
                continue  # Skip invalid payloads

            instance_fid = payload.get("instance_type")
            if not isinstance(instance_fid, str) or not instance_fid.startswith("it_"):
                continue  # Skip payloads without valid instance_type

            region = payload.get("region")
            if not isinstance(region, str) or not region:
                continue  # Skip payloads without region
            if region not in self._regions:
                continue

            display_name = self._names.get(instance_fid) or INSTANCE_TYPE_NAMES.get(instance_fid)
            if not display_name:
                continue

            aliases = self._derive_aliases(display_name)
            if not aliases:
                continue

            self._names[instance_fid] = display_name
            family = self._detect_family(display_name)
            if family:
                self._record_family_member(family, instance_fid)

            for alias in aliases:
                key = alias.lower()
                if not key:
                    continue

                existing_fid = self._map.get(key)
                if key in overrides and existing_fid and instance_fid == existing_fid:
                    continue

                if instance_fid != existing_fid:
                    overrides.add(key)
                    self._map[key] = instance_fid

        if overrides:
            logger.debug("Hydrated Mithril instance overrides: %s", ", ".join(sorted(overrides)))

    def _iter_lookup_keys(self, normalized_spec: str) -> list[str]:
        keys = [normalized_spec]
        parsed = self._parse_key(normalized_spec)
        if parsed and parsed not in keys:
            keys.append(parsed)
        return keys

    @staticmethod
    def _derive_aliases(display_name: str) -> set[str]:
        aliases: set[str] = set()
        if not display_name:
            return aliases

        name = display_name.strip()
        if not name:
            return aliases

        lowered = name.lower()
        aliases.add(lowered)

        try:
            components = InstanceParser.parse(lowered)
        except Exception:  # noqa: BLE001
            components = None

        if components:
            if components.gpu_count > 1:
                aliases.add(f"{components.gpu_count}x{components.gpu_type}")
            aliases.add(components.gpu_type)

        return {alias for alias in aliases if alias}

    @staticmethod
    def _detect_family(value: str | None) -> str | None:
        if not value:
            return None
        lowered = value.lower()
        for family in ("b200", "h100", "a100"):
            if family in lowered:
                return family
        return None

    @staticmethod
    def _synthesize_display_name(instance_fid: str) -> str:
        if not instance_fid or "_" not in instance_fid:
            return instance_fid or "unknown-instance"
        return instance_fid.split("_", 1)[1]

    @staticmethod
    def _build_family_index(names: Mapping[str, str]) -> dict[str, list[str]]:
        index: dict[str, list[str]] = {}
        for instance_fid, display_name in names.items():
            family = InstanceTypeResolver._detect_family(display_name)
            if not family:
                continue
            members = index.setdefault(family, [])
            if instance_fid not in members:
                members.append(instance_fid)
        return index

    def _record_family_member(self, family: str, instance_fid: str) -> None:
        members = self._family_ids.setdefault(family, [])
        if instance_fid not in members:
            members.append(instance_fid)
