from enum import Enum


class GetAvailabilityV2ReservationAvailabilityGetMode(str, Enum):
    CHECK = "check"
    LATEST_END_TIME = "latest_end_time"
    SLOTS = "slots"

    def __str__(self) -> str:
        return str(self.value)
