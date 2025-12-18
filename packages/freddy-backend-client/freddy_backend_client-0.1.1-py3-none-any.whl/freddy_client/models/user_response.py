from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserResponse")


@_attrs_define
class UserResponse:
    """Schema for user response (without sensitive data).

    Attributes:
        email (str):
        id (str): User ID with usr_ prefix
        is_active (bool):
        last_verified (datetime.datetime | None):
        global_role_id (None | str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        first_name (None | str | Unset):
        last_name (None | str | Unset):
    """

    email: str
    id: str
    is_active: bool
    last_verified: datetime.datetime | None
    global_role_id: None | str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    first_name: None | str | Unset = UNSET
    last_name: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        id = self.id

        is_active = self.is_active

        last_verified: None | str
        if isinstance(self.last_verified, datetime.datetime):
            last_verified = self.last_verified.isoformat()
        else:
            last_verified = self.last_verified

        global_role_id: None | str
        global_role_id = self.global_role_id

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        first_name: None | str | Unset
        if isinstance(self.first_name, Unset):
            first_name = UNSET
        else:
            first_name = self.first_name

        last_name: None | str | Unset
        if isinstance(self.last_name, Unset):
            last_name = UNSET
        else:
            last_name = self.last_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "id": id,
                "is_active": is_active,
                "last_verified": last_verified,
                "global_role_id": global_role_id,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        id = d.pop("id")

        is_active = d.pop("is_active")

        def _parse_last_verified(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_verified_type_0 = isoparse(data)

                return last_verified_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        last_verified = _parse_last_verified(d.pop("last_verified"))

        def _parse_global_role_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        global_role_id = _parse_global_role_id(d.pop("global_role_id"))

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_first_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        first_name = _parse_first_name(d.pop("first_name", UNSET))

        def _parse_last_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        last_name = _parse_last_name(d.pop("last_name", UNSET))

        user_response = cls(
            email=email,
            id=id,
            is_active=is_active,
            last_verified=last_verified,
            global_role_id=global_role_id,
            created_at=created_at,
            updated_at=updated_at,
            first_name=first_name,
            last_name=last_name,
        )

        user_response.additional_properties = d
        return user_response

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
