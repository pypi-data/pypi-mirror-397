from enum import Enum


class ListLifecycleScriptsV2LifecycleScriptsGetSortBy(str, Enum):
    CREATED_AT = "created_at"
    LAST_MODIFIED_AT = "last_modified_at"

    def __str__(self) -> str:
        return str(self.value)
