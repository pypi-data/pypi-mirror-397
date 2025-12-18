from enum import Enum


class LifecycleScriptScope(str, Enum):
    ORGANIZATION = "ORGANIZATION"
    PLATFORM = "PLATFORM"
    PROJECT = "PROJECT"

    def __str__(self) -> str:
        return str(self.value)
