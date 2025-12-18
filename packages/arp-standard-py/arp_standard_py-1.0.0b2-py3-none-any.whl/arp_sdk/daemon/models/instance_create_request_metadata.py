from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.instance_create_request_metadata_extensions import InstanceCreateRequestMetadataExtensions
  from ..models.instance_create_request_metadata_annotations import InstanceCreateRequestMetadataAnnotations
  from ..models.instance_create_request_metadata_labels import InstanceCreateRequestMetadataLabels





T = TypeVar("T", bound="InstanceCreateRequestMetadata")



@_attrs_define
class InstanceCreateRequestMetadata:
    """ 
        Attributes:
            annotations (InstanceCreateRequestMetadataAnnotations | Unset):
            extensions (InstanceCreateRequestMetadataExtensions | Unset): Optional vendor extension map. Keys must be
                namespaced as <reverse_dns_or_org>.<key>.
            labels (InstanceCreateRequestMetadataLabels | Unset):
     """

    annotations: InstanceCreateRequestMetadataAnnotations | Unset = UNSET
    extensions: InstanceCreateRequestMetadataExtensions | Unset = UNSET
    labels: InstanceCreateRequestMetadataLabels | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.instance_create_request_metadata_extensions import InstanceCreateRequestMetadataExtensions
        from ..models.instance_create_request_metadata_annotations import InstanceCreateRequestMetadataAnnotations
        from ..models.instance_create_request_metadata_labels import InstanceCreateRequestMetadataLabels
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
        from ..models.instance_create_request_metadata_extensions import InstanceCreateRequestMetadataExtensions
        from ..models.instance_create_request_metadata_annotations import InstanceCreateRequestMetadataAnnotations
        from ..models.instance_create_request_metadata_labels import InstanceCreateRequestMetadataLabels
        d = dict(src_dict)
        _annotations = d.pop("annotations", UNSET)
        annotations: InstanceCreateRequestMetadataAnnotations | Unset
        if isinstance(_annotations,  Unset):
            annotations = UNSET
        else:
            annotations = InstanceCreateRequestMetadataAnnotations.from_dict(_annotations)




        _extensions = d.pop("extensions", UNSET)
        extensions: InstanceCreateRequestMetadataExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = InstanceCreateRequestMetadataExtensions.from_dict(_extensions)




        _labels = d.pop("labels", UNSET)
        labels: InstanceCreateRequestMetadataLabels | Unset
        if isinstance(_labels,  Unset):
            labels = UNSET
        else:
            labels = InstanceCreateRequestMetadataLabels.from_dict(_labels)




        instance_create_request_metadata = cls(
            annotations=annotations,
            extensions=extensions,
            labels=labels,
        )

        return instance_create_request_metadata

