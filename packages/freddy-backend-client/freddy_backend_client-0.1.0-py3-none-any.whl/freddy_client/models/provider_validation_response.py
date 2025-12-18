from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ProviderValidationResponse")


@_attrs_define
class ProviderValidationResponse:
    """Schema for provider validation response.

    Attributes:
        provider_name (str):
        exists (bool):
        is_active (bool):
        has_credentials (bool):
        can_be_used (bool):
    """

    provider_name: str
    exists: bool
    is_active: bool
    has_credentials: bool
    can_be_used: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider_name = self.provider_name

        exists = self.exists

        is_active = self.is_active

        has_credentials = self.has_credentials

        can_be_used = self.can_be_used

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider_name": provider_name,
                "exists": exists,
                "is_active": is_active,
                "has_credentials": has_credentials,
                "can_be_used": can_be_used,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        provider_name = d.pop("provider_name")

        exists = d.pop("exists")

        is_active = d.pop("is_active")

        has_credentials = d.pop("has_credentials")

        can_be_used = d.pop("can_be_used")

        provider_validation_response = cls(
            provider_name=provider_name,
            exists=exists,
            is_active=is_active,
            has_credentials=has_credentials,
            can_be_used=can_be_used,
        )

        provider_validation_response.additional_properties = d
        return provider_validation_response

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
