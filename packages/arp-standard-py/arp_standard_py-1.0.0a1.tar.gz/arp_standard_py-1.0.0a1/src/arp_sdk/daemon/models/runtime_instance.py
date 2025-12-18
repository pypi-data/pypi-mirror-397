from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.runtime_instance_state import RuntimeInstanceState
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.runtime_instance_capabilities import RuntimeInstanceCapabilities
  from ..models.runtime_instance_extensions import RuntimeInstanceExtensions
  from ..models.runtime_instance_metadata import RuntimeInstanceMetadata





T = TypeVar("T", bound="RuntimeInstance")



@_attrs_define
class RuntimeInstance:
    """ 
        Attributes:
            instance_id (str):
            runtime_type (str):
            runtime_version (str):
            state (RuntimeInstanceState):
            address (str | Unset):
            capabilities (RuntimeInstanceCapabilities | Unset):
            extensions (RuntimeInstanceExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            metadata (RuntimeInstanceMetadata | Unset):
     """

    instance_id: str
    runtime_type: str
    runtime_version: str
    state: RuntimeInstanceState
    address: str | Unset = UNSET
    capabilities: RuntimeInstanceCapabilities | Unset = UNSET
    extensions: RuntimeInstanceExtensions | Unset = UNSET
    metadata: RuntimeInstanceMetadata | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.runtime_instance_capabilities import RuntimeInstanceCapabilities
        from ..models.runtime_instance_extensions import RuntimeInstanceExtensions
        from ..models.runtime_instance_metadata import RuntimeInstanceMetadata
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
        from ..models.runtime_instance_capabilities import RuntimeInstanceCapabilities
        from ..models.runtime_instance_extensions import RuntimeInstanceExtensions
        from ..models.runtime_instance_metadata import RuntimeInstanceMetadata
        d = dict(src_dict)
        instance_id = d.pop("instance_id")

        runtime_type = d.pop("runtime_type")

        runtime_version = d.pop("runtime_version")

        state = RuntimeInstanceState(d.pop("state"))




        address = d.pop("address", UNSET)

        _capabilities = d.pop("capabilities", UNSET)
        capabilities: RuntimeInstanceCapabilities | Unset
        if isinstance(_capabilities,  Unset):
            capabilities = UNSET
        else:
            capabilities = RuntimeInstanceCapabilities.from_dict(_capabilities)




        _extensions = d.pop("extensions", UNSET)
        extensions: RuntimeInstanceExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = RuntimeInstanceExtensions.from_dict(_extensions)




        _metadata = d.pop("metadata", UNSET)
        metadata: RuntimeInstanceMetadata | Unset
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = RuntimeInstanceMetadata.from_dict(_metadata)




        runtime_instance = cls(
            instance_id=instance_id,
            runtime_type=runtime_type,
            runtime_version=runtime_version,
            state=state,
            address=address,
            capabilities=capabilities,
            extensions=extensions,
            metadata=metadata,
        )

        return runtime_instance

