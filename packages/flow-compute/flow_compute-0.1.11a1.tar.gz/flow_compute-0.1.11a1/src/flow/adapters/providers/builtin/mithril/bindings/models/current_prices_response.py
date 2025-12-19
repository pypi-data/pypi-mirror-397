from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="CurrentPricesResponse")


@_attrs_define
class CurrentPricesResponse:
    """
    Attributes:
        spot_price_cents (Union[None, Unset, int]):
        reserved_price_cents (Union[None, Unset, int]):
        minimum_price_cents (Union[None, Unset, int]):
    """

    spot_price_cents: Union[None, Unset, int] = UNSET
    reserved_price_cents: Union[None, Unset, int] = UNSET
    minimum_price_cents: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        spot_price_cents: Union[None, Unset, int]
        if isinstance(self.spot_price_cents, Unset):
            spot_price_cents = UNSET
        else:
            spot_price_cents = self.spot_price_cents

        reserved_price_cents: Union[None, Unset, int]
        if isinstance(self.reserved_price_cents, Unset):
            reserved_price_cents = UNSET
        else:
            reserved_price_cents = self.reserved_price_cents

        minimum_price_cents: Union[None, Unset, int]
        if isinstance(self.minimum_price_cents, Unset):
            minimum_price_cents = UNSET
        else:
            minimum_price_cents = self.minimum_price_cents

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if spot_price_cents is not UNSET:
            field_dict["spot_price_cents"] = spot_price_cents
        if reserved_price_cents is not UNSET:
            field_dict["reserved_price_cents"] = reserved_price_cents
        if minimum_price_cents is not UNSET:
            field_dict["minimum_price_cents"] = minimum_price_cents

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_spot_price_cents(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        spot_price_cents = _parse_spot_price_cents(d.pop("spot_price_cents", UNSET))

        def _parse_reserved_price_cents(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        reserved_price_cents = _parse_reserved_price_cents(d.pop("reserved_price_cents", UNSET))

        def _parse_minimum_price_cents(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        minimum_price_cents = _parse_minimum_price_cents(d.pop("minimum_price_cents", UNSET))

        current_prices_response = cls(
            spot_price_cents=spot_price_cents,
            reserved_price_cents=reserved_price_cents,
            minimum_price_cents=minimum_price_cents,
        )

        current_prices_response.additional_properties = d
        return current_prices_response

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
