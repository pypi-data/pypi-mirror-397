from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.usage_summary_response_time_range import UsageSummaryResponseTimeRange
    from ..models.usage_summary_response_top_models_item import (
        UsageSummaryResponseTopModelsItem,
    )


T = TypeVar("T", bound="UsageSummaryResponse")


@_attrs_define
class UsageSummaryResponse:
    """Response model for overall usage summary.

    Attributes:
        organization_id (str): Organization ID
        total_requests (int): Total number of requests
        total_synapses (float): Total synapses (input + output)
        total_neurons (float): Total neurons
        total_cost (float): Total cost in CHF
        average_cost_per_request (float): Average cost per request
        top_models (list[UsageSummaryResponseTopModelsItem]): Most used models
        time_range (UsageSummaryResponseTimeRange): Time range of the data
    """

    organization_id: str
    total_requests: int
    total_synapses: float
    total_neurons: float
    total_cost: float
    average_cost_per_request: float
    top_models: list[UsageSummaryResponseTopModelsItem]
    time_range: UsageSummaryResponseTimeRange
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        total_requests = self.total_requests

        total_synapses = self.total_synapses

        total_neurons = self.total_neurons

        total_cost = self.total_cost

        average_cost_per_request = self.average_cost_per_request

        top_models = []
        for top_models_item_data in self.top_models:
            top_models_item = top_models_item_data.to_dict()
            top_models.append(top_models_item)

        time_range = self.time_range.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organization_id": organization_id,
                "total_requests": total_requests,
                "total_synapses": total_synapses,
                "total_neurons": total_neurons,
                "total_cost": total_cost,
                "average_cost_per_request": average_cost_per_request,
                "top_models": top_models,
                "time_range": time_range,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.usage_summary_response_time_range import (
            UsageSummaryResponseTimeRange,
        )
        from ..models.usage_summary_response_top_models_item import (
            UsageSummaryResponseTopModelsItem,
        )

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        total_requests = d.pop("total_requests")

        total_synapses = d.pop("total_synapses")

        total_neurons = d.pop("total_neurons")

        total_cost = d.pop("total_cost")

        average_cost_per_request = d.pop("average_cost_per_request")

        top_models = []
        _top_models = d.pop("top_models")
        for top_models_item_data in _top_models:
            top_models_item = UsageSummaryResponseTopModelsItem.from_dict(
                top_models_item_data
            )

            top_models.append(top_models_item)

        time_range = UsageSummaryResponseTimeRange.from_dict(d.pop("time_range"))

        usage_summary_response = cls(
            organization_id=organization_id,
            total_requests=total_requests,
            total_synapses=total_synapses,
            total_neurons=total_neurons,
            total_cost=total_cost,
            average_cost_per_request=average_cost_per_request,
            top_models=top_models,
            time_range=time_range,
        )

        usage_summary_response.additional_properties = d
        return usage_summary_response

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
