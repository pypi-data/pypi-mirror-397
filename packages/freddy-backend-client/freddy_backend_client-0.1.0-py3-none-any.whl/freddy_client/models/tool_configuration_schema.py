from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mcp_tool_schema import MCPToolSchema
    from ..models.tool_configuration_schema_system_tools_type_0 import (
        ToolConfigurationSchemaSystemToolsType0,
    )


T = TypeVar("T", bound="ToolConfigurationSchema")


@_attrs_define
class ToolConfigurationSchema:
    """Tool configuration schema.

    Attributes:
        system_tools (None | ToolConfigurationSchemaSystemToolsType0 | Unset): System tools configuration
        mcp_tools (list[MCPToolSchema] | None | Unset): MCP tools configuration
        streamline_tools (list[str] | None | Unset): Streamline automation IDs
    """

    system_tools: None | ToolConfigurationSchemaSystemToolsType0 | Unset = UNSET
    mcp_tools: list[MCPToolSchema] | None | Unset = UNSET
    streamline_tools: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.tool_configuration_schema_system_tools_type_0 import (
            ToolConfigurationSchemaSystemToolsType0,
        )

        system_tools: dict[str, Any] | None | Unset
        if isinstance(self.system_tools, Unset):
            system_tools = UNSET
        elif isinstance(self.system_tools, ToolConfigurationSchemaSystemToolsType0):
            system_tools = self.system_tools.to_dict()
        else:
            system_tools = self.system_tools

        mcp_tools: list[dict[str, Any]] | None | Unset
        if isinstance(self.mcp_tools, Unset):
            mcp_tools = UNSET
        elif isinstance(self.mcp_tools, list):
            mcp_tools = []
            for mcp_tools_type_0_item_data in self.mcp_tools:
                mcp_tools_type_0_item = mcp_tools_type_0_item_data.to_dict()
                mcp_tools.append(mcp_tools_type_0_item)

        else:
            mcp_tools = self.mcp_tools

        streamline_tools: list[str] | None | Unset
        if isinstance(self.streamline_tools, Unset):
            streamline_tools = UNSET
        elif isinstance(self.streamline_tools, list):
            streamline_tools = self.streamline_tools

        else:
            streamline_tools = self.streamline_tools

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if system_tools is not UNSET:
            field_dict["system_tools"] = system_tools
        if mcp_tools is not UNSET:
            field_dict["mcp_tools"] = mcp_tools
        if streamline_tools is not UNSET:
            field_dict["streamline_tools"] = streamline_tools

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mcp_tool_schema import MCPToolSchema
        from ..models.tool_configuration_schema_system_tools_type_0 import (
            ToolConfigurationSchemaSystemToolsType0,
        )

        d = dict(src_dict)

        def _parse_system_tools(
            data: object,
        ) -> None | ToolConfigurationSchemaSystemToolsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                system_tools_type_0 = ToolConfigurationSchemaSystemToolsType0.from_dict(
                    data
                )

                return system_tools_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ToolConfigurationSchemaSystemToolsType0 | Unset, data)

        system_tools = _parse_system_tools(d.pop("system_tools", UNSET))

        def _parse_mcp_tools(data: object) -> list[MCPToolSchema] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                mcp_tools_type_0 = []
                _mcp_tools_type_0 = data
                for mcp_tools_type_0_item_data in _mcp_tools_type_0:
                    mcp_tools_type_0_item = MCPToolSchema.from_dict(
                        mcp_tools_type_0_item_data
                    )

                    mcp_tools_type_0.append(mcp_tools_type_0_item)

                return mcp_tools_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[MCPToolSchema] | None | Unset, data)

        mcp_tools = _parse_mcp_tools(d.pop("mcp_tools", UNSET))

        def _parse_streamline_tools(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                streamline_tools_type_0 = cast(list[str], data)

                return streamline_tools_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        streamline_tools = _parse_streamline_tools(d.pop("streamline_tools", UNSET))

        tool_configuration_schema = cls(
            system_tools=system_tools,
            mcp_tools=mcp_tools,
            streamline_tools=streamline_tools,
        )

        tool_configuration_schema.additional_properties = d
        return tool_configuration_schema

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
