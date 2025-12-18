from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="LogoutResponse")


@_attrs_define
class LogoutResponse:
    """Response schema for logout endpoint.

    Example:
        {'logged_out_at': '2025-10-31T14:05:00Z', 'message': 'Successfully logged out'}

    Attributes:
        message (str):
        logged_out_at (str):
    """

    message: str
    logged_out_at: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        logged_out_at = self.logged_out_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
                "logged_out_at": logged_out_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        message = d.pop("message")

        logged_out_at = d.pop("logged_out_at")

        logout_response = cls(
            message=message,
            logged_out_at=logged_out_at,
        )

        logout_response.additional_properties = d
        return logout_response

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
