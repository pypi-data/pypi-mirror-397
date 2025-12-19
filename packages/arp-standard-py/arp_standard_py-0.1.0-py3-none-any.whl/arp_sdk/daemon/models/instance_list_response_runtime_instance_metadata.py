from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.instance_list_response_runtime_instance_metadata_annotations import InstanceListResponseRuntimeInstanceMetadataAnnotations
  from ..models.instance_list_response_runtime_instance_metadata_extensions import InstanceListResponseRuntimeInstanceMetadataExtensions
  from ..models.instance_list_response_runtime_instance_metadata_labels import InstanceListResponseRuntimeInstanceMetadataLabels





T = TypeVar("T", bound="InstanceListResponseRuntimeInstanceMetadata")



@_attrs_define
class InstanceListResponseRuntimeInstanceMetadata:
    """ 
        Attributes:
            annotations (InstanceListResponseRuntimeInstanceMetadataAnnotations | Unset):
            extensions (InstanceListResponseRuntimeInstanceMetadataExtensions | Unset): Optional vendor extension map. Keys
                must be namespaced as <reverse_dns_or_org>.<key>.
            labels (InstanceListResponseRuntimeInstanceMetadataLabels | Unset):
     """

    annotations: InstanceListResponseRuntimeInstanceMetadataAnnotations | Unset = UNSET
    extensions: InstanceListResponseRuntimeInstanceMetadataExtensions | Unset = UNSET
    labels: InstanceListResponseRuntimeInstanceMetadataLabels | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.instance_list_response_runtime_instance_metadata_annotations import InstanceListResponseRuntimeInstanceMetadataAnnotations
        from ..models.instance_list_response_runtime_instance_metadata_extensions import InstanceListResponseRuntimeInstanceMetadataExtensions
        from ..models.instance_list_response_runtime_instance_metadata_labels import InstanceListResponseRuntimeInstanceMetadataLabels
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
        from ..models.instance_list_response_runtime_instance_metadata_annotations import InstanceListResponseRuntimeInstanceMetadataAnnotations
        from ..models.instance_list_response_runtime_instance_metadata_extensions import InstanceListResponseRuntimeInstanceMetadataExtensions
        from ..models.instance_list_response_runtime_instance_metadata_labels import InstanceListResponseRuntimeInstanceMetadataLabels
        d = dict(src_dict)
        _annotations = d.pop("annotations", UNSET)
        annotations: InstanceListResponseRuntimeInstanceMetadataAnnotations | Unset
        if isinstance(_annotations,  Unset):
            annotations = UNSET
        else:
            annotations = InstanceListResponseRuntimeInstanceMetadataAnnotations.from_dict(_annotations)




        _extensions = d.pop("extensions", UNSET)
        extensions: InstanceListResponseRuntimeInstanceMetadataExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = InstanceListResponseRuntimeInstanceMetadataExtensions.from_dict(_extensions)




        _labels = d.pop("labels", UNSET)
        labels: InstanceListResponseRuntimeInstanceMetadataLabels | Unset
        if isinstance(_labels,  Unset):
            labels = UNSET
        else:
            labels = InstanceListResponseRuntimeInstanceMetadataLabels.from_dict(_labels)




        instance_list_response_runtime_instance_metadata = cls(
            annotations=annotations,
            extensions=extensions,
            labels=labels,
        )

        return instance_list_response_runtime_instance_metadata

