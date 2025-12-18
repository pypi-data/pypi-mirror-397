from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="VersionInfoBuild")



@_attrs_define
class VersionInfoBuild:
    """ 
        Attributes:
            built_at (datetime.datetime | Unset):
            commit (str | Unset):
            dirty (bool | Unset):
     """

    built_at: datetime.datetime | Unset = UNSET
    commit: str | Unset = UNSET
    dirty: bool | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        built_at: str | Unset = UNSET
        if not isinstance(self.built_at, Unset):
            built_at = self.built_at.isoformat()

        commit = self.commit

        dirty = self.dirty


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if built_at is not UNSET:
            field_dict["built_at"] = built_at
        if commit is not UNSET:
            field_dict["commit"] = commit
        if dirty is not UNSET:
            field_dict["dirty"] = dirty

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _built_at = d.pop("built_at", UNSET)
        built_at: datetime.datetime | Unset
        if isinstance(_built_at,  Unset):
            built_at = UNSET
        else:
            built_at = isoparse(_built_at)




        commit = d.pop("commit", UNSET)

        dirty = d.pop("dirty", UNSET)

        version_info_build = cls(
            built_at=built_at,
            commit=commit,
            dirty=dirty,
        )

        return version_info_build

