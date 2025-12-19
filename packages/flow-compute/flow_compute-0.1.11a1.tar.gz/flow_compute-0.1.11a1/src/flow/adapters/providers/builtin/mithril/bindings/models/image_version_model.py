from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="ImageVersionModel")


@_attrs_define
class ImageVersionModel:
    """
    Attributes:
        image_version_fid (str):
        image_version_name (str):
        os (str):
        kernel (str):
        stable (bool):
        deactivated_at (Union[None, Unset, str]):
        nvidia_driver (Union[None, Unset, str]):
        cuda (Union[None, Unset, str]):
        cuda_toolkit (Union[None, Unset, str]):
        nvidia_container_toolkit (Union[None, Unset, str]):
        packages (Union[None, Unset, str]):
    """

    image_version_fid: str
    image_version_name: str
    os: str
    kernel: str
    stable: bool
    deactivated_at: Union[None, Unset, str] = UNSET
    nvidia_driver: Union[None, Unset, str] = UNSET
    cuda: Union[None, Unset, str] = UNSET
    cuda_toolkit: Union[None, Unset, str] = UNSET
    nvidia_container_toolkit: Union[None, Unset, str] = UNSET
    packages: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        image_version_fid = self.image_version_fid

        image_version_name = self.image_version_name

        os = self.os

        kernel = self.kernel

        stable = self.stable

        deactivated_at: Union[None, Unset, str]
        if isinstance(self.deactivated_at, Unset):
            deactivated_at = UNSET
        else:
            deactivated_at = self.deactivated_at

        nvidia_driver: Union[None, Unset, str]
        if isinstance(self.nvidia_driver, Unset):
            nvidia_driver = UNSET
        else:
            nvidia_driver = self.nvidia_driver

        cuda: Union[None, Unset, str]
        if isinstance(self.cuda, Unset):
            cuda = UNSET
        else:
            cuda = self.cuda

        cuda_toolkit: Union[None, Unset, str]
        if isinstance(self.cuda_toolkit, Unset):
            cuda_toolkit = UNSET
        else:
            cuda_toolkit = self.cuda_toolkit

        nvidia_container_toolkit: Union[None, Unset, str]
        if isinstance(self.nvidia_container_toolkit, Unset):
            nvidia_container_toolkit = UNSET
        else:
            nvidia_container_toolkit = self.nvidia_container_toolkit

        packages: Union[None, Unset, str]
        if isinstance(self.packages, Unset):
            packages = UNSET
        else:
            packages = self.packages

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "image_version_fid": image_version_fid,
                "image_version_name": image_version_name,
                "os": os,
                "kernel": kernel,
                "stable": stable,
            }
        )
        if deactivated_at is not UNSET:
            field_dict["deactivated_at"] = deactivated_at
        if nvidia_driver is not UNSET:
            field_dict["nvidia_driver"] = nvidia_driver
        if cuda is not UNSET:
            field_dict["cuda"] = cuda
        if cuda_toolkit is not UNSET:
            field_dict["cuda_toolkit"] = cuda_toolkit
        if nvidia_container_toolkit is not UNSET:
            field_dict["nvidia_container_toolkit"] = nvidia_container_toolkit
        if packages is not UNSET:
            field_dict["packages"] = packages

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        image_version_fid = d.pop("image_version_fid")

        image_version_name = d.pop("image_version_name")

        os = d.pop("os")

        kernel = d.pop("kernel")

        stable = d.pop("stable")

        def _parse_deactivated_at(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        deactivated_at = _parse_deactivated_at(d.pop("deactivated_at", UNSET))

        def _parse_nvidia_driver(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        nvidia_driver = _parse_nvidia_driver(d.pop("nvidia_driver", UNSET))

        def _parse_cuda(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        cuda = _parse_cuda(d.pop("cuda", UNSET))

        def _parse_cuda_toolkit(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        cuda_toolkit = _parse_cuda_toolkit(d.pop("cuda_toolkit", UNSET))

        def _parse_nvidia_container_toolkit(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        nvidia_container_toolkit = _parse_nvidia_container_toolkit(
            d.pop("nvidia_container_toolkit", UNSET)
        )

        def _parse_packages(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        packages = _parse_packages(d.pop("packages", UNSET))

        image_version_model = cls(
            image_version_fid=image_version_fid,
            image_version_name=image_version_name,
            os=os,
            kernel=kernel,
            stable=stable,
            deactivated_at=deactivated_at,
            nvidia_driver=nvidia_driver,
            cuda=cuda,
            cuda_toolkit=cuda_toolkit,
            nvidia_container_toolkit=nvidia_container_toolkit,
            packages=packages,
        )

        image_version_model.additional_properties = d
        return image_version_model

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
