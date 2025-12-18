from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.instance_register_request_extensions import InstanceRegisterRequestExtensions
  from ..models.instance_register_request_metadata import InstanceRegisterRequestMetadata





T = TypeVar("T", bound="InstanceRegisterRequest")



@_attrs_define
class InstanceRegisterRequest:
    """ 
        Attributes:
            runtime_api_endpoint (str): Transport-agnostic locator URI for an API endpoint (e.g. http://127.0.0.1:43120).
                Future deployments may use other URI schemes (e.g. unix://...).
            extensions (InstanceRegisterRequestExtensions | Unset): Optional vendor extension map. Keys must be namespaced
                as <reverse_dns_or_org>.<key>.
            metadata (InstanceRegisterRequestMetadata | Unset):
            runtime_name (str | Unset):
            runtime_profile (str | Unset):
     """

    runtime_api_endpoint: str
    extensions: InstanceRegisterRequestExtensions | Unset = UNSET
    metadata: InstanceRegisterRequestMetadata | Unset = UNSET
    runtime_name: str | Unset = UNSET
    runtime_profile: str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.instance_register_request_extensions import InstanceRegisterRequestExtensions
        from ..models.instance_register_request_metadata import InstanceRegisterRequestMetadata
        runtime_api_endpoint = self.runtime_api_endpoint

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        runtime_name = self.runtime_name

        runtime_profile = self.runtime_profile


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "runtime_api_endpoint": runtime_api_endpoint,
        })
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if runtime_name is not UNSET:
            field_dict["runtime_name"] = runtime_name
        if runtime_profile is not UNSET:
            field_dict["runtime_profile"] = runtime_profile

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.instance_register_request_extensions import InstanceRegisterRequestExtensions
        from ..models.instance_register_request_metadata import InstanceRegisterRequestMetadata
        d = dict(src_dict)
        runtime_api_endpoint = d.pop("runtime_api_endpoint")

        _extensions = d.pop("extensions", UNSET)
        extensions: InstanceRegisterRequestExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = InstanceRegisterRequestExtensions.from_dict(_extensions)




        _metadata = d.pop("metadata", UNSET)
        metadata: InstanceRegisterRequestMetadata | Unset
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = InstanceRegisterRequestMetadata.from_dict(_metadata)




        runtime_name = d.pop("runtime_name", UNSET)

        runtime_profile = d.pop("runtime_profile", UNSET)

        instance_register_request = cls(
            runtime_api_endpoint=runtime_api_endpoint,
            extensions=extensions,
            metadata=metadata,
            runtime_name=runtime_name,
            runtime_profile=runtime_profile,
        )

        return instance_register_request

