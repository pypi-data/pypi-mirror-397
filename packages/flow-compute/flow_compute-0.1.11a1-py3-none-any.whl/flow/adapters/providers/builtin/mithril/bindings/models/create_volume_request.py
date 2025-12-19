from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.create_volume_request_disk_interface import CreateVolumeRequestDiskInterface


T = TypeVar("T", bound="CreateVolumeRequest")


@_attrs_define
class CreateVolumeRequest:
    """
    Attributes:
        name (str):
        project (str):
        disk_interface (CreateVolumeRequestDiskInterface):
        region (str):
        size_gb (int):
    """

    name: str
    project: str
    disk_interface: CreateVolumeRequestDiskInterface
    region: str
    size_gb: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        project = self.project

        disk_interface = self.disk_interface.value

        region = self.region

        size_gb = self.size_gb

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "project": project,
                "disk_interface": disk_interface,
                "region": region,
                "size_gb": size_gb,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        project = d.pop("project")

        disk_interface = CreateVolumeRequestDiskInterface(d.pop("disk_interface"))

        region = d.pop("region")

        size_gb = d.pop("size_gb")

        create_volume_request = cls(
            name=name,
            project=project,
            disk_interface=disk_interface,
            region=region,
            size_gb=size_gb,
        )

        create_volume_request.additional_properties = d
        return create_volume_request

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
