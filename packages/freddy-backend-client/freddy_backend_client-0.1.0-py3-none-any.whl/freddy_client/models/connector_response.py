from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConnectorResponse")


@_attrs_define
class ConnectorResponse:
    """Personal connector response.

    Attributes:
        connector_id (str): Connector ID
        connector_type (str): Connector type
        is_active (bool): Whether connector is active
        created_at (datetime.datetime): Creation timestamp
        mcp_configuration_id (str): Associated MCP config ID
        account_email (None | str | Unset): Connected account email
        last_sync_at (datetime.datetime | None | Unset): Last sync timestamp
        icon_id (None | str | Unset): Icon ID
        icon_url (None | str | Unset): Icon URL
    """

    connector_id: str
    connector_type: str
    is_active: bool
    created_at: datetime.datetime
    mcp_configuration_id: str
    account_email: None | str | Unset = UNSET
    last_sync_at: datetime.datetime | None | Unset = UNSET
    icon_id: None | str | Unset = UNSET
    icon_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        connector_id = self.connector_id

        connector_type = self.connector_type

        is_active = self.is_active

        created_at = self.created_at.isoformat()

        mcp_configuration_id = self.mcp_configuration_id

        account_email: None | str | Unset
        if isinstance(self.account_email, Unset):
            account_email = UNSET
        else:
            account_email = self.account_email

        last_sync_at: None | str | Unset
        if isinstance(self.last_sync_at, Unset):
            last_sync_at = UNSET
        elif isinstance(self.last_sync_at, datetime.datetime):
            last_sync_at = self.last_sync_at.isoformat()
        else:
            last_sync_at = self.last_sync_at

        icon_id: None | str | Unset
        if isinstance(self.icon_id, Unset):
            icon_id = UNSET
        else:
            icon_id = self.icon_id

        icon_url: None | str | Unset
        if isinstance(self.icon_url, Unset):
            icon_url = UNSET
        else:
            icon_url = self.icon_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "connector_id": connector_id,
                "connector_type": connector_type,
                "is_active": is_active,
                "created_at": created_at,
                "mcp_configuration_id": mcp_configuration_id,
            }
        )
        if account_email is not UNSET:
            field_dict["account_email"] = account_email
        if last_sync_at is not UNSET:
            field_dict["last_sync_at"] = last_sync_at
        if icon_id is not UNSET:
            field_dict["icon_id"] = icon_id
        if icon_url is not UNSET:
            field_dict["icon_url"] = icon_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        connector_id = d.pop("connector_id")

        connector_type = d.pop("connector_type")

        is_active = d.pop("is_active")

        created_at = isoparse(d.pop("created_at"))

        mcp_configuration_id = d.pop("mcp_configuration_id")

        def _parse_account_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        account_email = _parse_account_email(d.pop("account_email", UNSET))

        def _parse_last_sync_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_sync_at_type_0 = isoparse(data)

                return last_sync_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_sync_at = _parse_last_sync_at(d.pop("last_sync_at", UNSET))

        def _parse_icon_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        icon_id = _parse_icon_id(d.pop("icon_id", UNSET))

        def _parse_icon_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        icon_url = _parse_icon_url(d.pop("icon_url", UNSET))

        connector_response = cls(
            connector_id=connector_id,
            connector_type=connector_type,
            is_active=is_active,
            created_at=created_at,
            mcp_configuration_id=mcp_configuration_id,
            account_email=account_email,
            last_sync_at=last_sync_at,
            icon_id=icon_id,
            icon_url=icon_url,
        )

        connector_response.additional_properties = d
        return connector_response

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
