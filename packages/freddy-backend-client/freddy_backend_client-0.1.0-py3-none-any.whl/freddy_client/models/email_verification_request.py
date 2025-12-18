from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device_information import DeviceInformation


T = TypeVar("T", bound="EmailVerificationRequest")


@_attrs_define
class EmailVerificationRequest:
    """Request schema for email verification endpoint.

    Example:
        {'device_information': {'device_id': 'device-123', 'platform': 'web'}, 'email_key':
            'uuid-12345678-1234-1234-1234-123456789abc', 'verification_code': 1234}

    Attributes:
        email_key (str): Email verification key
        verification_code (int): 4-digit verification code
        device_information (DeviceInformation | None | Unset): Device tracking information
    """

    email_key: str
    verification_code: int
    device_information: DeviceInformation | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.device_information import DeviceInformation

        email_key = self.email_key

        verification_code = self.verification_code

        device_information: dict[str, Any] | None | Unset
        if isinstance(self.device_information, Unset):
            device_information = UNSET
        elif isinstance(self.device_information, DeviceInformation):
            device_information = self.device_information.to_dict()
        else:
            device_information = self.device_information

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email_key": email_key,
                "verification_code": verification_code,
            }
        )
        if device_information is not UNSET:
            field_dict["device_information"] = device_information

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.device_information import DeviceInformation

        d = dict(src_dict)
        email_key = d.pop("email_key")

        verification_code = d.pop("verification_code")

        def _parse_device_information(data: object) -> DeviceInformation | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                device_information_type_0 = DeviceInformation.from_dict(data)

                return device_information_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DeviceInformation | None | Unset, data)

        device_information = _parse_device_information(
            d.pop("device_information", UNSET)
        )

        email_verification_request = cls(
            email_key=email_key,
            verification_code=verification_code,
            device_information=device_information,
        )

        email_verification_request.additional_properties = d
        return email_verification_request

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
