from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rule_list_paginated_response_filters import (
        RuleListPaginatedResponseFilters,
    )
    from ..models.rule_list_response import RuleListResponse


T = TypeVar("T", bound="RuleListPaginatedResponse")


@_attrs_define
class RuleListPaginatedResponse:
    """Schema for paginated rule list.

    Attributes:
        rules (list[RuleListResponse]): List of rules
        total (int): Total number of rules
        skip (int): Number of rules skipped
        limit (int): Maximum number of rules returned
        filters (RuleListPaginatedResponseFilters | Unset): Applied filters
    """

    rules: list[RuleListResponse]
    total: int
    skip: int
    limit: int
    filters: RuleListPaginatedResponseFilters | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rules = []
        for rules_item_data in self.rules:
            rules_item = rules_item_data.to_dict()
            rules.append(rules_item)

        total = self.total

        skip = self.skip

        limit = self.limit

        filters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "rules": rules,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        )
        if filters is not UNSET:
            field_dict["filters"] = filters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rule_list_paginated_response_filters import (
            RuleListPaginatedResponseFilters,
        )
        from ..models.rule_list_response import RuleListResponse

        d = dict(src_dict)
        rules = []
        _rules = d.pop("rules")
        for rules_item_data in _rules:
            rules_item = RuleListResponse.from_dict(rules_item_data)

            rules.append(rules_item)

        total = d.pop("total")

        skip = d.pop("skip")

        limit = d.pop("limit")

        _filters = d.pop("filters", UNSET)
        filters: RuleListPaginatedResponseFilters | Unset
        if isinstance(_filters, Unset):
            filters = UNSET
        else:
            filters = RuleListPaginatedResponseFilters.from_dict(_filters)

        rule_list_paginated_response = cls(
            rules=rules,
            total=total,
            skip=skip,
            limit=limit,
            filters=filters,
        )

        rule_list_paginated_response.additional_properties = d
        return rule_list_paginated_response

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
