from enum import Enum


class GetBidsV2SpotBidsGetStatus(str, Enum):
    ALLOCATED = "Allocated"
    OPEN = "Open"
    PAUSED = "Paused"
    PREEMPTING = "Preempting"
    TERMINATED = "Terminated"

    def __str__(self) -> str:
        return str(self.value)
