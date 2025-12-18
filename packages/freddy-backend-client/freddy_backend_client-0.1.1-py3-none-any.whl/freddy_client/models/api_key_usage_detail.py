from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.api_key_usage_detail_limit import ApiKeyUsageDetailLimit
    from ..models.api_key_usage_detail_usage import ApiKeyUsageDetailUsage


T = TypeVar("T", bound="ApiKeyUsageDetail")


@_attrs_define
class ApiKeyUsageDetail:
    """Detailed usage information for a specific API key.

    Attributes:
        api_key_id (str): API key ID
        api_key_name (str): API key name
        organization_id (str): Organization ID
        month (int): Month (1-12)
        year (int): Year
        usage (ApiKeyUsageDetailUsage): Usage metrics
        limit (ApiKeyUsageDetailLimit): Limit information
    """

    api_key_id: str
    api_key_name: str
    organization_id: str
    month: int
    year: int
    usage: ApiKeyUsageDetailUsage
    limit: ApiKeyUsageDetailLimit
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        api_key_id = self.api_key_id

        api_key_name = self.api_key_name

        organization_id = self.organization_id

        month = self.month

        year = self.year

        usage = self.usage.to_dict()

        limit = self.limit.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "api_key_id": api_key_id,
                "api_key_name": api_key_name,
                "organization_id": organization_id,
                "month": month,
                "year": year,
                "usage": usage,
                "limit": limit,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_key_usage_detail_limit import ApiKeyUsageDetailLimit
        from ..models.api_key_usage_detail_usage import ApiKeyUsageDetailUsage

        d = dict(src_dict)
        api_key_id = d.pop("api_key_id")

        api_key_name = d.pop("api_key_name")

        organization_id = d.pop("organization_id")

        month = d.pop("month")

        year = d.pop("year")

        usage = ApiKeyUsageDetailUsage.from_dict(d.pop("usage"))

        limit = ApiKeyUsageDetailLimit.from_dict(d.pop("limit"))

        api_key_usage_detail = cls(
            api_key_id=api_key_id,
            api_key_name=api_key_name,
            organization_id=organization_id,
            month=month,
            year=year,
            usage=usage,
            limit=limit,
        )

        api_key_usage_detail.additional_properties = d
        return api_key_usage_detail

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
