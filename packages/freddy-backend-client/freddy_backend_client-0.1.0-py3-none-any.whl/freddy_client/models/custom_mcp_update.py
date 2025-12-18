from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_mcp_update_credentials_type_0 import (
        CustomMCPUpdateCredentialsType0,
    )
    from ..models.custom_mcp_update_tool_configuration_type_0 import (
        CustomMCPUpdateToolConfigurationType0,
    )


T = TypeVar("T", bound="CustomMCPUpdate")


@_attrs_define
class CustomMCPUpdate:
    """Request schema for updating a custom MCP configuration.

    Attributes:
        name (None | str | Unset): Display name
        server_url (None | str | Unset): HTTPS URL to MCP server
        is_active (bool | None | Unset): Enable/disable configuration
        credentials (CustomMCPUpdateCredentialsType0 | None | Unset): Updated credentials (will be encrypted)
        tool_configuration (CustomMCPUpdateToolConfigurationType0 | None | Unset): Tool enablement configuration
    """

    name: None | str | Unset = UNSET
    server_url: None | str | Unset = UNSET
    is_active: bool | None | Unset = UNSET
    credentials: CustomMCPUpdateCredentialsType0 | None | Unset = UNSET
    tool_configuration: CustomMCPUpdateToolConfigurationType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.custom_mcp_update_credentials_type_0 import (
            CustomMCPUpdateCredentialsType0,
        )
        from ..models.custom_mcp_update_tool_configuration_type_0 import (
            CustomMCPUpdateToolConfigurationType0,
        )

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        server_url: None | str | Unset
        if isinstance(self.server_url, Unset):
            server_url = UNSET
        else:
            server_url = self.server_url

        is_active: bool | None | Unset
        if isinstance(self.is_active, Unset):
            is_active = UNSET
        else:
            is_active = self.is_active

        credentials: dict[str, Any] | None | Unset
        if isinstance(self.credentials, Unset):
            credentials = UNSET
        elif isinstance(self.credentials, CustomMCPUpdateCredentialsType0):
            credentials = self.credentials.to_dict()
        else:
            credentials = self.credentials

        tool_configuration: dict[str, Any] | None | Unset
        if isinstance(self.tool_configuration, Unset):
            tool_configuration = UNSET
        elif isinstance(self.tool_configuration, CustomMCPUpdateToolConfigurationType0):
            tool_configuration = self.tool_configuration.to_dict()
        else:
            tool_configuration = self.tool_configuration

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if server_url is not UNSET:
            field_dict["server_url"] = server_url
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if credentials is not UNSET:
            field_dict["credentials"] = credentials
        if tool_configuration is not UNSET:
            field_dict["tool_configuration"] = tool_configuration

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.custom_mcp_update_credentials_type_0 import (
            CustomMCPUpdateCredentialsType0,
        )
        from ..models.custom_mcp_update_tool_configuration_type_0 import (
            CustomMCPUpdateToolConfigurationType0,
        )

        d = dict(src_dict)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_server_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        server_url = _parse_server_url(d.pop("server_url", UNSET))

        def _parse_is_active(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_active = _parse_is_active(d.pop("is_active", UNSET))

        def _parse_credentials(
            data: object,
        ) -> CustomMCPUpdateCredentialsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                credentials_type_0 = CustomMCPUpdateCredentialsType0.from_dict(data)

                return credentials_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CustomMCPUpdateCredentialsType0 | None | Unset, data)

        credentials = _parse_credentials(d.pop("credentials", UNSET))

        def _parse_tool_configuration(
            data: object,
        ) -> CustomMCPUpdateToolConfigurationType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tool_configuration_type_0 = (
                    CustomMCPUpdateToolConfigurationType0.from_dict(data)
                )

                return tool_configuration_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CustomMCPUpdateToolConfigurationType0 | None | Unset, data)

        tool_configuration = _parse_tool_configuration(
            d.pop("tool_configuration", UNSET)
        )

        custom_mcp_update = cls(
            name=name,
            server_url=server_url,
            is_active=is_active,
            credentials=credentials,
            tool_configuration=tool_configuration,
        )

        custom_mcp_update.additional_properties = d
        return custom_mcp_update

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
