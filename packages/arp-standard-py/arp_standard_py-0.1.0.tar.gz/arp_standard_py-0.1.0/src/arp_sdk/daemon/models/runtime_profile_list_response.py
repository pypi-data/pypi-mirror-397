from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.runtime_profile_list_response_runtime_profile import RuntimeProfileListResponseRuntimeProfile
  from ..models.runtime_profile_list_response_extensions import RuntimeProfileListResponseExtensions
  from ..models.runtime_profile_list_response_pagination import RuntimeProfileListResponsePagination





T = TypeVar("T", bound="RuntimeProfileListResponse")



@_attrs_define
class RuntimeProfileListResponse:
    """ 
        Attributes:
            profiles (list[RuntimeProfileListResponseRuntimeProfile]):
            extensions (RuntimeProfileListResponseExtensions | Unset): Optional vendor extension map. Keys must be
                namespaced as <reverse_dns_or_org>.<key>.
            pagination (RuntimeProfileListResponsePagination | Unset):
     """

    profiles: list[RuntimeProfileListResponseRuntimeProfile]
    extensions: RuntimeProfileListResponseExtensions | Unset = UNSET
    pagination: RuntimeProfileListResponsePagination | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.runtime_profile_list_response_runtime_profile import RuntimeProfileListResponseRuntimeProfile
        from ..models.runtime_profile_list_response_extensions import RuntimeProfileListResponseExtensions
        from ..models.runtime_profile_list_response_pagination import RuntimeProfileListResponsePagination
        profiles = []
        for profiles_item_data in self.profiles:
            profiles_item = profiles_item_data.to_dict()
            profiles.append(profiles_item)



        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        pagination: dict[str, Any] | Unset = UNSET
        if not isinstance(self.pagination, Unset):
            pagination = self.pagination.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "profiles": profiles,
        })
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if pagination is not UNSET:
            field_dict["pagination"] = pagination

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.runtime_profile_list_response_runtime_profile import RuntimeProfileListResponseRuntimeProfile
        from ..models.runtime_profile_list_response_extensions import RuntimeProfileListResponseExtensions
        from ..models.runtime_profile_list_response_pagination import RuntimeProfileListResponsePagination
        d = dict(src_dict)
        profiles = []
        _profiles = d.pop("profiles")
        for profiles_item_data in (_profiles):
            profiles_item = RuntimeProfileListResponseRuntimeProfile.from_dict(profiles_item_data)



            profiles.append(profiles_item)


        _extensions = d.pop("extensions", UNSET)
        extensions: RuntimeProfileListResponseExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = RuntimeProfileListResponseExtensions.from_dict(_extensions)




        _pagination = d.pop("pagination", UNSET)
        pagination: RuntimeProfileListResponsePagination | Unset
        if isinstance(_pagination,  Unset):
            pagination = UNSET
        else:
            pagination = RuntimeProfileListResponsePagination.from_dict(_pagination)




        runtime_profile_list_response = cls(
            profiles=profiles,
            extensions=extensions,
            pagination=pagination,
        )

        return runtime_profile_list_response

