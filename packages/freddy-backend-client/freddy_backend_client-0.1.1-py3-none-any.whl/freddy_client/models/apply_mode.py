from enum import Enum


class ApplyMode(str, Enum):
    ALWAYS = "always"
    AUTO = "auto"
    MANUAL = "manual"

    def __str__(self) -> str:
        return str(self.value)
