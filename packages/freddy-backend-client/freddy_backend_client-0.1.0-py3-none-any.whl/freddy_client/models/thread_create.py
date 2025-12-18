from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.thread_create_metadata_type_0 import ThreadCreateMetadataType0


T = TypeVar("T", bound="ThreadCreate")


@_attrs_define
class ThreadCreate:
    """Request schema for creating a new thread.

    Attributes:
        organization_id (str): Organization ID
        title (None | str | Unset): Thread title
        metadata (None | ThreadCreateMetadataType0 | Unset): Custom key-value pairs (max 16 pairs, keys ≤64 chars,
            values ≤512 chars)
        assistant_id (None | str | Unset): Assistant ID to bind
        visible_in_ui (bool | None | Unset): Whether this thread should be visible in the user interface
    """

    organization_id: str
    title: None | str | Unset = UNSET
    metadata: None | ThreadCreateMetadataType0 | Unset = UNSET
    assistant_id: None | str | Unset = UNSET
    visible_in_ui: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.thread_create_metadata_type_0 import ThreadCreateMetadataType0

        organization_id = self.organization_id

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, ThreadCreateMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        assistant_id: None | str | Unset
        if isinstance(self.assistant_id, Unset):
            assistant_id = UNSET
        else:
            assistant_id = self.assistant_id

        visible_in_ui: bool | None | Unset
        if isinstance(self.visible_in_ui, Unset):
            visible_in_ui = UNSET
        else:
            visible_in_ui = self.visible_in_ui

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organization_id": organization_id,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if assistant_id is not UNSET:
            field_dict["assistant_id"] = assistant_id
        if visible_in_ui is not UNSET:
            field_dict["visible_in_ui"] = visible_in_ui

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.thread_create_metadata_type_0 import ThreadCreateMetadataType0

        d = dict(src_dict)
        organization_id = d.pop("organization_id")

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_metadata(data: object) -> None | ThreadCreateMetadataType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = ThreadCreateMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ThreadCreateMetadataType0 | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        def _parse_assistant_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        assistant_id = _parse_assistant_id(d.pop("assistant_id", UNSET))

        def _parse_visible_in_ui(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        visible_in_ui = _parse_visible_in_ui(d.pop("visible_in_ui", UNSET))

        thread_create = cls(
            organization_id=organization_id,
            title=title,
            metadata=metadata,
            assistant_id=assistant_id,
            visible_in_ui=visible_in_ui,
        )

        thread_create.additional_properties = d
        return thread_create

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
