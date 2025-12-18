from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.change_log_response import ChangeLogResponse


T = TypeVar("T", bound="ChangeLogListResponse")


@_attrs_define
class ChangeLogListResponse:
    """Schema for paginated change log list.

    Attributes:
        logs (list[ChangeLogResponse]): List of change logs
        total_count (int): Total number of logs
        skip (int): Number of records skipped
        take (int): Number of records returned
    """

    logs: list[ChangeLogResponse]
    total_count: int
    skip: int
    take: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        logs = []
        for logs_item_data in self.logs:
            logs_item = logs_item_data.to_dict()
            logs.append(logs_item)

        total_count = self.total_count

        skip = self.skip

        take = self.take

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "logs": logs,
                "total_count": total_count,
                "skip": skip,
                "take": take,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.change_log_response import ChangeLogResponse

        d = dict(src_dict)
        logs = []
        _logs = d.pop("logs")
        for logs_item_data in _logs:
            logs_item = ChangeLogResponse.from_dict(logs_item_data)

            logs.append(logs_item)

        total_count = d.pop("total_count")

        skip = d.pop("skip")

        take = d.pop("take")

        change_log_list_response = cls(
            logs=logs,
            total_count=total_count,
            skip=skip,
            take=take,
        )

        change_log_list_response.additional_properties = d
        return change_log_list_response

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
