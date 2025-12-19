from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.runtime_profile_list_response_pagination_extensions import RuntimeProfileListResponsePaginationExtensions





T = TypeVar("T", bound="RuntimeProfileListResponsePagination")



@_attrs_define
class RuntimeProfileListResponsePagination:
    """ 
        Attributes:
            extensions (RuntimeProfileListResponsePaginationExtensions | Unset): Optional vendor extension map. Keys must be
                namespaced as <reverse_dns_or_org>.<key>.
            next_page_token (str | Unset):
            page_size (int | Unset):
     """

    extensions: RuntimeProfileListResponsePaginationExtensions | Unset = UNSET
    next_page_token: str | Unset = UNSET
    page_size: int | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.runtime_profile_list_response_pagination_extensions import RuntimeProfileListResponsePaginationExtensions
        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        next_page_token = self.next_page_token

        page_size = self.page_size


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if next_page_token is not UNSET:
            field_dict["next_page_token"] = next_page_token
        if page_size is not UNSET:
            field_dict["page_size"] = page_size

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.runtime_profile_list_response_pagination_extensions import RuntimeProfileListResponsePaginationExtensions
        d = dict(src_dict)
        _extensions = d.pop("extensions", UNSET)
        extensions: RuntimeProfileListResponsePaginationExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = RuntimeProfileListResponsePaginationExtensions.from_dict(_extensions)




        next_page_token = d.pop("next_page_token", UNSET)

        page_size = d.pop("page_size", UNSET)

        runtime_profile_list_response_pagination = cls(
            extensions=extensions,
            next_page_token=next_page_token,
            page_size=page_size,
        )

        return runtime_profile_list_response_pagination

