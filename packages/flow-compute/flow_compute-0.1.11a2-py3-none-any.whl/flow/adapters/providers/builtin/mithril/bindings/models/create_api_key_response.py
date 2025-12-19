from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="CreateApiKeyResponse")


@_attrs_define
class CreateApiKeyResponse:
    """
    Attributes:
        fid (str):
        name (str):
        created_at (str):
        expires_at (str):
        snippet (str):
        secret (str):
        deactivated_at (Union[None, Unset, str]):
    """

    fid: str
    name: str
    created_at: str
    expires_at: str
    snippet: str
    secret: str
    deactivated_at: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fid = self.fid

        name = self.name

        created_at = self.created_at

        expires_at = self.expires_at

        snippet = self.snippet

        secret = self.secret

        deactivated_at: Union[None, Unset, str]
        if isinstance(self.deactivated_at, Unset):
            deactivated_at = UNSET
        else:
            deactivated_at = self.deactivated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fid": fid,
                "name": name,
                "created_at": created_at,
                "expires_at": expires_at,
                "snippet": snippet,
                "secret": secret,
            }
        )
        if deactivated_at is not UNSET:
            field_dict["deactivated_at"] = deactivated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fid = d.pop("fid")

        name = d.pop("name")

        created_at = d.pop("created_at")

        expires_at = d.pop("expires_at")

        snippet = d.pop("snippet")

        secret = d.pop("secret")

        def _parse_deactivated_at(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        deactivated_at = _parse_deactivated_at(d.pop("deactivated_at", UNSET))

        create_api_key_response = cls(
            fid=fid,
            name=name,
            created_at=created_at,
            expires_at=expires_at,
            snippet=snippet,
            secret=secret,
            deactivated_at=deactivated_at,
        )

        create_api_key_response.additional_properties = d
        return create_api_key_response

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
