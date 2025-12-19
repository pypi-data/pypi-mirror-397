from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="CreatedSshKeyModel")


@_attrs_define
class CreatedSshKeyModel:
    """
    Attributes:
        fid (str):
        name (str):
        project (str):
        public_key (str):
        created_at (str):
        required (bool):
        private_key (Union[None, Unset, str]):
    """

    fid: str
    name: str
    project: str
    public_key: str
    created_at: str
    required: bool
    private_key: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fid = self.fid

        name = self.name

        project = self.project

        public_key = self.public_key

        created_at = self.created_at

        required = self.required

        private_key: Union[None, Unset, str]
        if isinstance(self.private_key, Unset):
            private_key = UNSET
        else:
            private_key = self.private_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fid": fid,
                "name": name,
                "project": project,
                "public_key": public_key,
                "created_at": created_at,
                "required": required,
            }
        )
        if private_key is not UNSET:
            field_dict["private_key"] = private_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fid = d.pop("fid")

        name = d.pop("name")

        project = d.pop("project")

        public_key = d.pop("public_key")

        created_at = d.pop("created_at")

        required = d.pop("required")

        def _parse_private_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        private_key = _parse_private_key(d.pop("private_key", UNSET))

        created_ssh_key_model = cls(
            fid=fid,
            name=name,
            project=project,
            public_key=public_key,
            created_at=created_at,
            required=required,
            private_key=private_key,
        )

        created_ssh_key_model.additional_properties = d
        return created_ssh_key_model

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
