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
            instance_id (str | Unset):
            runtime_api_endpoint (str | Unset): Transport-agnostic locator URI for an API endpoint (e.g.
                http://127.0.0.1:43120). Future deployments may use other URI schemes (e.g. unix://...).
            runtime_name (str | Unset):
            runtime_profile (str | Unset):
     """

    instance_id: str | Unset = UNSET
    runtime_api_endpoint: str | Unset = UNSET
    runtime_name: str | Unset = UNSET
    runtime_profile: str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        instance_id = self.instance_id

        runtime_api_endpoint = self.runtime_api_endpoint

        runtime_name = self.runtime_name

        runtime_profile = self.runtime_profile


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if instance_id is not UNSET:
            field_dict["instance_id"] = instance_id
        if runtime_api_endpoint is not UNSET:
            field_dict["runtime_api_endpoint"] = runtime_api_endpoint
        if runtime_name is not UNSET:
            field_dict["runtime_name"] = runtime_name
        if runtime_profile is not UNSET:
            field_dict["runtime_profile"] = runtime_profile

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        instance_id = d.pop("instance_id", UNSET)

        runtime_api_endpoint = d.pop("runtime_api_endpoint", UNSET)

        runtime_name = d.pop("runtime_name", UNSET)

        runtime_profile = d.pop("runtime_profile", UNSET)

        run_request_runtime_selector = cls(
            instance_id=instance_id,
            runtime_api_endpoint=runtime_api_endpoint,
            runtime_name=runtime_name,
            runtime_profile=runtime_profile,
        )

        return run_request_runtime_selector

