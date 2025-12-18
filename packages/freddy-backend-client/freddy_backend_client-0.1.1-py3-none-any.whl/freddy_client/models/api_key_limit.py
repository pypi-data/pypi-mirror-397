from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiKeyLimit")


@_attrs_define
class ApiKeyLimit:
    """Per-API-key spending limit.

    Attributes:
        api_key_id (str): API key ID
        api_key_name (str): API key name
        current_usage (float): Current usage in CHF
        utilization_percentage (float): Utilization percentage (0-100+)
        status (str): Status: ok, warning, exceeded, no_limit
        monthly_limit (float | None | Unset): Monthly limit in CHF (null if no limit)
    """

    api_key_id: str
    api_key_name: str
    current_usage: float
    utilization_percentage: float
    status: str
    monthly_limit: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        api_key_id = self.api_key_id

        api_key_name = self.api_key_name

        current_usage = self.current_usage

        utilization_percentage = self.utilization_percentage

        status = self.status

        monthly_limit: float | None | Unset
        if isinstance(self.monthly_limit, Unset):
            monthly_limit = UNSET
        else:
            monthly_limit = self.monthly_limit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "api_key_id": api_key_id,
                "api_key_name": api_key_name,
                "current_usage": current_usage,
                "utilization_percentage": utilization_percentage,
                "status": status,
            }
        )
        if monthly_limit is not UNSET:
            field_dict["monthly_limit"] = monthly_limit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        api_key_id = d.pop("api_key_id")

        api_key_name = d.pop("api_key_name")

        current_usage = d.pop("current_usage")

        utilization_percentage = d.pop("utilization_percentage")

        status = d.pop("status")

        def _parse_monthly_limit(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        monthly_limit = _parse_monthly_limit(d.pop("monthly_limit", UNSET))

        api_key_limit = cls(
            api_key_id=api_key_id,
            api_key_name=api_key_name,
            current_usage=current_usage,
            utilization_percentage=utilization_percentage,
            status=status,
            monthly_limit=monthly_limit,
        )

        api_key_limit.additional_properties = d
        return api_key_limit

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
