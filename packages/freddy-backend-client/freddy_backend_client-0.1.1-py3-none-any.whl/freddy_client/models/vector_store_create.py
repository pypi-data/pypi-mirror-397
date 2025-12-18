from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="VectorStoreCreate")


@_attrs_define
class VectorStoreCreate:
    """Schema for creating a vector store.

    Attributes:
        name (str): Name of the vector store
        description (None | str | Unset): Description of the vector store's purpose or contents
        access_mode (str | Unset): Access control level: public, organization, department, private Default:
            'organization'.
        access_departments (list[str] | None | Unset): Department IDs that can access (when access_mode is department)
        access_users (list[str] | None | Unset): User IDs that can access (when access_mode is private)
    """

    name: str
    description: None | str | Unset = UNSET
    access_mode: str | Unset = "organization"
    access_departments: list[str] | None | Unset = UNSET
    access_users: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

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
        field_dict.update(
            {
                "name": name,
            }
        )
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
        name = d.pop("name")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        access_mode = d.pop("access_mode", UNSET)

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

        vector_store_create = cls(
            name=name,
            description=description,
            access_mode=access_mode,
            access_departments=access_departments,
            access_users=access_users,
        )

        vector_store_create.additional_properties = d
        return vector_store_create

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
