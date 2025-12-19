from enum import Enum


class GetBidsV2SpotBidsGetSortBy(str, Enum):
    CREATED_AT = "created_at"
    STATUS = "status"

    def __str__(self) -> str:
        return str(self.value)
