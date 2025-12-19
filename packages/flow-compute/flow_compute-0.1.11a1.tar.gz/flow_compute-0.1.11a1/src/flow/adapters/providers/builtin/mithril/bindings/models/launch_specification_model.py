from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="LaunchSpecificationModel")


@_attrs_define
class LaunchSpecificationModel:
    """
    Attributes:
        volumes (list[str]): List of volume FIDs
        ssh_keys (list[str]): List of SSH key FIDs
        startup_script (Union[None, Unset, str]):
        kubernetes_cluster (Union[None, Unset, str]):
        image_version (Union[None, Unset, str]):
    """

    volumes: list[str]
    ssh_keys: list[str]
    startup_script: Union[None, Unset, str] = UNSET
    kubernetes_cluster: Union[None, Unset, str] = UNSET
    image_version: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        volumes = self.volumes

        ssh_keys = self.ssh_keys

        startup_script: Union[None, Unset, str]
        if isinstance(self.startup_script, Unset):
            startup_script = UNSET
        else:
            startup_script = self.startup_script

        kubernetes_cluster: Union[None, Unset, str]
        if isinstance(self.kubernetes_cluster, Unset):
            kubernetes_cluster = UNSET
        else:
            kubernetes_cluster = self.kubernetes_cluster

        image_version: Union[None, Unset, str]
        if isinstance(self.image_version, Unset):
            image_version = UNSET
        else:
            image_version = self.image_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "volumes": volumes,
                "ssh_keys": ssh_keys,
            }
        )
        if startup_script is not UNSET:
            field_dict["startup_script"] = startup_script
        if kubernetes_cluster is not UNSET:
            field_dict["kubernetes_cluster"] = kubernetes_cluster
        if image_version is not UNSET:
            field_dict["image_version"] = image_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        volumes = cast(list[str], d.pop("volumes"))

        ssh_keys = cast(list[str], d.pop("ssh_keys"))

        def _parse_startup_script(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        startup_script = _parse_startup_script(d.pop("startup_script", UNSET))

        def _parse_kubernetes_cluster(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        kubernetes_cluster = _parse_kubernetes_cluster(d.pop("kubernetes_cluster", UNSET))

        def _parse_image_version(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        image_version = _parse_image_version(d.pop("image_version", UNSET))

        launch_specification_model = cls(
            volumes=volumes,
            ssh_keys=ssh_keys,
            startup_script=startup_script,
            kubernetes_cluster=kubernetes_cluster,
            image_version=image_version,
        )

        launch_specification_model.additional_properties = d
        return launch_specification_model

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
