from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UsageByEntityType")


@_attrs_define
class UsageByEntityType:
    """Schema for usage statistics by entity type.

    Attributes:
        entity_type (str): Entity type
        count (int): Number of attachments for this entity type
        entity_ids (list[str]): List of entity IDs where rule is attached
    """

    entity_type: str
    count: int
    entity_ids: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        entity_type = self.entity_type

        count = self.count

        entity_ids = self.entity_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entity_type": entity_type,
                "count": count,
                "entity_ids": entity_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        entity_type = d.pop("entity_type")

        count = d.pop("count")

        entity_ids = cast(list[str], d.pop("entity_ids"))

        usage_by_entity_type = cls(
            entity_type=entity_type,
            count=count,
            entity_ids=entity_ids,
        )

        usage_by_entity_type.additional_properties = d
        return usage_by_entity_type

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
