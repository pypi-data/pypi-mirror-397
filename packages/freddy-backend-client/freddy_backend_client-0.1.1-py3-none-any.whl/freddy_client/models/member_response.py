from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.role_info import RoleInfo
    from ..models.status_info import StatusInfo


T = TypeVar("T", bound="MemberResponse")


@_attrs_define
class MemberResponse:
    """Schema for individual member response.

    Attributes:
        id (str): Organization user ID
        user_id (str): User ID
        organization_id (str): Organization ID
        email (str): User's email address
        role (RoleInfo): Schema for role information in member responses.
        status (StatusInfo): Schema for status information in member responses.
        joined_at (datetime.datetime): When user joined the organization
        created_at (datetime.datetime): When membership was created
        last_modified_at (datetime.datetime): When membership was last modified
        full_name (None | str | Unset): User's full name
        username (None | str | Unset): User's username
        profile_image (None | str | Unset): User's profile image URL
    """

    id: str
    user_id: str
    organization_id: str
    email: str
    role: RoleInfo
    status: StatusInfo
    joined_at: datetime.datetime
    created_at: datetime.datetime
    last_modified_at: datetime.datetime
    full_name: None | str | Unset = UNSET
    username: None | str | Unset = UNSET
    profile_image: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        user_id = self.user_id

        organization_id = self.organization_id

        email = self.email

        role = self.role.to_dict()

        status = self.status.to_dict()

        joined_at = self.joined_at.isoformat()

        created_at = self.created_at.isoformat()

        last_modified_at = self.last_modified_at.isoformat()

        full_name: None | str | Unset
        if isinstance(self.full_name, Unset):
            full_name = UNSET
        else:
            full_name = self.full_name

        username: None | str | Unset
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

        profile_image: None | str | Unset
        if isinstance(self.profile_image, Unset):
            profile_image = UNSET
        else:
            profile_image = self.profile_image

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "user_id": user_id,
                "organization_id": organization_id,
                "email": email,
                "role": role,
                "status": status,
                "joined_at": joined_at,
                "created_at": created_at,
                "last_modified_at": last_modified_at,
            }
        )
        if full_name is not UNSET:
            field_dict["full_name"] = full_name
        if username is not UNSET:
            field_dict["username"] = username
        if profile_image is not UNSET:
            field_dict["profile_image"] = profile_image

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.role_info import RoleInfo
        from ..models.status_info import StatusInfo

        d = dict(src_dict)
        id = d.pop("id")

        user_id = d.pop("user_id")

        organization_id = d.pop("organization_id")

        email = d.pop("email")

        role = RoleInfo.from_dict(d.pop("role"))

        status = StatusInfo.from_dict(d.pop("status"))

        joined_at = isoparse(d.pop("joined_at"))

        created_at = isoparse(d.pop("created_at"))

        last_modified_at = isoparse(d.pop("last_modified_at"))

        def _parse_full_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        full_name = _parse_full_name(d.pop("full_name", UNSET))

        def _parse_username(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        username = _parse_username(d.pop("username", UNSET))

        def _parse_profile_image(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        profile_image = _parse_profile_image(d.pop("profile_image", UNSET))

        member_response = cls(
            id=id,
            user_id=user_id,
            organization_id=organization_id,
            email=email,
            role=role,
            status=status,
            joined_at=joined_at,
            created_at=created_at,
            last_modified_at=last_modified_at,
            full_name=full_name,
            username=username,
            profile_image=profile_image,
        )

        member_response.additional_properties = d
        return member_response

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
