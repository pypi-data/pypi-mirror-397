from enum import Enum


class EntityType(str, Enum):
    ASSISTANT = "assistant"
    MODEL = "model"
    ORGANIZATION = "organization"
    USER = "user"
    VECTOR_STORE = "vector_store"

    def __str__(self) -> str:
        return str(self.value)
