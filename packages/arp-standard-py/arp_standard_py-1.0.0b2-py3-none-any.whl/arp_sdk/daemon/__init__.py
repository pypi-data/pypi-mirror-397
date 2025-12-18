"""ARP Daemon API facade (preferred) + low-level client package."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

__all__ = [
    'ArpApiError',
    'CreateInstancesRequest',
    'DaemonClient',
    'DeleteInstanceRequest',
    'DeleteRuntimeProfileRequest',
    'GetRunResultRequest',
    'GetRunStatusRequest',
    'GetRunTraceRequest',
    'Health',
    'HealthRequest',
    'InstanceCreateRequest',
    'InstanceCreateResponse',
    'InstanceListResponse',
    'InstanceRegisterRequest',
    'InstanceRegisterResponse',
    'ListInstancesRequest',
    'ListRunsRequest',
    'ListRuntimeProfilesRequest',
    'RegisterInstanceRequest',
    'RunListResponse',
    'RunRequest',
    'RunResult',
    'RunStatus',
    'RuntimeProfile',
    'RuntimeProfileListResponse',
    'RuntimeProfileUpsertRequest',
    'SubmitRunRequest',
    'TraceResponse',
    'UpsertRuntimeProfileRequest',
    'VersionInfo',
    'VersionRequest',
]

_EXPORT_MAP: dict[str, str] = {
    'CreateInstancesRequest': '.sdk',
    'DaemonClient': '.sdk',
    'DeleteInstanceRequest': '.sdk',
    'DeleteRuntimeProfileRequest': '.sdk',
    'GetRunResultRequest': '.sdk',
    'GetRunStatusRequest': '.sdk',
    'GetRunTraceRequest': '.sdk',
    'Health': '.models',
    'HealthRequest': '.sdk',
    'InstanceCreateRequest': '.models',
    'InstanceCreateResponse': '.models',
    'InstanceListResponse': '.models',
    'InstanceRegisterRequest': '.models',
    'InstanceRegisterResponse': '.models',
    'ListInstancesRequest': '.sdk',
    'ListRunsRequest': '.sdk',
    'ListRuntimeProfilesRequest': '.sdk',
    'RegisterInstanceRequest': '.sdk',
    'RunListResponse': '.models',
    'RunRequest': 'arp_sdk.runtime.models',
    'RunResult': 'arp_sdk.runtime.models',
    'RunStatus': 'arp_sdk.runtime.models',
    'RuntimeProfile': '.models',
    'RuntimeProfileListResponse': '.models',
    'RuntimeProfileUpsertRequest': '.models',
    'SubmitRunRequest': '.sdk',
    'TraceResponse': '.models',
    'UpsertRuntimeProfileRequest': '.sdk',
    'VersionInfo': '.models',
    'VersionRequest': '.sdk',
}

if TYPE_CHECKING:
    from arp_sdk.errors import ArpApiError
    from .sdk import CreateInstancesRequest, DaemonClient, DeleteInstanceRequest, DeleteRuntimeProfileRequest, GetRunResultRequest, GetRunStatusRequest, GetRunTraceRequest, HealthRequest, ListInstancesRequest, ListRunsRequest, ListRuntimeProfilesRequest, RegisterInstanceRequest, SubmitRunRequest, UpsertRuntimeProfileRequest, VersionRequest
    from .models import Health, InstanceCreateRequest, InstanceCreateResponse, InstanceListResponse, InstanceRegisterRequest, InstanceRegisterResponse, RunListResponse, RuntimeProfile, RuntimeProfileListResponse, RuntimeProfileUpsertRequest, TraceResponse, VersionInfo
    from arp_sdk.runtime.models import RunRequest, RunResult, RunStatus

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

