from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.runtime_profile_defaults import RuntimeProfileDefaults
  from ..models.runtime_profile_metadata import RuntimeProfileMetadata
  from ..models.runtime_profile_extensions import RuntimeProfileExtensions





T = TypeVar("T", bound="RuntimeProfile")



@_attrs_define
class RuntimeProfile:
    """ 
        Attributes:
            runtime_profile (str):
            defaults (RuntimeProfileDefaults | Unset):
            description (str | Unset):
            extensions (RuntimeProfileExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            metadata (RuntimeProfileMetadata | Unset):
            runtime_name (str | Unset):
     """

    runtime_profile: str
    defaults: RuntimeProfileDefaults | Unset = UNSET
    description: str | Unset = UNSET
    extensions: RuntimeProfileExtensions | Unset = UNSET
    metadata: RuntimeProfileMetadata | Unset = UNSET
    runtime_name: str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.runtime_profile_defaults import RuntimeProfileDefaults
        from ..models.runtime_profile_metadata import RuntimeProfileMetadata
        from ..models.runtime_profile_extensions import RuntimeProfileExtensions
        runtime_profile = self.runtime_profile

        defaults: dict[str, Any] | Unset = UNSET
        if not isinstance(self.defaults, Unset):
            defaults = self.defaults.to_dict()

        description = self.description

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        runtime_name = self.runtime_name


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "runtime_profile": runtime_profile,
        })
        if defaults is not UNSET:
            field_dict["defaults"] = defaults
        if description is not UNSET:
            field_dict["description"] = description
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if runtime_name is not UNSET:
            field_dict["runtime_name"] = runtime_name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.runtime_profile_defaults import RuntimeProfileDefaults
        from ..models.runtime_profile_metadata import RuntimeProfileMetadata
        from ..models.runtime_profile_extensions import RuntimeProfileExtensions
        d = dict(src_dict)
        runtime_profile = d.pop("runtime_profile")

        _defaults = d.pop("defaults", UNSET)
        defaults: RuntimeProfileDefaults | Unset
        if isinstance(_defaults,  Unset):
            defaults = UNSET
        else:
            defaults = RuntimeProfileDefaults.from_dict(_defaults)




        description = d.pop("description", UNSET)

        _extensions = d.pop("extensions", UNSET)
        extensions: RuntimeProfileExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = RuntimeProfileExtensions.from_dict(_extensions)




        _metadata = d.pop("metadata", UNSET)
        metadata: RuntimeProfileMetadata | Unset
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = RuntimeProfileMetadata.from_dict(_metadata)




        runtime_name = d.pop("runtime_name", UNSET)

        runtime_profile = cls(
            runtime_profile=runtime_profile,
            defaults=defaults,
            description=description,
            extensions=extensions,
            metadata=metadata,
            runtime_name=runtime_name,
        )

        return runtime_profile

