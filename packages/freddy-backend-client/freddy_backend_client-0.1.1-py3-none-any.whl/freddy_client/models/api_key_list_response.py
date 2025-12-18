from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.api_key_response import ApiKeyResponse


T = TypeVar("T", bound="ApiKeyListResponse")


@_attrs_define
class ApiKeyListResponse:
    """Response schema for listing API keys.

    Attributes:
        keys (list[ApiKeyResponse]): List of API keys
        total (int): Total number of keys
        page (int): Current page number
        page_size (int): Number of items per page
    """

    keys: list[ApiKeyResponse]
    total: int
    page: int
    page_size: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        keys = []
        for keys_item_data in self.keys:
            keys_item = keys_item_data.to_dict()
            keys.append(keys_item)

        total = self.total

        page = self.page

        page_size = self.page_size

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "keys": keys,
                "total": total,
                "page": page,
                "page_size": page_size,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_key_response import ApiKeyResponse

        d = dict(src_dict)
        keys = []
        _keys = d.pop("keys")
        for keys_item_data in _keys:
            keys_item = ApiKeyResponse.from_dict(keys_item_data)

            keys.append(keys_item)

        total = d.pop("total")

        page = d.pop("page")

        page_size = d.pop("page_size")

        api_key_list_response = cls(
            keys=keys,
            total=total,
            page=page,
            page_size=page_size,
        )

        api_key_list_response.additional_properties = d
        return api_key_list_response

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
