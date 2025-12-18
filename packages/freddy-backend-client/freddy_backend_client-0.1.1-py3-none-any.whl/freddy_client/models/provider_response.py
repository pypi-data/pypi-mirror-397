from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProviderResponse")


@_attrs_define
class ProviderResponse:
    """Schema for provider response.

    Attributes:
        provider_name (str):
        is_active (bool):
        has_credentials (bool):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        provider_org_id (None | str | Unset):
        provider_project_id (None | str | Unset):
    """

    provider_name: str
    is_active: bool
    has_credentials: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    provider_org_id: None | str | Unset = UNSET
    provider_project_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider_name = self.provider_name

        is_active = self.is_active

        has_credentials = self.has_credentials

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        provider_org_id: None | str | Unset
        if isinstance(self.provider_org_id, Unset):
            provider_org_id = UNSET
        else:
            provider_org_id = self.provider_org_id

        provider_project_id: None | str | Unset
        if isinstance(self.provider_project_id, Unset):
            provider_project_id = UNSET
        else:
            provider_project_id = self.provider_project_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider_name": provider_name,
                "is_active": is_active,
                "has_credentials": has_credentials,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if provider_org_id is not UNSET:
            field_dict["provider_org_id"] = provider_org_id
        if provider_project_id is not UNSET:
            field_dict["provider_project_id"] = provider_project_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        provider_name = d.pop("provider_name")

        is_active = d.pop("is_active")

        has_credentials = d.pop("has_credentials")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_provider_org_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provider_org_id = _parse_provider_org_id(d.pop("provider_org_id", UNSET))

        def _parse_provider_project_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provider_project_id = _parse_provider_project_id(
            d.pop("provider_project_id", UNSET)
        )

        provider_response = cls(
            provider_name=provider_name,
            is_active=is_active,
            has_credentials=has_credentials,
            created_at=created_at,
            updated_at=updated_at,
            provider_org_id=provider_org_id,
            provider_project_id=provider_project_id,
        )

        provider_response.additional_properties = d
        return provider_response

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
