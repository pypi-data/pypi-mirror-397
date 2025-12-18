from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.status_count import StatusCount


T = TypeVar("T", bound="StatusSummaryResponse")


@_attrs_define
class StatusSummaryResponse:
    """Schema for status summary response.

    Attributes:
        status_counts (list[StatusCount]): List of status counts
    """

    status_counts: list[StatusCount]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status_counts = []
        for status_counts_item_data in self.status_counts:
            status_counts_item = status_counts_item_data.to_dict()
            status_counts.append(status_counts_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status_counts": status_counts,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.status_count import StatusCount

        d = dict(src_dict)
        status_counts = []
        _status_counts = d.pop("status_counts")
        for status_counts_item_data in _status_counts:
            status_counts_item = StatusCount.from_dict(status_counts_item_data)

            status_counts.append(status_counts_item)

        status_summary_response = cls(
            status_counts=status_counts,
        )

        status_summary_response.additional_properties = d
        return status_summary_response

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
