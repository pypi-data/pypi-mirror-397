from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.access_level import AccessLevel

T = TypeVar("T", bound="AccessRightGrantRequest")


@_attrs_define
class AccessRightGrantRequest:
    """Request schema for granting access rights.

    Attributes:
        user_id (str): User ID to grant access to
        access_level (AccessLevel): Access level enumeration.
    """

    user_id: str
    access_level: AccessLevel
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        access_level = self.access_level.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "access_level": access_level,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id")

        access_level = AccessLevel(d.pop("access_level"))

        access_right_grant_request = cls(
            user_id=user_id,
            access_level=access_level,
        )

        access_right_grant_request.additional_properties = d
        return access_right_grant_request

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
