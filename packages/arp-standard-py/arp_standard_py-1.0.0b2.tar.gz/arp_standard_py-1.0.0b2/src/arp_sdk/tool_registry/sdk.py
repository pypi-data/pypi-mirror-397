from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeVar, overload

import httpx

from arp_sdk.errors import ArpApiError
from arp_sdk.models import (
    ToolDefinition,
    ToolInvocationResult,
)

from .api.health import (
    health,
)

from .api.invocations import (
    invoke_tool,
)

from .api.tools import (
    get_tool,
    list_tools,
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
class GetToolRequest:
    tool_id: str

@dataclass(slots=True)
class HealthRequest:
    pass

@dataclass(slots=True)
class InvokeToolRequest:
    invocation_id: str
    args: dict[str, Any]
    tool_id: str | None = None
    tool_name: str | None = None
    context: dict[str, Any] | None = None
    caller: dict[str, Any] | None = None
    extensions: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        satisfied = False
        if self.tool_id is not None:
            satisfied = True
        if self.tool_name is not None:
            satisfied = True
        if not satisfied:
            raise ValueError("InvokeToolRequest does not satisfy request constraints")

    def to_body(self) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if self.invocation_id is not None:
            body['invocation_id'] = self.invocation_id
        if self.tool_id is not None:
            body['tool_id'] = self.tool_id
        if self.tool_name is not None:
            body['tool_name'] = self.tool_name
        if self.args is not None:
            body['args'] = self.args
        if self.context is not None:
            body['context'] = self.context
        if self.caller is not None:
            body['caller'] = self.caller
        if self.extensions is not None:
            body['extensions'] = self.extensions
        return body

@dataclass(slots=True)
class ListToolsRequest:
    pass

@dataclass(slots=True)
class VersionRequest:
    pass

class ToolRegistryClient:
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
    def get_tool(self, tool_id: str) -> ToolDefinition: ...

    @overload
    def get_tool(self, tool_id: GetToolRequest) -> ToolDefinition: ...

    def get_tool(self, tool_id: GetToolRequest | str) -> ToolDefinition:
        value = tool_id.tool_id if isinstance(tool_id, GetToolRequest) else tool_id
        tool_id = value
        resp = get_tool.sync_detailed(client=self._client, tool_id=tool_id)
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

    def invoke_tool(self, request: InvokeToolRequest) -> ToolInvocationResult:
        body = request.to_body()
        resp = invoke_tool.sync_detailed(client=self._client, body=body)
        result = _unwrap(resp)
        return result

    @overload
    def list_tools(self) -> list[ToolDefinition]: ...

    @overload
    def list_tools(self, request: ListToolsRequest) -> list[ToolDefinition]: ...

    def list_tools(self, request: ListToolsRequest | None = None) -> list[ToolDefinition]:
        _ = request
        resp = list_tools.sync_detailed(client=self._client)
        return _unwrap(resp)

    @overload
    def version(self) -> VersionInfo: ...

    @overload
    def version(self, request: VersionRequest) -> VersionInfo: ...

    def version(self, request: VersionRequest | None = None) -> VersionInfo:
        _ = request
        resp = version.sync_detailed(client=self._client)
        return _unwrap(resp)

__all__ = [
    'ToolRegistryClient',
    'GetToolRequest',
    'HealthRequest',
    'InvokeToolRequest',
    'ListToolsRequest',
    'VersionRequest',
]
