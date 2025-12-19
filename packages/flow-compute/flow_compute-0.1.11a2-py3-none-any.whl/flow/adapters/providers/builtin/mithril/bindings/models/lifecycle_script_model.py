from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.lifecycle_script_scope import LifecycleScriptScope


T = TypeVar("T", bound="LifecycleScriptModel")


@_attrs_define
class LifecycleScriptModel:
    """
    Attributes:
        fid (str):
        name (str):
        description (str):
        content_url (str):
        project (str):
        created_at (str):
        created_by (str):
        last_modified_at (str):
        last_modified_by (str):
        scope (LifecycleScriptScope):
    """

    fid: str
    name: str
    description: str
    content_url: str
    project: str
    created_at: str
    created_by: str
    last_modified_at: str
    last_modified_by: str
    scope: LifecycleScriptScope
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fid = self.fid

        name = self.name

        description = self.description

        content_url = self.content_url

        project = self.project

        created_at = self.created_at

        created_by = self.created_by

        last_modified_at = self.last_modified_at

        last_modified_by = self.last_modified_by

        scope = self.scope.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fid": fid,
                "name": name,
                "description": description,
                "content_url": content_url,
                "project": project,
                "created_at": created_at,
                "created_by": created_by,
                "last_modified_at": last_modified_at,
                "last_modified_by": last_modified_by,
                "scope": scope,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fid = d.pop("fid")

        name = d.pop("name")

        description = d.pop("description")

        content_url = d.pop("content_url")

        project = d.pop("project")

        created_at = d.pop("created_at")

        created_by = d.pop("created_by")

        last_modified_at = d.pop("last_modified_at")

        last_modified_by = d.pop("last_modified_by")

        scope = LifecycleScriptScope(d.pop("scope"))

        lifecycle_script_model = cls(
            fid=fid,
            name=name,
            description=description,
            content_url=content_url,
            project=project,
            created_at=created_at,
            created_by=created_by,
            last_modified_at=last_modified_at,
            last_modified_by=last_modified_by,
            scope=scope,
        )

        lifecycle_script_model.additional_properties = d
        return lifecycle_script_model

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
