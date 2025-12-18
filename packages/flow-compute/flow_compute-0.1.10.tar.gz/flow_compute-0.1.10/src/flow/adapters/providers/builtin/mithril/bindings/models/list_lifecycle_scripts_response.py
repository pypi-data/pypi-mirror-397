from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
    from ..models.lifecycle_script_model import LifecycleScriptModel


T = TypeVar("T", bound="ListLifecycleScriptsResponse")


@_attrs_define
class ListLifecycleScriptsResponse:
    """
    Attributes:
        data (list['LifecycleScriptModel']):
        next_cursor (Union[None, Unset, str]):
    """

    data: list["LifecycleScriptModel"]
    next_cursor: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.lifecycle_script_model import LifecycleScriptModel

        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        next_cursor: Union[None, Unset, str]
        if isinstance(self.next_cursor, Unset):
            next_cursor = UNSET
        else:
            next_cursor = self.next_cursor

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )
        if next_cursor is not UNSET:
            field_dict["next_cursor"] = next_cursor

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.lifecycle_script_model import LifecycleScriptModel

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = LifecycleScriptModel.from_dict(data_item_data)

            data.append(data_item)

        def _parse_next_cursor(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        next_cursor = _parse_next_cursor(d.pop("next_cursor", UNSET))

        list_lifecycle_scripts_response = cls(
            data=data,
            next_cursor=next_cursor,
        )

        list_lifecycle_scripts_response.additional_properties = d
        return list_lifecycle_scripts_response

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
