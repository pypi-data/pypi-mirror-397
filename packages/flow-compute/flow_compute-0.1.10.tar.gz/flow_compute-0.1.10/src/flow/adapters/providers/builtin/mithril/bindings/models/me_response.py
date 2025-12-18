from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="MeResponse")


@_attrs_define
class MeResponse:
    """
    Attributes:
        id (str):
        email (str):
        organization_id (str):
        user_name (Union[None, Unset, str]):
        organization_role (Union[None, Unset, str]):
    """

    id: str
    email: str
    organization_id: str
    user_name: Union[None, Unset, str] = UNSET
    organization_role: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        organization_id = self.organization_id

        user_name: Union[None, Unset, str]
        if isinstance(self.user_name, Unset):
            user_name = UNSET
        else:
            user_name = self.user_name

        organization_role: Union[None, Unset, str]
        if isinstance(self.organization_role, Unset):
            organization_role = UNSET
        else:
            organization_role = self.organization_role

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "email": email,
                "organization_id": organization_id,
            }
        )
        if user_name is not UNSET:
            field_dict["user_name"] = user_name
        if organization_role is not UNSET:
            field_dict["organization_role"] = organization_role

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        email = d.pop("email")

        organization_id = d.pop("organization_id")

        def _parse_user_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        user_name = _parse_user_name(d.pop("user_name", UNSET))

        def _parse_organization_role(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        organization_role = _parse_organization_role(d.pop("organization_role", UNSET))

        me_response = cls(
            id=id,
            email=email,
            organization_id=organization_id,
            user_name=user_name,
            organization_role=organization_role,
        )

        me_response.additional_properties = d
        return me_response

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
