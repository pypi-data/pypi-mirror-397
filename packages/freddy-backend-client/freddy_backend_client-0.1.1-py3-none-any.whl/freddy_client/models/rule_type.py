from enum import Enum


class RuleType(str, Enum):
    BEHAVIOR = "behavior"
    CONSTRAINT = "constraint"
    CONTENT_POLICY = "content_policy"
    CONTEXT = "context"
    FORMATTING = "formatting"
    GUARDRAILS = "guardrails"

    def __str__(self) -> str:
        return str(self.value)
