from enum import Enum


class AdkExecutableCodeLanguage(str, Enum):
    PYTHON = "PYTHON"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return str(self.value)
