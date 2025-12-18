from enum import Enum


class ReasoningConfigEffort(str, Enum):
    HIGH = "high"
    LOW = "low"
    MAXIMUM = "maximum"
    MEDIUM = "medium"
    OFF = "off"

    def __str__(self) -> str:
        return str(self.value)
