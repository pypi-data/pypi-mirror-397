from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.update_message_response_role import UpdateMessageResponseRole
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_message_response_attachments_item import (
        UpdateMessageResponseAttachmentsItem,
    )
    from ..models.update_message_response_metadata import UpdateMessageResponseMetadata


T = TypeVar("T", bound="UpdateMessageResponse")


@_attrs_define
class UpdateMessageResponse:
    """Response schema for updated message.

    Attributes:
        id (str): Message ID with msg_ prefix
        created_at (datetime.datetime): Creation timestamp
        thread_id (str): Thread ID with thread_ prefix
        role (UpdateMessageResponseRole): Message role
        content (str): Message text content
        updated_at (datetime.datetime | None | Unset): Last update timestamp
        attachments (list[UpdateMessageResponseAttachmentsItem] | Unset): File attachments
        metadata (UpdateMessageResponseMetadata | Unset): Custom metadata
    """

    id: str
    created_at: datetime.datetime
    thread_id: str
    role: UpdateMessageResponseRole
    content: str
    updated_at: datetime.datetime | None | Unset = UNSET
    attachments: list[UpdateMessageResponseAttachmentsItem] | Unset = UNSET
    metadata: UpdateMessageResponseMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        created_at = self.created_at.isoformat()

        thread_id = self.thread_id

        role = self.role.value

        content = self.content

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        attachments: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.attachments, Unset):
            attachments = []
            for attachments_item_data in self.attachments:
                attachments_item = attachments_item_data.to_dict()
                attachments.append(attachments_item)

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "created_at": created_at,
                "thread_id": thread_id,
                "role": role,
                "content": content,
            }
        )
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if attachments is not UNSET:
            field_dict["attachments"] = attachments
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_message_response_attachments_item import (
            UpdateMessageResponseAttachmentsItem,
        )
        from ..models.update_message_response_metadata import (
            UpdateMessageResponseMetadata,
        )

        d = dict(src_dict)
        id = d.pop("id")

        created_at = isoparse(d.pop("created_at"))

        thread_id = d.pop("thread_id")

        role = UpdateMessageResponseRole(d.pop("role"))

        content = d.pop("content")

        def _parse_updated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        _attachments = d.pop("attachments", UNSET)
        attachments: list[UpdateMessageResponseAttachmentsItem] | Unset = UNSET
        if _attachments is not UNSET:
            attachments = []
            for attachments_item_data in _attachments:
                attachments_item = UpdateMessageResponseAttachmentsItem.from_dict(
                    attachments_item_data
                )

                attachments.append(attachments_item)

        _metadata = d.pop("metadata", UNSET)
        metadata: UpdateMessageResponseMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = UpdateMessageResponseMetadata.from_dict(_metadata)

        update_message_response = cls(
            id=id,
            created_at=created_at,
            thread_id=thread_id,
            role=role,
            content=content,
            updated_at=updated_at,
            attachments=attachments,
            metadata=metadata,
        )

        update_message_response.additional_properties = d
        return update_message_response

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
