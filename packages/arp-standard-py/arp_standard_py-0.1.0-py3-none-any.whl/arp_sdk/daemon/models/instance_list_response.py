from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.instance_list_response_runtime_instance import InstanceListResponseRuntimeInstance
  from ..models.instance_list_response_extensions import InstanceListResponseExtensions





T = TypeVar("T", bound="InstanceListResponse")



@_attrs_define
class InstanceListResponse:
    """ 
        Attributes:
            instances (list[InstanceListResponseRuntimeInstance]):
            extensions (InstanceListResponseExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
     """

    instances: list[InstanceListResponseRuntimeInstance]
    extensions: InstanceListResponseExtensions | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.instance_list_response_runtime_instance import InstanceListResponseRuntimeInstance
        from ..models.instance_list_response_extensions import InstanceListResponseExtensions
        instances = []
        for instances_item_data in self.instances:
            instances_item = instances_item_data.to_dict()
            instances.append(instances_item)



        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "instances": instances,
        })
        if extensions is not UNSET:
            field_dict["extensions"] = extensions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.instance_list_response_runtime_instance import InstanceListResponseRuntimeInstance
        from ..models.instance_list_response_extensions import InstanceListResponseExtensions
        d = dict(src_dict)
        instances = []
        _instances = d.pop("instances")
        for instances_item_data in (_instances):
            instances_item = InstanceListResponseRuntimeInstance.from_dict(instances_item_data)



            instances.append(instances_item)


        _extensions = d.pop("extensions", UNSET)
        extensions: InstanceListResponseExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = InstanceListResponseExtensions.from_dict(_extensions)




        instance_list_response = cls(
            instances=instances,
            extensions=extensions,
        )

        return instance_list_response

