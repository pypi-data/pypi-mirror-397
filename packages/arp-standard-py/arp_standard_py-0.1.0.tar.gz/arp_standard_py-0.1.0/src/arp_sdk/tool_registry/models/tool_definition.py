from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.tool_definition_source import ToolDefinitionSource
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.tool_definition_extensions import ToolDefinitionExtensions
  from ..models.tool_definition_output_schema import ToolDefinitionOutputSchema
  from ..models.tool_definition_input_schema import ToolDefinitionInputSchema
  from ..models.tool_definition_metadata import ToolDefinitionMetadata





T = TypeVar("T", bound="ToolDefinition")



@_attrs_define
class ToolDefinition:
    """ 
        Attributes:
            input_schema (ToolDefinitionInputSchema):
            name (str):
            source (ToolDefinitionSource):
            tool_id (str):
            description (str | Unset):
            extensions (ToolDefinitionExtensions | Unset): Optional vendor extension map. Keys must be namespaced as
                <reverse_dns_or_org>.<key>.
            metadata (ToolDefinitionMetadata | Unset):
            output_schema (ToolDefinitionOutputSchema | Unset):
     """

    input_schema: ToolDefinitionInputSchema
    name: str
    source: ToolDefinitionSource
    tool_id: str
    description: str | Unset = UNSET
    extensions: ToolDefinitionExtensions | Unset = UNSET
    metadata: ToolDefinitionMetadata | Unset = UNSET
    output_schema: ToolDefinitionOutputSchema | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.tool_definition_extensions import ToolDefinitionExtensions
        from ..models.tool_definition_output_schema import ToolDefinitionOutputSchema
        from ..models.tool_definition_input_schema import ToolDefinitionInputSchema
        from ..models.tool_definition_metadata import ToolDefinitionMetadata
        input_schema = self.input_schema.to_dict()

        name = self.name

        source = self.source.value

        tool_id = self.tool_id

        description = self.description

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        output_schema: dict[str, Any] | Unset = UNSET
        if not isinstance(self.output_schema, Unset):
            output_schema = self.output_schema.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "input_schema": input_schema,
            "name": name,
            "source": source,
            "tool_id": tool_id,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if output_schema is not UNSET:
            field_dict["output_schema"] = output_schema

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tool_definition_extensions import ToolDefinitionExtensions
        from ..models.tool_definition_output_schema import ToolDefinitionOutputSchema
        from ..models.tool_definition_input_schema import ToolDefinitionInputSchema
        from ..models.tool_definition_metadata import ToolDefinitionMetadata
        d = dict(src_dict)
        input_schema = ToolDefinitionInputSchema.from_dict(d.pop("input_schema"))




        name = d.pop("name")

        source = ToolDefinitionSource(d.pop("source"))




        tool_id = d.pop("tool_id")

        description = d.pop("description", UNSET)

        _extensions = d.pop("extensions", UNSET)
        extensions: ToolDefinitionExtensions | Unset
        if isinstance(_extensions,  Unset):
            extensions = UNSET
        else:
            extensions = ToolDefinitionExtensions.from_dict(_extensions)




        _metadata = d.pop("metadata", UNSET)
        metadata: ToolDefinitionMetadata | Unset
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = ToolDefinitionMetadata.from_dict(_metadata)




        _output_schema = d.pop("output_schema", UNSET)
        output_schema: ToolDefinitionOutputSchema | Unset
        if isinstance(_output_schema,  Unset):
            output_schema = UNSET
        else:
            output_schema = ToolDefinitionOutputSchema.from_dict(_output_schema)




        tool_definition = cls(
            input_schema=input_schema,
            name=name,
            source=source,
            tool_id=tool_id,
            description=description,
            extensions=extensions,
            metadata=metadata,
            output_schema=output_schema,
        )

        return tool_definition

