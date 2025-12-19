"""Public API for the Flow SDK.

Exports the primary client and essential models for GPU workload orchestration.
This is the stable public API - everything else is internal.
"""

# Primary client and legacy Flow class
# Decorators for convenience
from flow.sdk import decorators
from flow.sdk.client import Client, Flow

# Essential models
from flow.sdk.models import (
    AvailableInstance,
    Instance,
    Resources,
    RunParams,
    Task,
    TaskConfig,
    TaskSpec,
    TaskStatus,
    User,
    Volume,
    VolumeSpec,
)

__all__ = [
    "AvailableInstance",
    # Primary client (new)
    "Client",
    # Legacy client (deprecated but maintained)
    "Flow",
    # Instance types
    "Instance",
    "Resources",
    "RunParams",
    # Core models
    "Task",
    "TaskConfig",
    "TaskSpec",
    "TaskStatus",
    # User
    "User",
    # Storage
    "Volume",
    "VolumeSpec",
    # Utilities
    "decorators",
]
