from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.version_info_extensions import VersionInfoExtensions
  from ..models.version_info_build import VersionInfoBuild





T = TypeVar("T", bound="VersionInfo")



@_attrs_define
class VersionInfo:
    """ 
        Attributes:
            service_name (str):
            service_version (str):
            supported_api_versions (list[str]):
            build (VersionInfoBuild | Unset):
            extensions (VersionInfoExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
     """

    service_name: str
    service_version: str
    supported_api_versions: list[str]
    build: VersionInfoBuild | Unset = UNSET
    extensions: VersionInfoExtensions | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.version_info_extensions import VersionInfoExtensions
        from ..models.version_info_build import VersionInfoBuild
        service_name = self.service_name

        service_version = self.service_version

        supported_api_versions = self.supported_api_versions



        build: dict[str, Any] | Unset = UNSET
        if not isinstance(self.build, Unset):
            build = self.build.to_dict()

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "service_name": service_name,
            "service_version": service_version,
            "supported_api_versions": supported_api_versions,
        })
        if build is not UNSET:
            field_dict["build"] = build
        if extensions is not UNSET:
            field_dict["extensions"] = extensions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.version_info_extensions import VersionInfoExtensions
        from ..models.version_info_build import VersionInfoBuild
        d = dict(src_dict)
        service_name = d.pop("service_name")

        service_version = d.pop("service_version")

        supported_api_versions = cast(list[str], d.pop("supported_api_versions"))


        _build = d.pop("build", UNSET)
        build: VersionInfoBuild | Unset
        if isinstance(_build,  Unset):
            build = UNSET
        else:
            build = VersionInfoBuild.from_dict(_build)




        _extensions = d.pop("extensions", UNSET)
        extensions: VersionInfoExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = VersionInfoExtensions.from_dict(_extensions)




        version_info = cls(
            service_name=service_name,
            service_version=service_version,
            supported_api_versions=supported_api_versions,
            build=build,
            extensions=extensions,
        )

        return version_info

