from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.run_request_input_context import RunRequestInputContext
  from ..models.run_request_input_data import RunRequestInputData





T = TypeVar("T", bound="RunRequestInput")



@_attrs_define
class RunRequestInput:
    """ 
        Attributes:
            goal (str):
            context (RunRequestInputContext | Unset):
            data (RunRequestInputData | Unset):
     """

    goal: str
    context: RunRequestInputContext | Unset = UNSET
    data: RunRequestInputData | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.run_request_input_context import RunRequestInputContext
        from ..models.run_request_input_data import RunRequestInputData
        goal = self.goal

        context: dict[str, Any] | Unset = UNSET
        if not isinstance(self.context, Unset):
            context = self.context.to_dict()

        data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "goal": goal,
        })
        if context is not UNSET:
            field_dict["context"] = context
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_request_input_context import RunRequestInputContext
        from ..models.run_request_input_data import RunRequestInputData
        d = dict(src_dict)
        goal = d.pop("goal")

        _context = d.pop("context", UNSET)
        context: RunRequestInputContext | Unset
        if isinstance(_context,  Unset):
            context = UNSET
        else:
            context = RunRequestInputContext.from_dict(_context)




        _data = d.pop("data", UNSET)
        data: RunRequestInputData | Unset
        if isinstance(_data,  Unset):
            data = UNSET
        else:
            data = RunRequestInputData.from_dict(_data)




        run_request_input = cls(
            goal=goal,
            context=context,
            data=data,
        )

        return run_request_input

