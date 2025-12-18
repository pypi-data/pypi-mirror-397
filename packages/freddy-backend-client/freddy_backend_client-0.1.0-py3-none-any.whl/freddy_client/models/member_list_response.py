from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.member_response import MemberResponse


T = TypeVar("T", bound="MemberListResponse")


@_attrs_define
class MemberListResponse:
    """Schema for paginated member list response.

    Attributes:
        users (list[MemberResponse]): List of members
        total_users_count (int): Total number of members
        skip (int): Number of records skipped
        take (int): Number of records returned
    """

    users: list[MemberResponse]
    total_users_count: int
    skip: int
    take: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        users = []
        for users_item_data in self.users:
            users_item = users_item_data.to_dict()
            users.append(users_item)

        total_users_count = self.total_users_count

        skip = self.skip

        take = self.take

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "users": users,
                "total_users_count": total_users_count,
                "skip": skip,
                "take": take,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.member_response import MemberResponse

        d = dict(src_dict)
        users = []
        _users = d.pop("users")
        for users_item_data in _users:
            users_item = MemberResponse.from_dict(users_item_data)

            users.append(users_item)

        total_users_count = d.pop("total_users_count")

        skip = d.pop("skip")

        take = d.pop("take")

        member_list_response = cls(
            users=users,
            total_users_count=total_users_count,
            skip=skip,
            take=take,
        )

        member_list_response.additional_properties = d
        return member_list_response

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
