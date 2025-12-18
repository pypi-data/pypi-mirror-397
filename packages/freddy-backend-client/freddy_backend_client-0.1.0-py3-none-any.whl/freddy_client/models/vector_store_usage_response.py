from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.vector_store_usage_item import VectorStoreUsageItem


T = TypeVar("T", bound="VectorStoreUsageResponse")


@_attrs_define
class VectorStoreUsageResponse:
    """Vector store usage summary for organization.

    Attributes:
        total_size_bytes (int): Total storage used in bytes
        total_size_mb (float): Total storage used in MB
        total_files (int): Total number of files
        vector_store_count (int): Number of vector stores
        vector_stores (list[VectorStoreUsageItem]): Usage breakdown by vector store
    """

    total_size_bytes: int
    total_size_mb: float
    total_files: int
    vector_store_count: int
    vector_stores: list[VectorStoreUsageItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_size_bytes = self.total_size_bytes

        total_size_mb = self.total_size_mb

        total_files = self.total_files

        vector_store_count = self.vector_store_count

        vector_stores = []
        for vector_stores_item_data in self.vector_stores:
            vector_stores_item = vector_stores_item_data.to_dict()
            vector_stores.append(vector_stores_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_size_bytes": total_size_bytes,
                "total_size_mb": total_size_mb,
                "total_files": total_files,
                "vector_store_count": vector_store_count,
                "vector_stores": vector_stores,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.vector_store_usage_item import VectorStoreUsageItem

        d = dict(src_dict)
        total_size_bytes = d.pop("total_size_bytes")

        total_size_mb = d.pop("total_size_mb")

        total_files = d.pop("total_files")

        vector_store_count = d.pop("vector_store_count")

        vector_stores = []
        _vector_stores = d.pop("vector_stores")
        for vector_stores_item_data in _vector_stores:
            vector_stores_item = VectorStoreUsageItem.from_dict(vector_stores_item_data)

            vector_stores.append(vector_stores_item)

        vector_store_usage_response = cls(
            total_size_bytes=total_size_bytes,
            total_size_mb=total_size_mb,
            total_files=total_files,
            vector_store_count=vector_store_count,
            vector_stores=vector_stores,
        )

        vector_store_usage_response.additional_properties = d
        return vector_store_usage_response

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
