from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.trace_response_extensions import TraceResponseExtensions
  from ..models.trace_response_trace_event import TraceResponseTraceEvent





T = TypeVar("T", bound="TraceResponse")



@_attrs_define
class TraceResponse:
    """ 
        Attributes:
            events (list[TraceResponseTraceEvent] | Unset):
            extensions (TraceResponseExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            trace_uri (str | Unset):
     """

    events: list[TraceResponseTraceEvent] | Unset = UNSET
    extensions: TraceResponseExtensions | Unset = UNSET
    trace_uri: str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.trace_response_extensions import TraceResponseExtensions
        from ..models.trace_response_trace_event import TraceResponseTraceEvent
        events: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.events, Unset):
            events = []
            for events_item_data in self.events:
                events_item = events_item_data.to_dict()
                events.append(events_item)



        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        trace_uri = self.trace_uri


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if events is not UNSET:
            field_dict["events"] = events
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if trace_uri is not UNSET:
            field_dict["trace_uri"] = trace_uri

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.trace_response_extensions import TraceResponseExtensions
        from ..models.trace_response_trace_event import TraceResponseTraceEvent
        d = dict(src_dict)
        _events = d.pop("events", UNSET)
        events: list[TraceResponseTraceEvent] | Unset = UNSET
        if _events is not UNSET:
            events = []
            for events_item_data in _events:
                events_item = TraceResponseTraceEvent.from_dict(events_item_data)



                events.append(events_item)


        _extensions = d.pop("extensions", UNSET)
        extensions: TraceResponseExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = TraceResponseExtensions.from_dict(_extensions)




        trace_uri = d.pop("trace_uri", UNSET)

        trace_response = cls(
            events=events,
            extensions=extensions,
            trace_uri=trace_uri,
        )

        return trace_response

