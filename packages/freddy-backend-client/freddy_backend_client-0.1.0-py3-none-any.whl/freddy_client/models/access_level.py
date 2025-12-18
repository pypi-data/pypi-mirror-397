from enum import Enum


class AccessLevel(str, Enum):
    EDIT = "edit"
    OWNER = "owner"
    VIEW = "view"

    def __str__(self) -> str:
        return str(self.value)
