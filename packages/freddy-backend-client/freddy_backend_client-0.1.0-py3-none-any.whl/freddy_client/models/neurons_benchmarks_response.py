from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.neurons_benchmarks_response_benchmarks import (
        NeuronsBenchmarksResponseBenchmarks,
    )
    from ..models.neurons_benchmarks_response_comparisons import (
        NeuronsBenchmarksResponseComparisons,
    )
    from ..models.neurons_benchmarks_response_rankings import (
        NeuronsBenchmarksResponseRankings,
    )


T = TypeVar("T", bound="NeuronsBenchmarksResponse")


@_attrs_define
class NeuronsBenchmarksResponse:
    """Response model for benchmarks (supports neurons, synapses, or combined).

    Attributes:
        organization_id (str): Organization ID
        benchmarks (NeuronsBenchmarksResponseBenchmarks): Performance benchmarks
        comparisons (NeuronsBenchmarksResponseComparisons): Industry comparisons
        rankings (NeuronsBenchmarksResponseRankings): Performance rankings
        metric (None | str | Unset): Metric type analyzed: 'neurons', 'synapses', 'all', or null
    """

    organization_id: str
    benchmarks: NeuronsBenchmarksResponseBenchmarks
    comparisons: NeuronsBenchmarksResponseComparisons
    rankings: NeuronsBenchmarksResponseRankings
    metric: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        benchmarks = self.benchmarks.to_dict()

        comparisons = self.comparisons.to_dict()

        rankings = self.rankings.to_dict()

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
                "benchmarks": benchmarks,
                "comparisons": comparisons,
                "rankings": rankings,
            }
        )
        if metric is not UNSET:
            field_dict["metric"] = metric

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.neurons_benchmarks_response_benchmarks import (
            NeuronsBenchmarksResponseBenchmarks,
        )
        from ..models.neurons_benchmarks_response_comparisons import (
            NeuronsBenchmarksResponseComparisons,
        )
        from ..models.neurons_benchmarks_response_rankings import (
            NeuronsBenchmarksResponseRankings,
        )

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        benchmarks = NeuronsBenchmarksResponseBenchmarks.from_dict(d.pop("benchmarks"))

        comparisons = NeuronsBenchmarksResponseComparisons.from_dict(
            d.pop("comparisons")
        )

        rankings = NeuronsBenchmarksResponseRankings.from_dict(d.pop("rankings"))

        def _parse_metric(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        metric = _parse_metric(d.pop("metric", UNSET))

        neurons_benchmarks_response = cls(
            organization_id=organization_id,
            benchmarks=benchmarks,
            comparisons=comparisons,
            rankings=rankings,
            metric=metric,
        )

        neurons_benchmarks_response.additional_properties = d
        return neurons_benchmarks_response

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
