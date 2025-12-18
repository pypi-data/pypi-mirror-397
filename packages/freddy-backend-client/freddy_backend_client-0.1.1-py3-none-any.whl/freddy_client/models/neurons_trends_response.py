from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.neurons_trends_response_forecasts import (
        NeuronsTrendsResponseForecasts,
    )
    from ..models.neurons_trends_response_patterns_item import (
        NeuronsTrendsResponsePatternsItem,
    )
    from ..models.neurons_trends_response_period import NeuronsTrendsResponsePeriod
    from ..models.neurons_trends_response_trends import NeuronsTrendsResponseTrends


T = TypeVar("T", bound="NeuronsTrendsResponse")


@_attrs_define
class NeuronsTrendsResponse:
    """Response model for trends analysis (supports neurons, synapses, or combined).

    Attributes:
        organization_id (str): Organization ID
        period (NeuronsTrendsResponsePeriod): Analysis period
        trends (NeuronsTrendsResponseTrends): Trend analysis data
        patterns (list[NeuronsTrendsResponsePatternsItem]): Identified patterns
        forecasts (NeuronsTrendsResponseForecasts): Trend forecasts
        metric (None | str | Unset): Metric type analyzed: 'neurons', 'synapses', 'all', or null
    """

    organization_id: str
    period: NeuronsTrendsResponsePeriod
    trends: NeuronsTrendsResponseTrends
    patterns: list[NeuronsTrendsResponsePatternsItem]
    forecasts: NeuronsTrendsResponseForecasts
    metric: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        period = self.period.to_dict()

        trends = self.trends.to_dict()

        patterns = []
        for patterns_item_data in self.patterns:
            patterns_item = patterns_item_data.to_dict()
            patterns.append(patterns_item)

        forecasts = self.forecasts.to_dict()

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
                "period": period,
                "trends": trends,
                "patterns": patterns,
                "forecasts": forecasts,
            }
        )
        if metric is not UNSET:
            field_dict["metric"] = metric

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.neurons_trends_response_forecasts import (
            NeuronsTrendsResponseForecasts,
        )
        from ..models.neurons_trends_response_patterns_item import (
            NeuronsTrendsResponsePatternsItem,
        )
        from ..models.neurons_trends_response_period import NeuronsTrendsResponsePeriod
        from ..models.neurons_trends_response_trends import NeuronsTrendsResponseTrends

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        period = NeuronsTrendsResponsePeriod.from_dict(d.pop("period"))

        trends = NeuronsTrendsResponseTrends.from_dict(d.pop("trends"))

        patterns = []
        _patterns = d.pop("patterns")
        for patterns_item_data in _patterns:
            patterns_item = NeuronsTrendsResponsePatternsItem.from_dict(
                patterns_item_data
            )

            patterns.append(patterns_item)

        forecasts = NeuronsTrendsResponseForecasts.from_dict(d.pop("forecasts"))

        def _parse_metric(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        metric = _parse_metric(d.pop("metric", UNSET))

        neurons_trends_response = cls(
            organization_id=organization_id,
            period=period,
            trends=trends,
            patterns=patterns,
            forecasts=forecasts,
            metric=metric,
        )

        neurons_trends_response.additional_properties = d
        return neurons_trends_response

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
