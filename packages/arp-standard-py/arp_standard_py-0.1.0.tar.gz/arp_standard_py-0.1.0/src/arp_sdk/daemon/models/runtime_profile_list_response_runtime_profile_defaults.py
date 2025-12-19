from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.runtime_profile_list_response_runtime_profile_defaults_env import RuntimeProfileListResponseRuntimeProfileDefaultsEnv





T = TypeVar("T", bound="RuntimeProfileListResponseRuntimeProfileDefaults")



@_attrs_define
class RuntimeProfileListResponseRuntimeProfileDefaults:
    """ 
        Attributes:
            args (list[str] | Unset):
            env (RuntimeProfileListResponseRuntimeProfileDefaultsEnv | Unset):
            tool_registry_url (str | Unset): Transport-agnostic locator URI for an API endpoint (e.g.
                http://127.0.0.1:43120). Future deployments may use other URI schemes (e.g. unix://...).
     """

    args: list[str] | Unset = UNSET
    env: RuntimeProfileListResponseRuntimeProfileDefaultsEnv | Unset = UNSET
    tool_registry_url: str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.runtime_profile_list_response_runtime_profile_defaults_env import RuntimeProfileListResponseRuntimeProfileDefaultsEnv
        args: list[str] | Unset = UNSET
        if not isinstance(self.args, Unset):
            args = self.args



        env: dict[str, Any] | Unset = UNSET
        if not isinstance(self.env, Unset):
            env = self.env.to_dict()

        tool_registry_url = self.tool_registry_url


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if args is not UNSET:
            field_dict["args"] = args
        if env is not UNSET:
            field_dict["env"] = env
        if tool_registry_url is not UNSET:
            field_dict["tool_registry_url"] = tool_registry_url

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.runtime_profile_list_response_runtime_profile_defaults_env import RuntimeProfileListResponseRuntimeProfileDefaultsEnv
        d = dict(src_dict)
        args = cast(list[str], d.pop("args", UNSET))


        _env = d.pop("env", UNSET)
        env: RuntimeProfileListResponseRuntimeProfileDefaultsEnv | Unset
        if isinstance(_env,  Unset):
            env = UNSET
        else:
            env = RuntimeProfileListResponseRuntimeProfileDefaultsEnv.from_dict(_env)




        tool_registry_url = d.pop("tool_registry_url", UNSET)

        runtime_profile_list_response_runtime_profile_defaults = cls(
            args=args,
            env=env,
            tool_registry_url=tool_registry_url,
        )

        return runtime_profile_list_response_runtime_profile_defaults

