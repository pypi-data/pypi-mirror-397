from enum import Enum


class GetInstancesV2InstancesGetSortBy(str, Enum):
    CREATED_AT = "created_at"
    INSTANCE_STATUS = "instance_status"
    INSTANCE_TYPE_FID = "instance_type_fid"

    def __str__(self) -> str:
        return str(self.value)
