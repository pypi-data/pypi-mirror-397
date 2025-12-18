from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
    from ..models.historical_price_point_model import HistoricalPricePointModel


T = TypeVar("T", bound="HistoricalPricesResponseModel")


@_attrs_define
class HistoricalPricesResponseModel:
    """Response model for historical pricing data.

    Attributes:
        prices (list['HistoricalPricePointModel']): List of historical price points
    """

    prices: list["HistoricalPricePointModel"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.historical_price_point_model import HistoricalPricePointModel

        prices = []
        for prices_item_data in self.prices:
            prices_item = prices_item_data.to_dict()
            prices.append(prices_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "prices": prices,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.historical_price_point_model import HistoricalPricePointModel

        d = dict(src_dict)
        prices = []
        _prices = d.pop("prices")
        for prices_item_data in _prices:
            prices_item = HistoricalPricePointModel.from_dict(prices_item_data)

            prices.append(prices_item)

        historical_prices_response_model = cls(
            prices=prices,
        )

        historical_prices_response_model.additional_properties = d
        return historical_prices_response_model

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
