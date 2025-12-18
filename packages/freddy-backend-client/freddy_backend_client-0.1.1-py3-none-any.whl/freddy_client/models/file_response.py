from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileResponse")


@_attrs_define
class FileResponse:
    """Response schema for file metadata.

    Attributes:
        id (str): File ID (file_ prefix)
        original_filename (str):
        file_size (int):
        mime_type (str):
        storage_path (str):
        organization_id (str):
        uploaded_at (datetime.datetime):
        uploaded_by (None | str | Unset):
        uploaded_by_api_key_id (None | str | Unset):
    """

    id: str
    original_filename: str
    file_size: int
    mime_type: str
    storage_path: str
    organization_id: str
    uploaded_at: datetime.datetime
    uploaded_by: None | str | Unset = UNSET
    uploaded_by_api_key_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        original_filename = self.original_filename

        file_size = self.file_size

        mime_type = self.mime_type

        storage_path = self.storage_path

        organization_id = self.organization_id

        uploaded_at = self.uploaded_at.isoformat()

        uploaded_by: None | str | Unset
        if isinstance(self.uploaded_by, Unset):
            uploaded_by = UNSET
        else:
            uploaded_by = self.uploaded_by

        uploaded_by_api_key_id: None | str | Unset
        if isinstance(self.uploaded_by_api_key_id, Unset):
            uploaded_by_api_key_id = UNSET
        else:
            uploaded_by_api_key_id = self.uploaded_by_api_key_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "original_filename": original_filename,
                "file_size": file_size,
                "mime_type": mime_type,
                "storage_path": storage_path,
                "organization_id": organization_id,
                "uploaded_at": uploaded_at,
            }
        )
        if uploaded_by is not UNSET:
            field_dict["uploaded_by"] = uploaded_by
        if uploaded_by_api_key_id is not UNSET:
            field_dict["uploaded_by_api_key_id"] = uploaded_by_api_key_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        original_filename = d.pop("original_filename")

        file_size = d.pop("file_size")

        mime_type = d.pop("mime_type")

        storage_path = d.pop("storage_path")

        organization_id = d.pop("organization_id")

        uploaded_at = isoparse(d.pop("uploaded_at"))

        def _parse_uploaded_by(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        uploaded_by = _parse_uploaded_by(d.pop("uploaded_by", UNSET))

        def _parse_uploaded_by_api_key_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        uploaded_by_api_key_id = _parse_uploaded_by_api_key_id(
            d.pop("uploaded_by_api_key_id", UNSET)
        )

        file_response = cls(
            id=id,
            original_filename=original_filename,
            file_size=file_size,
            mime_type=mime_type,
            storage_path=storage_path,
            organization_id=organization_id,
            uploaded_at=uploaded_at,
            uploaded_by=uploaded_by,
            uploaded_by_api_key_id=uploaded_by_api_key_id,
        )

        file_response.additional_properties = d
        return file_response

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
