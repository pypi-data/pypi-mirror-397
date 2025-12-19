from enum import Enum

class RuntimeInstanceState(str, Enum):
    BUSY = "busy"
    ERROR = "error"
    READY = "ready"
    STARTING = "starting"
    STOPPED = "stopped"
    STOPPING = "stopping"

    def __str__(self) -> str:
        return str(self.value)
