from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.health_checks_item_status import HealthChecksItemStatus
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.health_checks_item_details import HealthChecksItemDetails





T = TypeVar("T", bound="HealthChecksItem")



@_attrs_define
class HealthChecksItem:
    """ 
        Attributes:
            name (str):
            status (HealthChecksItemStatus):
            details (HealthChecksItemDetails | Unset):
            message (str | Unset):
     """

    name: str
    status: HealthChecksItemStatus
    details: HealthChecksItemDetails | Unset = UNSET
    message: str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.health_checks_item_details import HealthChecksItemDetails
        name = self.name

        status = self.status.value

        details: dict[str, Any] | Unset = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict()

        message = self.message


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "name": name,
            "status": status,
        })
        if details is not UNSET:
            field_dict["details"] = details
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.health_checks_item_details import HealthChecksItemDetails
        d = dict(src_dict)
        name = d.pop("name")

        status = HealthChecksItemStatus(d.pop("status"))




        _details = d.pop("details", UNSET)
        details: HealthChecksItemDetails | Unset
        if isinstance(_details,  Unset):
            details = UNSET
        else:
            details = HealthChecksItemDetails.from_dict(_details)




        message = d.pop("message", UNSET)

        health_checks_item = cls(
            name=name,
            status=status,
            details=details,
            message=message,
        )

        return health_checks_item

