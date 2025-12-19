from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.volume_model_interface import VolumeModelInterface
from typing import cast


T = TypeVar("T", bound="VolumeModel")


@_attrs_define
class VolumeModel:
    """
    Attributes:
        fid (str):
        name (str):
        region (str):
        created_at (str):
        capacity_gb (int):
        project (str):
        interface (VolumeModelInterface):
        bids (list[str]):
        reservations (list[str]):
    """

    fid: str
    name: str
    region: str
    created_at: str
    capacity_gb: int
    project: str
    interface: VolumeModelInterface
    bids: list[str]
    reservations: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fid = self.fid

        name = self.name

        region = self.region

        created_at = self.created_at

        capacity_gb = self.capacity_gb

        project = self.project

        interface = self.interface.value

        bids = self.bids

        reservations = self.reservations

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fid": fid,
                "name": name,
                "region": region,
                "created_at": created_at,
                "capacity_gb": capacity_gb,
                "project": project,
                "interface": interface,
                "bids": bids,
                "reservations": reservations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fid = d.pop("fid")

        name = d.pop("name")

        region = d.pop("region")

        created_at = d.pop("created_at")

        capacity_gb = d.pop("capacity_gb")

        project = d.pop("project")

        interface = VolumeModelInterface(d.pop("interface"))

        bids = cast(list[str], d.pop("bids"))

        reservations = cast(list[str], d.pop("reservations"))

        volume_model = cls(
            fid=fid,
            name=name,
            region=region,
            created_at=created_at,
            capacity_gb=capacity_gb,
            project=project,
            interface=interface,
            bids=bids,
            reservations=reservations,
        )

        volume_model.additional_properties = d
        return volume_model

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
