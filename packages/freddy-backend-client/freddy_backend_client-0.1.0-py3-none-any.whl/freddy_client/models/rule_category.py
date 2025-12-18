from enum import Enum


class RuleCategory(str, Enum):
    CREATIVE = "creative"
    CUSTOM = "custom"
    PROFESSIONAL = "professional"
    SAFETY = "safety"
    TECHNICAL = "technical"

    def __str__(self) -> str:
        return str(self.value)
