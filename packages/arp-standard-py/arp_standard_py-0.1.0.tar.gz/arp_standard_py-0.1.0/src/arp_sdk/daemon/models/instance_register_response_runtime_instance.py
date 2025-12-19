from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.instance_register_response_runtime_instance_state import InstanceRegisterResponseRuntimeInstanceState
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.instance_register_response_runtime_instance_metadata import InstanceRegisterResponseRuntimeInstanceMetadata
  from ..models.instance_register_response_runtime_instance_extensions import InstanceRegisterResponseRuntimeInstanceExtensions





T = TypeVar("T", bound="InstanceRegisterResponseRuntimeInstance")



@_attrs_define
class InstanceRegisterResponseRuntimeInstance:
    """ 
        Attributes:
            instance_id (str):
            runtime_api_endpoint (str): Transport-agnostic locator URI for an API endpoint (e.g. http://127.0.0.1:43120).
                Future deployments may use other URI schemes (e.g. unix://...).
            state (InstanceRegisterResponseRuntimeInstanceState):
            extensions (InstanceRegisterResponseRuntimeInstanceExtensions | Unset): Optional vendor extension map. Keys must
                be namespaced as <reverse_dns_or_org>.<key>.
            managed (bool | Unset):  Default: True.
            metadata (InstanceRegisterResponseRuntimeInstanceMetadata | Unset):
            runtime_name (str | Unset):
            runtime_profile (str | Unset):
            runtime_version (str | Unset):
     """

    instance_id: str
    runtime_api_endpoint: str
    state: InstanceRegisterResponseRuntimeInstanceState
    extensions: InstanceRegisterResponseRuntimeInstanceExtensions | Unset = UNSET
    managed: bool | Unset = True
    metadata: InstanceRegisterResponseRuntimeInstanceMetadata | Unset = UNSET
    runtime_name: str | Unset = UNSET
    runtime_profile: str | Unset = UNSET
    runtime_version: str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.instance_register_response_runtime_instance_metadata import InstanceRegisterResponseRuntimeInstanceMetadata
        from ..models.instance_register_response_runtime_instance_extensions import InstanceRegisterResponseRuntimeInstanceExtensions
        instance_id = self.instance_id

        runtime_api_endpoint = self.runtime_api_endpoint

        state = self.state.value

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        managed = self.managed

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        runtime_name = self.runtime_name

        runtime_profile = self.runtime_profile

        runtime_version = self.runtime_version


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "instance_id": instance_id,
            "runtime_api_endpoint": runtime_api_endpoint,
            "state": state,
        })
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if managed is not UNSET:
            field_dict["managed"] = managed
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if runtime_name is not UNSET:
            field_dict["runtime_name"] = runtime_name
        if runtime_profile is not UNSET:
            field_dict["runtime_profile"] = runtime_profile
        if runtime_version is not UNSET:
            field_dict["runtime_version"] = runtime_version

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.instance_register_response_runtime_instance_metadata import InstanceRegisterResponseRuntimeInstanceMetadata
        from ..models.instance_register_response_runtime_instance_extensions import InstanceRegisterResponseRuntimeInstanceExtensions
        d = dict(src_dict)
        instance_id = d.pop("instance_id")

        runtime_api_endpoint = d.pop("runtime_api_endpoint")

        state = InstanceRegisterResponseRuntimeInstanceState(d.pop("state"))




        _extensions = d.pop("extensions", UNSET)
        extensions: InstanceRegisterResponseRuntimeInstanceExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = InstanceRegisterResponseRuntimeInstanceExtensions.from_dict(_extensions)




        managed = d.pop("managed", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: InstanceRegisterResponseRuntimeInstanceMetadata | Unset
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = InstanceRegisterResponseRuntimeInstanceMetadata.from_dict(_metadata)




        runtime_name = d.pop("runtime_name", UNSET)

        runtime_profile = d.pop("runtime_profile", UNSET)

        runtime_version = d.pop("runtime_version", UNSET)

        instance_register_response_runtime_instance = cls(
            instance_id=instance_id,
            runtime_api_endpoint=runtime_api_endpoint,
            state=state,
            extensions=extensions,
            managed=managed,
            metadata=metadata,
            runtime_name=runtime_name,
            runtime_profile=runtime_profile,
            runtime_version=runtime_version,
        )

        return instance_register_response_runtime_instance

