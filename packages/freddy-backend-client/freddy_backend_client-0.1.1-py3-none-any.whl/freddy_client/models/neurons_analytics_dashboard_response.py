from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.neurons_analytics_dashboard_response_current_summary import (
        NeuronsAnalyticsDashboardResponseCurrentSummary,
    )
    from ..models.neurons_analytics_dashboard_response_daily_trends_item import (
        NeuronsAnalyticsDashboardResponseDailyTrendsItem,
    )
    from ..models.neurons_analytics_dashboard_response_efficiency_metrics import (
        NeuronsAnalyticsDashboardResponseEfficiencyMetrics,
    )
    from ..models.neurons_analytics_dashboard_response_insights_item import (
        NeuronsAnalyticsDashboardResponseInsightsItem,
    )
    from ..models.neurons_analytics_dashboard_response_period import (
        NeuronsAnalyticsDashboardResponsePeriod,
    )
    from ..models.neurons_analytics_dashboard_response_predictions import (
        NeuronsAnalyticsDashboardResponsePredictions,
    )
    from ..models.neurons_analytics_dashboard_response_usage_patterns import (
        NeuronsAnalyticsDashboardResponseUsagePatterns,
    )


T = TypeVar("T", bound="NeuronsAnalyticsDashboardResponse")


@_attrs_define
class NeuronsAnalyticsDashboardResponse:
    """Response model for analytics dashboard (supports neurons, synapses, or combined).

    Attributes:
        organization_id (str): Organization ID
        period (NeuronsAnalyticsDashboardResponsePeriod): Analysis period information
        current_summary (NeuronsAnalyticsDashboardResponseCurrentSummary): Current period summary metrics
        daily_trends (list[NeuronsAnalyticsDashboardResponseDailyTrendsItem]): Daily usage trends
        usage_patterns (NeuronsAnalyticsDashboardResponseUsagePatterns): Usage pattern analysis
        efficiency_metrics (NeuronsAnalyticsDashboardResponseEfficiencyMetrics): Efficiency and optimization metrics
        predictions (NeuronsAnalyticsDashboardResponsePredictions): Predictive projections
        insights (list[NeuronsAnalyticsDashboardResponseInsightsItem]): AI-generated insights and recommendations
        metric (None | str | Unset): Metric type analyzed: 'neurons', 'synapses', 'all', or null
    """

    organization_id: str
    period: NeuronsAnalyticsDashboardResponsePeriod
    current_summary: NeuronsAnalyticsDashboardResponseCurrentSummary
    daily_trends: list[NeuronsAnalyticsDashboardResponseDailyTrendsItem]
    usage_patterns: NeuronsAnalyticsDashboardResponseUsagePatterns
    efficiency_metrics: NeuronsAnalyticsDashboardResponseEfficiencyMetrics
    predictions: NeuronsAnalyticsDashboardResponsePredictions
    insights: list[NeuronsAnalyticsDashboardResponseInsightsItem]
    metric: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        period = self.period.to_dict()

        current_summary = self.current_summary.to_dict()

        daily_trends = []
        for daily_trends_item_data in self.daily_trends:
            daily_trends_item = daily_trends_item_data.to_dict()
            daily_trends.append(daily_trends_item)

        usage_patterns = self.usage_patterns.to_dict()

        efficiency_metrics = self.efficiency_metrics.to_dict()

        predictions = self.predictions.to_dict()

        insights = []
        for insights_item_data in self.insights:
            insights_item = insights_item_data.to_dict()
            insights.append(insights_item)

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
                "current_summary": current_summary,
                "daily_trends": daily_trends,
                "usage_patterns": usage_patterns,
                "efficiency_metrics": efficiency_metrics,
                "predictions": predictions,
                "insights": insights,
            }
        )
        if metric is not UNSET:
            field_dict["metric"] = metric

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.neurons_analytics_dashboard_response_current_summary import (
            NeuronsAnalyticsDashboardResponseCurrentSummary,
        )
        from ..models.neurons_analytics_dashboard_response_daily_trends_item import (
            NeuronsAnalyticsDashboardResponseDailyTrendsItem,
        )
        from ..models.neurons_analytics_dashboard_response_efficiency_metrics import (
            NeuronsAnalyticsDashboardResponseEfficiencyMetrics,
        )
        from ..models.neurons_analytics_dashboard_response_insights_item import (
            NeuronsAnalyticsDashboardResponseInsightsItem,
        )
        from ..models.neurons_analytics_dashboard_response_period import (
            NeuronsAnalyticsDashboardResponsePeriod,
        )
        from ..models.neurons_analytics_dashboard_response_predictions import (
            NeuronsAnalyticsDashboardResponsePredictions,
        )
        from ..models.neurons_analytics_dashboard_response_usage_patterns import (
            NeuronsAnalyticsDashboardResponseUsagePatterns,
        )

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        period = NeuronsAnalyticsDashboardResponsePeriod.from_dict(d.pop("period"))

        current_summary = NeuronsAnalyticsDashboardResponseCurrentSummary.from_dict(
            d.pop("current_summary")
        )

        daily_trends = []
        _daily_trends = d.pop("daily_trends")
        for daily_trends_item_data in _daily_trends:
            daily_trends_item = (
                NeuronsAnalyticsDashboardResponseDailyTrendsItem.from_dict(
                    daily_trends_item_data
                )
            )

            daily_trends.append(daily_trends_item)

        usage_patterns = NeuronsAnalyticsDashboardResponseUsagePatterns.from_dict(
            d.pop("usage_patterns")
        )

        efficiency_metrics = (
            NeuronsAnalyticsDashboardResponseEfficiencyMetrics.from_dict(
                d.pop("efficiency_metrics")
            )
        )

        predictions = NeuronsAnalyticsDashboardResponsePredictions.from_dict(
            d.pop("predictions")
        )

        insights = []
        _insights = d.pop("insights")
        for insights_item_data in _insights:
            insights_item = NeuronsAnalyticsDashboardResponseInsightsItem.from_dict(
                insights_item_data
            )

            insights.append(insights_item)

        def _parse_metric(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        metric = _parse_metric(d.pop("metric", UNSET))

        neurons_analytics_dashboard_response = cls(
            organization_id=organization_id,
            period=period,
            current_summary=current_summary,
            daily_trends=daily_trends,
            usage_patterns=usage_patterns,
            efficiency_metrics=efficiency_metrics,
            predictions=predictions,
            insights=insights,
            metric=metric,
        )

        neurons_analytics_dashboard_response.additional_properties = d
        return neurons_analytics_dashboard_response

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
