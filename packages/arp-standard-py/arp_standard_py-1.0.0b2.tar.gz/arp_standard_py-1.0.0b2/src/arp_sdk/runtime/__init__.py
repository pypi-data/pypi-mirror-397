"""ARP Runtime API facade (preferred) + low-level client package."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

__all__ = [
    'ArpApiError',
    'CancelRunRequest',
    'CreateRunRequest',
    'GetRunResultRequest',
    'GetRunStatusRequest',
    'Health',
    'HealthRequest',
    'RunRequest',
    'RunResult',
    'RunStatus',
    'RuntimeClient',
    'StreamRunEventsRequest',
    'VersionInfo',
    'VersionRequest',
]

_EXPORT_MAP: dict[str, str] = {
    'CancelRunRequest': '.sdk',
    'CreateRunRequest': '.sdk',
    'GetRunResultRequest': '.sdk',
    'GetRunStatusRequest': '.sdk',
    'Health': '.models',
    'HealthRequest': '.sdk',
    'RunRequest': '.models',
    'RunResult': '.models',
    'RunStatus': '.models',
    'RuntimeClient': '.sdk',
    'StreamRunEventsRequest': '.sdk',
    'VersionInfo': '.models',
    'VersionRequest': '.sdk',
}

if TYPE_CHECKING:
    from arp_sdk.errors import ArpApiError
    from .sdk import CancelRunRequest, CreateRunRequest, GetRunResultRequest, GetRunStatusRequest, HealthRequest, RuntimeClient, StreamRunEventsRequest, VersionRequest
    from .models import Health, RunRequest, RunResult, RunStatus, VersionInfo

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

