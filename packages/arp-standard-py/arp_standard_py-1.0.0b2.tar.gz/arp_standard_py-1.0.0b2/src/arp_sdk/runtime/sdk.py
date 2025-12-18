from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeVar, overload

import httpx

from arp_sdk.errors import ArpApiError
from arp_sdk.models import (
    RunRequest,
    RunResult,
    RunStatus,
)

from .api.health import (
    health,
)

from .api.runs import (
    cancel_run,
    create_run,
    get_run_result,
    get_run_status,
    stream_run_events,
)

from .api.version import (
    version,
)

from .client import Client as _LowLevelClient
from .models import ErrorEnvelope as _ErrorEnvelope
from .models import Health, VersionInfo
from .types import Response as _Response
from .types import Unset as _Unset

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
class CancelRunRequest:
    run_id: str

@dataclass(slots=True)
class CreateRunRequest:
    body: RunRequest

@dataclass(slots=True)
class GetRunResultRequest:
    run_id: str

@dataclass(slots=True)
class GetRunStatusRequest:
    run_id: str

@dataclass(slots=True)
class HealthRequest:
    pass

@dataclass(slots=True)
class StreamRunEventsRequest:
    run_id: str

@dataclass(slots=True)
class VersionRequest:
    pass

class RuntimeClient:
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
    def cancel_run(self, run_id: str) -> RunStatus: ...

    @overload
    def cancel_run(self, run_id: CancelRunRequest) -> RunStatus: ...

    def cancel_run(self, run_id: CancelRunRequest | str) -> RunStatus:
        value = run_id.run_id if isinstance(run_id, CancelRunRequest) else run_id
        run_id = value
        resp = cancel_run.sync_detailed(client=self._client, run_id=run_id)
        result = _unwrap(resp)
        return result

    @overload
    def create_run(self, body: RunRequest) -> RunStatus: ...

    @overload
    def create_run(self, body: CreateRunRequest) -> RunStatus: ...

    def create_run(self, body: CreateRunRequest | RunRequest) -> RunStatus:
        payload = body.body if isinstance(body, CreateRunRequest) else body
        resp = create_run.sync_detailed(client=self._client, body=payload)
        result = _unwrap(resp)
        return result

    @overload
    def get_run_result(self, run_id: str) -> RunResult: ...

    @overload
    def get_run_result(self, run_id: GetRunResultRequest) -> RunResult: ...

    def get_run_result(self, run_id: GetRunResultRequest | str) -> RunResult:
        value = run_id.run_id if isinstance(run_id, GetRunResultRequest) else run_id
        run_id = value
        resp = get_run_result.sync_detailed(client=self._client, run_id=run_id)
        result = _unwrap(resp)
        return result

    @overload
    def get_run_status(self, run_id: str) -> RunStatus: ...

    @overload
    def get_run_status(self, run_id: GetRunStatusRequest) -> RunStatus: ...

    def get_run_status(self, run_id: GetRunStatusRequest | str) -> RunStatus:
        value = run_id.run_id if isinstance(run_id, GetRunStatusRequest) else run_id
        run_id = value
        resp = get_run_status.sync_detailed(client=self._client, run_id=run_id)
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
    def stream_run_events(self, run_id: str) -> str: ...

    @overload
    def stream_run_events(self, run_id: StreamRunEventsRequest) -> str: ...

    def stream_run_events(self, run_id: StreamRunEventsRequest | str) -> str:
        value = run_id.run_id if isinstance(run_id, StreamRunEventsRequest) else run_id
        run_id = value
        resp = stream_run_events.sync_detailed(client=self._client, run_id=run_id)
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
    'RuntimeClient',
    'CancelRunRequest',
    'CreateRunRequest',
    'GetRunResultRequest',
    'GetRunStatusRequest',
    'HealthRequest',
    'StreamRunEventsRequest',
    'VersionRequest',
]
