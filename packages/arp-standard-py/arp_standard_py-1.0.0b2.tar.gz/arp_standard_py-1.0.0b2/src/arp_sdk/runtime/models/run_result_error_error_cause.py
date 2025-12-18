from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.run_result_error_error_cause_details import RunResultErrorErrorCauseDetails
  from ..models.run_result_error_error_cause_extensions import RunResultErrorErrorCauseExtensions





T = TypeVar("T", bound="RunResultErrorErrorCause")



@_attrs_define
class RunResultErrorErrorCause:
    """ 
        Attributes:
            message (str):
            code (str | Unset):
            details (RunResultErrorErrorCauseDetails | Unset):
            extensions (RunResultErrorErrorCauseExtensions | Unset): Optional vendor extension map. Keys must be namespaced
                as <reverse_dns_or_org>.<key>.
     """

    message: str
    code: str | Unset = UNSET
    details: RunResultErrorErrorCauseDetails | Unset = UNSET
    extensions: RunResultErrorErrorCauseExtensions | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.run_result_error_error_cause_details import RunResultErrorErrorCauseDetails
        from ..models.run_result_error_error_cause_extensions import RunResultErrorErrorCauseExtensions
        message = self.message

        code = self.code

        details: dict[str, Any] | Unset = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict()

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "message": message,
        })
        if code is not UNSET:
            field_dict["code"] = code
        if details is not UNSET:
            field_dict["details"] = details
        if extensions is not UNSET:
            field_dict["extensions"] = extensions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_result_error_error_cause_details import RunResultErrorErrorCauseDetails
        from ..models.run_result_error_error_cause_extensions import RunResultErrorErrorCauseExtensions
        d = dict(src_dict)
        message = d.pop("message")

        code = d.pop("code", UNSET)

        _details = d.pop("details", UNSET)
        details: RunResultErrorErrorCauseDetails | Unset
        if isinstance(_details,  Unset):
            details = UNSET
        else:
            details = RunResultErrorErrorCauseDetails.from_dict(_details)




        _extensions = d.pop("extensions", UNSET)
        extensions: RunResultErrorErrorCauseExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = RunResultErrorErrorCauseExtensions.from_dict(_extensions)




        run_result_error_error_cause = cls(
            message=message,
            code=code,
            details=details,
            extensions=extensions,
        )

        return run_result_error_error_cause

