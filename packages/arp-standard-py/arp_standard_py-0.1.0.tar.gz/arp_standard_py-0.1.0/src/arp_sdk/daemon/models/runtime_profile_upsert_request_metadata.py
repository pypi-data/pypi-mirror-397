from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.runtime_profile_upsert_request_metadata_labels import RuntimeProfileUpsertRequestMetadataLabels
  from ..models.runtime_profile_upsert_request_metadata_annotations import RuntimeProfileUpsertRequestMetadataAnnotations
  from ..models.runtime_profile_upsert_request_metadata_extensions import RuntimeProfileUpsertRequestMetadataExtensions





T = TypeVar("T", bound="RuntimeProfileUpsertRequestMetadata")



@_attrs_define
class RuntimeProfileUpsertRequestMetadata:
    """ 
        Attributes:
            annotations (RuntimeProfileUpsertRequestMetadataAnnotations | Unset):
            extensions (RuntimeProfileUpsertRequestMetadataExtensions | Unset): Optional vendor extension map. Keys must be
                namespaced as <reverse_dns_or_org>.<key>.
            labels (RuntimeProfileUpsertRequestMetadataLabels | Unset):
     """

    annotations: RuntimeProfileUpsertRequestMetadataAnnotations | Unset = UNSET
    extensions: RuntimeProfileUpsertRequestMetadataExtensions | Unset = UNSET
    labels: RuntimeProfileUpsertRequestMetadataLabels | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.runtime_profile_upsert_request_metadata_labels import RuntimeProfileUpsertRequestMetadataLabels
        from ..models.runtime_profile_upsert_request_metadata_annotations import RuntimeProfileUpsertRequestMetadataAnnotations
        from ..models.runtime_profile_upsert_request_metadata_extensions import RuntimeProfileUpsertRequestMetadataExtensions
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
        from ..models.runtime_profile_upsert_request_metadata_labels import RuntimeProfileUpsertRequestMetadataLabels
        from ..models.runtime_profile_upsert_request_metadata_annotations import RuntimeProfileUpsertRequestMetadataAnnotations
        from ..models.runtime_profile_upsert_request_metadata_extensions import RuntimeProfileUpsertRequestMetadataExtensions
        d = dict(src_dict)
        _annotations = d.pop("annotations", UNSET)
        annotations: RuntimeProfileUpsertRequestMetadataAnnotations | Unset
        if isinstance(_annotations,  Unset):
            annotations = UNSET
        else:
            annotations = RuntimeProfileUpsertRequestMetadataAnnotations.from_dict(_annotations)




        _extensions = d.pop("extensions", UNSET)
        extensions: RuntimeProfileUpsertRequestMetadataExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = RuntimeProfileUpsertRequestMetadataExtensions.from_dict(_extensions)




        _labels = d.pop("labels", UNSET)
        labels: RuntimeProfileUpsertRequestMetadataLabels | Unset
        if isinstance(_labels,  Unset):
            labels = UNSET
        else:
            labels = RuntimeProfileUpsertRequestMetadataLabels.from_dict(_labels)




        runtime_profile_upsert_request_metadata = cls(
            annotations=annotations,
            extensions=extensions,
            labels=labels,
        )

        return runtime_profile_upsert_request_metadata

