from enum import Enum


class KubernetesClusterModelStatus(str, Enum):
    AVAILABLE = "Available"
    PENDING = "Pending"
    TERMINATED = "Terminated"

    def __str__(self) -> str:
        return str(self.value)
