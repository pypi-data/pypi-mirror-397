from enum import Enum


class RuleScope(str, Enum):
    ASSISTANT = "assistant"
    GLOBAL = "global"
    MODEL = "model"
    ORGANIZATION = "organization"
    USER = "user"
    VECTOR_STORE = "vector_store"

    def __str__(self) -> str:
        return str(self.value)
