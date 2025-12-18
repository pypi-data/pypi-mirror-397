from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device_information import DeviceInformation


T = TypeVar("T", bound="RegisterRequest")


@_attrs_define
class RegisterRequest:
    """Request schema for user registration endpoint.

    Example:
        {'device_information': {'device': 'Chrome Browser', 'device_id': 'device-123', 'platform': 'web'}, 'email':
            'user@company.com', 'full_name': 'John Doe', 'organization_id': 'org_12345678901234567890123456789012',
            'password': 'SecurePassword123!', 'user_name': 'johndoe'}

    Attributes:
        email (str): User email address (primary identifier)
        password (str): Password (min 8 chars with complexity, max 72 chars due to bcrypt limit)
        full_name (str): User's full name
        user_name (None | str | Unset): Preferred username (defaults to email prefix if omitted, min 3 chars)
        organization_id (None | str | Unset): Organization UID to associate the user with
        device_information (DeviceInformation | None | Unset): Device tracking information
    """

    email: str
    password: str
    full_name: str
    user_name: None | str | Unset = UNSET
    organization_id: None | str | Unset = UNSET
    device_information: DeviceInformation | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.device_information import DeviceInformation

        email = self.email

        password = self.password

        full_name = self.full_name

        user_name: None | str | Unset
        if isinstance(self.user_name, Unset):
            user_name = UNSET
        else:
            user_name = self.user_name

        organization_id: None | str | Unset
        if isinstance(self.organization_id, Unset):
            organization_id = UNSET
        else:
            organization_id = self.organization_id

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
                "email": email,
                "password": password,
                "full_name": full_name,
            }
        )
        if user_name is not UNSET:
            field_dict["user_name"] = user_name
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id
        if device_information is not UNSET:
            field_dict["device_information"] = device_information

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.device_information import DeviceInformation

        d = dict(src_dict)
        email = d.pop("email")

        password = d.pop("password")

        full_name = d.pop("full_name")

        def _parse_user_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_name = _parse_user_name(d.pop("user_name", UNSET))

        def _parse_organization_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        organization_id = _parse_organization_id(d.pop("organization_id", UNSET))

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

        register_request = cls(
            email=email,
            password=password,
            full_name=full_name,
            user_name=user_name,
            organization_id=organization_id,
            device_information=device_information,
        )

        register_request.additional_properties = d
        return register_request

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
