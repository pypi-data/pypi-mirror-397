from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FiltersAppliedSchema")


@_attrs_define
class FiltersAppliedSchema:
    """Applied filters schema.

    Attributes:
        search (None | str | Unset): Search term
        access_mode (None | str | Unset): Access mode filter
        include_inactive (bool | Unset): Include inactive assistants Default: False.
        sort_by (str | Unset): Sort field Default: 'name'.
        sort_order (str | Unset): Sort order Default: 'asc'.
    """

    search: None | str | Unset = UNSET
    access_mode: None | str | Unset = UNSET
    include_inactive: bool | Unset = False
    sort_by: str | Unset = "name"
    sort_order: str | Unset = "asc"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        search: None | str | Unset
        if isinstance(self.search, Unset):
            search = UNSET
        else:
            search = self.search

        access_mode: None | str | Unset
        if isinstance(self.access_mode, Unset):
            access_mode = UNSET
        else:
            access_mode = self.access_mode

        include_inactive = self.include_inactive

        sort_by = self.sort_by

        sort_order = self.sort_order

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if search is not UNSET:
            field_dict["search"] = search
        if access_mode is not UNSET:
            field_dict["access_mode"] = access_mode
        if include_inactive is not UNSET:
            field_dict["include_inactive"] = include_inactive
        if sort_by is not UNSET:
            field_dict["sort_by"] = sort_by
        if sort_order is not UNSET:
            field_dict["sort_order"] = sort_order

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_search(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        search = _parse_search(d.pop("search", UNSET))

        def _parse_access_mode(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        access_mode = _parse_access_mode(d.pop("access_mode", UNSET))

        include_inactive = d.pop("include_inactive", UNSET)

        sort_by = d.pop("sort_by", UNSET)

        sort_order = d.pop("sort_order", UNSET)

        filters_applied_schema = cls(
            search=search,
            access_mode=access_mode,
            include_inactive=include_inactive,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        filters_applied_schema.additional_properties = d
        return filters_applied_schema

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
