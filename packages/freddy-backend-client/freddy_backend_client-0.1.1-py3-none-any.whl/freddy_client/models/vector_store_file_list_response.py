from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.vector_store_file_response import VectorStoreFileResponse


T = TypeVar("T", bound="VectorStoreFileListResponse")


@_attrs_define
class VectorStoreFileListResponse:
    """Schema for paginated list of files in vector store.

    Attributes:
        total (int): Total number of files in the vector store
        page (int): Current page number
        page_size (int): Number of items per page
        total_pages (int): Total number of pages
        files (list[VectorStoreFileResponse]): List of files in the current page
    """

    total: int
    page: int
    page_size: int
    total_pages: int
    files: list[VectorStoreFileResponse]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total = self.total

        page = self.page

        page_size = self.page_size

        total_pages = self.total_pages

        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_dict()
            files.append(files_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "files": files,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.vector_store_file_response import VectorStoreFileResponse

        d = dict(src_dict)
        total = d.pop("total")

        page = d.pop("page")

        page_size = d.pop("page_size")

        total_pages = d.pop("total_pages")

        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = VectorStoreFileResponse.from_dict(files_item_data)

            files.append(files_item)

        vector_store_file_list_response = cls(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            files=files,
        )

        vector_store_file_list_response.additional_properties = d
        return vector_store_file_list_response

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
