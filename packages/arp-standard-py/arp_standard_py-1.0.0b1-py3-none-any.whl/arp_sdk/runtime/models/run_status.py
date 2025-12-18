from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.run_status_state import RunStatusState
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime

if TYPE_CHECKING:
  from ..models.run_status_extensions import RunStatusExtensions





T = TypeVar("T", bound="RunStatus")



@_attrs_define
class RunStatus:
    """ 
        Attributes:
            run_id (str):
            state (RunStatusState):
            ended_at (datetime.datetime | Unset):
            extensions (RunStatusExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            runtime_instance_id (str | Unset):
            started_at (datetime.datetime | Unset):
     """

    run_id: str
    state: RunStatusState
    ended_at: datetime.datetime | Unset = UNSET
    extensions: RunStatusExtensions | Unset = UNSET
    runtime_instance_id: str | Unset = UNSET
    started_at: datetime.datetime | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.run_status_extensions import RunStatusExtensions
        run_id = self.run_id

        state = self.state.value

        ended_at: str | Unset = UNSET
        if not isinstance(self.ended_at, Unset):
            ended_at = self.ended_at.isoformat()

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        runtime_instance_id = self.runtime_instance_id

        started_at: str | Unset = UNSET
        if not isinstance(self.started_at, Unset):
            started_at = self.started_at.isoformat()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "run_id": run_id,
            "state": state,
        })
        if ended_at is not UNSET:
            field_dict["ended_at"] = ended_at
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if runtime_instance_id is not UNSET:
            field_dict["runtime_instance_id"] = runtime_instance_id
        if started_at is not UNSET:
            field_dict["started_at"] = started_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_status_extensions import RunStatusExtensions
        d = dict(src_dict)
        run_id = d.pop("run_id")

        state = RunStatusState(d.pop("state"))




        _ended_at = d.pop("ended_at", UNSET)
        ended_at: datetime.datetime | Unset
        if isinstance(_ended_at,  Unset):
            ended_at = UNSET
        else:
            ended_at = isoparse(_ended_at)




        _extensions = d.pop("extensions", UNSET)
        extensions: RunStatusExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = RunStatusExtensions.from_dict(_extensions)




        runtime_instance_id = d.pop("runtime_instance_id", UNSET)

        _started_at = d.pop("started_at", UNSET)
        started_at: datetime.datetime | Unset
        if isinstance(_started_at,  Unset):
            started_at = UNSET
        else:
            started_at = isoparse(_started_at)




        run_status = cls(
            run_id=run_id,
            state=state,
            ended_at=ended_at,
            extensions=extensions,
            runtime_instance_id=runtime_instance_id,
            started_at=started_at,
        )

        return run_status

