from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PasswordUpdateRequest")


@_attrs_define
class PasswordUpdateRequest:
    """Request schema for password update endpoint.

    Example:
        {'confirm_password': 'NewSecurePassword456!', 'current_password': 'CurrentPassword123!', 'new_password':
            'NewSecurePassword456!'}

    Attributes:
        current_password (str): Current password for verification
        new_password (str): New password (min 8 chars with complexity, max 72 chars due to bcrypt limit)
        confirm_password (str): Confirmation of new password (must match new_password)
    """

    current_password: str
    new_password: str
    confirm_password: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        current_password = self.current_password

        new_password = self.new_password

        confirm_password = self.confirm_password

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "current_password": current_password,
                "new_password": new_password,
                "confirm_password": confirm_password,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        current_password = d.pop("current_password")

        new_password = d.pop("new_password")

        confirm_password = d.pop("confirm_password")

        password_update_request = cls(
            current_password=current_password,
            new_password=new_password,
            confirm_password=confirm_password,
        )

        password_update_request.additional_properties = d
        return password_update_request

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
