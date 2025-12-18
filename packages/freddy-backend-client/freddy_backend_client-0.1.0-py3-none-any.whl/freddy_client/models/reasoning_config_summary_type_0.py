from enum import Enum


class ReasoningConfigSummaryType0(str, Enum):
    AUTO = "auto"
    CONCISE = "concise"
    DETAILED = "detailed"
    OFF = "off"

    def __str__(self) -> str:
        return str(self.value)
