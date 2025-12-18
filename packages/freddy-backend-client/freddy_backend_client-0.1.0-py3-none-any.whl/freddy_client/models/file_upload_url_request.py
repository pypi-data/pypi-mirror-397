from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileUploadUrlRequest")


@_attrs_define
class FileUploadUrlRequest:
    """Request schema for generating upload URL.

    Example:
        {'file_size': 5242880, 'filename': 'document.pdf', 'mime_type': 'application/pdf', 'upload_type': 'standard'}

    Attributes:
        filename (str):
        file_size (int): File size in bytes
        mime_type (str): File MIME type
        upload_type (str | Unset): Upload type: 'resumable' for session URI (better for large files) or 'standard' for
            signed URL (simple PUT) Default: 'resumable'.
    """

    filename: str
    file_size: int
    mime_type: str
    upload_type: str | Unset = "resumable"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        filename = self.filename

        file_size = self.file_size

        mime_type = self.mime_type

        upload_type = self.upload_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "filename": filename,
                "file_size": file_size,
                "mime_type": mime_type,
            }
        )
        if upload_type is not UNSET:
            field_dict["upload_type"] = upload_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        filename = d.pop("filename")

        file_size = d.pop("file_size")

        mime_type = d.pop("mime_type")

        upload_type = d.pop("upload_type", UNSET)

        file_upload_url_request = cls(
            filename=filename,
            file_size=file_size,
            mime_type=mime_type,
            upload_type=upload_type,
        )

        file_upload_url_request.additional_properties = d
        return file_upload_url_request

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
