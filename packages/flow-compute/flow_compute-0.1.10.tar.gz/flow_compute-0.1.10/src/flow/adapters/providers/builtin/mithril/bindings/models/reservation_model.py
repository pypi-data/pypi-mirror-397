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
    from ..models.launch_specification_model import LaunchSpecificationModel


T = TypeVar("T", bound="ReservationModel")


@_attrs_define
class ReservationModel:
    """
    Attributes:
        fid (str):
        name (str):
        project (str):
        created_by (str):
        created_at (str):
        instance_quantity (int):
        instance_type (str):
        instances (list[str]):
        launch_specification (LaunchSpecificationModel):
        status (str):
        start_time (str):
        end_time (str):
        total_price (str):
        unit_price (str):
        deactivated_at (Union[None, Unset, str]):
        region (Union[None, Unset, str]):
    """

    fid: str
    name: str
    project: str
    created_by: str
    created_at: str
    instance_quantity: int
    instance_type: str
    instances: list[str]
    launch_specification: "LaunchSpecificationModel"
    status: str
    start_time: str
    end_time: str
    total_price: str
    unit_price: str
    deactivated_at: Union[None, Unset, str] = UNSET
    region: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.launch_specification_model import LaunchSpecificationModel

        fid = self.fid

        name = self.name

        project = self.project

        created_by = self.created_by

        created_at = self.created_at

        instance_quantity = self.instance_quantity

        instance_type = self.instance_type

        instances = self.instances

        launch_specification = self.launch_specification.to_dict()

        status = self.status

        start_time = self.start_time

        end_time = self.end_time

        total_price = self.total_price

        unit_price = self.unit_price

        deactivated_at: Union[None, Unset, str]
        if isinstance(self.deactivated_at, Unset):
            deactivated_at = UNSET
        else:
            deactivated_at = self.deactivated_at

        region: Union[None, Unset, str]
        if isinstance(self.region, Unset):
            region = UNSET
        else:
            region = self.region

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fid": fid,
                "name": name,
                "project": project,
                "created_by": created_by,
                "created_at": created_at,
                "instance_quantity": instance_quantity,
                "instance_type": instance_type,
                "instances": instances,
                "launch_specification": launch_specification,
                "status": status,
                "start_time": start_time,
                "end_time": end_time,
                "total_price": total_price,
                "unit_price": unit_price,
            }
        )
        if deactivated_at is not UNSET:
            field_dict["deactivated_at"] = deactivated_at
        if region is not UNSET:
            field_dict["region"] = region

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.launch_specification_model import LaunchSpecificationModel

        d = dict(src_dict)
        fid = d.pop("fid")

        name = d.pop("name")

        project = d.pop("project")

        created_by = d.pop("created_by")

        created_at = d.pop("created_at")

        instance_quantity = d.pop("instance_quantity")

        instance_type = d.pop("instance_type")

        instances = cast(list[str], d.pop("instances"))

        launch_specification = LaunchSpecificationModel.from_dict(d.pop("launch_specification"))

        status = d.pop("status")

        start_time = d.pop("start_time")

        end_time = d.pop("end_time")

        total_price = d.pop("total_price")

        unit_price = d.pop("unit_price")

        def _parse_deactivated_at(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        deactivated_at = _parse_deactivated_at(d.pop("deactivated_at", UNSET))

        def _parse_region(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        region = _parse_region(d.pop("region", UNSET))

        reservation_model = cls(
            fid=fid,
            name=name,
            project=project,
            created_by=created_by,
            created_at=created_at,
            instance_quantity=instance_quantity,
            instance_type=instance_type,
            instances=instances,
            launch_specification=launch_specification,
            status=status,
            start_time=start_time,
            end_time=end_time,
            total_price=total_price,
            unit_price=unit_price,
            deactivated_at=deactivated_at,
            region=region,
        )

        reservation_model.additional_properties = d
        return reservation_model

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
