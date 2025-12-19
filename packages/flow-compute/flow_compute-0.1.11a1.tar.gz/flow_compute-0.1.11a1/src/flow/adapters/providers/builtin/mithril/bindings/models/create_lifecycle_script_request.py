from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.public_lifecycle_script_scope import PublicLifecycleScriptScope
from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="CreateLifecycleScriptRequest")


@_attrs_define
class CreateLifecycleScriptRequest:
    """
    Attributes:
        project (str):
        name (str):
        content (str):
        description (Union[None, Unset, str]):  Default: ''.
        scope (Union[Unset, PublicLifecycleScriptScope]):
    """

    project: str
    name: str
    content: str
    description: Union[None, Unset, str] = ""
    scope: Union[Unset, PublicLifecycleScriptScope] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        project = self.project

        name = self.name

        content = self.content

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        scope: Union[Unset, str] = UNSET
        if not isinstance(self.scope, Unset):
            scope = self.scope.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "name": name,
                "content": content,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if scope is not UNSET:
            field_dict["scope"] = scope

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        project = d.pop("project")

        name = d.pop("name")

        content = d.pop("content")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        _scope = d.pop("scope", UNSET)
        scope: Union[Unset, PublicLifecycleScriptScope]
        if isinstance(_scope, Unset):
            scope = UNSET
        else:
            scope = PublicLifecycleScriptScope(_scope)

        create_lifecycle_script_request = cls(
            project=project,
            name=name,
            content=content,
            description=description,
            scope=scope,
        )

        create_lifecycle_script_request.additional_properties = d
        return create_lifecycle_script_request

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
