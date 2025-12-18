from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.thread_response_metadata_type_0 import ThreadResponseMetadataType0


T = TypeVar("T", bound="ThreadResponse")


@_attrs_define
class ThreadResponse:
    """Response schema for thread.

    Attributes:
        id (str): Thread ID with thread_ prefix
        created_at (str): ISO 8601 datetime of creation
        updated_at (str): ISO 8601 datetime of last update
        organization_id (str): Organization ID
        message_count (int): Total number of messages
        object_ (str | Unset): Object type, always 'thread' Default: 'thread'.
        last_message_at (None | str | Unset): ISO 8601 datetime of last message activity
        metadata (None | ThreadResponseMetadataType0 | Unset): Custom key-value pairs
        assistant_id (None | str | Unset): Bound assistant ID
        user_id (None | str | Unset): Creator user ID
        title (None | str | Unset): Thread title
        status (str | Unset): Streaming status (streaming or inactive) Default: 'inactive'.
        visible_in_ui (bool | Unset): Whether this thread should be visible in the user interface Default: True.
        last_model_used (None | str | Unset): Model used for the last message in this thread
    """

    id: str
    created_at: str
    updated_at: str
    organization_id: str
    message_count: int
    object_: str | Unset = "thread"
    last_message_at: None | str | Unset = UNSET
    metadata: None | ThreadResponseMetadataType0 | Unset = UNSET
    assistant_id: None | str | Unset = UNSET
    user_id: None | str | Unset = UNSET
    title: None | str | Unset = UNSET
    status: str | Unset = "inactive"
    visible_in_ui: bool | Unset = True
    last_model_used: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.thread_response_metadata_type_0 import ThreadResponseMetadataType0

        id = self.id

        created_at = self.created_at

        updated_at = self.updated_at

        organization_id = self.organization_id

        message_count = self.message_count

        object_ = self.object_

        last_message_at: None | str | Unset
        if isinstance(self.last_message_at, Unset):
            last_message_at = UNSET
        else:
            last_message_at = self.last_message_at

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, ThreadResponseMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        assistant_id: None | str | Unset
        if isinstance(self.assistant_id, Unset):
            assistant_id = UNSET
        else:
            assistant_id = self.assistant_id

        user_id: None | str | Unset
        if isinstance(self.user_id, Unset):
            user_id = UNSET
        else:
            user_id = self.user_id

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        status = self.status

        visible_in_ui = self.visible_in_ui

        last_model_used: None | str | Unset
        if isinstance(self.last_model_used, Unset):
            last_model_used = UNSET
        else:
            last_model_used = self.last_model_used

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "created_at": created_at,
                "updated_at": updated_at,
                "organization_id": organization_id,
                "message_count": message_count,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_
        if last_message_at is not UNSET:
            field_dict["last_message_at"] = last_message_at
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if assistant_id is not UNSET:
            field_dict["assistant_id"] = assistant_id
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if title is not UNSET:
            field_dict["title"] = title
        if status is not UNSET:
            field_dict["status"] = status
        if visible_in_ui is not UNSET:
            field_dict["visible_in_ui"] = visible_in_ui
        if last_model_used is not UNSET:
            field_dict["last_model_used"] = last_model_used

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.thread_response_metadata_type_0 import ThreadResponseMetadataType0

        d = dict(src_dict)
        id = d.pop("id")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        organization_id = d.pop("organization_id")

        message_count = d.pop("message_count")

        object_ = d.pop("object", UNSET)

        def _parse_last_message_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        last_message_at = _parse_last_message_at(d.pop("last_message_at", UNSET))

        def _parse_metadata(data: object) -> None | ThreadResponseMetadataType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = ThreadResponseMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ThreadResponseMetadataType0 | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        def _parse_assistant_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        assistant_id = _parse_assistant_id(d.pop("assistant_id", UNSET))

        def _parse_user_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_id = _parse_user_id(d.pop("user_id", UNSET))

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        status = d.pop("status", UNSET)

        visible_in_ui = d.pop("visible_in_ui", UNSET)

        def _parse_last_model_used(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        last_model_used = _parse_last_model_used(d.pop("last_model_used", UNSET))

        thread_response = cls(
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            organization_id=organization_id,
            message_count=message_count,
            object_=object_,
            last_message_at=last_message_at,
            metadata=metadata,
            assistant_id=assistant_id,
            user_id=user_id,
            title=title,
            status=status,
            visible_in_ui=visible_in_ui,
            last_model_used=last_model_used,
        )

        thread_response.additional_properties = d
        return thread_response

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
