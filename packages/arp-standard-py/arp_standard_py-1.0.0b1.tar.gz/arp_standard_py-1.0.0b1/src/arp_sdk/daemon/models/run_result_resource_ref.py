from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.run_result_resource_ref_extensions import RunResultResourceRefExtensions





T = TypeVar("T", bound="RunResultResourceRef")



@_attrs_define
class RunResultResourceRef:
    """ 
        Attributes:
            id (str):
            type_ (str):
            extensions (RunResultResourceRefExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            uri (str | Unset):
     """

    id: str
    type_: str
    extensions: RunResultResourceRefExtensions | Unset = UNSET
    uri: str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.run_result_resource_ref_extensions import RunResultResourceRefExtensions
        id = self.id

        type_ = self.type_

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        uri = self.uri


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "id": id,
            "type": type_,
        })
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if uri is not UNSET:
            field_dict["uri"] = uri

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_result_resource_ref_extensions import RunResultResourceRefExtensions
        d = dict(src_dict)
        id = d.pop("id")

        type_ = d.pop("type")

        _extensions = d.pop("extensions", UNSET)
        extensions: RunResultResourceRefExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = RunResultResourceRefExtensions.from_dict(_extensions)




        uri = d.pop("uri", UNSET)

        run_result_resource_ref = cls(
            id=id,
            type_=type_,
            extensions=extensions,
            uri=uri,
        )

        return run_result_resource_ref

