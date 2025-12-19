from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.instance_register_response_runtime_instance_metadata_labels import InstanceRegisterResponseRuntimeInstanceMetadataLabels
  from ..models.instance_register_response_runtime_instance_metadata_annotations import InstanceRegisterResponseRuntimeInstanceMetadataAnnotations
  from ..models.instance_register_response_runtime_instance_metadata_extensions import InstanceRegisterResponseRuntimeInstanceMetadataExtensions





T = TypeVar("T", bound="InstanceRegisterResponseRuntimeInstanceMetadata")



@_attrs_define
class InstanceRegisterResponseRuntimeInstanceMetadata:
    """ 
        Attributes:
            annotations (InstanceRegisterResponseRuntimeInstanceMetadataAnnotations | Unset):
            extensions (InstanceRegisterResponseRuntimeInstanceMetadataExtensions | Unset): Optional vendor extension map.
                Keys must be namespaced as <reverse_dns_or_org>.<key>.
            labels (InstanceRegisterResponseRuntimeInstanceMetadataLabels | Unset):
     """

    annotations: InstanceRegisterResponseRuntimeInstanceMetadataAnnotations | Unset = UNSET
    extensions: InstanceRegisterResponseRuntimeInstanceMetadataExtensions | Unset = UNSET
    labels: InstanceRegisterResponseRuntimeInstanceMetadataLabels | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.instance_register_response_runtime_instance_metadata_labels import InstanceRegisterResponseRuntimeInstanceMetadataLabels
        from ..models.instance_register_response_runtime_instance_metadata_annotations import InstanceRegisterResponseRuntimeInstanceMetadataAnnotations
        from ..models.instance_register_response_runtime_instance_metadata_extensions import InstanceRegisterResponseRuntimeInstanceMetadataExtensions
        annotations: dict[str, Any] | Unset = UNSET
        if not isinstance(self.annotations, Unset):
            annotations = self.annotations.to_dict()

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        labels: dict[str, Any] | Unset = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if annotations is not UNSET:
            field_dict["annotations"] = annotations
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if labels is not UNSET:
            field_dict["labels"] = labels

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.instance_register_response_runtime_instance_metadata_labels import InstanceRegisterResponseRuntimeInstanceMetadataLabels
        from ..models.instance_register_response_runtime_instance_metadata_annotations import InstanceRegisterResponseRuntimeInstanceMetadataAnnotations
        from ..models.instance_register_response_runtime_instance_metadata_extensions import InstanceRegisterResponseRuntimeInstanceMetadataExtensions
        d = dict(src_dict)
        _annotations = d.pop("annotations", UNSET)
        annotations: InstanceRegisterResponseRuntimeInstanceMetadataAnnotations | Unset
        if isinstance(_annotations,  Unset):
            annotations = UNSET
        else:
            annotations = InstanceRegisterResponseRuntimeInstanceMetadataAnnotations.from_dict(_annotations)




        _extensions = d.pop("extensions", UNSET)
        extensions: InstanceRegisterResponseRuntimeInstanceMetadataExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = InstanceRegisterResponseRuntimeInstanceMetadataExtensions.from_dict(_extensions)




        _labels = d.pop("labels", UNSET)
        labels: InstanceRegisterResponseRuntimeInstanceMetadataLabels | Unset
        if isinstance(_labels,  Unset):
            labels = UNSET
        else:
            labels = InstanceRegisterResponseRuntimeInstanceMetadataLabels.from_dict(_labels)




        instance_register_response_runtime_instance_metadata = cls(
            annotations=annotations,
            extensions=extensions,
            labels=labels,
        )

        return instance_register_response_runtime_instance_metadata

