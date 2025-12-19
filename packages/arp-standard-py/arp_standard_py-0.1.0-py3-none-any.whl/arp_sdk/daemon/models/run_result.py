from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.run_result_usage import RunResultUsage
  from ..models.run_result_resource_ref import RunResultResourceRef
  from ..models.run_result_error import RunResultError
  from ..models.run_result_output import RunResultOutput
  from ..models.run_result_extensions import RunResultExtensions





T = TypeVar("T", bound="RunResult")



@_attrs_define
class RunResult:
    """ 
        Attributes:
            ok (bool):
            run_id (str):
            artifacts (list[RunResultResourceRef] | Unset):
            error (RunResultError | Unset):
            extensions (RunResultExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            output (RunResultOutput | Unset):
            usage (RunResultUsage | Unset):
     """

    ok: bool
    run_id: str
    artifacts: list[RunResultResourceRef] | Unset = UNSET
    error: RunResultError | Unset = UNSET
    extensions: RunResultExtensions | Unset = UNSET
    output: RunResultOutput | Unset = UNSET
    usage: RunResultUsage | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.run_result_usage import RunResultUsage
        from ..models.run_result_resource_ref import RunResultResourceRef
        from ..models.run_result_error import RunResultError
        from ..models.run_result_output import RunResultOutput
        from ..models.run_result_extensions import RunResultExtensions
        ok = self.ok

        run_id = self.run_id

        artifacts: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.artifacts, Unset):
            artifacts = []
            for artifacts_item_data in self.artifacts:
                artifacts_item = artifacts_item_data.to_dict()
                artifacts.append(artifacts_item)



        error: dict[str, Any] | Unset = UNSET
        if not isinstance(self.error, Unset):
            error = self.error.to_dict()

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        output: dict[str, Any] | Unset = UNSET
        if not isinstance(self.output, Unset):
            output = self.output.to_dict()

        usage: dict[str, Any] | Unset = UNSET
        if not isinstance(self.usage, Unset):
            usage = self.usage.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "ok": ok,
            "run_id": run_id,
        })
        if artifacts is not UNSET:
            field_dict["artifacts"] = artifacts
        if error is not UNSET:
            field_dict["error"] = error
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if output is not UNSET:
            field_dict["output"] = output
        if usage is not UNSET:
            field_dict["usage"] = usage

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_result_usage import RunResultUsage
        from ..models.run_result_resource_ref import RunResultResourceRef
        from ..models.run_result_error import RunResultError
        from ..models.run_result_output import RunResultOutput
        from ..models.run_result_extensions import RunResultExtensions
        d = dict(src_dict)
        ok = d.pop("ok")

        run_id = d.pop("run_id")

        _artifacts = d.pop("artifacts", UNSET)
        artifacts: list[RunResultResourceRef] | Unset = UNSET
        if _artifacts is not UNSET:
            artifacts = []
            for artifacts_item_data in _artifacts:
                artifacts_item = RunResultResourceRef.from_dict(artifacts_item_data)



                artifacts.append(artifacts_item)


        _error = d.pop("error", UNSET)
        error: RunResultError | Unset
        if isinstance(_error,  Unset):
            error = UNSET
        else:
            error = RunResultError.from_dict(_error)




        _extensions = d.pop("extensions", UNSET)
        extensions: RunResultExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = RunResultExtensions.from_dict(_extensions)




        _output = d.pop("output", UNSET)
        output: RunResultOutput | Unset
        if isinstance(_output,  Unset):
            output = UNSET
        else:
            output = RunResultOutput.from_dict(_output)




        _usage = d.pop("usage", UNSET)
        usage: RunResultUsage | Unset
        if isinstance(_usage,  Unset):
            usage = UNSET
        else:
            usage = RunResultUsage.from_dict(_usage)




        run_result = cls(
            ok=ok,
            run_id=run_id,
            artifacts=artifacts,
            error=error,
            extensions=extensions,
            output=output,
            usage=usage,
        )

        return run_result

