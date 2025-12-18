from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, File, Unset

T = TypeVar("T", bound="BodyUploadIconV1IconsOrganizationsOrgIdPost")


@_attrs_define
class BodyUploadIconV1IconsOrganizationsOrgIdPost:
    """
    Attributes:
        file (File): Icon file (SVG, PNG, JPG)
        name (str): Icon name
        description (None | str | Unset): Icon description
        tags (None | str | Unset): Comma-separated tags
        category (str | Unset): Icon category Default: 'custom'.
    """

    file: File
    name: str
    description: None | str | Unset = UNSET
    tags: None | str | Unset = UNSET
    category: str | Unset = "custom"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file = self.file.to_tuple()

        name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        tags: None | str | Unset
        if isinstance(self.tags, Unset):
            tags = UNSET
        else:
            tags = self.tags

        category = self.category

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file": file,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if tags is not UNSET:
            field_dict["tags"] = tags
        if category is not UNSET:
            field_dict["category"] = category

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("file", self.file.to_tuple()))

        files.append(("name", (None, str(self.name).encode(), "text/plain")))

        if not isinstance(self.description, Unset):
            if isinstance(self.description, str):
                files.append(
                    (
                        "description",
                        (None, str(self.description).encode(), "text/plain"),
                    )
                )
            else:
                files.append(
                    (
                        "description",
                        (None, str(self.description).encode(), "text/plain"),
                    )
                )

        if not isinstance(self.tags, Unset):
            if isinstance(self.tags, str):
                files.append(("tags", (None, str(self.tags).encode(), "text/plain")))
            else:
                files.append(("tags", (None, str(self.tags).encode(), "text/plain")))

        if not isinstance(self.category, Unset):
            files.append(
                ("category", (None, str(self.category).encode(), "text/plain"))
            )

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file = File(payload=BytesIO(d.pop("file")))

        name = d.pop("name")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_tags(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        tags = _parse_tags(d.pop("tags", UNSET))

        category = d.pop("category", UNSET)

        body_upload_icon_v1_icons_organizations_org_id_post = cls(
            file=file,
            name=name,
            description=description,
            tags=tags,
            category=category,
        )

        body_upload_icon_v1_icons_organizations_org_id_post.additional_properties = d
        return body_upload_icon_v1_icons_organizations_org_id_post

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
