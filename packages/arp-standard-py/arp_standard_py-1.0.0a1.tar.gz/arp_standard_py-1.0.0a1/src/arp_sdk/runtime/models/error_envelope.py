from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.error_envelope_error import ErrorEnvelopeError
  from ..models.error_envelope_extensions import ErrorEnvelopeExtensions





T = TypeVar("T", bound="ErrorEnvelope")



@_attrs_define
class ErrorEnvelope:
    """ 
        Attributes:
            error (ErrorEnvelopeError):
            extensions (ErrorEnvelopeExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
     """

    error: ErrorEnvelopeError
    extensions: ErrorEnvelopeExtensions | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.error_envelope_error import ErrorEnvelopeError
        from ..models.error_envelope_extensions import ErrorEnvelopeExtensions
        error = self.error.to_dict()

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "error": error,
        })
        if extensions is not UNSET:
            field_dict["extensions"] = extensions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error_envelope_error import ErrorEnvelopeError
        from ..models.error_envelope_extensions import ErrorEnvelopeExtensions
        d = dict(src_dict)
        error = ErrorEnvelopeError.from_dict(d.pop("error"))




        _extensions = d.pop("extensions", UNSET)
        extensions: ErrorEnvelopeExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = ErrorEnvelopeExtensions.from_dict(_extensions)




        error_envelope = cls(
            error=error,
            extensions=extensions,
        )

        return error_envelope

