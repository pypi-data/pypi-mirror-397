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
  from ..models.instance_create_response_runtime_instance_capabilities import InstanceCreateResponseRuntimeInstanceCapabilities
  from ..models.instance_create_response_runtime_instance_extensions import InstanceCreateResponseRuntimeInstanceExtensions
  from ..models.instance_create_response_runtime_instance_metadata import InstanceCreateResponseRuntimeInstanceMetadata





T = TypeVar("T", bound="InstanceCreateResponseRuntimeInstance")



@_attrs_define
class InstanceCreateResponseRuntimeInstance:
    """ 
        Attributes:
            instance_id (str):
            runtime_type (str):
            runtime_version (str):
            state (InstanceCreateResponseRuntimeInstanceState):
            address (str | Unset):
            capabilities (InstanceCreateResponseRuntimeInstanceCapabilities | Unset):
            extensions (InstanceCreateResponseRuntimeInstanceExtensions | Unset): Optional vendor extension map. Keys must
                be namespaced as <reverse_dns_or_org>.<key>.
            metadata (InstanceCreateResponseRuntimeInstanceMetadata | Unset):
     """

    instance_id: str
    runtime_type: str
    runtime_version: str
    state: InstanceCreateResponseRuntimeInstanceState
    address: str | Unset = UNSET
    capabilities: InstanceCreateResponseRuntimeInstanceCapabilities | Unset = UNSET
    extensions: InstanceCreateResponseRuntimeInstanceExtensions | Unset = UNSET
    metadata: InstanceCreateResponseRuntimeInstanceMetadata | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.instance_create_response_runtime_instance_capabilities import InstanceCreateResponseRuntimeInstanceCapabilities
        from ..models.instance_create_response_runtime_instance_extensions import InstanceCreateResponseRuntimeInstanceExtensions
        from ..models.instance_create_response_runtime_instance_metadata import InstanceCreateResponseRuntimeInstanceMetadata
        instance_id = self.instance_id

        runtime_type = self.runtime_type

        runtime_version = self.runtime_version

        state = self.state.value

        address = self.address

        capabilities: dict[str, Any] | Unset = UNSET
        if not isinstance(self.capabilities, Unset):
            capabilities = self.capabilities.to_dict()

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "instance_id": instance_id,
            "runtime_type": runtime_type,
            "runtime_version": runtime_version,
            "state": state,
        })
        if address is not UNSET:
            field_dict["address"] = address
        if capabilities is not UNSET:
            field_dict["capabilities"] = capabilities
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.instance_create_response_runtime_instance_capabilities import InstanceCreateResponseRuntimeInstanceCapabilities
        from ..models.instance_create_response_runtime_instance_extensions import InstanceCreateResponseRuntimeInstanceExtensions
        from ..models.instance_create_response_runtime_instance_metadata import InstanceCreateResponseRuntimeInstanceMetadata
        d = dict(src_dict)
        instance_id = d.pop("instance_id")

        runtime_type = d.pop("runtime_type")

        runtime_version = d.pop("runtime_version")

        state = InstanceCreateResponseRuntimeInstanceState(d.pop("state"))




        address = d.pop("address", UNSET)

        _capabilities = d.pop("capabilities", UNSET)
        capabilities: InstanceCreateResponseRuntimeInstanceCapabilities | Unset
        if isinstance(_capabilities,  Unset):
            capabilities = UNSET
        else:
            capabilities = InstanceCreateResponseRuntimeInstanceCapabilities.from_dict(_capabilities)




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




        instance_create_response_runtime_instance = cls(
            instance_id=instance_id,
            runtime_type=runtime_type,
            runtime_version=runtime_version,
            state=state,
            address=address,
            capabilities=capabilities,
            extensions=extensions,
            metadata=metadata,
        )

        return instance_create_response_runtime_instance

