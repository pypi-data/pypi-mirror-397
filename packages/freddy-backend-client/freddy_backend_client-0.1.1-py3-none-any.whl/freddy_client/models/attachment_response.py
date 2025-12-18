from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rule_summary import RuleSummary


T = TypeVar("T", bound="AttachmentResponse")


@_attrs_define
class AttachmentResponse:
    """Response schema for attachment.

    Attributes:
        id (str): Attachment ID with ratt_ prefix
        rule_id (str): Rule ID
        entity_type (str): Entity type
        entity_id (str): Entity ID
        priority (int): Priority (1-100)
        attached_by (str): User ID who attached the entity
        attached_at (int): Unix timestamp of attachment
        is_active (bool): Whether attachment is active
        created_at (datetime.datetime): Creation timestamp
        updated_at (datetime.datetime): Last update timestamp
        character_limit (int | None | Unset): Character limit
        rule_summary (None | RuleSummary | Unset): Summary of the attached rule
    """

    id: str
    rule_id: str
    entity_type: str
    entity_id: str
    priority: int
    attached_by: str
    attached_at: int
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    character_limit: int | None | Unset = UNSET
    rule_summary: None | RuleSummary | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.rule_summary import RuleSummary

        id = self.id

        rule_id = self.rule_id

        entity_type = self.entity_type

        entity_id = self.entity_id

        priority = self.priority

        attached_by = self.attached_by

        attached_at = self.attached_at

        is_active = self.is_active

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        character_limit: int | None | Unset
        if isinstance(self.character_limit, Unset):
            character_limit = UNSET
        else:
            character_limit = self.character_limit

        rule_summary: dict[str, Any] | None | Unset
        if isinstance(self.rule_summary, Unset):
            rule_summary = UNSET
        elif isinstance(self.rule_summary, RuleSummary):
            rule_summary = self.rule_summary.to_dict()
        else:
            rule_summary = self.rule_summary

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "rule_id": rule_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "priority": priority,
                "attached_by": attached_by,
                "attached_at": attached_at,
                "is_active": is_active,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if character_limit is not UNSET:
            field_dict["character_limit"] = character_limit
        if rule_summary is not UNSET:
            field_dict["rule_summary"] = rule_summary

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rule_summary import RuleSummary

        d = dict(src_dict)
        id = d.pop("id")

        rule_id = d.pop("rule_id")

        entity_type = d.pop("entity_type")

        entity_id = d.pop("entity_id")

        priority = d.pop("priority")

        attached_by = d.pop("attached_by")

        attached_at = d.pop("attached_at")

        is_active = d.pop("is_active")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_character_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        character_limit = _parse_character_limit(d.pop("character_limit", UNSET))

        def _parse_rule_summary(data: object) -> None | RuleSummary | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rule_summary_type_0 = RuleSummary.from_dict(data)

                return rule_summary_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RuleSummary | Unset, data)

        rule_summary = _parse_rule_summary(d.pop("rule_summary", UNSET))

        attachment_response = cls(
            id=id,
            rule_id=rule_id,
            entity_type=entity_type,
            entity_id=entity_id,
            priority=priority,
            attached_by=attached_by,
            attached_at=attached_at,
            is_active=is_active,
            created_at=created_at,
            updated_at=updated_at,
            character_limit=character_limit,
            rule_summary=rule_summary,
        )

        attachment_response.additional_properties = d
        return attachment_response

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
