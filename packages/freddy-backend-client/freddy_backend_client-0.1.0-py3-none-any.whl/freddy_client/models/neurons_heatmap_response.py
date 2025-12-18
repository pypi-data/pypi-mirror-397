from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.neurons_heatmap_response_heatmap_data import (
        NeuronsHeatmapResponseHeatmapData,
    )
    from ..models.neurons_heatmap_response_patterns import (
        NeuronsHeatmapResponsePatterns,
    )
    from ..models.neurons_heatmap_response_peak_hours_item import (
        NeuronsHeatmapResponsePeakHoursItem,
    )


T = TypeVar("T", bound="NeuronsHeatmapResponse")


@_attrs_define
class NeuronsHeatmapResponse:
    """Response model for usage heatmap (supports neurons, synapses, or combined).

    Attributes:
        organization_id (str): Organization ID
        heatmap_data (NeuronsHeatmapResponseHeatmapData): Heatmap visualization data
        peak_hours (list[NeuronsHeatmapResponsePeakHoursItem]): Peak usage hours
        patterns (NeuronsHeatmapResponsePatterns): Usage patterns by time
        metric (None | str | Unset): Metric type analyzed: 'neurons', 'synapses', 'all', or null
    """

    organization_id: str
    heatmap_data: NeuronsHeatmapResponseHeatmapData
    peak_hours: list[NeuronsHeatmapResponsePeakHoursItem]
    patterns: NeuronsHeatmapResponsePatterns
    metric: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        heatmap_data = self.heatmap_data.to_dict()

        peak_hours = []
        for peak_hours_item_data in self.peak_hours:
            peak_hours_item = peak_hours_item_data.to_dict()
            peak_hours.append(peak_hours_item)

        patterns = self.patterns.to_dict()

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
                "heatmap_data": heatmap_data,
                "peak_hours": peak_hours,
                "patterns": patterns,
            }
        )
        if metric is not UNSET:
            field_dict["metric"] = metric

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.neurons_heatmap_response_heatmap_data import (
            NeuronsHeatmapResponseHeatmapData,
        )
        from ..models.neurons_heatmap_response_patterns import (
            NeuronsHeatmapResponsePatterns,
        )
        from ..models.neurons_heatmap_response_peak_hours_item import (
            NeuronsHeatmapResponsePeakHoursItem,
        )

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        heatmap_data = NeuronsHeatmapResponseHeatmapData.from_dict(
            d.pop("heatmap_data")
        )

        peak_hours = []
        _peak_hours = d.pop("peak_hours")
        for peak_hours_item_data in _peak_hours:
            peak_hours_item = NeuronsHeatmapResponsePeakHoursItem.from_dict(
                peak_hours_item_data
            )

            peak_hours.append(peak_hours_item)

        patterns = NeuronsHeatmapResponsePatterns.from_dict(d.pop("patterns"))

        def _parse_metric(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        metric = _parse_metric(d.pop("metric", UNSET))

        neurons_heatmap_response = cls(
            organization_id=organization_id,
            heatmap_data=heatmap_data,
            peak_hours=peak_hours,
            patterns=patterns,
            metric=metric,
        )

        neurons_heatmap_response.additional_properties = d
        return neurons_heatmap_response

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
