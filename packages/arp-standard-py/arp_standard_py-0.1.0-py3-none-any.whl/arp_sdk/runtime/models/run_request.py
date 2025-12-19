from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.run_request_tool_policy import RunRequestToolPolicy
  from ..models.run_request_limits import RunRequestLimits
  from ..models.run_request_metadata import RunRequestMetadata
  from ..models.run_request_input import RunRequestInput
  from ..models.run_request_extensions import RunRequestExtensions
  from ..models.run_request_runtime_selector import RunRequestRuntimeSelector





T = TypeVar("T", bound="RunRequest")



@_attrs_define
class RunRequest:
    """ 
        Attributes:
            input_ (RunRequestInput):
            extensions (RunRequestExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            limits (RunRequestLimits | Unset):
            metadata (RunRequestMetadata | Unset):
            run_id (str | Unset):
            runtime_selector (RunRequestRuntimeSelector | Unset):
            tool_policy (RunRequestToolPolicy | Unset):
     """

    input_: RunRequestInput
    extensions: RunRequestExtensions | Unset = UNSET
    limits: RunRequestLimits | Unset = UNSET
    metadata: RunRequestMetadata | Unset = UNSET
    run_id: str | Unset = UNSET
    runtime_selector: RunRequestRuntimeSelector | Unset = UNSET
    tool_policy: RunRequestToolPolicy | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.run_request_tool_policy import RunRequestToolPolicy
        from ..models.run_request_limits import RunRequestLimits
        from ..models.run_request_metadata import RunRequestMetadata
        from ..models.run_request_input import RunRequestInput
        from ..models.run_request_extensions import RunRequestExtensions
        from ..models.run_request_runtime_selector import RunRequestRuntimeSelector
        input_ = self.input_.to_dict()

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        limits: dict[str, Any] | Unset = UNSET
        if not isinstance(self.limits, Unset):
            limits = self.limits.to_dict()

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        run_id = self.run_id

        runtime_selector: dict[str, Any] | Unset = UNSET
        if not isinstance(self.runtime_selector, Unset):
            runtime_selector = self.runtime_selector.to_dict()

        tool_policy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tool_policy, Unset):
            tool_policy = self.tool_policy.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "input": input_,
        })
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if limits is not UNSET:
            field_dict["limits"] = limits
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if run_id is not UNSET:
            field_dict["run_id"] = run_id
        if runtime_selector is not UNSET:
            field_dict["runtime_selector"] = runtime_selector
        if tool_policy is not UNSET:
            field_dict["tool_policy"] = tool_policy

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_request_tool_policy import RunRequestToolPolicy
        from ..models.run_request_limits import RunRequestLimits
        from ..models.run_request_metadata import RunRequestMetadata
        from ..models.run_request_input import RunRequestInput
        from ..models.run_request_extensions import RunRequestExtensions
        from ..models.run_request_runtime_selector import RunRequestRuntimeSelector
        d = dict(src_dict)
        input_ = RunRequestInput.from_dict(d.pop("input"))




        _extensions = d.pop("extensions", UNSET)
        extensions: RunRequestExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = RunRequestExtensions.from_dict(_extensions)




        _limits = d.pop("limits", UNSET)
        limits: RunRequestLimits | Unset
        if isinstance(_limits,  Unset):
            limits = UNSET
        else:
            limits = RunRequestLimits.from_dict(_limits)




        _metadata = d.pop("metadata", UNSET)
        metadata: RunRequestMetadata | Unset
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = RunRequestMetadata.from_dict(_metadata)




        run_id = d.pop("run_id", UNSET)

        _runtime_selector = d.pop("runtime_selector", UNSET)
        runtime_selector: RunRequestRuntimeSelector | Unset
        if isinstance(_runtime_selector,  Unset):
            runtime_selector = UNSET
        else:
            runtime_selector = RunRequestRuntimeSelector.from_dict(_runtime_selector)




        _tool_policy = d.pop("tool_policy", UNSET)
        tool_policy: RunRequestToolPolicy | Unset
        if isinstance(_tool_policy,  Unset):
            tool_policy = UNSET
        else:
            tool_policy = RunRequestToolPolicy.from_dict(_tool_policy)




        run_request = cls(
            input_=input_,
            extensions=extensions,
            limits=limits,
            metadata=metadata,
            run_id=run_id,
            runtime_selector=runtime_selector,
            tool_policy=tool_policy,
        )

        return run_request

