from enum import Enum


class GetReservationsV2ReservationGetStatus(str, Enum):
    ACTIVE = "Active"
    CANCELED = "Canceled"
    ENDED = "Ended"
    PENDING = "Pending"

    def __str__(self) -> str:
        return str(self.value)
