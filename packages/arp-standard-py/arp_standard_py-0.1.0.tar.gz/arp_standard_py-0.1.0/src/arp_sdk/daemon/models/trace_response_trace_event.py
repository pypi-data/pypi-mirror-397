from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.trace_response_trace_event_level import TraceResponseTraceEventLevel
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime

if TYPE_CHECKING:
  from ..models.trace_response_trace_event_extensions import TraceResponseTraceEventExtensions
  from ..models.trace_response_trace_event_data import TraceResponseTraceEventData





T = TypeVar("T", bound="TraceResponseTraceEvent")



@_attrs_define
class TraceResponseTraceEvent:
    """ 
        Attributes:
            level (TraceResponseTraceEventLevel):
            run_id (str):
            seq (int):
            time (datetime.datetime):
            type_ (str):
            data (TraceResponseTraceEventData | Unset):
            extensions (TraceResponseTraceEventExtensions | Unset): Optional vendor extension map. Keys must be namespaced
                as <reverse_dns_or_org>.<key>.
     """

    level: TraceResponseTraceEventLevel
    run_id: str
    seq: int
    time: datetime.datetime
    type_: str
    data: TraceResponseTraceEventData | Unset = UNSET
    extensions: TraceResponseTraceEventExtensions | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.trace_response_trace_event_extensions import TraceResponseTraceEventExtensions
        from ..models.trace_response_trace_event_data import TraceResponseTraceEventData
        level = self.level.value

        run_id = self.run_id

        seq = self.seq

        time = self.time.isoformat()

        type_ = self.type_

        data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "level": level,
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
        from ..models.trace_response_trace_event_extensions import TraceResponseTraceEventExtensions
        from ..models.trace_response_trace_event_data import TraceResponseTraceEventData
        d = dict(src_dict)
        level = TraceResponseTraceEventLevel(d.pop("level"))




        run_id = d.pop("run_id")

        seq = d.pop("seq")

        time = isoparse(d.pop("time"))




        type_ = d.pop("type")

        _data = d.pop("data", UNSET)
        data: TraceResponseTraceEventData | Unset
        if isinstance(_data,  Unset):
            data = UNSET
        else:
            data = TraceResponseTraceEventData.from_dict(_data)




        _extensions = d.pop("extensions", UNSET)
        extensions: TraceResponseTraceEventExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = TraceResponseTraceEventExtensions.from_dict(_extensions)




        trace_response_trace_event = cls(
            level=level,
            run_id=run_id,
            seq=seq,
            time=time,
            type_=type_,
            data=data,
            extensions=extensions,
        )

        return trace_response_trace_event

