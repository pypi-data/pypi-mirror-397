from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AttachmentSummary")


@_attrs_define
class AttachmentSummary:
    """Summary of an attachment for inclusion in rule details.

    Attributes:
        id (str): Attachment ID
        entity_type (str): Entity type
        entity_id (str): Entity ID
        priority (int): Priority
        is_active (bool): Whether attachment is active
        character_limit (int | None | Unset): Character limit
    """

    id: str
    entity_type: str
    entity_id: str
    priority: int
    is_active: bool
    character_limit: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        entity_type = self.entity_type

        entity_id = self.entity_id

        priority = self.priority

        is_active = self.is_active

        character_limit: int | None | Unset
        if isinstance(self.character_limit, Unset):
            character_limit = UNSET
        else:
            character_limit = self.character_limit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "priority": priority,
                "is_active": is_active,
            }
        )
        if character_limit is not UNSET:
            field_dict["character_limit"] = character_limit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        entity_type = d.pop("entity_type")

        entity_id = d.pop("entity_id")

        priority = d.pop("priority")

        is_active = d.pop("is_active")

        def _parse_character_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        character_limit = _parse_character_limit(d.pop("character_limit", UNSET))

        attachment_summary = cls(
            id=id,
            entity_type=entity_type,
            entity_id=entity_id,
            priority=priority,
            is_active=is_active,
            character_limit=character_limit,
        )

        attachment_summary.additional_properties = d
        return attachment_summary

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
