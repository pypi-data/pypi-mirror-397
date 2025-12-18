from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="VectorStoreUpdate")


@_attrs_define
class VectorStoreUpdate:
    """Schema for updating a vector store.

    Attributes:
        name (None | str | Unset): New name for the vector store
        description (None | str | Unset): New description for the vector store
        access_mode (None | str | Unset): New access control level: public, organization, department, private
        access_departments (list[str] | None | Unset): Updated list of department IDs with access
        access_users (list[str] | None | Unset): Updated list of user IDs with access
    """

    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    access_mode: None | str | Unset = UNSET
    access_departments: list[str] | None | Unset = UNSET
    access_users: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        access_mode: None | str | Unset
        if isinstance(self.access_mode, Unset):
            access_mode = UNSET
        else:
            access_mode = self.access_mode

        access_departments: list[str] | None | Unset
        if isinstance(self.access_departments, Unset):
            access_departments = UNSET
        elif isinstance(self.access_departments, list):
            access_departments = self.access_departments

        else:
            access_departments = self.access_departments

        access_users: list[str] | None | Unset
        if isinstance(self.access_users, Unset):
            access_users = UNSET
        elif isinstance(self.access_users, list):
            access_users = self.access_users

        else:
            access_users = self.access_users

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if access_mode is not UNSET:
            field_dict["access_mode"] = access_mode
        if access_departments is not UNSET:
            field_dict["access_departments"] = access_departments
        if access_users is not UNSET:
            field_dict["access_users"] = access_users

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

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_access_mode(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        access_mode = _parse_access_mode(d.pop("access_mode", UNSET))

        def _parse_access_departments(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                access_departments_type_0 = cast(list[str], data)

                return access_departments_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        access_departments = _parse_access_departments(
            d.pop("access_departments", UNSET)
        )

        def _parse_access_users(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                access_users_type_0 = cast(list[str], data)

                return access_users_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        access_users = _parse_access_users(d.pop("access_users", UNSET))

        vector_store_update = cls(
            name=name,
            description=description,
            access_mode=access_mode,
            access_departments=access_departments,
            access_users=access_users,
        )

        vector_store_update.additional_properties = d
        return vector_store_update

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
