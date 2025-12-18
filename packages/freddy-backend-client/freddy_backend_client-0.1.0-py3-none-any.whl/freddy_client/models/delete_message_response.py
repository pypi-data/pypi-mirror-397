from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeleteMessageResponse")


@_attrs_define
class DeleteMessageResponse:
    """Response schema for deleted message.

    Attributes:
        id (str): Deleted message ID with msg_ prefix
        deleted (bool | Unset): Deletion confirmation Default: True.
        object_ (Literal['thread.message.deleted'] | Unset): Object type identifier Default: 'thread.message.deleted'.
    """

    id: str
    deleted: bool | Unset = True
    object_: Literal["thread.message.deleted"] | Unset = "thread.message.deleted"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        deleted = self.deleted

        object_ = self.object_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        deleted = d.pop("deleted", UNSET)

        object_ = cast(
            Literal["thread.message.deleted"] | Unset, d.pop("object", UNSET)
        )
        if object_ != "thread.message.deleted" and not isinstance(object_, Unset):
            raise ValueError(
                f"object must match const 'thread.message.deleted', got '{object_}'"
            )

        delete_message_response = cls(
            id=id,
            deleted=deleted,
            object_=object_,
        )

        delete_message_response.additional_properties = d
        return delete_message_response

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
