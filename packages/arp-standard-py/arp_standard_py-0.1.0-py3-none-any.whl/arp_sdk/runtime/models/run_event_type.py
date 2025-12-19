from enum import Enum

class RunEventType(str, Enum):
    ERROR = "error"
    FINAL = "final"
    STEP = "step"
    TOKEN = "token"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"

    def __str__(self) -> str:
        return str(self.value)
