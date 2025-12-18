from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiKeyResponse")


@_attrs_define
class ApiKeyResponse:
    """Response schema for API key (without sensitive data).

    Attributes:
        id (str): API key ID
        organization_id (str): Organization ID
        key_name (str): Key name
        key_prefix (str): Key prefix for identification
        is_active (bool): Whether the key is active
        is_paused (bool): Whether the key is paused
        created_by (str): User ID who created the key
        created_at (datetime.datetime): Creation timestamp
        usage_limit_chf (float | None | Unset): Per-key spending limit
        scopes (list[str] | None | Unset): Permission scopes
        last_used_at (datetime.datetime | None | Unset): Last use timestamp
        expires_at (datetime.datetime | None | Unset): Expiration timestamp
    """

    id: str
    organization_id: str
    key_name: str
    key_prefix: str
    is_active: bool
    is_paused: bool
    created_by: str
    created_at: datetime.datetime
    usage_limit_chf: float | None | Unset = UNSET
    scopes: list[str] | None | Unset = UNSET
    last_used_at: datetime.datetime | None | Unset = UNSET
    expires_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        organization_id = self.organization_id

        key_name = self.key_name

        key_prefix = self.key_prefix

        is_active = self.is_active

        is_paused = self.is_paused

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        usage_limit_chf: float | None | Unset
        if isinstance(self.usage_limit_chf, Unset):
            usage_limit_chf = UNSET
        else:
            usage_limit_chf = self.usage_limit_chf

        scopes: list[str] | None | Unset
        if isinstance(self.scopes, Unset):
            scopes = UNSET
        elif isinstance(self.scopes, list):
            scopes = self.scopes

        else:
            scopes = self.scopes

        last_used_at: None | str | Unset
        if isinstance(self.last_used_at, Unset):
            last_used_at = UNSET
        elif isinstance(self.last_used_at, datetime.datetime):
            last_used_at = self.last_used_at.isoformat()
        else:
            last_used_at = self.last_used_at

        expires_at: None | str | Unset
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "organization_id": organization_id,
                "key_name": key_name,
                "key_prefix": key_prefix,
                "is_active": is_active,
                "is_paused": is_paused,
                "created_by": created_by,
                "created_at": created_at,
            }
        )
        if usage_limit_chf is not UNSET:
            field_dict["usage_limit_chf"] = usage_limit_chf
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if last_used_at is not UNSET:
            field_dict["last_used_at"] = last_used_at
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        organization_id = d.pop("organization_id")

        key_name = d.pop("key_name")

        key_prefix = d.pop("key_prefix")

        is_active = d.pop("is_active")

        is_paused = d.pop("is_paused")

        created_by = d.pop("created_by")

        created_at = isoparse(d.pop("created_at"))

        def _parse_usage_limit_chf(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        usage_limit_chf = _parse_usage_limit_chf(d.pop("usage_limit_chf", UNSET))

        def _parse_scopes(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                scopes_type_0 = cast(list[str], data)

                return scopes_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        scopes = _parse_scopes(d.pop("scopes", UNSET))

        def _parse_last_used_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_used_at_type_0 = isoparse(data)

                return last_used_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_used_at = _parse_last_used_at(d.pop("last_used_at", UNSET))

        def _parse_expires_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

        api_key_response = cls(
            id=id,
            organization_id=organization_id,
            key_name=key_name,
            key_prefix=key_prefix,
            is_active=is_active,
            is_paused=is_paused,
            created_by=created_by,
            created_at=created_at,
            usage_limit_chf=usage_limit_chf,
            scopes=scopes,
            last_used_at=last_used_at,
            expires_at=expires_at,
        )

        api_key_response.additional_properties = d
        return api_key_response

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
