from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast


T = TypeVar("T", bound="CreateKubernetesClusterRequest")


@_attrs_define
class CreateKubernetesClusterRequest:
    """
    Attributes:
        name (str):
        project (str):
        region (str):
        ssh_keys (list[str]):
        instance_type (str):
    """

    name: str
    project: str
    region: str
    ssh_keys: list[str]
    instance_type: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        project = self.project

        region = self.region

        ssh_keys = self.ssh_keys

        instance_type = self.instance_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "project": project,
                "region": region,
                "ssh_keys": ssh_keys,
                "instance_type": instance_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        project = d.pop("project")

        region = d.pop("region")

        ssh_keys = cast(list[str], d.pop("ssh_keys"))

        instance_type = d.pop("instance_type")

        create_kubernetes_cluster_request = cls(
            name=name,
            project=project,
            region=region,
            ssh_keys=ssh_keys,
            instance_type=instance_type,
        )

        create_kubernetes_cluster_request.additional_properties = d
        return create_kubernetes_cluster_request

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
