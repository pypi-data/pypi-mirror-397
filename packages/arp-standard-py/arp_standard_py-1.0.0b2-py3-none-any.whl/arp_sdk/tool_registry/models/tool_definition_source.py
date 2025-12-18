from enum import Enum

class ToolDefinitionSource(str, Enum):
    REGISTRY_LOCAL = "registry_local"
    REMOTE = "remote"

    def __str__(self) -> str:
        return str(self.value)
