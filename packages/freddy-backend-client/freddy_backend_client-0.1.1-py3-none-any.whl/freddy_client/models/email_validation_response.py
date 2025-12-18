from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.organization_info import OrganizationInfo


T = TypeVar("T", bound="EmailValidationResponse")


@_attrs_define
class EmailValidationResponse:
    """Response schema for email validation endpoint.

    Example:
        {'email': 'user@aitronos.com', 'is_valid': True, 'message': 'Email is valid for signup', 'organization': {'id':
            'org_123abc456def789ghi012jkl345mno67', 'name': 'Aitronos', 'requires_invitation': False}, 'success': True}

    Attributes:
        success (bool): Whether the validation was successful
        is_valid (bool): Whether the email is valid for signup
        email (str): The validated email address
        message (str): Human-readable validation message
        organization (None | OrganizationInfo | Unset): Organization info if email domain is associated
        reason (None | str | Unset): Reason for invalid email (no_organization, already_registered, etc.)
    """

    success: bool
    is_valid: bool
    email: str
    message: str
    organization: None | OrganizationInfo | Unset = UNSET
    reason: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.organization_info import OrganizationInfo

        success = self.success

        is_valid = self.is_valid

        email = self.email

        message = self.message

        organization: dict[str, Any] | None | Unset
        if isinstance(self.organization, Unset):
            organization = UNSET
        elif isinstance(self.organization, OrganizationInfo):
            organization = self.organization.to_dict()
        else:
            organization = self.organization

        reason: None | str | Unset
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "success": success,
                "is_valid": is_valid,
                "email": email,
                "message": message,
            }
        )
        if organization is not UNSET:
            field_dict["organization"] = organization
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.organization_info import OrganizationInfo

        d = dict(src_dict)
        success = d.pop("success")

        is_valid = d.pop("is_valid")

        email = d.pop("email")

        message = d.pop("message")

        def _parse_organization(data: object) -> None | OrganizationInfo | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                organization_type_0 = OrganizationInfo.from_dict(data)

                return organization_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OrganizationInfo | Unset, data)

        organization = _parse_organization(d.pop("organization", UNSET))

        def _parse_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason = _parse_reason(d.pop("reason", UNSET))

        email_validation_response = cls(
            success=success,
            is_valid=is_valid,
            email=email,
            message=message,
            organization=organization,
            reason=reason,
        )

        email_validation_response.additional_properties = d
        return email_validation_response

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
