from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FileRegisterRequest")


@_attrs_define
class FileRegisterRequest:
    """Request schema for registering completed upload.

    Attributes:
        filename (str):
        gcs_path (str): GCS path where file was uploaded
        file_size (int): File size in bytes
        mime_type (str): File MIME type
    """

    filename: str
    gcs_path: str
    file_size: int
    mime_type: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        filename = self.filename

        gcs_path = self.gcs_path

        file_size = self.file_size

        mime_type = self.mime_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "filename": filename,
                "gcs_path": gcs_path,
                "file_size": file_size,
                "mime_type": mime_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        filename = d.pop("filename")

        gcs_path = d.pop("gcs_path")

        file_size = d.pop("file_size")

        mime_type = d.pop("mime_type")

        file_register_request = cls(
            filename=filename,
            gcs_path=gcs_path,
            file_size=file_size,
            mime_type=mime_type,
        )

        file_register_request.additional_properties = d
        return file_register_request

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
