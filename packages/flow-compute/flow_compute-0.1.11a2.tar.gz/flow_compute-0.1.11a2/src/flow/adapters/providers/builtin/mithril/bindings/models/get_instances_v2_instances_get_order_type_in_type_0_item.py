from enum import Enum


class GetInstancesV2InstancesGetOrderTypeInType0Item(str, Enum):
    BID = "Bid"
    RESERVATION = "Reservation"

    def __str__(self) -> str:
        return str(self.value)
