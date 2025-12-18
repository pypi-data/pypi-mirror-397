from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiLimits")


@_attrs_define
class ApiLimits:
    """API-level aggregated spending limits.

    Attributes:
        current_usage (float): Current API usage in CHF
        utilization_percentage (float): Utilization percentage (0-100+)
        remaining_budget (float): Remaining budget in CHF (can be negative)
        status (str): Status: ok, warning, exceeded, no_limit
        monthly_limit (float | None | Unset): Monthly limit in CHF (total API key limit, not org limit)
    """

    current_usage: float
    utilization_percentage: float
    remaining_budget: float
    status: str
    monthly_limit: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        current_usage = self.current_usage

        utilization_percentage = self.utilization_percentage

        remaining_budget = self.remaining_budget

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
                "current_usage": current_usage,
                "utilization_percentage": utilization_percentage,
                "remaining_budget": remaining_budget,
                "status": status,
            }
        )
        if monthly_limit is not UNSET:
            field_dict["monthly_limit"] = monthly_limit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        current_usage = d.pop("current_usage")

        utilization_percentage = d.pop("utilization_percentage")

        remaining_budget = d.pop("remaining_budget")

        status = d.pop("status")

        def _parse_monthly_limit(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        monthly_limit = _parse_monthly_limit(d.pop("monthly_limit", UNSET))

        api_limits = cls(
            current_usage=current_usage,
            utilization_percentage=utilization_percentage,
            remaining_budget=remaining_budget,
            status=status,
            monthly_limit=monthly_limit,
        )

        api_limits.additional_properties = d
        return api_limits

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
