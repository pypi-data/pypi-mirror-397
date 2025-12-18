from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.icon_response import IconResponse


T = TypeVar("T", bound="IconListResponse")


@_attrs_define
class IconListResponse:
    """Schema for icon list response.

    Attributes:
        icons (list[IconResponse]):
        total (int):
        limit (int):
        offset (int):
    """

    icons: list[IconResponse]
    total: int
    limit: int
    offset: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        icons = []
        for icons_item_data in self.icons:
            icons_item = icons_item_data.to_dict()
            icons.append(icons_item)

        total = self.total

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "icons": icons,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.icon_response import IconResponse

        d = dict(src_dict)
        icons = []
        _icons = d.pop("icons")
        for icons_item_data in _icons:
            icons_item = IconResponse.from_dict(icons_item_data)

            icons.append(icons_item)

        total = d.pop("total")

        limit = d.pop("limit")

        offset = d.pop("offset")

        icon_list_response = cls(
            icons=icons,
            total=total,
            limit=limit,
            offset=offset,
        )

        icon_list_response.additional_properties = d
        return icon_list_response

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
