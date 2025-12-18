from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InviteUserRequest")


@_attrs_define
class InviteUserRequest:
    """Schema for inviting a new user to the organization.

    Attributes:
        email (str): Email address to invite
        role_id (str): Role ID to assign
        send_invitation (bool | Unset): Whether to send invitation email Default: True.
    """

    email: str
    role_id: str
    send_invitation: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        role_id = self.role_id

        send_invitation = self.send_invitation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "role_id": role_id,
            }
        )
        if send_invitation is not UNSET:
            field_dict["send_invitation"] = send_invitation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        role_id = d.pop("role_id")

        send_invitation = d.pop("send_invitation", UNSET)

        invite_user_request = cls(
            email=email,
            role_id=role_id,
            send_invitation=send_invitation,
        )

        invite_user_request.additional_properties = d
        return invite_user_request

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
