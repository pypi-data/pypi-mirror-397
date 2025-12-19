"""ARP Tool Registry API facade (preferred) + low-level client package."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

__all__ = [
    'ArpApiError',
    'GetToolRequest',
    'Health',
    'HealthRequest',
    'InvokeToolRequest',
    'ListToolsRequest',
    'ToolDefinition',
    'ToolInvocationResult',
    'ToolRegistryClient',
    'VersionInfo',
    'VersionRequest',
]

_EXPORT_MAP: dict[str, str] = {
    'GetToolRequest': '.sdk',
    'Health': '.models',
    'HealthRequest': '.sdk',
    'InvokeToolRequest': '.sdk',
    'ListToolsRequest': '.sdk',
    'ToolDefinition': '.models',
    'ToolInvocationResult': '.models',
    'ToolRegistryClient': '.sdk',
    'VersionInfo': '.models',
    'VersionRequest': '.sdk',
}

if TYPE_CHECKING:
    from arp_sdk.errors import ArpApiError
    from .sdk import GetToolRequest, HealthRequest, InvokeToolRequest, ListToolsRequest, ToolRegistryClient, VersionRequest
    from .models import Health, ToolDefinition, ToolInvocationResult, VersionInfo

def __getattr__(name: str) -> Any:
    if name == "ArpApiError":
        from arp_sdk.errors import ArpApiError as _ArpApiError

        return _ArpApiError
    module = _EXPORT_MAP.get(name)
    if module is None:
        raise AttributeError(name)
    if module.startswith("."):
        return getattr(import_module(module, __name__), name)
    return getattr(import_module(module), name)

