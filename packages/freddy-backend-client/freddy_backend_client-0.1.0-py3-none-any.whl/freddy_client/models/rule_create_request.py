from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.apply_mode import ApplyMode
from ..models.rule_category import RuleCategory
from ..models.rule_scope_api import RuleScopeAPI
from ..models.rule_type import RuleType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment_create_inline import AttachmentCreateInline


T = TypeVar("T", bound="RuleCreateRequest")


@_attrs_define
class RuleCreateRequest:
    """Request schema for creating a rule.

    Attributes:
        name (str): Rule name
        content (str): Rule content (max 50KB)
        description (None | str | Unset): Rule description
        category (None | RuleCategory | Unset): Rule category
        rule_type (None | RuleType | Unset): Rule type
        scope (None | RuleScopeAPI | Unset): Rule scope (global scope restricted - admin only)
        apply_mode (ApplyMode | None | Unset): Rule apply mode
        is_public (bool | Unset): Whether rule is public Default: False.
        is_active (bool | Unset): Whether rule is active Default: True.
        attachments (list[AttachmentCreateInline] | None | Unset): Optional list of entities to attach to this rule upon
            creation
    """

    name: str
    content: str
    description: None | str | Unset = UNSET
    category: None | RuleCategory | Unset = UNSET
    rule_type: None | RuleType | Unset = UNSET
    scope: None | RuleScopeAPI | Unset = UNSET
    apply_mode: ApplyMode | None | Unset = UNSET
    is_public: bool | Unset = False
    is_active: bool | Unset = True
    attachments: list[AttachmentCreateInline] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

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

        is_public = self.is_public

        is_active = self.is_active

        attachments: list[dict[str, Any]] | None | Unset
        if isinstance(self.attachments, Unset):
            attachments = UNSET
        elif isinstance(self.attachments, list):
            attachments = []
            for attachments_type_0_item_data in self.attachments:
                attachments_type_0_item = attachments_type_0_item_data.to_dict()
                attachments.append(attachments_type_0_item)

        else:
            attachments = self.attachments

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "content": content,
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
        if is_public is not UNSET:
            field_dict["is_public"] = is_public
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if attachments is not UNSET:
            field_dict["attachments"] = attachments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.attachment_create_inline import AttachmentCreateInline

        d = dict(src_dict)
        name = d.pop("name")

        content = d.pop("content")

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

        is_public = d.pop("is_public", UNSET)

        is_active = d.pop("is_active", UNSET)

        def _parse_attachments(
            data: object,
        ) -> list[AttachmentCreateInline] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                attachments_type_0 = []
                _attachments_type_0 = data
                for attachments_type_0_item_data in _attachments_type_0:
                    attachments_type_0_item = AttachmentCreateInline.from_dict(
                        attachments_type_0_item_data
                    )

                    attachments_type_0.append(attachments_type_0_item)

                return attachments_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[AttachmentCreateInline] | None | Unset, data)

        attachments = _parse_attachments(d.pop("attachments", UNSET))

        rule_create_request = cls(
            name=name,
            content=content,
            description=description,
            category=category,
            rule_type=rule_type,
            scope=scope,
            apply_mode=apply_mode,
            is_public=is_public,
            is_active=is_active,
            attachments=attachments,
        )

        rule_create_request.additional_properties = d
        return rule_create_request

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
