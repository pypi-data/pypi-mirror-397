from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.vector_store_response import VectorStoreResponse


T = TypeVar("T", bound="SuccessResponseListVectorStoreResponse")


@_attrs_define
class SuccessResponseListVectorStoreResponse:
    """
    Attributes:
        message (str): Human-readable success message
        data (list[VectorStoreResponse]): Response data
        success (bool | Unset): Whether the request was successful Default: True.
    """

    message: str
    data: list[VectorStoreResponse]
    success: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        success = self.success

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
                "data": data,
            }
        )
        if success is not UNSET:
            field_dict["success"] = success

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.vector_store_response import VectorStoreResponse

        d = dict(src_dict)
        message = d.pop("message")

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = VectorStoreResponse.from_dict(data_item_data)

            data.append(data_item)

        success = d.pop("success", UNSET)

        success_response_list_vector_store_response = cls(
            message=message,
            data=data,
            success=success,
        )

        success_response_list_vector_store_response.additional_properties = d
        return success_response_list_vector_store_response

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
