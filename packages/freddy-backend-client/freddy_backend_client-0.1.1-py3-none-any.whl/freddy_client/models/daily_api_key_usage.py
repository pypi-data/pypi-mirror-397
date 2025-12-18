from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DailyApiKeyUsage")


@_attrs_define
class DailyApiKeyUsage:
    """Daily API key usage data.

    Attributes:
        date (str): Date (YYYY-MM-DD)
        requests (int): API key requests count
        cost (float): API key cost in CHF
        synapses (float): Total synapses
        neurons (float): Total neurons
    """

    date: str
    requests: int
    cost: float
    synapses: float
    neurons: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        date = self.date

        requests = self.requests

        cost = self.cost

        synapses = self.synapses

        neurons = self.neurons

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "date": date,
                "requests": requests,
                "cost": cost,
                "synapses": synapses,
                "neurons": neurons,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        date = d.pop("date")

        requests = d.pop("requests")

        cost = d.pop("cost")

        synapses = d.pop("synapses")

        neurons = d.pop("neurons")

        daily_api_key_usage = cls(
            date=date,
            requests=requests,
            cost=cost,
            synapses=synapses,
            neurons=neurons,
        )

        daily_api_key_usage.additional_properties = d
        return daily_api_key_usage

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
