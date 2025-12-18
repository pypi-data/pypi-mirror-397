from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExportRequest")


@_attrs_define
class ExportRequest:
    """Schema for export request with filters.

    Attributes:
        search_term (None | str | Unset): Search across full_name, email, and username
        role_id (None | str | Unset): Filter by role ID
        status_id (None | str | Unset): Filter by status ID
        include_deleted (bool | Unset): Include soft-deleted members Default: False.
    """

    search_term: None | str | Unset = UNSET
    role_id: None | str | Unset = UNSET
    status_id: None | str | Unset = UNSET
    include_deleted: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        search_term: None | str | Unset
        if isinstance(self.search_term, Unset):
            search_term = UNSET
        else:
            search_term = self.search_term

        role_id: None | str | Unset
        if isinstance(self.role_id, Unset):
            role_id = UNSET
        else:
            role_id = self.role_id

        status_id: None | str | Unset
        if isinstance(self.status_id, Unset):
            status_id = UNSET
        else:
            status_id = self.status_id

        include_deleted = self.include_deleted

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if search_term is not UNSET:
            field_dict["search_term"] = search_term
        if role_id is not UNSET:
            field_dict["role_id"] = role_id
        if status_id is not UNSET:
            field_dict["status_id"] = status_id
        if include_deleted is not UNSET:
            field_dict["include_deleted"] = include_deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_search_term(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        search_term = _parse_search_term(d.pop("search_term", UNSET))

        def _parse_role_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        role_id = _parse_role_id(d.pop("role_id", UNSET))

        def _parse_status_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status_id = _parse_status_id(d.pop("status_id", UNSET))

        include_deleted = d.pop("include_deleted", UNSET)

        export_request = cls(
            search_term=search_term,
            role_id=role_id,
            status_id=status_id,
            include_deleted=include_deleted,
        )

        export_request.additional_properties = d
        return export_request

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
