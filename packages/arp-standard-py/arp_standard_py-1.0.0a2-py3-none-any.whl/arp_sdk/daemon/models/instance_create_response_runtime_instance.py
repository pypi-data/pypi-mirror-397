from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.instance_create_response_runtime_instance_state import InstanceCreateResponseRuntimeInstanceState
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.instance_create_response_runtime_instance_extensions import InstanceCreateResponseRuntimeInstanceExtensions
  from ..models.instance_create_response_runtime_instance_metadata import InstanceCreateResponseRuntimeInstanceMetadata





T = TypeVar("T", bound="InstanceCreateResponseRuntimeInstance")



@_attrs_define
class InstanceCreateResponseRuntimeInstance:
    """ 
        Attributes:
            instance_id (str):
            runtime_api_base_url (str):
            runtime_type (str):
            state (InstanceCreateResponseRuntimeInstanceState):
            extensions (InstanceCreateResponseRuntimeInstanceExtensions | Unset): Optional vendor extension map. Keys must
                be namespaced as <reverse_dns_or_org>.<key>.
            metadata (InstanceCreateResponseRuntimeInstanceMetadata | Unset):
            runtime_version (str | Unset):
     """

    instance_id: str
    runtime_api_base_url: str
    runtime_type: str
    state: InstanceCreateResponseRuntimeInstanceState
    extensions: InstanceCreateResponseRuntimeInstanceExtensions | Unset = UNSET
    metadata: InstanceCreateResponseRuntimeInstanceMetadata | Unset = UNSET
    runtime_version: str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.instance_create_response_runtime_instance_extensions import InstanceCreateResponseRuntimeInstanceExtensions
        from ..models.instance_create_response_runtime_instance_metadata import InstanceCreateResponseRuntimeInstanceMetadata
        instance_id = self.instance_id

        runtime_api_base_url = self.runtime_api_base_url

        runtime_type = self.runtime_type

        state = self.state.value

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        runtime_version = self.runtime_version


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "instance_id": instance_id,
            "runtime_api_base_url": runtime_api_base_url,
            "runtime_type": runtime_type,
            "state": state,
        })
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if runtime_version is not UNSET:
            field_dict["runtime_version"] = runtime_version

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.instance_create_response_runtime_instance_extensions import InstanceCreateResponseRuntimeInstanceExtensions
        from ..models.instance_create_response_runtime_instance_metadata import InstanceCreateResponseRuntimeInstanceMetadata
        d = dict(src_dict)
        instance_id = d.pop("instance_id")

        runtime_api_base_url = d.pop("runtime_api_base_url")

        runtime_type = d.pop("runtime_type")

        state = InstanceCreateResponseRuntimeInstanceState(d.pop("state"))




        _extensions = d.pop("extensions", UNSET)
        extensions: InstanceCreateResponseRuntimeInstanceExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = InstanceCreateResponseRuntimeInstanceExtensions.from_dict(_extensions)




        _metadata = d.pop("metadata", UNSET)
        metadata: InstanceCreateResponseRuntimeInstanceMetadata | Unset
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = InstanceCreateResponseRuntimeInstanceMetadata.from_dict(_metadata)




        runtime_version = d.pop("runtime_version", UNSET)

        instance_create_response_runtime_instance = cls(
            instance_id=instance_id,
            runtime_api_base_url=runtime_api_base_url,
            runtime_type=runtime_type,
            state=state,
            extensions=extensions,
            metadata=metadata,
            runtime_version=runtime_version,
        )

        return instance_create_response_runtime_instance

