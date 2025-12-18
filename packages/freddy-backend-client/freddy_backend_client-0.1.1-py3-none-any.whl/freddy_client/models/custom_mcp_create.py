from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_mcp_create_credentials_type_0 import (
        CustomMCPCreateCredentialsType0,
    )
    from ..models.custom_mcp_create_tool_configuration_type_0 import (
        CustomMCPCreateToolConfigurationType0,
    )


T = TypeVar("T", bound="CustomMCPCreate")


@_attrs_define
class CustomMCPCreate:
    """Request schema for creating a custom MCP configuration.

    Attributes:
        name (str): Display name
        organization_id (str): Organization ID
        server_url (str): HTTPS URL to MCP server
        transport_type (str): Transport type: 'sse' or 'streamable_http'
        auth_type (str): Authentication type: 'none', 'api_key', 'bearer_token', 'oauth'
        credentials (CustomMCPCreateCredentialsType0 | None | Unset): Authentication credentials (will be encrypted)
        tool_configuration (CustomMCPCreateToolConfigurationType0 | None | Unset): Tool enablement configuration
    """

    name: str
    organization_id: str
    server_url: str
    transport_type: str
    auth_type: str
    credentials: CustomMCPCreateCredentialsType0 | None | Unset = UNSET
    tool_configuration: CustomMCPCreateToolConfigurationType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.custom_mcp_create_credentials_type_0 import (
            CustomMCPCreateCredentialsType0,
        )
        from ..models.custom_mcp_create_tool_configuration_type_0 import (
            CustomMCPCreateToolConfigurationType0,
        )

        name = self.name

        organization_id = self.organization_id

        server_url = self.server_url

        transport_type = self.transport_type

        auth_type = self.auth_type

        credentials: dict[str, Any] | None | Unset
        if isinstance(self.credentials, Unset):
            credentials = UNSET
        elif isinstance(self.credentials, CustomMCPCreateCredentialsType0):
            credentials = self.credentials.to_dict()
        else:
            credentials = self.credentials

        tool_configuration: dict[str, Any] | None | Unset
        if isinstance(self.tool_configuration, Unset):
            tool_configuration = UNSET
        elif isinstance(self.tool_configuration, CustomMCPCreateToolConfigurationType0):
            tool_configuration = self.tool_configuration.to_dict()
        else:
            tool_configuration = self.tool_configuration

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "organization_id": organization_id,
                "server_url": server_url,
                "transport_type": transport_type,
                "auth_type": auth_type,
            }
        )
        if credentials is not UNSET:
            field_dict["credentials"] = credentials
        if tool_configuration is not UNSET:
            field_dict["tool_configuration"] = tool_configuration

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_mcp_create_credentials_type_0 import (
            CustomMCPCreateCredentialsType0,
        )
        from ..models.custom_mcp_create_tool_configuration_type_0 import (
            CustomMCPCreateToolConfigurationType0,
        )

        d = dict(src_dict)
        name = d.pop("name")

        organization_id = d.pop("organization_id")

        server_url = d.pop("server_url")

        transport_type = d.pop("transport_type")

        auth_type = d.pop("auth_type")

        def _parse_credentials(
            data: object,
        ) -> CustomMCPCreateCredentialsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                credentials_type_0 = CustomMCPCreateCredentialsType0.from_dict(data)

                return credentials_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CustomMCPCreateCredentialsType0 | None | Unset, data)

        credentials = _parse_credentials(d.pop("credentials", UNSET))

        def _parse_tool_configuration(
            data: object,
        ) -> CustomMCPCreateToolConfigurationType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tool_configuration_type_0 = (
                    CustomMCPCreateToolConfigurationType0.from_dict(data)
                )

                return tool_configuration_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CustomMCPCreateToolConfigurationType0 | None | Unset, data)

        tool_configuration = _parse_tool_configuration(
            d.pop("tool_configuration", UNSET)
        )

        custom_mcp_create = cls(
            name=name,
            organization_id=organization_id,
            server_url=server_url,
            transport_type=transport_type,
            auth_type=auth_type,
            credentials=credentials,
            tool_configuration=tool_configuration,
        )

        custom_mcp_create.additional_properties = d
        return custom_mcp_create

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
