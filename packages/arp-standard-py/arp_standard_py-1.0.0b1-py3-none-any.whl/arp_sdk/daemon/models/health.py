from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.health_status import HealthStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime

if TYPE_CHECKING:
  from ..models.health_checks_item import HealthChecksItem
  from ..models.health_extensions import HealthExtensions





T = TypeVar("T", bound="Health")



@_attrs_define
class Health:
    """ 
        Attributes:
            status (HealthStatus):
            time (datetime.datetime):
            checks (list[HealthChecksItem] | Unset):
            extensions (HealthExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
     """

    status: HealthStatus
    time: datetime.datetime
    checks: list[HealthChecksItem] | Unset = UNSET
    extensions: HealthExtensions | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.health_checks_item import HealthChecksItem
        from ..models.health_extensions import HealthExtensions
        status = self.status.value

        time = self.time.isoformat()

        checks: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.checks, Unset):
            checks = []
            for checks_item_data in self.checks:
                checks_item = checks_item_data.to_dict()
                checks.append(checks_item)



        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "status": status,
            "time": time,
        })
        if checks is not UNSET:
            field_dict["checks"] = checks
        if extensions is not UNSET:
            field_dict["extensions"] = extensions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.health_checks_item import HealthChecksItem
        from ..models.health_extensions import HealthExtensions
        d = dict(src_dict)
        status = HealthStatus(d.pop("status"))




        time = isoparse(d.pop("time"))




        _checks = d.pop("checks", UNSET)
        checks: list[HealthChecksItem] | Unset = UNSET
        if _checks is not UNSET:
            checks = []
            for checks_item_data in _checks:
                checks_item = HealthChecksItem.from_dict(checks_item_data)



                checks.append(checks_item)


        _extensions = d.pop("extensions", UNSET)
        extensions: HealthExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = HealthExtensions.from_dict(_extensions)




        health = cls(
            status=status,
            time=time,
            checks=checks,
            extensions=extensions,
        )

        return health

