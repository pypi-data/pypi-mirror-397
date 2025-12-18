from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.apply_mode import ApplyMode
from ..models.rule_category import RuleCategory
from ..models.rule_scope_api import RuleScopeAPI
from ..models.rule_type import RuleType
from ..types import UNSET, Unset

T = TypeVar("T", bound="RuleUpdateRequest")


@_attrs_define
class RuleUpdateRequest:
    """Request schema for updating a rule.

    Attributes:
        name (None | str | Unset):
        content (None | str | Unset):
        description (None | str | Unset):
        category (None | RuleCategory | Unset):
        rule_type (None | RuleType | Unset):
        scope (None | RuleScopeAPI | Unset): Rule scope (global scope restricted - admin only)
        apply_mode (ApplyMode | None | Unset):
        is_public (bool | None | Unset):
        is_active (bool | None | Unset):
    """

    name: None | str | Unset = UNSET
    content: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    category: None | RuleCategory | Unset = UNSET
    rule_type: None | RuleType | Unset = UNSET
    scope: None | RuleScopeAPI | Unset = UNSET
    apply_mode: ApplyMode | None | Unset = UNSET
    is_public: bool | None | Unset = UNSET
    is_active: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        content: None | str | Unset
        if isinstance(self.content, Unset):
            content = UNSET
        else:
            content = self.content

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        category: None | str | Unset
        if isinstance(self.category, Unset):
            category = UNSET
        elif isinstance(self.category, RuleCategory):
            category = self.category.value
        else:
            category = self.category

        rule_type: None | str | Unset
        if isinstance(self.rule_type, Unset):
            rule_type = UNSET
        elif isinstance(self.rule_type, RuleType):
            rule_type = self.rule_type.value
        else:
            rule_type = self.rule_type

        scope: None | str | Unset
        if isinstance(self.scope, Unset):
            scope = UNSET
        elif isinstance(self.scope, RuleScopeAPI):
            scope = self.scope.value
        else:
            scope = self.scope

        apply_mode: None | str | Unset
        if isinstance(self.apply_mode, Unset):
            apply_mode = UNSET
        elif isinstance(self.apply_mode, ApplyMode):
            apply_mode = self.apply_mode.value
        else:
            apply_mode = self.apply_mode

        is_public: bool | None | Unset
        if isinstance(self.is_public, Unset):
            is_public = UNSET
        else:
            is_public = self.is_public

        is_active: bool | None | Unset
        if isinstance(self.is_active, Unset):
            is_active = UNSET
        else:
            is_active = self.is_active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if content is not UNSET:
            field_dict["content"] = content
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
        if is_public is not UNSET:
            field_dict["is_public"] = is_public
        if is_active is not UNSET:
            field_dict["is_active"] = is_active

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_content(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        content = _parse_content(d.pop("content", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_category(data: object) -> None | RuleCategory | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                category_type_0 = RuleCategory(data)

                return category_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RuleCategory | Unset, data)

        category = _parse_category(d.pop("category", UNSET))

        def _parse_rule_type(data: object) -> None | RuleType | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                rule_type_type_0 = RuleType(data)

                return rule_type_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RuleType | Unset, data)

        rule_type = _parse_rule_type(d.pop("rule_type", UNSET))

        def _parse_scope(data: object) -> None | RuleScopeAPI | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                scope_type_0 = RuleScopeAPI(data)

                return scope_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RuleScopeAPI | Unset, data)

        scope = _parse_scope(d.pop("scope", UNSET))

        def _parse_apply_mode(data: object) -> ApplyMode | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                apply_mode_type_0 = ApplyMode(data)

                return apply_mode_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ApplyMode | None | Unset, data)

        apply_mode = _parse_apply_mode(d.pop("apply_mode", UNSET))

        def _parse_is_public(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_public = _parse_is_public(d.pop("is_public", UNSET))

        def _parse_is_active(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_active = _parse_is_active(d.pop("is_active", UNSET))

        rule_update_request = cls(
            name=name,
            content=content,
            description=description,
            category=category,
            rule_type=rule_type,
            scope=scope,
            apply_mode=apply_mode,
            is_public=is_public,
            is_active=is_active,
        )

        rule_update_request.additional_properties = d
        return rule_update_request

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
