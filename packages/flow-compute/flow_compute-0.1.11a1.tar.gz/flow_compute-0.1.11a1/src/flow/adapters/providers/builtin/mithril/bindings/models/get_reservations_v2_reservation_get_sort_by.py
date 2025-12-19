from enum import Enum


class GetReservationsV2ReservationGetSortBy(str, Enum):
    CREATED_AT = "created_at"
    STATUS = "status"

    def __str__(self) -> str:
        return str(self.value)
