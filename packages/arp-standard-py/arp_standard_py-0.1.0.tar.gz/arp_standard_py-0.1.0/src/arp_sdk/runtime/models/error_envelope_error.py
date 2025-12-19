from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.error_envelope_error_error_cause import ErrorEnvelopeErrorErrorCause
  from ..models.error_envelope_error_extensions import ErrorEnvelopeErrorExtensions
  from ..models.error_envelope_error_details import ErrorEnvelopeErrorDetails





T = TypeVar("T", bound="ErrorEnvelopeError")



@_attrs_define
class ErrorEnvelopeError:
    """ 
        Attributes:
            code (str):
            message (str):
            cause (ErrorEnvelopeErrorErrorCause | Unset):
            details (ErrorEnvelopeErrorDetails | Unset):
            extensions (ErrorEnvelopeErrorExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            retryable (bool | Unset):
     """

    code: str
    message: str
    cause: ErrorEnvelopeErrorErrorCause | Unset = UNSET
    details: ErrorEnvelopeErrorDetails | Unset = UNSET
    extensions: ErrorEnvelopeErrorExtensions | Unset = UNSET
    retryable: bool | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.error_envelope_error_error_cause import ErrorEnvelopeErrorErrorCause
        from ..models.error_envelope_error_extensions import ErrorEnvelopeErrorExtensions
        from ..models.error_envelope_error_details import ErrorEnvelopeErrorDetails
        code = self.code

        message = self.message

        cause: dict[str, Any] | Unset = UNSET
        if not isinstance(self.cause, Unset):
            cause = self.cause.to_dict()

        details: dict[str, Any] | Unset = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict()

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        retryable = self.retryable


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "code": code,
            "message": message,
        })
        if cause is not UNSET:
            field_dict["cause"] = cause
        if details is not UNSET:
            field_dict["details"] = details
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if retryable is not UNSET:
            field_dict["retryable"] = retryable

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error_envelope_error_error_cause import ErrorEnvelopeErrorErrorCause
        from ..models.error_envelope_error_extensions import ErrorEnvelopeErrorExtensions
        from ..models.error_envelope_error_details import ErrorEnvelopeErrorDetails
        d = dict(src_dict)
        code = d.pop("code")

        message = d.pop("message")

        _cause = d.pop("cause", UNSET)
        cause: ErrorEnvelopeErrorErrorCause | Unset
        if isinstance(_cause,  Unset):
            cause = UNSET
        else:
            cause = ErrorEnvelopeErrorErrorCause.from_dict(_cause)




        _details = d.pop("details", UNSET)
        details: ErrorEnvelopeErrorDetails | Unset
        if isinstance(_details,  Unset):
            details = UNSET
        else:
            details = ErrorEnvelopeErrorDetails.from_dict(_details)




        _extensions = d.pop("extensions", UNSET)
        extensions: ErrorEnvelopeErrorExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = ErrorEnvelopeErrorExtensions.from_dict(_extensions)




        retryable = d.pop("retryable", UNSET)

        error_envelope_error = cls(
            code=code,
            message=message,
            cause=cause,
            details=details,
            extensions=extensions,
            retryable=retryable,
        )

        return error_envelope_error

