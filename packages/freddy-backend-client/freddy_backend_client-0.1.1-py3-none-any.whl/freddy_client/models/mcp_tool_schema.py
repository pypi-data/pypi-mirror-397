from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mcp_tool_schema_allowed_tools_type_1 import (
        MCPToolSchemaAllowedToolsType1,
    )
    from ..models.mcp_tool_schema_headers_type_0 import MCPToolSchemaHeadersType0
    from ..models.mcp_tool_schema_require_approval_type_0 import (
        MCPToolSchemaRequireApprovalType0,
    )


T = TypeVar("T", bound="MCPToolSchema")


@_attrs_define
class MCPToolSchema:
    """MCP tool configuration schema.

    Attributes:
        server_label (str): Server label
        type_ (str | Unset): Tool type Default: 'mcp'.
        allowed_tools (list[str] | MCPToolSchemaAllowedToolsType1 | None | Unset): Allowed tools
        authorization (None | str | Unset): OAuth token
        connector_id (None | str | Unset): Connector ID
        headers (MCPToolSchemaHeadersType0 | None | Unset): Custom headers
        require_approval (MCPToolSchemaRequireApprovalType0 | None | str | Unset): Approval policy
        server_description (None | str | Unset): Server description
        server_url (None | str | Unset): Server URL
    """

    server_label: str
    type_: str | Unset = "mcp"
    allowed_tools: list[str] | MCPToolSchemaAllowedToolsType1 | None | Unset = UNSET
    authorization: None | str | Unset = UNSET
    connector_id: None | str | Unset = UNSET
    headers: MCPToolSchemaHeadersType0 | None | Unset = UNSET
    require_approval: MCPToolSchemaRequireApprovalType0 | None | str | Unset = UNSET
    server_description: None | str | Unset = UNSET
    server_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.mcp_tool_schema_allowed_tools_type_1 import (
            MCPToolSchemaAllowedToolsType1,
        )
        from ..models.mcp_tool_schema_headers_type_0 import MCPToolSchemaHeadersType0
        from ..models.mcp_tool_schema_require_approval_type_0 import (
            MCPToolSchemaRequireApprovalType0,
        )

        server_label = self.server_label

        type_ = self.type_

        allowed_tools: dict[str, Any] | list[str] | None | Unset
        if isinstance(self.allowed_tools, Unset):
            allowed_tools = UNSET
        elif isinstance(self.allowed_tools, list):
            allowed_tools = self.allowed_tools

        elif isinstance(self.allowed_tools, MCPToolSchemaAllowedToolsType1):
            allowed_tools = self.allowed_tools.to_dict()
        else:
            allowed_tools = self.allowed_tools

        authorization: None | str | Unset
        if isinstance(self.authorization, Unset):
            authorization = UNSET
        else:
            authorization = self.authorization

        connector_id: None | str | Unset
        if isinstance(self.connector_id, Unset):
            connector_id = UNSET
        else:
            connector_id = self.connector_id

        headers: dict[str, Any] | None | Unset
        if isinstance(self.headers, Unset):
            headers = UNSET
        elif isinstance(self.headers, MCPToolSchemaHeadersType0):
            headers = self.headers.to_dict()
        else:
            headers = self.headers

        require_approval: dict[str, Any] | None | str | Unset
        if isinstance(self.require_approval, Unset):
            require_approval = UNSET
        elif isinstance(self.require_approval, MCPToolSchemaRequireApprovalType0):
            require_approval = self.require_approval.to_dict()
        else:
            require_approval = self.require_approval

        server_description: None | str | Unset
        if isinstance(self.server_description, Unset):
            server_description = UNSET
        else:
            server_description = self.server_description

        server_url: None | str | Unset
        if isinstance(self.server_url, Unset):
            server_url = UNSET
        else:
            server_url = self.server_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "server_label": server_label,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_
        if allowed_tools is not UNSET:
            field_dict["allowed_tools"] = allowed_tools
        if authorization is not UNSET:
            field_dict["authorization"] = authorization
        if connector_id is not UNSET:
            field_dict["connector_id"] = connector_id
        if headers is not UNSET:
            field_dict["headers"] = headers
        if require_approval is not UNSET:
            field_dict["require_approval"] = require_approval
        if server_description is not UNSET:
            field_dict["server_description"] = server_description
        if server_url is not UNSET:
            field_dict["server_url"] = server_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mcp_tool_schema_allowed_tools_type_1 import (
            MCPToolSchemaAllowedToolsType1,
        )
        from ..models.mcp_tool_schema_headers_type_0 import MCPToolSchemaHeadersType0
        from ..models.mcp_tool_schema_require_approval_type_0 import (
            MCPToolSchemaRequireApprovalType0,
        )

        d = dict(src_dict)
        server_label = d.pop("server_label")

        type_ = d.pop("type", UNSET)

        def _parse_allowed_tools(
            data: object,
        ) -> list[str] | MCPToolSchemaAllowedToolsType1 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                allowed_tools_type_0 = cast(list[str], data)

                return allowed_tools_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                allowed_tools_type_1 = MCPToolSchemaAllowedToolsType1.from_dict(data)

                return allowed_tools_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | MCPToolSchemaAllowedToolsType1 | None | Unset, data)

        allowed_tools = _parse_allowed_tools(d.pop("allowed_tools", UNSET))

        def _parse_authorization(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        authorization = _parse_authorization(d.pop("authorization", UNSET))

        def _parse_connector_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        connector_id = _parse_connector_id(d.pop("connector_id", UNSET))

        def _parse_headers(data: object) -> MCPToolSchemaHeadersType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                headers_type_0 = MCPToolSchemaHeadersType0.from_dict(data)

                return headers_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MCPToolSchemaHeadersType0 | None | Unset, data)

        headers = _parse_headers(d.pop("headers", UNSET))

        def _parse_require_approval(
            data: object,
        ) -> MCPToolSchemaRequireApprovalType0 | None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                require_approval_type_0 = MCPToolSchemaRequireApprovalType0.from_dict(
                    data
                )

                return require_approval_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MCPToolSchemaRequireApprovalType0 | None | str | Unset, data)

        require_approval = _parse_require_approval(d.pop("require_approval", UNSET))

        def _parse_server_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        server_description = _parse_server_description(
            d.pop("server_description", UNSET)
        )

        def _parse_server_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        server_url = _parse_server_url(d.pop("server_url", UNSET))

        mcp_tool_schema = cls(
            server_label=server_label,
            type_=type_,
            allowed_tools=allowed_tools,
            authorization=authorization,
            connector_id=connector_id,
            headers=headers,
            require_approval=require_approval,
            server_description=server_description,
            server_url=server_url,
        )

        mcp_tool_schema.additional_properties = d
        return mcp_tool_schema

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
