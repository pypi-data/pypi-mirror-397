from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="MCPConfigurationResponse")


@_attrs_define
class MCPConfigurationResponse:
    """Response schema for MCP configuration.

    Attributes:
        id (str): MCP configuration ID
        name (str): Display name
        type_ (str): MCP type
        organization_id (str): Organization ID
        server_url (str): MCP server URL
        transport_type (str): Transport type
        auth_type (str): Authentication type
        is_active (bool): Whether configuration is active
        connection_status (str): Connection status
        created_at (datetime.datetime): Creation timestamp
        updated_at (datetime.datetime): Last update timestamp
        user_id (None | str | Unset): User ID (for personal MCPs)
        last_connected_at (datetime.datetime | None | Unset): Last successful connection timestamp
        error_message (None | str | Unset): Last error message
    """

    id: str
    name: str
    type_: str
    organization_id: str
    server_url: str
    transport_type: str
    auth_type: str
    is_active: bool
    connection_status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    user_id: None | str | Unset = UNSET
    last_connected_at: datetime.datetime | None | Unset = UNSET
    error_message: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        type_ = self.type_

        organization_id = self.organization_id

        server_url = self.server_url

        transport_type = self.transport_type

        auth_type = self.auth_type

        is_active = self.is_active

        connection_status = self.connection_status

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        user_id: None | str | Unset
        if isinstance(self.user_id, Unset):
            user_id = UNSET
        else:
            user_id = self.user_id

        last_connected_at: None | str | Unset
        if isinstance(self.last_connected_at, Unset):
            last_connected_at = UNSET
        elif isinstance(self.last_connected_at, datetime.datetime):
            last_connected_at = self.last_connected_at.isoformat()
        else:
            last_connected_at = self.last_connected_at

        error_message: None | str | Unset
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "type": type_,
                "organizationId": organization_id,
                "serverUrl": server_url,
                "transportType": transport_type,
                "authType": auth_type,
                "isActive": is_active,
                "connectionStatus": connection_status,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if last_connected_at is not UNSET:
            field_dict["lastConnectedAt"] = last_connected_at
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        type_ = d.pop("type")

        organization_id = d.pop("organizationId")

        server_url = d.pop("serverUrl")

        transport_type = d.pop("transportType")

        auth_type = d.pop("authType")

        is_active = d.pop("isActive")

        connection_status = d.pop("connectionStatus")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        def _parse_user_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_id = _parse_user_id(d.pop("userId", UNSET))

        def _parse_last_connected_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_connected_at_type_0 = isoparse(data)

                return last_connected_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_connected_at = _parse_last_connected_at(d.pop("lastConnectedAt", UNSET))

        def _parse_error_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_message = _parse_error_message(d.pop("errorMessage", UNSET))

        mcp_configuration_response = cls(
            id=id,
            name=name,
            type_=type_,
            organization_id=organization_id,
            server_url=server_url,
            transport_type=transport_type,
            auth_type=auth_type,
            is_active=is_active,
            connection_status=connection_status,
            created_at=created_at,
            updated_at=updated_at,
            user_id=user_id,
            last_connected_at=last_connected_at,
            error_message=error_message,
        )

        mcp_configuration_response.additional_properties = d
        return mcp_configuration_response

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
