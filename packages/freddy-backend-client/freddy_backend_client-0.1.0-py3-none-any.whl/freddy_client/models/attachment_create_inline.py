from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.entity_type import EntityType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AttachmentCreateInline")


@_attrs_define
class AttachmentCreateInline:
    """Inline attachment configuration for rule creation.

    Attributes:
        entity_type (EntityType): Entity type enumeration for attachments.
        entity_id (str): ID of entity to attach
        priority (int | Unset): Priority (1-100, default 50) Default: 50.
        character_limit (int | None | Unset): Character limit for rule content (100-50000)
    """

    entity_type: EntityType
    entity_id: str
    priority: int | Unset = 50
    character_limit: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        entity_type = self.entity_type.value

        entity_id = self.entity_id

        priority = self.priority

        character_limit: int | None | Unset
        if isinstance(self.character_limit, Unset):
            character_limit = UNSET
        else:
            character_limit = self.character_limit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entity_type": entity_type,
                "entity_id": entity_id,
            }
        )
        if priority is not UNSET:
            field_dict["priority"] = priority
        if character_limit is not UNSET:
            field_dict["character_limit"] = character_limit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        entity_type = EntityType(d.pop("entity_type"))

        entity_id = d.pop("entity_id")

        priority = d.pop("priority", UNSET)

        def _parse_character_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        character_limit = _parse_character_limit(d.pop("character_limit", UNSET))

        attachment_create_inline = cls(
            entity_type=entity_type,
            entity_id=entity_id,
            priority=priority,
            character_limit=character_limit,
        )

        attachment_create_inline.additional_properties = d
        return attachment_create_inline

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
