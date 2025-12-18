from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union


T = TypeVar("T", bound="InstanceModel")


@_attrs_define
class InstanceModel:
    """
    Attributes:
        fid (str):
        name (str):
        project (str):
        created_at (str):
        created_by (str):
        instance_type (str):
        status (str):
        region (Union[None, Unset, str]):
        bid (Union[None, Unset, str]):
        reservation (Union[None, Unset, str]):
        ssh_destination (Union[None, Unset, str]):
        private_ip (Union[None, Unset, str]):
    """

    fid: str
    name: str
    project: str
    created_at: str
    created_by: str
    instance_type: str
    status: str
    region: Union[None, Unset, str] = UNSET
    bid: Union[None, Unset, str] = UNSET
    reservation: Union[None, Unset, str] = UNSET
    ssh_destination: Union[None, Unset, str] = UNSET
    private_ip: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fid = self.fid

        name = self.name

        project = self.project

        created_at = self.created_at

        created_by = self.created_by

        instance_type = self.instance_type

        status = self.status

        region: Union[None, Unset, str]
        if isinstance(self.region, Unset):
            region = UNSET
        else:
            region = self.region

        bid: Union[None, Unset, str]
        if isinstance(self.bid, Unset):
            bid = UNSET
        else:
            bid = self.bid

        reservation: Union[None, Unset, str]
        if isinstance(self.reservation, Unset):
            reservation = UNSET
        else:
            reservation = self.reservation

        ssh_destination: Union[None, Unset, str]
        if isinstance(self.ssh_destination, Unset):
            ssh_destination = UNSET
        else:
            ssh_destination = self.ssh_destination

        private_ip: Union[None, Unset, str]
        if isinstance(self.private_ip, Unset):
            private_ip = UNSET
        else:
            private_ip = self.private_ip

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fid": fid,
                "name": name,
                "project": project,
                "created_at": created_at,
                "created_by": created_by,
                "instance_type": instance_type,
                "status": status,
            }
        )
        if region is not UNSET:
            field_dict["region"] = region
        if bid is not UNSET:
            field_dict["bid"] = bid
        if reservation is not UNSET:
            field_dict["reservation"] = reservation
        if ssh_destination is not UNSET:
            field_dict["ssh_destination"] = ssh_destination
        if private_ip is not UNSET:
            field_dict["private_ip"] = private_ip

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fid = d.pop("fid")

        name = d.pop("name")

        project = d.pop("project")

        created_at = d.pop("created_at")

        created_by = d.pop("created_by")

        instance_type = d.pop("instance_type")

        status = d.pop("status")

        def _parse_region(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        region = _parse_region(d.pop("region", UNSET))

        def _parse_bid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        bid = _parse_bid(d.pop("bid", UNSET))

        def _parse_reservation(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        reservation = _parse_reservation(d.pop("reservation", UNSET))

        def _parse_ssh_destination(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        ssh_destination = _parse_ssh_destination(d.pop("ssh_destination", UNSET))

        def _parse_private_ip(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        private_ip = _parse_private_ip(d.pop("private_ip", UNSET))

        instance_model = cls(
            fid=fid,
            name=name,
            project=project,
            created_at=created_at,
            created_by=created_by,
            instance_type=instance_type,
            status=status,
            region=region,
            bid=bid,
            reservation=reservation,
            ssh_destination=ssh_destination,
            private_ip=private_ip,
        )

        instance_model.additional_properties = d
        return instance_model

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
