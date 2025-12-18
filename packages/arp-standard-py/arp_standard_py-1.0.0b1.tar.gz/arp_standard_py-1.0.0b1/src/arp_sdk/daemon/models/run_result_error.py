from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.run_result_error_extensions import RunResultErrorExtensions
  from ..models.run_result_error_details import RunResultErrorDetails
  from ..models.run_result_error_error_cause import RunResultErrorErrorCause





T = TypeVar("T", bound="RunResultError")



@_attrs_define
class RunResultError:
    """ 
        Attributes:
            code (str):
            message (str):
            cause (RunResultErrorErrorCause | Unset):
            details (RunResultErrorDetails | Unset):
            extensions (RunResultErrorExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            retryable (bool | Unset):
     """

    code: str
    message: str
    cause: RunResultErrorErrorCause | Unset = UNSET
    details: RunResultErrorDetails | Unset = UNSET
    extensions: RunResultErrorExtensions | Unset = UNSET
    retryable: bool | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.run_result_error_extensions import RunResultErrorExtensions
        from ..models.run_result_error_details import RunResultErrorDetails
        from ..models.run_result_error_error_cause import RunResultErrorErrorCause
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
        from ..models.run_result_error_extensions import RunResultErrorExtensions
        from ..models.run_result_error_details import RunResultErrorDetails
        from ..models.run_result_error_error_cause import RunResultErrorErrorCause
        d = dict(src_dict)
        code = d.pop("code")

        message = d.pop("message")

        _cause = d.pop("cause", UNSET)
        cause: RunResultErrorErrorCause | Unset
        if isinstance(_cause,  Unset):
            cause = UNSET
        else:
            cause = RunResultErrorErrorCause.from_dict(_cause)




        _details = d.pop("details", UNSET)
        details: RunResultErrorDetails | Unset
        if isinstance(_details,  Unset):
            details = UNSET
        else:
            details = RunResultErrorDetails.from_dict(_details)




        _extensions = d.pop("extensions", UNSET)
        extensions: RunResultErrorExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = RunResultErrorExtensions.from_dict(_extensions)




        retryable = d.pop("retryable", UNSET)

        run_result_error = cls(
            code=code,
            message=message,
            cause=cause,
            details=details,
            extensions=extensions,
            retryable=retryable,
        )

        return run_result_error

