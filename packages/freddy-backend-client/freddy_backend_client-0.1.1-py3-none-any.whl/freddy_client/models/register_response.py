from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RegisterResponse")


@_attrs_define
class RegisterResponse:
    """Response schema for user registration endpoint.

    Example:
        {'email': 'user@company.com', 'email_key': 'uuid-12345678-1234-1234-1234-123456789abc', 'message': 'Registration
            successful. Please check your email for a 4-digit verification code.', 'recommended_username': 'user',
            'success': True, 'type': 'registration', 'user_id': 'prg_abc123def456', 'verification_required': True}

    Attributes:
        success (bool):
        user_id (str): User ID (UUID)
        email (str):
        email_key (str): Email verification key (UUID)
        verification_required (bool): Whether email verification is required
        type_ (str): Verification type: 'registration'
        message (str):
        recommended_username (None | str | Unset): Recommended username if not provided during registration
    """

    success: bool
    user_id: str
    email: str
    email_key: str
    verification_required: bool
    type_: str
    message: str
    recommended_username: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        user_id = self.user_id

        email = self.email

        email_key = self.email_key

        verification_required = self.verification_required

        type_ = self.type_

        message = self.message

        recommended_username: None | str | Unset
        if isinstance(self.recommended_username, Unset):
            recommended_username = UNSET
        else:
            recommended_username = self.recommended_username

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "success": success,
                "user_id": user_id,
                "email": email,
                "email_key": email_key,
                "verification_required": verification_required,
                "type": type_,
                "message": message,
            }
        )
        if recommended_username is not UNSET:
            field_dict["recommended_username"] = recommended_username

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = d.pop("success")

        user_id = d.pop("user_id")

        email = d.pop("email")

        email_key = d.pop("email_key")

        verification_required = d.pop("verification_required")

        type_ = d.pop("type")

        message = d.pop("message")

        def _parse_recommended_username(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        recommended_username = _parse_recommended_username(
            d.pop("recommended_username", UNSET)
        )

        register_response = cls(
            success=success,
            user_id=user_id,
            email=email,
            email_key=email_key,
            verification_required=verification_required,
            type_=type_,
            message=message,
            recommended_username=recommended_username,
        )

        register_response.additional_properties = d
        return register_response

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
