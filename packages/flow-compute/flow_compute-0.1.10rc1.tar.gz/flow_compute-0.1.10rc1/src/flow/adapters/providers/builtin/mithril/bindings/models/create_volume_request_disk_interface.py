from enum import Enum


class CreateVolumeRequestDiskInterface(str, Enum):
    BLOCK = "Block"
    FILE = "File"

    def __str__(self) -> str:
        return str(self.value)
