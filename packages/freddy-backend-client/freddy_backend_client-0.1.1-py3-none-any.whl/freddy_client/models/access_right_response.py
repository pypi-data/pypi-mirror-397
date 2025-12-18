from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="AccessRightResponse")


@_attrs_define
class AccessRightResponse:
    """Response schema for access right.

    Attributes:
        id (str): Access right ID with racc_ prefix
        rule_id (str): Rule ID
        user_id (str): User ID
        access_level (str): Access level (owner, edit, view)
        granted_by (str): User ID who granted the access
        granted_at (datetime.datetime): Timestamp when access was granted
        is_deleted (bool): Whether access right is deleted
        created_at (datetime.datetime): Creation timestamp
        updated_at (datetime.datetime): Last update timestamp
    """

    id: str
    rule_id: str
    user_id: str
    access_level: str
    granted_by: str
    granted_at: datetime.datetime
    is_deleted: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        rule_id = self.rule_id

        user_id = self.user_id

        access_level = self.access_level

        granted_by = self.granted_by

        granted_at = self.granted_at.isoformat()

        is_deleted = self.is_deleted

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "rule_id": rule_id,
                "user_id": user_id,
                "access_level": access_level,
                "granted_by": granted_by,
                "granted_at": granted_at,
                "is_deleted": is_deleted,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        rule_id = d.pop("rule_id")

        user_id = d.pop("user_id")

        access_level = d.pop("access_level")

        granted_by = d.pop("granted_by")

        granted_at = isoparse(d.pop("granted_at"))

        is_deleted = d.pop("is_deleted")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        access_right_response = cls(
            id=id,
            rule_id=rule_id,
            user_id=user_id,
            access_level=access_level,
            granted_by=granted_by,
            granted_at=granted_at,
            is_deleted=is_deleted,
            created_at=created_at,
            updated_at=updated_at,
        )

        access_right_response.additional_properties = d
        return access_right_response

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
