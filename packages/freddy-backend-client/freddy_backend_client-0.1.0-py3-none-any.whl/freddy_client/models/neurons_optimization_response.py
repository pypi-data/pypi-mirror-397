from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.neurons_optimization_response_current_efficiency import (
        NeuronsOptimizationResponseCurrentEfficiency,
    )
    from ..models.neurons_optimization_response_optimization_opportunities_item import (
        NeuronsOptimizationResponseOptimizationOpportunitiesItem,
    )
    from ..models.neurons_optimization_response_potential_savings import (
        NeuronsOptimizationResponsePotentialSavings,
    )
    from ..models.neurons_optimization_response_recommendations_item import (
        NeuronsOptimizationResponseRecommendationsItem,
    )


T = TypeVar("T", bound="NeuronsOptimizationResponse")


@_attrs_define
class NeuronsOptimizationResponse:
    """Response model for optimization insights (supports neurons, synapses, or combined).

    Attributes:
        organization_id (str): Organization ID
        current_efficiency (NeuronsOptimizationResponseCurrentEfficiency): Current efficiency metrics
        optimization_opportunities (list[NeuronsOptimizationResponseOptimizationOpportunitiesItem]): Optimization
            opportunities
        recommendations (list[NeuronsOptimizationResponseRecommendationsItem]): Actionable recommendations
        potential_savings (NeuronsOptimizationResponsePotentialSavings): Potential cost savings
        metric (None | str | Unset): Metric type analyzed: 'neurons', 'synapses', 'all', or null
    """

    organization_id: str
    current_efficiency: NeuronsOptimizationResponseCurrentEfficiency
    optimization_opportunities: list[
        NeuronsOptimizationResponseOptimizationOpportunitiesItem
    ]
    recommendations: list[NeuronsOptimizationResponseRecommendationsItem]
    potential_savings: NeuronsOptimizationResponsePotentialSavings
    metric: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        current_efficiency = self.current_efficiency.to_dict()

        optimization_opportunities = []
        for optimization_opportunities_item_data in self.optimization_opportunities:
            optimization_opportunities_item = (
                optimization_opportunities_item_data.to_dict()
            )
            optimization_opportunities.append(optimization_opportunities_item)

        recommendations = []
        for recommendations_item_data in self.recommendations:
            recommendations_item = recommendations_item_data.to_dict()
            recommendations.append(recommendations_item)

        potential_savings = self.potential_savings.to_dict()

        metric: None | str | Unset
        if isinstance(self.metric, Unset):
            metric = UNSET
        else:
            metric = self.metric

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organization_id": organization_id,
                "current_efficiency": current_efficiency,
                "optimization_opportunities": optimization_opportunities,
                "recommendations": recommendations,
                "potential_savings": potential_savings,
            }
        )
        if metric is not UNSET:
            field_dict["metric"] = metric

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.neurons_optimization_response_current_efficiency import (
            NeuronsOptimizationResponseCurrentEfficiency,
        )
        from ..models.neurons_optimization_response_optimization_opportunities_item import (
            NeuronsOptimizationResponseOptimizationOpportunitiesItem,
        )
        from ..models.neurons_optimization_response_potential_savings import (
            NeuronsOptimizationResponsePotentialSavings,
        )
        from ..models.neurons_optimization_response_recommendations_item import (
            NeuronsOptimizationResponseRecommendationsItem,
        )

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        current_efficiency = NeuronsOptimizationResponseCurrentEfficiency.from_dict(
            d.pop("current_efficiency")
        )

        optimization_opportunities = []
        _optimization_opportunities = d.pop("optimization_opportunities")
        for optimization_opportunities_item_data in _optimization_opportunities:
            optimization_opportunities_item = (
                NeuronsOptimizationResponseOptimizationOpportunitiesItem.from_dict(
                    optimization_opportunities_item_data
                )
            )

            optimization_opportunities.append(optimization_opportunities_item)

        recommendations = []
        _recommendations = d.pop("recommendations")
        for recommendations_item_data in _recommendations:
            recommendations_item = (
                NeuronsOptimizationResponseRecommendationsItem.from_dict(
                    recommendations_item_data
                )
            )

            recommendations.append(recommendations_item)

        potential_savings = NeuronsOptimizationResponsePotentialSavings.from_dict(
            d.pop("potential_savings")
        )

        def _parse_metric(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        metric = _parse_metric(d.pop("metric", UNSET))

        neurons_optimization_response = cls(
            organization_id=organization_id,
            current_efficiency=current_efficiency,
            optimization_opportunities=optimization_opportunities,
            recommendations=recommendations,
            potential_savings=potential_savings,
            metric=metric,
        )

        neurons_optimization_response.additional_properties = d
        return neurons_optimization_response

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
