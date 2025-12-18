from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.content_block import ContentBlock
    from ..models.file_reference import FileReference


T = TypeVar("T", bound="InputMessage")


@_attrs_define
class InputMessage:
    """Input message with role and content.

    Content can be either:
    - Simple string (convenience)
    - Array of ContentBlock objects (structured)

    Files can be referenced via:
    - files[] array (recommended for multiple files)
    - ContentBlock with type='file' (alternative)

        Attributes:
            role (str): Message role: 'user', 'assistant', or 'system'
            content (list[ContentBlock] | str): Message content as text blocks array or string
            files (list[FileReference] | None | Unset): Array of file references for context retrieval. Each file reference
                contains only file_id. Relevant chunks from these files will be injected into the conversation.
            id (None | str | Unset): Unique ID of the input message. Populated when items are returned via API.
    """

    role: str
    content: list[ContentBlock] | str
    files: list[FileReference] | None | Unset = UNSET
    id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role = self.role

        content: list[dict[str, Any]] | str
        if isinstance(self.content, list):
            content = []
            for content_type_0_item_data in self.content:
                content_type_0_item = content_type_0_item_data.to_dict()
                content.append(content_type_0_item)

        else:
            content = self.content

        files: list[dict[str, Any]] | None | Unset
        if isinstance(self.files, Unset):
            files = UNSET
        elif isinstance(self.files, list):
            files = []
            for files_type_0_item_data in self.files:
                files_type_0_item = files_type_0_item_data.to_dict()
                files.append(files_type_0_item)

        else:
            files = self.files

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "role": role,
                "content": content,
            }
        )
        if files is not UNSET:
            field_dict["files"] = files
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.content_block import ContentBlock
        from ..models.file_reference import FileReference

        d = dict(src_dict)
        role = d.pop("role")

        def _parse_content(data: object) -> list[ContentBlock] | str:
            try:
                if not isinstance(data, list):
                    raise TypeError()
                content_type_0 = []
                _content_type_0 = data
                for content_type_0_item_data in _content_type_0:
                    content_type_0_item = ContentBlock.from_dict(
                        content_type_0_item_data
                    )

                    content_type_0.append(content_type_0_item)

                return content_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ContentBlock] | str, data)

        content = _parse_content(d.pop("content"))

        def _parse_files(data: object) -> list[FileReference] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                files_type_0 = []
                _files_type_0 = data
                for files_type_0_item_data in _files_type_0:
                    files_type_0_item = FileReference.from_dict(files_type_0_item_data)

                    files_type_0.append(files_type_0_item)

                return files_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[FileReference] | None | Unset, data)

        files = _parse_files(d.pop("files", UNSET))

        def _parse_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        id = _parse_id(d.pop("id", UNSET))

        input_message = cls(
            role=role,
            content=content,
            files=files,
            id=id,
        )

        input_message.additional_properties = d
        return input_message

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
