from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.api_key_daily_usage_response_period import (
        ApiKeyDailyUsageResponsePeriod,
    )
    from ..models.api_key_usage_summary import ApiKeyUsageSummary
    from ..models.daily_api_key_usage import DailyApiKeyUsage


T = TypeVar("T", bound="ApiKeyDailyUsageResponse")


@_attrs_define
class ApiKeyDailyUsageResponse:
    """API key daily usage response.

    Attributes:
        organization_id (str): Organization ID
        period (ApiKeyDailyUsageResponsePeriod): Time period info
        daily_usage (list[DailyApiKeyUsage]): Daily usage data
        summary (ApiKeyUsageSummary): API Key usage summary response.
    """

    organization_id: str
    period: ApiKeyDailyUsageResponsePeriod
    daily_usage: list[DailyApiKeyUsage]
    summary: ApiKeyUsageSummary
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        period = self.period.to_dict()

        daily_usage = []
        for daily_usage_item_data in self.daily_usage:
            daily_usage_item = daily_usage_item_data.to_dict()
            daily_usage.append(daily_usage_item)

        summary = self.summary.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organization_id": organization_id,
                "period": period,
                "daily_usage": daily_usage,
                "summary": summary,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_key_daily_usage_response_period import (
            ApiKeyDailyUsageResponsePeriod,
        )
        from ..models.api_key_usage_summary import ApiKeyUsageSummary
        from ..models.daily_api_key_usage import DailyApiKeyUsage

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        period = ApiKeyDailyUsageResponsePeriod.from_dict(d.pop("period"))

        daily_usage = []
        _daily_usage = d.pop("daily_usage")
        for daily_usage_item_data in _daily_usage:
            daily_usage_item = DailyApiKeyUsage.from_dict(daily_usage_item_data)

            daily_usage.append(daily_usage_item)

        summary = ApiKeyUsageSummary.from_dict(d.pop("summary"))

        api_key_daily_usage_response = cls(
            organization_id=organization_id,
            period=period,
            daily_usage=daily_usage,
            summary=summary,
        )

        api_key_daily_usage_response.additional_properties = d
        return api_key_daily_usage_response

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
