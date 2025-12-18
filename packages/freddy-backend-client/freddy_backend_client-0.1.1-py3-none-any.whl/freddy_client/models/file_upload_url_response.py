from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileUploadUrlResponse")


@_attrs_define
class FileUploadUrlResponse:
    """Response schema for upload URL.

    Example:
        {'chunk_size_recommended': 5242880, 'expires_at': '2024-12-08T10:00:00Z', 'file_id': 'file_xyz789', 'gcs_path':
            'files/org_abc123/file_xyz789/document.pdf', 'max_file_size': 104857600, 'upload_type': 'resumable',
            'upload_url': 'https://storage.googleapis.com/upload/...'}

    Attributes:
        upload_url (str): Resumable upload session URI
        gcs_path (str): Destination path in GCS
        file_id (str): Generated File ID
        expires_at (datetime.datetime): Session expiry (7 days)
        max_file_size (int): Maximum file size in bytes
        chunk_size_recommended (int): Recommended chunk size (5MB)
        upload_type (str | Unset): Upload type Default: 'resumable'.
    """

    upload_url: str
    gcs_path: str
    file_id: str
    expires_at: datetime.datetime
    max_file_size: int
    chunk_size_recommended: int
    upload_type: str | Unset = "resumable"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        upload_url = self.upload_url

        gcs_path = self.gcs_path

        file_id = self.file_id

        expires_at = self.expires_at.isoformat()

        max_file_size = self.max_file_size

        chunk_size_recommended = self.chunk_size_recommended

        upload_type = self.upload_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "upload_url": upload_url,
                "gcs_path": gcs_path,
                "file_id": file_id,
                "expires_at": expires_at,
                "max_file_size": max_file_size,
                "chunk_size_recommended": chunk_size_recommended,
            }
        )
        if upload_type is not UNSET:
            field_dict["upload_type"] = upload_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        upload_url = d.pop("upload_url")

        gcs_path = d.pop("gcs_path")

        file_id = d.pop("file_id")

        expires_at = isoparse(d.pop("expires_at"))

        max_file_size = d.pop("max_file_size")

        chunk_size_recommended = d.pop("chunk_size_recommended")

        upload_type = d.pop("upload_type", UNSET)

        file_upload_url_response = cls(
            upload_url=upload_url,
            gcs_path=gcs_path,
            file_id=file_id,
            expires_at=expires_at,
            max_file_size=max_file_size,
            chunk_size_recommended=chunk_size_recommended,
            upload_type=upload_type,
        )

        file_upload_url_response.additional_properties = d
        return file_upload_url_response

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
