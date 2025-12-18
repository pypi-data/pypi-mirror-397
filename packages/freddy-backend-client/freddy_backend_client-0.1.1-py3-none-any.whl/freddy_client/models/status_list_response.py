from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.status_response import StatusResponse


T = TypeVar("T", bound="StatusListResponse")


@_attrs_define
class StatusListResponse:
    """Schema for statuses list response.

    Attributes:
        statuses (list[StatusResponse]): List of available statuses
    """

    statuses: list[StatusResponse]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        statuses = []
        for statuses_item_data in self.statuses:
            statuses_item = statuses_item_data.to_dict()
            statuses.append(statuses_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "statuses": statuses,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.status_response import StatusResponse

        d = dict(src_dict)
        statuses = []
        _statuses = d.pop("statuses")
        for statuses_item_data in _statuses:
            statuses_item = StatusResponse.from_dict(statuses_item_data)

            statuses.append(statuses_item)

        status_list_response = cls(
            statuses=statuses,
        )

        status_list_response.additional_properties = d
        return status_list_response

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
