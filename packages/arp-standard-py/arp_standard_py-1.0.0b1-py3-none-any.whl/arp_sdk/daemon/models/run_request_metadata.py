from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.run_request_metadata_labels import RunRequestMetadataLabels
  from ..models.run_request_metadata_extensions import RunRequestMetadataExtensions
  from ..models.run_request_metadata_annotations import RunRequestMetadataAnnotations





T = TypeVar("T", bound="RunRequestMetadata")



@_attrs_define
class RunRequestMetadata:
    """ 
        Attributes:
            annotations (RunRequestMetadataAnnotations | Unset):
            extensions (RunRequestMetadataExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            labels (RunRequestMetadataLabels | Unset):
     """

    annotations: RunRequestMetadataAnnotations | Unset = UNSET
    extensions: RunRequestMetadataExtensions | Unset = UNSET
    labels: RunRequestMetadataLabels | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.run_request_metadata_labels import RunRequestMetadataLabels
        from ..models.run_request_metadata_extensions import RunRequestMetadataExtensions
        from ..models.run_request_metadata_annotations import RunRequestMetadataAnnotations
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
        from ..models.run_request_metadata_labels import RunRequestMetadataLabels
        from ..models.run_request_metadata_extensions import RunRequestMetadataExtensions
        from ..models.run_request_metadata_annotations import RunRequestMetadataAnnotations
        d = dict(src_dict)
        _annotations = d.pop("annotations", UNSET)
        annotations: RunRequestMetadataAnnotations | Unset
        if isinstance(_annotations,  Unset):
            annotations = UNSET
        else:
            annotations = RunRequestMetadataAnnotations.from_dict(_annotations)




        _extensions = d.pop("extensions", UNSET)
        extensions: RunRequestMetadataExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = RunRequestMetadataExtensions.from_dict(_extensions)




        _labels = d.pop("labels", UNSET)
        labels: RunRequestMetadataLabels | Unset
        if isinstance(_labels,  Unset):
            labels = UNSET
        else:
            labels = RunRequestMetadataLabels.from_dict(_labels)




        run_request_metadata = cls(
            annotations=annotations,
            extensions=extensions,
            labels=labels,
        )

        return run_request_metadata

