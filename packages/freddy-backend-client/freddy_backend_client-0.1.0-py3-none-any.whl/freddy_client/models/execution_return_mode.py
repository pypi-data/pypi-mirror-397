from enum import Enum


class ExecutionReturnMode(str, Enum):
    POLL = "poll"
    WAIT = "wait"

    def __str__(self) -> str:
        return str(self.value)
