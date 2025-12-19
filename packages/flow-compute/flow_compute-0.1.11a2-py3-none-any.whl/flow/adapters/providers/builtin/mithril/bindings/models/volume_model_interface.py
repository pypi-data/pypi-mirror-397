from enum import Enum


class VolumeModelInterface(str, Enum):
    BLOCK = "Block"
    FILE = "File"

    def __str__(self) -> str:
        return str(self.value)
