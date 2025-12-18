from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="InvitationResponse")


@_attrs_define
class InvitationResponse:
    """Schema for invitation creation response.

    Attributes:
        invitation_id (str): Created invitation ID
        email (str): Email address invited
        role_id (str): Role assigned to invitation
        user_id (str): User ID of invited user
    """

    invitation_id: str
    email: str
    role_id: str
    user_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        invitation_id = self.invitation_id

        email = self.email

        role_id = self.role_id

        user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "invitation_id": invitation_id,
                "email": email,
                "role_id": role_id,
                "user_id": user_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        invitation_id = d.pop("invitation_id")

        email = d.pop("email")

        role_id = d.pop("role_id")

        user_id = d.pop("user_id")

        invitation_response = cls(
            invitation_id=invitation_id,
            email=email,
            role_id=role_id,
            user_id=user_id,
        )

        invitation_response.additional_properties = d
        return invitation_response

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
