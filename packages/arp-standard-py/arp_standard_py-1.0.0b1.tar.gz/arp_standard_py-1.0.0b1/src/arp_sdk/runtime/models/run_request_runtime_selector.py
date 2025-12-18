from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="RunRequestRuntimeSelector")



@_attrs_define
class RunRequestRuntimeSelector:
    """ 
        Attributes:
            address (str | Unset):
            instance_id (str | Unset):
            profile (str | Unset):
            runtime_type (str | Unset):
     """

    address: str | Unset = UNSET
    instance_id: str | Unset = UNSET
    profile: str | Unset = UNSET
    runtime_type: str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        address = self.address

        instance_id = self.instance_id

        profile = self.profile

        runtime_type = self.runtime_type


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if address is not UNSET:
            field_dict["address"] = address
        if instance_id is not UNSET:
            field_dict["instance_id"] = instance_id
        if profile is not UNSET:
            field_dict["profile"] = profile
        if runtime_type is not UNSET:
            field_dict["runtime_type"] = runtime_type

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        address = d.pop("address", UNSET)

        instance_id = d.pop("instance_id", UNSET)

        profile = d.pop("profile", UNSET)

        runtime_type = d.pop("runtime_type", UNSET)

        run_request_runtime_selector = cls(
            address=address,
            instance_id=instance_id,
            profile=profile,
            runtime_type=runtime_type,
        )

        return run_request_runtime_selector

