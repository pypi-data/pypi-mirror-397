from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ResendCodeResponse")


@_attrs_define
class ResendCodeResponse:
    """Response schema for resend code endpoint.

    Example:
        {'email_key': 'uuid-12345678-1234-1234-1234-123456789abc', 'message': 'A new verification code has been sent to
            your email', 'success': True, 'type': 'registration'}

    Attributes:
        success (bool):
        message (str):
        email_key (str):
        type_ (str): Verification type: 'login', 'registration', or 'password_reset'
    """

    success: bool
    message: str
    email_key: str
    type_: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        message = self.message

        email_key = self.email_key

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "success": success,
                "message": message,
                "email_key": email_key,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = d.pop("success")

        message = d.pop("message")

        email_key = d.pop("email_key")

        type_ = d.pop("type")

        resend_code_response = cls(
            success=success,
            message=message,
            email_key=email_key,
            type_=type_,
        )

        resend_code_response.additional_properties = d
        return resend_code_response

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
