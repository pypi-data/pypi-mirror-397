from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ApiKeyUsageSummary")


@_attrs_define
class ApiKeyUsageSummary:
    """API Key usage summary response.

    Attributes:
        organization_id (str): Organization ID
        month (int): Month
        year (int): Year
        total_api_key_requests (int): Total API key requests
        total_api_key_cost (float): Total API key cost in CHF
        average_cost_per_request (float): Average cost per API request
        total_synapses (float): Total synapses
        total_neurons (float): Total neurons
        generated_at (str): Report generation timestamp
    """

    organization_id: str
    month: int
    year: int
    total_api_key_requests: int
    total_api_key_cost: float
    average_cost_per_request: float
    total_synapses: float
    total_neurons: float
    generated_at: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        month = self.month

        year = self.year

        total_api_key_requests = self.total_api_key_requests

        total_api_key_cost = self.total_api_key_cost

        average_cost_per_request = self.average_cost_per_request

        total_synapses = self.total_synapses

        total_neurons = self.total_neurons

        generated_at = self.generated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organization_id": organization_id,
                "month": month,
                "year": year,
                "total_api_key_requests": total_api_key_requests,
                "total_api_key_cost": total_api_key_cost,
                "average_cost_per_request": average_cost_per_request,
                "total_synapses": total_synapses,
                "total_neurons": total_neurons,
                "generated_at": generated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        month = d.pop("month")

        year = d.pop("year")

        total_api_key_requests = d.pop("total_api_key_requests")

        total_api_key_cost = d.pop("total_api_key_cost")

        average_cost_per_request = d.pop("average_cost_per_request")

        total_synapses = d.pop("total_synapses")

        total_neurons = d.pop("total_neurons")

        generated_at = d.pop("generated_at")

        api_key_usage_summary = cls(
            organization_id=organization_id,
            month=month,
            year=year,
            total_api_key_requests=total_api_key_requests,
            total_api_key_cost=total_api_key_cost,
            average_cost_per_request=average_cost_per_request,
            total_synapses=total_synapses,
            total_neurons=total_neurons,
            generated_at=generated_at,
        )

        api_key_usage_summary.additional_properties = d
        return api_key_usage_summary

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
