from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PasswordResetVerifyRequest")


@_attrs_define
class PasswordResetVerifyRequest:
    """Request schema for password reset verification endpoint.

    Example:
        {'email': 'user@example.com', 'new_password': 'NewSecurePassword123!', 'verification_code': 1234}

    Attributes:
        email (str): User email address
        verification_code (int): 4-digit verification code
        new_password (str): New password (min 8 chars with complexity, max 72 chars due to bcrypt limit)
    """

    email: str
    verification_code: int
    new_password: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        verification_code = self.verification_code

        new_password = self.new_password

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "verification_code": verification_code,
                "new_password": new_password,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        verification_code = d.pop("verification_code")

        new_password = d.pop("new_password")

        password_reset_verify_request = cls(
            email=email,
            verification_code=verification_code,
            new_password=new_password,
        )

        password_reset_verify_request.additional_properties = d
        return password_reset_verify_request

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
