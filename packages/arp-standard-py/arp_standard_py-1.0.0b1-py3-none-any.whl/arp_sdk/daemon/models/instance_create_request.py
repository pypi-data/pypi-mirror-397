from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.instance_create_request_env import InstanceCreateRequestEnv
  from ..models.instance_create_request_extensions import InstanceCreateRequestExtensions





T = TypeVar("T", bound="InstanceCreateRequest")



@_attrs_define
class InstanceCreateRequest:
    """ 
        Attributes:
            profile (str):
            args (list[str] | Unset):
            count (int | Unset):  Default: 1.
            env (InstanceCreateRequestEnv | Unset):
            extensions (InstanceCreateRequestExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            runtime_type (str | Unset):
     """

    profile: str
    args: list[str] | Unset = UNSET
    count: int | Unset = 1
    env: InstanceCreateRequestEnv | Unset = UNSET
    extensions: InstanceCreateRequestExtensions | Unset = UNSET
    runtime_type: str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.instance_create_request_env import InstanceCreateRequestEnv
        from ..models.instance_create_request_extensions import InstanceCreateRequestExtensions
        profile = self.profile

        args: list[str] | Unset = UNSET
        if not isinstance(self.args, Unset):
            args = self.args



        count = self.count

        env: dict[str, Any] | Unset = UNSET
        if not isinstance(self.env, Unset):
            env = self.env.to_dict()

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        runtime_type = self.runtime_type


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "profile": profile,
        })
        if args is not UNSET:
            field_dict["args"] = args
        if count is not UNSET:
            field_dict["count"] = count
        if env is not UNSET:
            field_dict["env"] = env
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if runtime_type is not UNSET:
            field_dict["runtime_type"] = runtime_type

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.instance_create_request_env import InstanceCreateRequestEnv
        from ..models.instance_create_request_extensions import InstanceCreateRequestExtensions
        d = dict(src_dict)
        profile = d.pop("profile")

        args = cast(list[str], d.pop("args", UNSET))


        count = d.pop("count", UNSET)

        _env = d.pop("env", UNSET)
        env: InstanceCreateRequestEnv | Unset
        if isinstance(_env,  Unset):
            env = UNSET
        else:
            env = InstanceCreateRequestEnv.from_dict(_env)




        _extensions = d.pop("extensions", UNSET)
        extensions: InstanceCreateRequestExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = InstanceCreateRequestExtensions.from_dict(_extensions)




        runtime_type = d.pop("runtime_type", UNSET)

        instance_create_request = cls(
            profile=profile,
            args=args,
            count=count,
            env=env,
            extensions=extensions,
            runtime_type=runtime_type,
        )

        return instance_create_request

