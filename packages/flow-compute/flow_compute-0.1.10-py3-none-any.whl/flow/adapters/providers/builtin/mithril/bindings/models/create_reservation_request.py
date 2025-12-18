from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
    from ..models.launch_specification_model import LaunchSpecificationModel


T = TypeVar("T", bound="CreateReservationRequest")


@_attrs_define
class CreateReservationRequest:
    """
    Attributes:
        project (str):
        instance_type (str):
        region (str):
        start_time (Any):
        end_time (Any):
        instance_quantity (int):
        name (str):
        launch_specification (LaunchSpecificationModel):
    """

    project: str
    instance_type: str
    region: str
    start_time: Any
    end_time: Any
    instance_quantity: int
    name: str
    launch_specification: "LaunchSpecificationModel"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.launch_specification_model import LaunchSpecificationModel

        project = self.project

        instance_type = self.instance_type

        region = self.region

        start_time = self.start_time

        end_time = self.end_time

        instance_quantity = self.instance_quantity

        name = self.name

        launch_specification = self.launch_specification.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "instance_type": instance_type,
                "region": region,
                "start_time": start_time,
                "end_time": end_time,
                "instance_quantity": instance_quantity,
                "name": name,
                "launch_specification": launch_specification,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.launch_specification_model import LaunchSpecificationModel

        d = dict(src_dict)
        project = d.pop("project")

        instance_type = d.pop("instance_type")

        region = d.pop("region")

        start_time = d.pop("start_time")

        end_time = d.pop("end_time")

        instance_quantity = d.pop("instance_quantity")

        name = d.pop("name")

        launch_specification = LaunchSpecificationModel.from_dict(d.pop("launch_specification"))

        create_reservation_request = cls(
            project=project,
            instance_type=instance_type,
            region=region,
            start_time=start_time,
            end_time=end_time,
            instance_quantity=instance_quantity,
            name=name,
            launch_specification=launch_specification,
        )

        create_reservation_request.additional_properties = d
        return create_reservation_request

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
