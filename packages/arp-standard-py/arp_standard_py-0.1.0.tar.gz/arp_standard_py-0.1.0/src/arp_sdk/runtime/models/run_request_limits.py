from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="RunRequestLimits")



@_attrs_define
class RunRequestLimits:
    """ 
        Attributes:
            max_steps (int | Unset):
            max_tokens (int | Unset):
            timeout_ms (int | Unset):
     """

    max_steps: int | Unset = UNSET
    max_tokens: int | Unset = UNSET
    timeout_ms: int | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        max_steps = self.max_steps

        max_tokens = self.max_tokens

        timeout_ms = self.timeout_ms


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if max_steps is not UNSET:
            field_dict["max_steps"] = max_steps
        if max_tokens is not UNSET:
            field_dict["max_tokens"] = max_tokens
        if timeout_ms is not UNSET:
            field_dict["timeout_ms"] = timeout_ms

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        max_steps = d.pop("max_steps", UNSET)

        max_tokens = d.pop("max_tokens", UNSET)

        timeout_ms = d.pop("timeout_ms", UNSET)

        run_request_limits = cls(
            max_steps=max_steps,
            max_tokens=max_tokens,
            timeout_ms=timeout_ms,
        )

        return run_request_limits

