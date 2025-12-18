from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="UpdateBidRequest")


@_attrs_define
class UpdateBidRequest:
    """
    Attributes:
        limit_price (Union[None, Unset, str]):
        paused (Union[None, Unset, bool]):
        volumes (Union[None, Unset, list[str]]):
    """

    limit_price: Union[None, Unset, str] = UNSET
    paused: Union[None, Unset, bool] = UNSET
    volumes: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        limit_price: Union[None, Unset, str]
        if isinstance(self.limit_price, Unset):
            limit_price = UNSET
        else:
            limit_price = self.limit_price

        paused: Union[None, Unset, bool]
        if isinstance(self.paused, Unset):
            paused = UNSET
        else:
            paused = self.paused

        volumes: Union[None, Unset, list[str]]
        if isinstance(self.volumes, Unset):
            volumes = UNSET
        elif isinstance(self.volumes, list):
            volumes = self.volumes

        else:
            volumes = self.volumes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if limit_price is not UNSET:
            field_dict["limit_price"] = limit_price
        if paused is not UNSET:
            field_dict["paused"] = paused
        if volumes is not UNSET:
            field_dict["volumes"] = volumes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_limit_price(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        limit_price = _parse_limit_price(d.pop("limit_price", UNSET))

        def _parse_paused(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        paused = _parse_paused(d.pop("paused", UNSET))

        def _parse_volumes(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                volumes_type_0 = cast(list[str], data)

                return volumes_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        volumes = _parse_volumes(d.pop("volumes", UNSET))

        update_bid_request = cls(
            limit_price=limit_price,
            paused=paused,
            volumes=volumes,
        )

        update_bid_request.additional_properties = d
        return update_bid_request

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
