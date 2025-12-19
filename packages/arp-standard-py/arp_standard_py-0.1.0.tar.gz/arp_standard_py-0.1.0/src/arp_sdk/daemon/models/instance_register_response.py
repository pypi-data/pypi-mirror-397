from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.instance_register_response_extensions import InstanceRegisterResponseExtensions
  from ..models.instance_register_response_runtime_instance import InstanceRegisterResponseRuntimeInstance





T = TypeVar("T", bound="InstanceRegisterResponse")



@_attrs_define
class InstanceRegisterResponse:
    """ 
        Attributes:
            instance (InstanceRegisterResponseRuntimeInstance):
            extensions (InstanceRegisterResponseExtensions | Unset): Optional vendor extension map. Keys must be namespaced
                as <reverse_dns_or_org>.<key>.
     """

    instance: InstanceRegisterResponseRuntimeInstance
    extensions: InstanceRegisterResponseExtensions | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.instance_register_response_extensions import InstanceRegisterResponseExtensions
        from ..models.instance_register_response_runtime_instance import InstanceRegisterResponseRuntimeInstance
        instance = self.instance.to_dict()

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "instance": instance,
        })
        if extensions is not UNSET:
            field_dict["extensions"] = extensions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.instance_register_response_extensions import InstanceRegisterResponseExtensions
        from ..models.instance_register_response_runtime_instance import InstanceRegisterResponseRuntimeInstance
        d = dict(src_dict)
        instance = InstanceRegisterResponseRuntimeInstance.from_dict(d.pop("instance"))




        _extensions = d.pop("extensions", UNSET)
        extensions: InstanceRegisterResponseExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = InstanceRegisterResponseExtensions.from_dict(_extensions)




        instance_register_response = cls(
            instance=instance,
            extensions=extensions,
        )

        return instance_register_response

