from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.api_key_limit import ApiKeyLimit
    from ..models.api_limits import ApiLimits
    from ..models.limits_summary import LimitsSummary
    from ..models.organization_limits import OrganizationLimits


T = TypeVar("T", bound="UsageLimitsResponse")


@_attrs_define
class UsageLimitsResponse:
    """Response model for GET /v1/analytics/usage/limits/{org_id}.

    Attributes:
        organization_limits (OrganizationLimits): Organization-level spending limits.
        api_limits (ApiLimits): API-level aggregated spending limits.
        api_key_limits (list[ApiKeyLimit]): Per-key breakdown
        summary (LimitsSummary): Summary statistics for limits.
    """

    organization_limits: OrganizationLimits
    api_limits: ApiLimits
    api_key_limits: list[ApiKeyLimit]
    summary: LimitsSummary
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_limits = self.organization_limits.to_dict()

        api_limits = self.api_limits.to_dict()

        api_key_limits = []
        for api_key_limits_item_data in self.api_key_limits:
            api_key_limits_item = api_key_limits_item_data.to_dict()
            api_key_limits.append(api_key_limits_item)

        summary = self.summary.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organization_limits": organization_limits,
                "api_limits": api_limits,
                "api_key_limits": api_key_limits,
                "summary": summary,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_key_limit import ApiKeyLimit
        from ..models.api_limits import ApiLimits
        from ..models.limits_summary import LimitsSummary
        from ..models.organization_limits import OrganizationLimits

        d = dict(src_dict)
        organization_limits = OrganizationLimits.from_dict(d.pop("organization_limits"))

        api_limits = ApiLimits.from_dict(d.pop("api_limits"))

        api_key_limits = []
        _api_key_limits = d.pop("api_key_limits")
        for api_key_limits_item_data in _api_key_limits:
            api_key_limits_item = ApiKeyLimit.from_dict(api_key_limits_item_data)

            api_key_limits.append(api_key_limits_item)

        summary = LimitsSummary.from_dict(d.pop("summary"))

        usage_limits_response = cls(
            organization_limits=organization_limits,
            api_limits=api_limits,
            api_key_limits=api_key_limits,
            summary=summary,
        )

        usage_limits_response.additional_properties = d
        return usage_limits_response

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
