from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiKeyUpdate")


@_attrs_define
class ApiKeyUpdate:
    """Request schema for updating an API key.

    Attributes:
        key_name (None | str | Unset): New name for the API key
        usage_limit_chf (float | None | Unset): New per-key monthly spending limit in CHF
        scopes (list[str] | None | Unset): New permission scopes
        expires_at (datetime.datetime | None | Unset): New expiration timestamp
    """

    key_name: None | str | Unset = UNSET
    usage_limit_chf: float | None | Unset = UNSET
    scopes: list[str] | None | Unset = UNSET
    expires_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key_name: None | str | Unset
        if isinstance(self.key_name, Unset):
            key_name = UNSET
        else:
            key_name = self.key_name

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

        expires_at: None | str | Unset
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if key_name is not UNSET:
            field_dict["key_name"] = key_name
        if usage_limit_chf is not UNSET:
            field_dict["usage_limit_chf"] = usage_limit_chf
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_key_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        key_name = _parse_key_name(d.pop("key_name", UNSET))

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

        api_key_update = cls(
            key_name=key_name,
            usage_limit_chf=usage_limit_chf,
            scopes=scopes,
            expires_at=expires_at,
        )

        api_key_update.additional_properties = d
        return api_key_update

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
