from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import File

T = TypeVar("T", bound="BodyUploadManualV1StreamlineAutomationsUploadManualPost")


@_attrs_define
class BodyUploadManualV1StreamlineAutomationsUploadManualPost:
    """
    Attributes:
        file (File):
        automation_name (str):
        organization_id (str):
    """

    file: File
    automation_name: str
    organization_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file = self.file.to_tuple()

        automation_name = self.automation_name

        organization_id = self.organization_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file": file,
                "automation_name": automation_name,
                "organization_id": organization_id,
            }
        )

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("file", self.file.to_tuple()))

        files.append(
            (
                "automation_name",
                (None, str(self.automation_name).encode(), "text/plain"),
            )
        )

        files.append(
            (
                "organization_id",
                (None, str(self.organization_id).encode(), "text/plain"),
            )
        )

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file = File(payload=BytesIO(d.pop("file")))

        automation_name = d.pop("automation_name")

        organization_id = d.pop("organization_id")

        body_upload_manual_v1_streamline_automations_upload_manual_post = cls(
            file=file,
            automation_name=automation_name,
            organization_id=organization_id,
        )

        body_upload_manual_v1_streamline_automations_upload_manual_post.additional_properties = d
        return body_upload_manual_v1_streamline_automations_upload_manual_post

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
