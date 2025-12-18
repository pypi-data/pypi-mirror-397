from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LimitUpdateRequest")


@_attrs_define
class LimitUpdateRequest:
    """Request model for PUT /v1/analytics/usage/limits/{org_id}.

    Attributes:
        monthly_api_limit (float | None | Unset): Organization limit in CHF (must be > 0)
        total_api_key_limit (float | None | Unset): Total API key limit in CHF (must be > 0)
        api_key_id (None | str | Unset): API key ID
        api_key_limit (float | None | Unset): API key limit in CHF (must be > 0)
    """

    monthly_api_limit: float | None | Unset = UNSET
    total_api_key_limit: float | None | Unset = UNSET
    api_key_id: None | str | Unset = UNSET
    api_key_limit: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        monthly_api_limit: float | None | Unset
        if isinstance(self.monthly_api_limit, Unset):
            monthly_api_limit = UNSET
        else:
            monthly_api_limit = self.monthly_api_limit

        total_api_key_limit: float | None | Unset
        if isinstance(self.total_api_key_limit, Unset):
            total_api_key_limit = UNSET
        else:
            total_api_key_limit = self.total_api_key_limit

        api_key_id: None | str | Unset
        if isinstance(self.api_key_id, Unset):
            api_key_id = UNSET
        else:
            api_key_id = self.api_key_id

        api_key_limit: float | None | Unset
        if isinstance(self.api_key_limit, Unset):
            api_key_limit = UNSET
        else:
            api_key_limit = self.api_key_limit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if monthly_api_limit is not UNSET:
            field_dict["monthly_api_limit"] = monthly_api_limit
        if total_api_key_limit is not UNSET:
            field_dict["total_api_key_limit"] = total_api_key_limit
        if api_key_id is not UNSET:
            field_dict["api_key_id"] = api_key_id
        if api_key_limit is not UNSET:
            field_dict["api_key_limit"] = api_key_limit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_monthly_api_limit(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        monthly_api_limit = _parse_monthly_api_limit(d.pop("monthly_api_limit", UNSET))

        def _parse_total_api_key_limit(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        total_api_key_limit = _parse_total_api_key_limit(
            d.pop("total_api_key_limit", UNSET)
        )

        def _parse_api_key_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        api_key_id = _parse_api_key_id(d.pop("api_key_id", UNSET))

        def _parse_api_key_limit(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        api_key_limit = _parse_api_key_limit(d.pop("api_key_limit", UNSET))

        limit_update_request = cls(
            monthly_api_limit=monthly_api_limit,
            total_api_key_limit=total_api_key_limit,
            api_key_id=api_key_id,
            api_key_limit=api_key_limit,
        )

        limit_update_request.additional_properties = d
        return limit_update_request

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
