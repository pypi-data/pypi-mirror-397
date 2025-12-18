from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="StatusCount")


@_attrs_define
class StatusCount:
    """Schema for status count in summary.

    Attributes:
        status_id (str): Status ID
        status_name (str): Status name
        count (int): Number of members with this status
    """

    status_id: str
    status_name: str
    count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status_id = self.status_id

        status_name = self.status_name

        count = self.count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status_id": status_id,
                "status_name": status_name,
                "count": count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status_id = d.pop("status_id")

        status_name = d.pop("status_name")

        count = d.pop("count")

        status_count = cls(
            status_id=status_id,
            status_name=status_name,
            count=count,
        )

        status_count.additional_properties = d
        return status_count

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
