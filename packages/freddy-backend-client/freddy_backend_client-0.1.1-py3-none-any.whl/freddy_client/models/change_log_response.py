from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.change_detail import ChangeDetail


T = TypeVar("T", bound="ChangeLogResponse")


@_attrs_define
class ChangeLogResponse:
    """Schema for change log entry.

    Attributes:
        id (str): Audit log ID
        user_id (str): User who made the change
        user_name (str): Name of user who made the change
        user_email (str): Email of user who made the change
        action (str): Action performed (created, updated, deleted)
        timestamp (datetime.datetime): When the change occurred
        resource_type (str): Type of resource changed
        resource_id (str): ID of the resource changed
        resource_name (str): Name of the resource changed
        changes (list[ChangeDetail]): List of changes made
    """

    id: str
    user_id: str
    user_name: str
    user_email: str
    action: str
    timestamp: datetime.datetime
    resource_type: str
    resource_id: str
    resource_name: str
    changes: list[ChangeDetail]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        user_id = self.user_id

        user_name = self.user_name

        user_email = self.user_email

        action = self.action

        timestamp = self.timestamp.isoformat()

        resource_type = self.resource_type

        resource_id = self.resource_id

        resource_name = self.resource_name

        changes = []
        for changes_item_data in self.changes:
            changes_item = changes_item_data.to_dict()
            changes.append(changes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "user_id": user_id,
                "user_name": user_name,
                "user_email": user_email,
                "action": action,
                "timestamp": timestamp,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "resource_name": resource_name,
                "changes": changes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.change_detail import ChangeDetail

        d = dict(src_dict)
        id = d.pop("id")

        user_id = d.pop("user_id")

        user_name = d.pop("user_name")

        user_email = d.pop("user_email")

        action = d.pop("action")

        timestamp = isoparse(d.pop("timestamp"))

        resource_type = d.pop("resource_type")

        resource_id = d.pop("resource_id")

        resource_name = d.pop("resource_name")

        changes = []
        _changes = d.pop("changes")
        for changes_item_data in _changes:
            changes_item = ChangeDetail.from_dict(changes_item_data)

            changes.append(changes_item)

        change_log_response = cls(
            id=id,
            user_id=user_id,
            user_name=user_name,
            user_email=user_email,
            action=action,
            timestamp=timestamp,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            changes=changes,
        )

        change_log_response.additional_properties = d
        return change_log_response

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
