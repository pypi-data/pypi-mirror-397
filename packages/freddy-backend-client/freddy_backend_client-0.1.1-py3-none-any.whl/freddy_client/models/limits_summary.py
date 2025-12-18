from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="LimitsSummary")


@_attrs_define
class LimitsSummary:
    """Summary statistics for limits.

    Attributes:
        total_keys (int): Total number of API keys
        keys_with_limits (int): Number of keys with limits configured
        keys_exceeded (int): Number of keys that exceeded limits
        overall_status (str): Overall status: ok, warning, exceeded
    """

    total_keys: int
    keys_with_limits: int
    keys_exceeded: int
    overall_status: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_keys = self.total_keys

        keys_with_limits = self.keys_with_limits

        keys_exceeded = self.keys_exceeded

        overall_status = self.overall_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_keys": total_keys,
                "keys_with_limits": keys_with_limits,
                "keys_exceeded": keys_exceeded,
                "overall_status": overall_status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total_keys = d.pop("total_keys")

        keys_with_limits = d.pop("keys_with_limits")

        keys_exceeded = d.pop("keys_exceeded")

        overall_status = d.pop("overall_status")

        limits_summary = cls(
            total_keys=total_keys,
            keys_with_limits=keys_with_limits,
            keys_exceeded=keys_exceeded,
            overall_status=overall_status,
        )

        limits_summary.additional_properties = d
        return limits_summary

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
