from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeVar, overload

import httpx

from arp_sdk.errors import ArpApiError
from arp_sdk.models import (
    InstanceCreateRequest,
    InstanceCreateResponse,
    InstanceListResponse,
    InstanceRegisterRequest,
    InstanceRegisterResponse,
    RunListResponse,
    RunRequest,
    RunResult,
    RunStatus,
    RuntimeProfile,
    RuntimeProfileListResponse,
    RuntimeProfileUpsertRequest,
    TraceResponse,
)

from .api.health import (
    health,
)

from .api.instances import (
    create_instances,
    delete_instance,
    list_instances,
    register_instance,
)

from .api.runs import (
    get_run_result,
    get_run_status,
    get_run_trace,
    list_runs,
    submit_run,
)

from .api.runtime_profiles import (
    delete_runtime_profile,
    list_runtime_profiles,
    upsert_runtime_profile,
)

from .api.version import (
    version,
)

from .client import Client as _LowLevelClient
from .models import ErrorEnvelope as _ErrorEnvelope
from .models import Health, VersionInfo
from .models import (
    RunRequest as _RunRequest,
)
from .types import Response as _Response
from .types import Unset as _Unset
from .types import UNSET as _UNSET

T = TypeVar("T")

def _coerce_model(value: Any, target: type[T]) -> T:
    if isinstance(value, target):
        return value
    if hasattr(value, "to_dict") and hasattr(target, "from_dict"):
        return target.from_dict(value.to_dict())  # type: ignore[attr-defined]
    if isinstance(value, dict) and hasattr(target, "from_dict"):
        return target.from_dict(value)  # type: ignore[attr-defined]
    raise TypeError(f"Cannot coerce {type(value)} to {target}")

def _raise_for_error_envelope(*, envelope: _ErrorEnvelope, status_code: int | None, raw: Any | None) -> None:
    details: Any | None = None
    if not isinstance(envelope.error.details, _Unset):
        details = envelope.error.details.to_dict()
    raise ArpApiError(
        code=str(envelope.error.code),
        message=str(envelope.error.message),
        details=details,
        status_code=status_code,
        raw=raw,
    )

def _unwrap(response: _Response[Any], *, allow_none: bool = False) -> Any:
    parsed = response.parsed
    if parsed is None:
        if allow_none:
            return None
        raise ArpApiError(
            code="unexpected_empty_response",
            message="API returned an empty response",
            status_code=int(response.status_code),
            raw=response.content,
        )
    if isinstance(parsed, _ErrorEnvelope):
        _raise_for_error_envelope(envelope=parsed, status_code=int(response.status_code), raw=parsed.to_dict())
    return parsed

@dataclass(slots=True)
class CreateInstancesRequest:
    body: InstanceCreateRequest

@dataclass(slots=True)
class DeleteInstanceRequest:
    instance_id: str

@dataclass(slots=True)
class DeleteRuntimeProfileRequest:
    runtime_profile: str

@dataclass(slots=True)
class GetRunResultRequest:
    run_id: str

@dataclass(slots=True)
class GetRunStatusRequest:
    run_id: str

@dataclass(slots=True)
class GetRunTraceRequest:
    run_id: str

@dataclass(slots=True)
class HealthRequest:
    pass

@dataclass(slots=True)
class ListInstancesRequest:
    pass

@dataclass(slots=True)
class ListRunsRequest:
    page_size: int | None = None
    page_token: str | None = None

@dataclass(slots=True)
class ListRuntimeProfilesRequest:
    pass

@dataclass(slots=True)
class RegisterInstanceRequest:
    body: InstanceRegisterRequest

@dataclass(slots=True)
class SubmitRunRequest:
    body: RunRequest

@dataclass(slots=True)
class UpsertRuntimeProfileRequest:
    runtime_profile: str
    body: RuntimeProfileUpsertRequest

@dataclass(slots=True)
class VersionRequest:
    pass

class DaemonClient:
    def __init__(
        self,
        base_url: str | None = None,
        *,
        client: _LowLevelClient | None = None,
        timeout: httpx.Timeout | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        verify_ssl: Any = True,
        follow_redirects: bool = False,
        raise_on_unexpected_status: bool = False,
        httpx_args: dict[str, Any] | None = None,
    ) -> None:
        if client is None:
            if base_url is None:
                raise ValueError("base_url is required when client is not provided")
            client = _LowLevelClient(
                base_url=base_url,
                timeout=timeout,
                headers={} if headers is None else dict(headers),
                cookies={} if cookies is None else dict(cookies),
                verify_ssl=verify_ssl,
                follow_redirects=follow_redirects,
                raise_on_unexpected_status=raise_on_unexpected_status,
                httpx_args={} if httpx_args is None else dict(httpx_args),
            )
        self._client = client

    @property
    def raw_client(self) -> _LowLevelClient:
        return self._client

    @overload
    def create_instances(self, body: InstanceCreateRequest) -> InstanceCreateResponse: ...

    @overload
    def create_instances(self, body: CreateInstancesRequest) -> InstanceCreateResponse: ...

    def create_instances(self, body: CreateInstancesRequest | InstanceCreateRequest) -> InstanceCreateResponse:
        payload = body.body if isinstance(body, CreateInstancesRequest) else body
        resp = create_instances.sync_detailed(client=self._client, body=payload)
        result = _unwrap(resp)
        return result

    @overload
    def delete_instance(self, instance_id: str) -> None: ...

    @overload
    def delete_instance(self, instance_id: DeleteInstanceRequest) -> None: ...

    def delete_instance(self, instance_id: DeleteInstanceRequest | str) -> None:
        value = instance_id.instance_id if isinstance(instance_id, DeleteInstanceRequest) else instance_id
        instance_id = value
        resp = delete_instance.sync_detailed(client=self._client, instance_id=instance_id)
        _unwrap(resp, allow_none=True)
        return None

    @overload
    def delete_runtime_profile(self, runtime_profile: str) -> None: ...

    @overload
    def delete_runtime_profile(self, runtime_profile: DeleteRuntimeProfileRequest) -> None: ...

    def delete_runtime_profile(self, runtime_profile: DeleteRuntimeProfileRequest | str) -> None:
        value = runtime_profile.runtime_profile if isinstance(runtime_profile, DeleteRuntimeProfileRequest) else runtime_profile
        runtime_profile = value
        resp = delete_runtime_profile.sync_detailed(client=self._client, runtime_profile=runtime_profile)
        _unwrap(resp, allow_none=True)
        return None

    @overload
    def get_run_result(self, run_id: str) -> RunResult: ...

    @overload
    def get_run_result(self, run_id: GetRunResultRequest) -> RunResult: ...

    def get_run_result(self, run_id: GetRunResultRequest | str) -> RunResult:
        value = run_id.run_id if isinstance(run_id, GetRunResultRequest) else run_id
        run_id = value
        resp = get_run_result.sync_detailed(client=self._client, run_id=run_id)
        result = _unwrap(resp)
        return _coerce_model(result, RunResult)

    @overload
    def get_run_status(self, run_id: str) -> RunStatus: ...

    @overload
    def get_run_status(self, run_id: GetRunStatusRequest) -> RunStatus: ...

    def get_run_status(self, run_id: GetRunStatusRequest | str) -> RunStatus:
        value = run_id.run_id if isinstance(run_id, GetRunStatusRequest) else run_id
        run_id = value
        resp = get_run_status.sync_detailed(client=self._client, run_id=run_id)
        result = _unwrap(resp)
        return _coerce_model(result, RunStatus)

    @overload
    def get_run_trace(self, run_id: str) -> TraceResponse: ...

    @overload
    def get_run_trace(self, run_id: GetRunTraceRequest) -> TraceResponse: ...

    def get_run_trace(self, run_id: GetRunTraceRequest | str) -> TraceResponse:
        value = run_id.run_id if isinstance(run_id, GetRunTraceRequest) else run_id
        run_id = value
        resp = get_run_trace.sync_detailed(client=self._client, run_id=run_id)
        result = _unwrap(resp)
        return result

    @overload
    def health(self) -> Health: ...

    @overload
    def health(self, request: HealthRequest) -> Health: ...

    def health(self, request: HealthRequest | None = None) -> Health:
        _ = request
        resp = health.sync_detailed(client=self._client)
        return _unwrap(resp)

    @overload
    def list_instances(self) -> InstanceListResponse: ...

    @overload
    def list_instances(self, request: ListInstancesRequest) -> InstanceListResponse: ...

    def list_instances(self, request: ListInstancesRequest | None = None) -> InstanceListResponse:
        _ = request
        resp = list_instances.sync_detailed(client=self._client)
        return _unwrap(resp)

    @overload
    def list_runs(self) -> RunListResponse: ...

    @overload
    def list_runs(self, request: ListRunsRequest) -> RunListResponse: ...

    @overload
    def list_runs(self, *, page_size: int | None = None, page_token: str | None = None) -> RunListResponse: ...

    def list_runs(self, request: ListRunsRequest | None = None, *, page_size: int | None = None, page_token: str | None = None) -> RunListResponse:
        if request is not None:
            page_size = request.page_size
            page_token = request.page_token
        resp = list_runs.sync_detailed(client=self._client, page_size=_UNSET if page_size is None else page_size, page_token=_UNSET if page_token is None else page_token)
        return _unwrap(resp)

    @overload
    def list_runtime_profiles(self) -> RuntimeProfileListResponse: ...

    @overload
    def list_runtime_profiles(self, request: ListRuntimeProfilesRequest) -> RuntimeProfileListResponse: ...

    def list_runtime_profiles(self, request: ListRuntimeProfilesRequest | None = None) -> RuntimeProfileListResponse:
        _ = request
        resp = list_runtime_profiles.sync_detailed(client=self._client)
        return _unwrap(resp)

    @overload
    def register_instance(self, body: InstanceRegisterRequest) -> InstanceRegisterResponse: ...

    @overload
    def register_instance(self, body: RegisterInstanceRequest) -> InstanceRegisterResponse: ...

    def register_instance(self, body: RegisterInstanceRequest | InstanceRegisterRequest) -> InstanceRegisterResponse:
        payload = body.body if isinstance(body, RegisterInstanceRequest) else body
        resp = register_instance.sync_detailed(client=self._client, body=payload)
        result = _unwrap(resp)
        return result

    @overload
    def submit_run(self, body: RunRequest) -> RunStatus: ...

    @overload
    def submit_run(self, body: SubmitRunRequest) -> RunStatus: ...

    def submit_run(self, body: SubmitRunRequest | RunRequest) -> RunStatus:
        payload = body.body if isinstance(body, SubmitRunRequest) else body
        payload = _coerce_model(payload, _RunRequest)
        resp = submit_run.sync_detailed(client=self._client, body=payload)
        result = _unwrap(resp)
        return _coerce_model(result, RunStatus)

    def upsert_runtime_profile(self, request: UpsertRuntimeProfileRequest) -> RuntimeProfile:
        resp = upsert_runtime_profile.sync_detailed(client=self._client, runtime_profile=request.runtime_profile, body=request.body)
        result = _unwrap(resp)
        return result

    @overload
    def version(self) -> VersionInfo: ...

    @overload
    def version(self, request: VersionRequest) -> VersionInfo: ...

    def version(self, request: VersionRequest | None = None) -> VersionInfo:
        _ = request
        resp = version.sync_detailed(client=self._client)
        return _unwrap(resp)

__all__ = [
    'DaemonClient',
    'CreateInstancesRequest',
    'DeleteInstanceRequest',
    'DeleteRuntimeProfileRequest',
    'GetRunResultRequest',
    'GetRunStatusRequest',
    'GetRunTraceRequest',
    'HealthRequest',
    'ListInstancesRequest',
    'ListRunsRequest',
    'ListRuntimeProfilesRequest',
    'RegisterInstanceRequest',
    'SubmitRunRequest',
    'UpsertRuntimeProfileRequest',
    'VersionRequest',
]
