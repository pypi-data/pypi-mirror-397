from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.kubernetes_cluster_model_status import KubernetesClusterModelStatus
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="KubernetesClusterModel")


@_attrs_define
class KubernetesClusterModel:
    """
    Attributes:
        fid (str):
        project (str):
        name (str):
        region (str):
        created_at (str):
        kube_host (Union[None, str]):
        ssh_keys (list[str]):
        instances (list[str]):
        join_command (Union[None, str]):
        status (KubernetesClusterModelStatus):
        deleted_at (Union[None, Unset, str]):
    """

    fid: str
    project: str
    name: str
    region: str
    created_at: str
    kube_host: Union[None, str]
    ssh_keys: list[str]
    instances: list[str]
    join_command: Union[None, str]
    status: KubernetesClusterModelStatus
    deleted_at: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fid = self.fid

        project = self.project

        name = self.name

        region = self.region

        created_at = self.created_at

        kube_host: Union[None, str]
        kube_host = self.kube_host

        ssh_keys = self.ssh_keys

        instances = self.instances

        join_command: Union[None, str]
        join_command = self.join_command

        status = self.status.value

        deleted_at: Union[None, Unset, str]
        if isinstance(self.deleted_at, Unset):
            deleted_at = UNSET
        else:
            deleted_at = self.deleted_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fid": fid,
                "project": project,
                "name": name,
                "region": region,
                "created_at": created_at,
                "kube_host": kube_host,
                "ssh_keys": ssh_keys,
                "instances": instances,
                "join_command": join_command,
                "status": status,
            }
        )
        if deleted_at is not UNSET:
            field_dict["deleted_at"] = deleted_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fid = d.pop("fid")

        project = d.pop("project")

        name = d.pop("name")

        region = d.pop("region")

        created_at = d.pop("created_at")

        def _parse_kube_host(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        kube_host = _parse_kube_host(d.pop("kube_host"))

        ssh_keys = cast(list[str], d.pop("ssh_keys"))

        instances = cast(list[str], d.pop("instances"))

        def _parse_join_command(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        join_command = _parse_join_command(d.pop("join_command"))

        status = KubernetesClusterModelStatus(d.pop("status"))

        def _parse_deleted_at(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        deleted_at = _parse_deleted_at(d.pop("deleted_at", UNSET))

        kubernetes_cluster_model = cls(
            fid=fid,
            project=project,
            name=name,
            region=region,
            created_at=created_at,
            kube_host=kube_host,
            ssh_keys=ssh_keys,
            instances=instances,
            join_command=join_command,
            status=status,
            deleted_at=deleted_at,
        )

        kubernetes_cluster_model.additional_properties = d
        return kubernetes_cluster_model

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
