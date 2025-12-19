from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.instance_register_request_metadata_extensions import InstanceRegisterRequestMetadataExtensions
  from ..models.instance_register_request_metadata_annotations import InstanceRegisterRequestMetadataAnnotations
  from ..models.instance_register_request_metadata_labels import InstanceRegisterRequestMetadataLabels





T = TypeVar("T", bound="InstanceRegisterRequestMetadata")



@_attrs_define
class InstanceRegisterRequestMetadata:
    """ 
        Attributes:
            annotations (InstanceRegisterRequestMetadataAnnotations | Unset):
            extensions (InstanceRegisterRequestMetadataExtensions | Unset): Optional vendor extension map. Keys must be
                namespaced as <reverse_dns_or_org>.<key>.
            labels (InstanceRegisterRequestMetadataLabels | Unset):
     """

    annotations: InstanceRegisterRequestMetadataAnnotations | Unset = UNSET
    extensions: InstanceRegisterRequestMetadataExtensions | Unset = UNSET
    labels: InstanceRegisterRequestMetadataLabels | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.instance_register_request_metadata_extensions import InstanceRegisterRequestMetadataExtensions
        from ..models.instance_register_request_metadata_annotations import InstanceRegisterRequestMetadataAnnotations
        from ..models.instance_register_request_metadata_labels import InstanceRegisterRequestMetadataLabels
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
        from ..models.instance_register_request_metadata_extensions import InstanceRegisterRequestMetadataExtensions
        from ..models.instance_register_request_metadata_annotations import InstanceRegisterRequestMetadataAnnotations
        from ..models.instance_register_request_metadata_labels import InstanceRegisterRequestMetadataLabels
        d = dict(src_dict)
        _annotations = d.pop("annotations", UNSET)
        annotations: InstanceRegisterRequestMetadataAnnotations | Unset
        if isinstance(_annotations,  Unset):
            annotations = UNSET
        else:
            annotations = InstanceRegisterRequestMetadataAnnotations.from_dict(_annotations)




        _extensions = d.pop("extensions", UNSET)
        extensions: InstanceRegisterRequestMetadataExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = InstanceRegisterRequestMetadataExtensions.from_dict(_extensions)




        _labels = d.pop("labels", UNSET)
        labels: InstanceRegisterRequestMetadataLabels | Unset
        if isinstance(_labels,  Unset):
            labels = UNSET
        else:
            labels = InstanceRegisterRequestMetadataLabels.from_dict(_labels)




        instance_register_request_metadata = cls(
            annotations=annotations,
            extensions=extensions,
            labels=labels,
        )

        return instance_register_request_metadata

