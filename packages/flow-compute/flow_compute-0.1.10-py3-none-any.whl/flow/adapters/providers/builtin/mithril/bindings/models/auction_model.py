from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset


T = TypeVar("T", bound="AuctionModel")


@_attrs_define
class AuctionModel:
    """
    Attributes:
        fid (str):
        instance_type (str):
        region (str):
        capacity (int):
        last_instance_price (str):
    """

    fid: str
    instance_type: str
    region: str
    capacity: int
    last_instance_price: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fid = self.fid

        instance_type = self.instance_type

        region = self.region

        capacity = self.capacity

        last_instance_price = self.last_instance_price

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fid": fid,
                "instance_type": instance_type,
                "region": region,
                "capacity": capacity,
                "last_instance_price": last_instance_price,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fid = d.pop("fid")

        instance_type = d.pop("instance_type")

        region = d.pop("region")

        capacity = d.pop("capacity")

        last_instance_price = d.pop("last_instance_price")

        auction_model = cls(
            fid=fid,
            instance_type=instance_type,
            region=region,
            capacity=capacity,
            last_instance_price=last_instance_price,
        )

        auction_model.additional_properties = d
        return auction_model

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
