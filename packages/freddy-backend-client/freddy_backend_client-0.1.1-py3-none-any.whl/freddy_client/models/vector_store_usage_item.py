from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VectorStoreUsageItem")


@_attrs_define
class VectorStoreUsageItem:
    """Individual vector store usage.

    Attributes:
        vector_store_id (str): Vector store ID
        vector_store_name (str): Vector store name
        data_size_bytes (int): Storage size in bytes
        data_size_mb (float): Storage size in MB
        file_count (int): Number of files
        usage_percentage (float): Percentage of total organization usage
        color (str): Color for UI visualization
    """

    vector_store_id: str
    vector_store_name: str
    data_size_bytes: int
    data_size_mb: float
    file_count: int
    usage_percentage: float
    color: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        vector_store_id = self.vector_store_id

        vector_store_name = self.vector_store_name

        data_size_bytes = self.data_size_bytes

        data_size_mb = self.data_size_mb

        file_count = self.file_count

        usage_percentage = self.usage_percentage

        color = self.color

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "vector_store_id": vector_store_id,
                "vector_store_name": vector_store_name,
                "data_size_bytes": data_size_bytes,
                "data_size_mb": data_size_mb,
                "file_count": file_count,
                "usage_percentage": usage_percentage,
                "color": color,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        vector_store_id = d.pop("vector_store_id")

        vector_store_name = d.pop("vector_store_name")

        data_size_bytes = d.pop("data_size_bytes")

        data_size_mb = d.pop("data_size_mb")

        file_count = d.pop("file_count")

        usage_percentage = d.pop("usage_percentage")

        color = d.pop("color")

        vector_store_usage_item = cls(
            vector_store_id=vector_store_id,
            vector_store_name=vector_store_name,
            data_size_bytes=data_size_bytes,
            data_size_mb=data_size_mb,
            file_count=file_count,
            usage_percentage=usage_percentage,
            color=color,
        )

        vector_store_usage_item.additional_properties = d
        return vector_store_usage_item

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
