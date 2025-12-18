from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.run_event_type import RunEventType
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime

if TYPE_CHECKING:
  from ..models.run_event_data import RunEventData
  from ..models.run_event_extensions import RunEventExtensions





T = TypeVar("T", bound="RunEvent")



@_attrs_define
class RunEvent:
    """ 
        Attributes:
            run_id (str):
            seq (int):
            time (datetime.datetime):
            type_ (RunEventType):
            data (RunEventData | Unset):
            extensions (RunEventExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
     """

    run_id: str
    seq: int
    time: datetime.datetime
    type_: RunEventType
    data: RunEventData | Unset = UNSET
    extensions: RunEventExtensions | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.run_event_data import RunEventData
        from ..models.run_event_extensions import RunEventExtensions
        run_id = self.run_id

        seq = self.seq

        time = self.time.isoformat()

        type_ = self.type_.value

        data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "run_id": run_id,
            "seq": seq,
            "time": time,
            "type": type_,
        })
        if data is not UNSET:
            field_dict["data"] = data
        if extensions is not UNSET:
            field_dict["extensions"] = extensions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_event_data import RunEventData
        from ..models.run_event_extensions import RunEventExtensions
        d = dict(src_dict)
        run_id = d.pop("run_id")

        seq = d.pop("seq")

        time = isoparse(d.pop("time"))




        type_ = RunEventType(d.pop("type"))




        _data = d.pop("data", UNSET)
        data: RunEventData | Unset
        if isinstance(_data,  Unset):
            data = UNSET
        else:
            data = RunEventData.from_dict(_data)




        _extensions = d.pop("extensions", UNSET)
        extensions: RunEventExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = RunEventExtensions.from_dict(_extensions)




        run_event = cls(
            run_id=run_id,
            seq=seq,
            time=time,
            type_=type_,
            data=data,
            extensions=extensions,
        )

        return run_event

