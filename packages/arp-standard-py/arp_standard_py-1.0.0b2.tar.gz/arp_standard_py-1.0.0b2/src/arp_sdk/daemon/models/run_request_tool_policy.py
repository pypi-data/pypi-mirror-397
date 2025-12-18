from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="RunRequestToolPolicy")



@_attrs_define
class RunRequestToolPolicy:
    """ 
        Attributes:
            allow_tool_ids (list[str] | Unset):
            deny_tool_ids (list[str] | Unset):
     """

    allow_tool_ids: list[str] | Unset = UNSET
    deny_tool_ids: list[str] | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        allow_tool_ids: list[str] | Unset = UNSET
        if not isinstance(self.allow_tool_ids, Unset):
            allow_tool_ids = self.allow_tool_ids



        deny_tool_ids: list[str] | Unset = UNSET
        if not isinstance(self.deny_tool_ids, Unset):
            deny_tool_ids = self.deny_tool_ids




        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if allow_tool_ids is not UNSET:
            field_dict["allow_tool_ids"] = allow_tool_ids
        if deny_tool_ids is not UNSET:
            field_dict["deny_tool_ids"] = deny_tool_ids

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        allow_tool_ids = cast(list[str], d.pop("allow_tool_ids", UNSET))


        deny_tool_ids = cast(list[str], d.pop("deny_tool_ids", UNSET))


        run_request_tool_policy = cls(
            allow_tool_ids=allow_tool_ids,
            deny_tool_ids=deny_tool_ids,
        )

        return run_request_tool_policy

