from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InvalidateLimitCacheRequest")


@_attrs_define
class InvalidateLimitCacheRequest:
    """Request schema for invalidating limit caches.

    Attributes:
        organization_id (str): Organization ID to invalidate caches for
        api_key_ids (list[str] | None | Unset): Optional list of API key IDs to invalidate per-key caches
    """

    organization_id: str
    api_key_ids: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        api_key_ids: list[str] | None | Unset
        if isinstance(self.api_key_ids, Unset):
            api_key_ids = UNSET
        elif isinstance(self.api_key_ids, list):
            api_key_ids = self.api_key_ids

        else:
            api_key_ids = self.api_key_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organization_id": organization_id,
            }
        )
        if api_key_ids is not UNSET:
            field_dict["api_key_ids"] = api_key_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        def _parse_api_key_ids(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                api_key_ids_type_0 = cast(list[str], data)

                return api_key_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        api_key_ids = _parse_api_key_ids(d.pop("api_key_ids", UNSET))

        invalidate_limit_cache_request = cls(
            organization_id=organization_id,
            api_key_ids=api_key_ids,
        )

        invalidate_limit_cache_request.additional_properties = d
        return invalidate_limit_cache_request

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
