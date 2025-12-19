from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="QuotaModel")


@_attrs_define
class QuotaModel:
    """Unified quota model for all quota types (instances, storage, Kubernetes).

    Attributes:
        fid (str): Unique identifier for the quota
        project (str): Project FID this quota belongs to
        product_type (str): Type of product (e.g., 'Spot', 'Reservations', 'Storage')
        total_quantity (int): Total quota quantity used
        used_quantity (int): Total quota quantity used
        units (str): Units for the quota (e.g., 'instances', 'GB')
        name (str): Human-readable display name for the quota
        instance_type (Union[None, Unset, str]): Instance type FID for instance quotas
    """

    fid: str
    project: str
    product_type: str
    total_quantity: int
    used_quantity: int
    units: str
    name: str
    instance_type: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fid = self.fid

        project = self.project

        product_type = self.product_type

        total_quantity = self.total_quantity

        used_quantity = self.used_quantity

        units = self.units

        name = self.name

        instance_type: Union[None, Unset, str]
        if isinstance(self.instance_type, Unset):
            instance_type = UNSET
        else:
            instance_type = self.instance_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fid": fid,
                "project": project,
                "product_type": product_type,
                "total_quantity": total_quantity,
                "used_quantity": used_quantity,
                "units": units,
                "name": name,
            }
        )
        if instance_type is not UNSET:
            field_dict["instance_type"] = instance_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fid = d.pop("fid")

        project = d.pop("project")

        product_type = d.pop("product_type")

        total_quantity = d.pop("total_quantity")

        used_quantity = d.pop("used_quantity")

        units = d.pop("units")

        name = d.pop("name")

        def _parse_instance_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        instance_type = _parse_instance_type(d.pop("instance_type", UNSET))

        quota_model = cls(
            fid=fid,
            project=project,
            product_type=product_type,
            total_quantity=total_quantity,
            used_quantity=used_quantity,
            units=units,
            name=name,
            instance_type=instance_type,
        )

        quota_model.additional_properties = d
        return quota_model

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
