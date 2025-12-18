from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset


T = TypeVar("T", bound="HistoricalPricePointModel")


@_attrs_define
class HistoricalPricePointModel:
    """A single historical price point for an instance type in a region.

    Attributes:
        spot_instance_price (str): Spot price per hour in dollars
        reserved_instance_price (str): Reserved price per hour in dollars
        timestamp (str): Timestamp when this price was recorded
        instance_type (str): Instance type FID
        region (str): Region name
    """

    spot_instance_price: str
    reserved_instance_price: str
    timestamp: str
    instance_type: str
    region: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        spot_instance_price = self.spot_instance_price

        reserved_instance_price = self.reserved_instance_price

        timestamp = self.timestamp

        instance_type = self.instance_type

        region = self.region

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "spot_instance_price": spot_instance_price,
                "reserved_instance_price": reserved_instance_price,
                "timestamp": timestamp,
                "instance_type": instance_type,
                "region": region,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        spot_instance_price = d.pop("spot_instance_price")

        reserved_instance_price = d.pop("reserved_instance_price")

        timestamp = d.pop("timestamp")

        instance_type = d.pop("instance_type")

        region = d.pop("region")

        historical_price_point_model = cls(
            spot_instance_price=spot_instance_price,
            reserved_instance_price=reserved_instance_price,
            timestamp=timestamp,
            instance_type=instance_type,
            region=region,
        )

        historical_price_point_model.additional_properties = d
        return historical_price_point_model

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
