from enum import Enum


class ReasoningConfigSchemaSummary(str, Enum):
    AUTO = "auto"
    CONCISE = "concise"
    DETAILED = "detailed"
    OFF = "off"

    def __str__(self) -> str:
        return str(self.value)
