from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.thread_response import ThreadResponse


T = TypeVar("T", bound="ThreadListResponse")


@_attrs_define
class ThreadListResponse:
    """Response schema for paginated thread list with cursor-based pagination.

    Attributes:
        data (list[ThreadResponse]): List of threads
        has_more (bool): Whether there are more results available
        limit (int): Maximum number of records returned
        total (int): Total count of threads (optional)
        object_ (str | Unset): Object type, always 'list' Default: 'list'.
        first_id (None | str | Unset): First thread ID in results (cursor)
        last_id (None | str | Unset): Last thread ID in results (cursor)
    """

    data: list[ThreadResponse]
    has_more: bool
    limit: int
    total: int
    object_: str | Unset = "list"
    first_id: None | str | Unset = UNSET
    last_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        has_more = self.has_more

        limit = self.limit

        total = self.total

        object_ = self.object_

        first_id: None | str | Unset
        if isinstance(self.first_id, Unset):
            first_id = UNSET
        else:
            first_id = self.first_id

        last_id: None | str | Unset
        if isinstance(self.last_id, Unset):
            last_id = UNSET
        else:
            last_id = self.last_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "has_more": has_more,
                "limit": limit,
                "total": total,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_
        if first_id is not UNSET:
            field_dict["first_id"] = first_id
        if last_id is not UNSET:
            field_dict["last_id"] = last_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.thread_response import ThreadResponse

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = ThreadResponse.from_dict(data_item_data)

            data.append(data_item)

        has_more = d.pop("has_more")

        limit = d.pop("limit")

        total = d.pop("total")

        object_ = d.pop("object", UNSET)

        def _parse_first_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        first_id = _parse_first_id(d.pop("first_id", UNSET))

        def _parse_last_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        last_id = _parse_last_id(d.pop("last_id", UNSET))

        thread_list_response = cls(
            data=data,
            has_more=has_more,
            limit=limit,
            total=total,
            object_=object_,
            first_id=first_id,
            last_id=last_id,
        )

        thread_list_response.additional_properties = d
        return thread_list_response

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
