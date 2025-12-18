from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.usage_by_entity_type import UsageByEntityType


T = TypeVar("T", bound="UsageStatisticsResponse")


@_attrs_define
class UsageStatisticsResponse:
    """Schema for rule usage statistics.

    Attributes:
        rule_id (str): Rule ID
        total_attachments (int): Total number of active attachments
        by_entity_type (list[UsageByEntityType]): Usage breakdown by entity type
    """

    rule_id: str
    total_attachments: int
    by_entity_type: list[UsageByEntityType]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rule_id = self.rule_id

        total_attachments = self.total_attachments

        by_entity_type = []
        for by_entity_type_item_data in self.by_entity_type:
            by_entity_type_item = by_entity_type_item_data.to_dict()
            by_entity_type.append(by_entity_type_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "rule_id": rule_id,
                "total_attachments": total_attachments,
                "by_entity_type": by_entity_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.usage_by_entity_type import UsageByEntityType

        d = dict(src_dict)
        rule_id = d.pop("rule_id")

        total_attachments = d.pop("total_attachments")

        by_entity_type = []
        _by_entity_type = d.pop("by_entity_type")
        for by_entity_type_item_data in _by_entity_type:
            by_entity_type_item = UsageByEntityType.from_dict(by_entity_type_item_data)

            by_entity_type.append(by_entity_type_item)

        usage_statistics_response = cls(
            rule_id=rule_id,
            total_attachments=total_attachments,
            by_entity_type=by_entity_type,
        )

        usage_statistics_response.additional_properties = d
        return usage_statistics_response

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
