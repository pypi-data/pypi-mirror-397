from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.login_response_device_info_type_0 import LoginResponseDeviceInfoType0
    from ..models.login_response_user import LoginResponseUser


T = TypeVar("T", bound="LoginResponse")


@_attrs_define
class LoginResponse:
    """Response schema for login endpoint.

    Example:
        {'device_info': {'device': 'Chrome Browser', 'platform': 'web'}, 'email': 'user@example.com', 'email_key':
            'uuid-12345678-1234-1234-1234-123456789abc', 'message': 'Login credentials verified. Please check your email for
            verification code.', 'next_step': 'email_verification', 'requires_verification': True, 'success': True, 'type':
            'login', 'user': {'email': 'user@example.com', 'id': 'uid_abc123def456', 'username': 'johndoe'}}

    Attributes:
        success (bool):
        message (str):
        email_key (str):
        email (str):
        requires_verification (bool):
        next_step (str):
        type_ (str): Verification type: 'login', 'registration', or 'password_reset'
        user (LoginResponseUser):
        device_info (LoginResponseDeviceInfoType0 | None | Unset):
    """

    success: bool
    message: str
    email_key: str
    email: str
    requires_verification: bool
    next_step: str
    type_: str
    user: LoginResponseUser
    device_info: LoginResponseDeviceInfoType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.login_response_device_info_type_0 import (
            LoginResponseDeviceInfoType0,
        )

        success = self.success

        message = self.message

        email_key = self.email_key

        email = self.email

        requires_verification = self.requires_verification

        next_step = self.next_step

        type_ = self.type_

        user = self.user.to_dict()

        device_info: dict[str, Any] | None | Unset
        if isinstance(self.device_info, Unset):
            device_info = UNSET
        elif isinstance(self.device_info, LoginResponseDeviceInfoType0):
            device_info = self.device_info.to_dict()
        else:
            device_info = self.device_info

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "success": success,
                "message": message,
                "email_key": email_key,
                "email": email,
                "requires_verification": requires_verification,
                "next_step": next_step,
                "type": type_,
                "user": user,
            }
        )
        if device_info is not UNSET:
            field_dict["device_info"] = device_info

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.login_response_device_info_type_0 import (
            LoginResponseDeviceInfoType0,
        )
        from ..models.login_response_user import LoginResponseUser

        d = dict(src_dict)
        success = d.pop("success")

        message = d.pop("message")

        email_key = d.pop("email_key")

        email = d.pop("email")

        requires_verification = d.pop("requires_verification")

        next_step = d.pop("next_step")

        type_ = d.pop("type")

        user = LoginResponseUser.from_dict(d.pop("user"))

        def _parse_device_info(
            data: object,
        ) -> LoginResponseDeviceInfoType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                device_info_type_0 = LoginResponseDeviceInfoType0.from_dict(data)

                return device_info_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(LoginResponseDeviceInfoType0 | None | Unset, data)

        device_info = _parse_device_info(d.pop("device_info", UNSET))

        login_response = cls(
            success=success,
            message=message,
            email_key=email_key,
            email=email,
            requires_verification=requires_verification,
            next_step=next_step,
            type_=type_,
            user=user,
            device_info=device_info,
        )

        login_response.additional_properties = d
        return login_response

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
