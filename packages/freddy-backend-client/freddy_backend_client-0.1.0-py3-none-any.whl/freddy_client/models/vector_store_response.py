from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="VectorStoreResponse")


@_attrs_define
class VectorStoreResponse:
    """Schema for vector store response.

    Attributes:
        id (str): Unique identifier for the vector store
        name (str): Human-readable name for the vector store
        organization_id (str): The organization this vector store belongs to
        created_by (str): User ID of the person who created this vector store
        created_at (datetime.datetime): ISO 8601 timestamp when the vector store was created
        updated_at (datetime.datetime): ISO 8601 timestamp when the vector store was last modified
        is_active (bool): Whether the vector store is active and available for use
        access_mode (str): Access control for the vector store
        file_count (int): Number of files currently stored in this vector store
        data_size (int): Total size of all files in bytes
        description (None | str | Unset): Brief description of the vector store's purpose and contents
        access_departments (list[str] | None | Unset): Array of department IDs that have access to this vector store
        access_users (list[str] | None | Unset): Array of user IDs with explicit access to this vector store
    """

    id: str
    name: str
    organization_id: str
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_active: bool
    access_mode: str
    file_count: int
    data_size: int
    description: None | str | Unset = UNSET
    access_departments: list[str] | None | Unset = UNSET
    access_users: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        organization_id = self.organization_id

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        is_active = self.is_active

        access_mode = self.access_mode

        file_count = self.file_count

        data_size = self.data_size

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

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
                "id": id,
                "name": name,
                "organization_id": organization_id,
                "created_by": created_by,
                "created_at": created_at,
                "updated_at": updated_at,
                "is_active": is_active,
                "access_mode": access_mode,
                "file_count": file_count,
                "data_size": data_size,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if access_departments is not UNSET:
            field_dict["access_departments"] = access_departments
        if access_users is not UNSET:
            field_dict["access_users"] = access_users

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        organization_id = d.pop("organization_id")

        created_by = d.pop("created_by")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        is_active = d.pop("is_active")

        access_mode = d.pop("access_mode")

        file_count = d.pop("file_count")

        data_size = d.pop("data_size")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

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

        vector_store_response = cls(
            id=id,
            name=name,
            organization_id=organization_id,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
            is_active=is_active,
            access_mode=access_mode,
            file_count=file_count,
            data_size=data_size,
            description=description,
            access_departments=access_departments,
            access_users=access_users,
        )

        vector_store_response.additional_properties = d
        return vector_store_response

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
