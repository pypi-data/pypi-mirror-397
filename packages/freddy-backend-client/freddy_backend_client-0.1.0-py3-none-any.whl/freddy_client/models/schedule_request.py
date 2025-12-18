from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ScheduleRequest")


@_attrs_define
class ScheduleRequest:
    """Schema for schedule automation request.

    Attributes:
        cron_expression (str): Cron expression (e.g., '0 9 * * *' for daily at 9am)
        timezone (str | Unset): Timezone for schedule (e.g., 'America/New_York') Default: 'UTC'.
    """

    cron_expression: str
    timezone: str | Unset = "UTC"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cron_expression = self.cron_expression

        timezone = self.timezone

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cron_expression": cron_expression,
            }
        )
        if timezone is not UNSET:
            field_dict["timezone"] = timezone

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cron_expression = d.pop("cron_expression")

        timezone = d.pop("timezone", UNSET)

        schedule_request = cls(
            cron_expression=cron_expression,
            timezone=timezone,
        )

        schedule_request.additional_properties = d
        return schedule_request

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
