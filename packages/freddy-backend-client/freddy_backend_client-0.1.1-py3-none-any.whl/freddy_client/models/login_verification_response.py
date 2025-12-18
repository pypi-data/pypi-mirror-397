from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.login_verification_response_user import LoginVerificationResponseUser


T = TypeVar("T", bound="LoginVerificationResponse")


@_attrs_define
class LoginVerificationResponse:
    """Response schema for login verification endpoint.

    Example:
        {'device_id': 'device-123', 'expires_in': 3600, 'refreshToken': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...', 'token_type': 'bearer', 'user': {'email':
            'user@example.com', 'id': 'usr_abc123def456', 'verified': True}}

    Attributes:
        refresh_token (str):
        token (str):
        token_type (str):
        expires_in (int):
        user (LoginVerificationResponseUser):
        device_id (None | str | Unset):
    """

    refresh_token: str
    token: str
    token_type: str
    expires_in: int
    user: LoginVerificationResponseUser
    device_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        refresh_token = self.refresh_token

        token = self.token

        token_type = self.token_type

        expires_in = self.expires_in

        user = self.user.to_dict()

        device_id: None | str | Unset
        if isinstance(self.device_id, Unset):
            device_id = UNSET
        else:
            device_id = self.device_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "refreshToken": refresh_token,
                "token": token,
                "token_type": token_type,
                "expires_in": expires_in,
                "user": user,
            }
        )
        if device_id is not UNSET:
            field_dict["device_id"] = device_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.login_verification_response_user import (
            LoginVerificationResponseUser,
        )

        d = dict(src_dict)
        refresh_token = d.pop("refreshToken")

        token = d.pop("token")

        token_type = d.pop("token_type")

        expires_in = d.pop("expires_in")

        user = LoginVerificationResponseUser.from_dict(d.pop("user"))

        def _parse_device_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        device_id = _parse_device_id(d.pop("device_id", UNSET))

        login_verification_response = cls(
            refresh_token=refresh_token,
            token=token,
            token_type=token_type,
            expires_in=expires_in,
            user=user,
            device_id=device_id,
        )

        login_verification_response.additional_properties = d
        return login_verification_response

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
