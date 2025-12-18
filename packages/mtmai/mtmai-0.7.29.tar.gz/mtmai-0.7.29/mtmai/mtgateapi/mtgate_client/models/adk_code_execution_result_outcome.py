from enum import Enum


class AdkCodeExecutionResultOutcome(str, Enum):
    DEADLINE_EXCEEDED = "DEADLINE_EXCEEDED"
    FAILED = "FAILED"
    OK = "OK"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return str(self.value)
