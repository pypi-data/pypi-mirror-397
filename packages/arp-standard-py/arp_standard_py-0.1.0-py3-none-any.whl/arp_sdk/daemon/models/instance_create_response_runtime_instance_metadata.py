from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.instance_create_response_runtime_instance_metadata_labels import InstanceCreateResponseRuntimeInstanceMetadataLabels
  from ..models.instance_create_response_runtime_instance_metadata_annotations import InstanceCreateResponseRuntimeInstanceMetadataAnnotations
  from ..models.instance_create_response_runtime_instance_metadata_extensions import InstanceCreateResponseRuntimeInstanceMetadataExtensions





T = TypeVar("T", bound="InstanceCreateResponseRuntimeInstanceMetadata")



@_attrs_define
class InstanceCreateResponseRuntimeInstanceMetadata:
    """ 
        Attributes:
            annotations (InstanceCreateResponseRuntimeInstanceMetadataAnnotations | Unset):
            extensions (InstanceCreateResponseRuntimeInstanceMetadataExtensions | Unset): Optional vendor extension map.
                Keys must be namespaced as <reverse_dns_or_org>.<key>.
            labels (InstanceCreateResponseRuntimeInstanceMetadataLabels | Unset):
     """

    annotations: InstanceCreateResponseRuntimeInstanceMetadataAnnotations | Unset = UNSET
    extensions: InstanceCreateResponseRuntimeInstanceMetadataExtensions | Unset = UNSET
    labels: InstanceCreateResponseRuntimeInstanceMetadataLabels | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.instance_create_response_runtime_instance_metadata_labels import InstanceCreateResponseRuntimeInstanceMetadataLabels
        from ..models.instance_create_response_runtime_instance_metadata_annotations import InstanceCreateResponseRuntimeInstanceMetadataAnnotations
        from ..models.instance_create_response_runtime_instance_metadata_extensions import InstanceCreateResponseRuntimeInstanceMetadataExtensions
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
        from ..models.instance_create_response_runtime_instance_metadata_labels import InstanceCreateResponseRuntimeInstanceMetadataLabels
        from ..models.instance_create_response_runtime_instance_metadata_annotations import InstanceCreateResponseRuntimeInstanceMetadataAnnotations
        from ..models.instance_create_response_runtime_instance_metadata_extensions import InstanceCreateResponseRuntimeInstanceMetadataExtensions
        d = dict(src_dict)
        _annotations = d.pop("annotations", UNSET)
        annotations: InstanceCreateResponseRuntimeInstanceMetadataAnnotations | Unset
        if isinstance(_annotations,  Unset):
            annotations = UNSET
        else:
            annotations = InstanceCreateResponseRuntimeInstanceMetadataAnnotations.from_dict(_annotations)




        _extensions = d.pop("extensions", UNSET)
        extensions: InstanceCreateResponseRuntimeInstanceMetadataExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = InstanceCreateResponseRuntimeInstanceMetadataExtensions.from_dict(_extensions)




        _labels = d.pop("labels", UNSET)
        labels: InstanceCreateResponseRuntimeInstanceMetadataLabels | Unset
        if isinstance(_labels,  Unset):
            labels = UNSET
        else:
            labels = InstanceCreateResponseRuntimeInstanceMetadataLabels.from_dict(_labels)




        instance_create_response_runtime_instance_metadata = cls(
            annotations=annotations,
            extensions=extensions,
            labels=labels,
        )

        return instance_create_response_runtime_instance_metadata

