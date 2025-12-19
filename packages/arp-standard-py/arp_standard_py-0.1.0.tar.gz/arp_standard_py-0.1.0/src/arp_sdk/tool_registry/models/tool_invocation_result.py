from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.tool_invocation_result_extensions import ToolInvocationResultExtensions
  from ..models.tool_invocation_result_result import ToolInvocationResultResult
  from ..models.tool_invocation_result_error import ToolInvocationResultError





T = TypeVar("T", bound="ToolInvocationResult")



@_attrs_define
class ToolInvocationResult:
    """ 
        Attributes:
            invocation_id (str):
            ok (bool):
            duration_ms (int | Unset):
            error (ToolInvocationResultError | Unset):
            extensions (ToolInvocationResultExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            result (ToolInvocationResultResult | Unset):
     """

    invocation_id: str
    ok: bool
    duration_ms: int | Unset = UNSET
    error: ToolInvocationResultError | Unset = UNSET
    extensions: ToolInvocationResultExtensions | Unset = UNSET
    result: ToolInvocationResultResult | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.tool_invocation_result_extensions import ToolInvocationResultExtensions
        from ..models.tool_invocation_result_result import ToolInvocationResultResult
        from ..models.tool_invocation_result_error import ToolInvocationResultError
        invocation_id = self.invocation_id

        ok = self.ok

        duration_ms = self.duration_ms

        error: dict[str, Any] | Unset = UNSET
        if not isinstance(self.error, Unset):
            error = self.error.to_dict()

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        result: dict[str, Any] | Unset = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "invocation_id": invocation_id,
            "ok": ok,
        })
        if duration_ms is not UNSET:
            field_dict["duration_ms"] = duration_ms
        if error is not UNSET:
            field_dict["error"] = error
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tool_invocation_result_extensions import ToolInvocationResultExtensions
        from ..models.tool_invocation_result_result import ToolInvocationResultResult
        from ..models.tool_invocation_result_error import ToolInvocationResultError
        d = dict(src_dict)
        invocation_id = d.pop("invocation_id")

        ok = d.pop("ok")

        duration_ms = d.pop("duration_ms", UNSET)

        _error = d.pop("error", UNSET)
        error: ToolInvocationResultError | Unset
        if isinstance(_error,  Unset):
            error = UNSET
        else:
            error = ToolInvocationResultError.from_dict(_error)




        _extensions = d.pop("extensions", UNSET)
        extensions: ToolInvocationResultExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = ToolInvocationResultExtensions.from_dict(_extensions)




        _result = d.pop("result", UNSET)
        result: ToolInvocationResultResult | Unset
        if isinstance(_result,  Unset):
            result = UNSET
        else:
            result = ToolInvocationResultResult.from_dict(_result)




        tool_invocation_result = cls(
            invocation_id=invocation_id,
            ok=ok,
            duration_ms=duration_ms,
            error=error,
            extensions=extensions,
            result=result,
        )

        return tool_invocation_result

