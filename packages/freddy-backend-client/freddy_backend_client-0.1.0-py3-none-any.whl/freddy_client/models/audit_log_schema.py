from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.audit_log_schema_metadata_type_0 import AuditLogSchemaMetadataType0
    from ..models.change_schema import ChangeSchema


T = TypeVar("T", bound="AuditLogSchema")


@_attrs_define
class AuditLogSchema:
    """Schema for audit log entry.

    Attributes:
        id (str): Audit log ID
        timestamp (int): Unix timestamp
        resource_type (str): Resource type
        resource_id (str): Resource ID
        resource_name (str): Resource name
        action (str): Action performed
        user_id (str): User ID
        user_name (str): User name
        user_email (str): User email
        changes (list[ChangeSchema] | None | Unset): Changes made
        metadata (AuditLogSchemaMetadataType0 | None | Unset): Additional metadata
    """

    id: str
    timestamp: int
    resource_type: str
    resource_id: str
    resource_name: str
    action: str
    user_id: str
    user_name: str
    user_email: str
    changes: list[ChangeSchema] | None | Unset = UNSET
    metadata: AuditLogSchemaMetadataType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.audit_log_schema_metadata_type_0 import (
            AuditLogSchemaMetadataType0,
        )

        id = self.id

        timestamp = self.timestamp

        resource_type = self.resource_type

        resource_id = self.resource_id

        resource_name = self.resource_name

        action = self.action

        user_id = self.user_id

        user_name = self.user_name

        user_email = self.user_email

        changes: list[dict[str, Any]] | None | Unset
        if isinstance(self.changes, Unset):
            changes = UNSET
        elif isinstance(self.changes, list):
            changes = []
            for changes_type_0_item_data in self.changes:
                changes_type_0_item = changes_type_0_item_data.to_dict()
                changes.append(changes_type_0_item)

        else:
            changes = self.changes

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, AuditLogSchemaMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "timestamp": timestamp,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "resource_name": resource_name,
                "action": action,
                "user_id": user_id,
                "user_name": user_name,
                "user_email": user_email,
            }
        )
        if changes is not UNSET:
            field_dict["changes"] = changes
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.audit_log_schema_metadata_type_0 import (
            AuditLogSchemaMetadataType0,
        )
        from ..models.change_schema import ChangeSchema

        d = dict(src_dict)
        id = d.pop("id")

        timestamp = d.pop("timestamp")

        resource_type = d.pop("resource_type")

        resource_id = d.pop("resource_id")

        resource_name = d.pop("resource_name")

        action = d.pop("action")

        user_id = d.pop("user_id")

        user_name = d.pop("user_name")

        user_email = d.pop("user_email")

        def _parse_changes(data: object) -> list[ChangeSchema] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                changes_type_0 = []
                _changes_type_0 = data
                for changes_type_0_item_data in _changes_type_0:
                    changes_type_0_item = ChangeSchema.from_dict(
                        changes_type_0_item_data
                    )

                    changes_type_0.append(changes_type_0_item)

                return changes_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ChangeSchema] | None | Unset, data)

        changes = _parse_changes(d.pop("changes", UNSET))

        def _parse_metadata(data: object) -> AuditLogSchemaMetadataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = AuditLogSchemaMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AuditLogSchemaMetadataType0 | None | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        audit_log_schema = cls(
            id=id,
            timestamp=timestamp,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            action=action,
            user_id=user_id,
            user_name=user_name,
            user_email=user_email,
            changes=changes,
            metadata=metadata,
        )

        audit_log_schema.additional_properties = d
        return audit_log_schema

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
