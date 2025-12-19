from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.instance_create_request_metadata import InstanceCreateRequestMetadata
  from ..models.instance_create_request_extensions import InstanceCreateRequestExtensions
  from ..models.instance_create_request_overrides import InstanceCreateRequestOverrides





T = TypeVar("T", bound="InstanceCreateRequest")



@_attrs_define
class InstanceCreateRequest:
    """ 
        Attributes:
            runtime_profile (str):
            count (int | Unset):  Default: 1.
            extensions (InstanceCreateRequestExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            metadata (InstanceCreateRequestMetadata | Unset):
            overrides (InstanceCreateRequestOverrides | Unset):
     """

    runtime_profile: str
    count: int | Unset = 1
    extensions: InstanceCreateRequestExtensions | Unset = UNSET
    metadata: InstanceCreateRequestMetadata | Unset = UNSET
    overrides: InstanceCreateRequestOverrides | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.instance_create_request_metadata import InstanceCreateRequestMetadata
        from ..models.instance_create_request_extensions import InstanceCreateRequestExtensions
        from ..models.instance_create_request_overrides import InstanceCreateRequestOverrides
        runtime_profile = self.runtime_profile

        count = self.count

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        overrides: dict[str, Any] | Unset = UNSET
        if not isinstance(self.overrides, Unset):
            overrides = self.overrides.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "runtime_profile": runtime_profile,
        })
        if count is not UNSET:
            field_dict["count"] = count
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if overrides is not UNSET:
            field_dict["overrides"] = overrides

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.instance_create_request_metadata import InstanceCreateRequestMetadata
        from ..models.instance_create_request_extensions import InstanceCreateRequestExtensions
        from ..models.instance_create_request_overrides import InstanceCreateRequestOverrides
        d = dict(src_dict)
        runtime_profile = d.pop("runtime_profile")

        count = d.pop("count", UNSET)

        _extensions = d.pop("extensions", UNSET)
        extensions: InstanceCreateRequestExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = InstanceCreateRequestExtensions.from_dict(_extensions)




        _metadata = d.pop("metadata", UNSET)
        metadata: InstanceCreateRequestMetadata | Unset
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = InstanceCreateRequestMetadata.from_dict(_metadata)




        _overrides = d.pop("overrides", UNSET)
        overrides: InstanceCreateRequestOverrides | Unset
        if isinstance(_overrides,  Unset):
            overrides = UNSET
        else:
            overrides = InstanceCreateRequestOverrides.from_dict(_overrides)




        instance_create_request = cls(
            runtime_profile=runtime_profile,
            count=count,
            extensions=extensions,
            metadata=metadata,
            overrides=overrides,
        )

        return instance_create_request

