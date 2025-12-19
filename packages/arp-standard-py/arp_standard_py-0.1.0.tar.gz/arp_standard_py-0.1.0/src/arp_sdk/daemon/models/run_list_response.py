from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.run_list_response_pagination import RunListResponsePagination
  from ..models.run_list_response_extensions import RunListResponseExtensions
  from ..models.run_list_response_run_status import RunListResponseRunStatus





T = TypeVar("T", bound="RunListResponse")



@_attrs_define
class RunListResponse:
    """ 
        Attributes:
            runs (list[RunListResponseRunStatus]):
            extensions (RunListResponseExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            pagination (RunListResponsePagination | Unset):
     """

    runs: list[RunListResponseRunStatus]
    extensions: RunListResponseExtensions | Unset = UNSET
    pagination: RunListResponsePagination | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.run_list_response_pagination import RunListResponsePagination
        from ..models.run_list_response_extensions import RunListResponseExtensions
        from ..models.run_list_response_run_status import RunListResponseRunStatus
        runs = []
        for runs_item_data in self.runs:
            runs_item = runs_item_data.to_dict()
            runs.append(runs_item)



        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        pagination: dict[str, Any] | Unset = UNSET
        if not isinstance(self.pagination, Unset):
            pagination = self.pagination.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "runs": runs,
        })
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if pagination is not UNSET:
            field_dict["pagination"] = pagination

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_list_response_pagination import RunListResponsePagination
        from ..models.run_list_response_extensions import RunListResponseExtensions
        from ..models.run_list_response_run_status import RunListResponseRunStatus
        d = dict(src_dict)
        runs = []
        _runs = d.pop("runs")
        for runs_item_data in (_runs):
            runs_item = RunListResponseRunStatus.from_dict(runs_item_data)



            runs.append(runs_item)


        _extensions = d.pop("extensions", UNSET)
        extensions: RunListResponseExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = RunListResponseExtensions.from_dict(_extensions)




        _pagination = d.pop("pagination", UNSET)
        pagination: RunListResponsePagination | Unset
        if isinstance(_pagination,  Unset):
            pagination = UNSET
        else:
            pagination = RunListResponsePagination.from_dict(_pagination)




        run_list_response = cls(
            runs=runs,
            extensions=extensions,
            pagination=pagination,
        )

        return run_list_response

