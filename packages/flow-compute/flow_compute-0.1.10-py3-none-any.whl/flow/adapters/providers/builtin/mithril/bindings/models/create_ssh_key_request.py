from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="CreateSshKeyRequest")


@_attrs_define
class CreateSshKeyRequest:
    """
    Attributes:
        project (str):
        name (str):
        public_key (Union[None, Unset, str]):
        required (Union[Unset, bool]):  Default: False.
    """

    project: str
    name: str
    public_key: Union[None, Unset, str] = UNSET
    required: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        project = self.project

        name = self.name

        public_key: Union[None, Unset, str]
        if isinstance(self.public_key, Unset):
            public_key = UNSET
        else:
            public_key = self.public_key

        required = self.required

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "name": name,
            }
        )
        if public_key is not UNSET:
            field_dict["public_key"] = public_key
        if required is not UNSET:
            field_dict["required"] = required

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        project = d.pop("project")

        name = d.pop("name")

        def _parse_public_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        public_key = _parse_public_key(d.pop("public_key", UNSET))

        required = d.pop("required", UNSET)

        create_ssh_key_request = cls(
            project=project,
            name=name,
            public_key=public_key,
            required=required,
        )

        create_ssh_key_request.additional_properties = d
        return create_ssh_key_request

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
