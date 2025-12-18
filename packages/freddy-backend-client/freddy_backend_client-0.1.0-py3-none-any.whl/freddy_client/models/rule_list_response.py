from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="RuleListResponse")


@_attrs_define
class RuleListResponse:
    """Response schema for rule list (optimized without full content).

    Attributes:
        id (str): Rule ID with rule_ prefix
        name (str): Rule name
        content_preview (str): First 200 characters of rule content
        content_length (int): Total character count of content
        organization_id (str): Organization ID
        created_by (str): User ID who created the rule
        is_public (bool): Whether rule is public
        is_active (bool): Whether rule is active
        version (int): Rule version number
        usage_count (int): Number of active attachments
        can_edit (bool): Whether current user can edit this rule
        created_at (datetime.datetime): Creation timestamp
        updated_at (datetime.datetime): Last update timestamp
        description (None | str | Unset): Rule description
        category (None | str | Unset): Rule category
        rule_type (None | str | Unset): Rule type
        scope (None | str | Unset): Rule scope
        apply_mode (None | str | Unset): Rule apply mode
    """

    id: str
    name: str
    content_preview: str
    content_length: int
    organization_id: str
    created_by: str
    is_public: bool
    is_active: bool
    version: int
    usage_count: int
    can_edit: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    description: None | str | Unset = UNSET
    category: None | str | Unset = UNSET
    rule_type: None | str | Unset = UNSET
    scope: None | str | Unset = UNSET
    apply_mode: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        content_preview = self.content_preview

        content_length = self.content_length

        organization_id = self.organization_id

        created_by = self.created_by

        is_public = self.is_public

        is_active = self.is_active

        version = self.version

        usage_count = self.usage_count

        can_edit = self.can_edit

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        category: None | str | Unset
        if isinstance(self.category, Unset):
            category = UNSET
        else:
            category = self.category

        rule_type: None | str | Unset
        if isinstance(self.rule_type, Unset):
            rule_type = UNSET
        else:
            rule_type = self.rule_type

        scope: None | str | Unset
        if isinstance(self.scope, Unset):
            scope = UNSET
        else:
            scope = self.scope

        apply_mode: None | str | Unset
        if isinstance(self.apply_mode, Unset):
            apply_mode = UNSET
        else:
            apply_mode = self.apply_mode

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "content_preview": content_preview,
                "content_length": content_length,
                "organization_id": organization_id,
                "created_by": created_by,
                "is_public": is_public,
                "is_active": is_active,
                "version": version,
                "usage_count": usage_count,
                "can_edit": can_edit,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if category is not UNSET:
            field_dict["category"] = category
        if rule_type is not UNSET:
            field_dict["rule_type"] = rule_type
        if scope is not UNSET:
            field_dict["scope"] = scope
        if apply_mode is not UNSET:
            field_dict["apply_mode"] = apply_mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        content_preview = d.pop("content_preview")

        content_length = d.pop("content_length")

        organization_id = d.pop("organization_id")

        created_by = d.pop("created_by")

        is_public = d.pop("is_public")

        is_active = d.pop("is_active")

        version = d.pop("version")

        usage_count = d.pop("usage_count")

        can_edit = d.pop("can_edit")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_category(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        category = _parse_category(d.pop("category", UNSET))

        def _parse_rule_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        rule_type = _parse_rule_type(d.pop("rule_type", UNSET))

        def _parse_scope(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        scope = _parse_scope(d.pop("scope", UNSET))

        def _parse_apply_mode(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        apply_mode = _parse_apply_mode(d.pop("apply_mode", UNSET))

        rule_list_response = cls(
            id=id,
            name=name,
            content_preview=content_preview,
            content_length=content_length,
            organization_id=organization_id,
            created_by=created_by,
            is_public=is_public,
            is_active=is_active,
            version=version,
            usage_count=usage_count,
            can_edit=can_edit,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            category=category,
            rule_type=rule_type,
            scope=scope,
            apply_mode=apply_mode,
        )

        rule_list_response.additional_properties = d
        return rule_list_response

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
