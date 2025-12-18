from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.usage_analytics_response_data_item import (
        UsageAnalyticsResponseDataItem,
    )
    from ..models.usage_analytics_response_summary import UsageAnalyticsResponseSummary


T = TypeVar("T", bound="UsageAnalyticsResponse")


@_attrs_define
class UsageAnalyticsResponse:
    """Response model for usage analytics (yearly, monthly, daily, hourly).

    Attributes:
        organization_id (str): Organization ID
        period (str): Time period (yearly, monthly, daily, hourly)
        data (list[UsageAnalyticsResponseDataItem]): Usage data points
        total_requests (int): Total number of requests
        total_cost (float): Total cost in CHF
        summary (UsageAnalyticsResponseSummary): Summary statistics
    """

    organization_id: str
    period: str
    data: list[UsageAnalyticsResponseDataItem]
    total_requests: int
    total_cost: float
    summary: UsageAnalyticsResponseSummary
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        period = self.period

        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        total_requests = self.total_requests

        total_cost = self.total_cost

        summary = self.summary.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organization_id": organization_id,
                "period": period,
                "data": data,
                "total_requests": total_requests,
                "total_cost": total_cost,
                "summary": summary,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.usage_analytics_response_data_item import (
            UsageAnalyticsResponseDataItem,
        )
        from ..models.usage_analytics_response_summary import (
            UsageAnalyticsResponseSummary,
        )

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        period = d.pop("period")

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = UsageAnalyticsResponseDataItem.from_dict(data_item_data)

            data.append(data_item)

        total_requests = d.pop("total_requests")

        total_cost = d.pop("total_cost")

        summary = UsageAnalyticsResponseSummary.from_dict(d.pop("summary"))

        usage_analytics_response = cls(
            organization_id=organization_id,
            period=period,
            data=data,
            total_requests=total_requests,
            total_cost=total_cost,
            summary=summary,
        )

        usage_analytics_response.additional_properties = d
        return usage_analytics_response

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
