from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="InstanceTypeModel")


@_attrs_define
class InstanceTypeModel:
    """
    Attributes:
        fid (str):
        name (str):
        num_cpus (int):
        cpu_type (str):
        ram_gb (int):
        num_gpus (int):
        gpu_type (str):
        gpu_memory_gb (int):
        gpu_socket (str):
        local_storage_gb (int):
        network_type (Union[None, Unset, str]):
    """

    fid: str
    name: str
    num_cpus: int
    cpu_type: str
    ram_gb: int
    num_gpus: int
    gpu_type: str
    gpu_memory_gb: int
    gpu_socket: str
    local_storage_gb: int
    network_type: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fid = self.fid

        name = self.name

        num_cpus = self.num_cpus

        cpu_type = self.cpu_type

        ram_gb = self.ram_gb

        num_gpus = self.num_gpus

        gpu_type = self.gpu_type

        gpu_memory_gb = self.gpu_memory_gb

        gpu_socket = self.gpu_socket

        local_storage_gb = self.local_storage_gb

        network_type: Union[None, Unset, str]
        if isinstance(self.network_type, Unset):
            network_type = UNSET
        else:
            network_type = self.network_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fid": fid,
                "name": name,
                "num_cpus": num_cpus,
                "cpu_type": cpu_type,
                "ram_gb": ram_gb,
                "num_gpus": num_gpus,
                "gpu_type": gpu_type,
                "gpu_memory_gb": gpu_memory_gb,
                "gpu_socket": gpu_socket,
                "local_storage_gb": local_storage_gb,
            }
        )
        if network_type is not UNSET:
            field_dict["network_type"] = network_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fid = d.pop("fid")

        name = d.pop("name")

        num_cpus = d.pop("num_cpus")

        cpu_type = d.pop("cpu_type")

        ram_gb = d.pop("ram_gb")

        num_gpus = d.pop("num_gpus")

        gpu_type = d.pop("gpu_type")

        gpu_memory_gb = d.pop("gpu_memory_gb")

        gpu_socket = d.pop("gpu_socket")

        local_storage_gb = d.pop("local_storage_gb")

        def _parse_network_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        network_type = _parse_network_type(d.pop("network_type", UNSET))

        instance_type_model = cls(
            fid=fid,
            name=name,
            num_cpus=num_cpus,
            cpu_type=cpu_type,
            ram_gb=ram_gb,
            num_gpus=num_gpus,
            gpu_type=gpu_type,
            gpu_memory_gb=gpu_memory_gb,
            gpu_socket=gpu_socket,
            local_storage_gb=local_storage_gb,
            network_type=network_type,
        )

        instance_type_model.additional_properties = d
        return instance_type_model

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
