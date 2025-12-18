from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserProfileResponse")


@_attrs_define
class UserProfileResponse:
    """Schema for user profile response with detailed information.

    Attributes:
        id (str): User ID with usr_ prefix
        email (str):
        is_active (bool):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        username (None | str | Unset):
        full_name (None | str | Unset):
        first_name (None | str | Unset):
        last_name (None | str | Unset):
        birthday (datetime.date | None | Unset):
        profile_image (None | str | Unset):
        timezone (None | str | Unset):
        country_id (None | str | Unset):
        post_code (None | str | Unset):
        gender (None | str | Unset):
        last_verified (datetime.datetime | None | Unset):
        last_login (datetime.datetime | None | Unset):
    """

    id: str
    email: str
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    username: None | str | Unset = UNSET
    full_name: None | str | Unset = UNSET
    first_name: None | str | Unset = UNSET
    last_name: None | str | Unset = UNSET
    birthday: datetime.date | None | Unset = UNSET
    profile_image: None | str | Unset = UNSET
    timezone: None | str | Unset = UNSET
    country_id: None | str | Unset = UNSET
    post_code: None | str | Unset = UNSET
    gender: None | str | Unset = UNSET
    last_verified: datetime.datetime | None | Unset = UNSET
    last_login: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        is_active = self.is_active

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        username: None | str | Unset
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

        full_name: None | str | Unset
        if isinstance(self.full_name, Unset):
            full_name = UNSET
        else:
            full_name = self.full_name

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

        birthday: None | str | Unset
        if isinstance(self.birthday, Unset):
            birthday = UNSET
        elif isinstance(self.birthday, datetime.date):
            birthday = self.birthday.isoformat()
        else:
            birthday = self.birthday

        profile_image: None | str | Unset
        if isinstance(self.profile_image, Unset):
            profile_image = UNSET
        else:
            profile_image = self.profile_image

        timezone: None | str | Unset
        if isinstance(self.timezone, Unset):
            timezone = UNSET
        else:
            timezone = self.timezone

        country_id: None | str | Unset
        if isinstance(self.country_id, Unset):
            country_id = UNSET
        else:
            country_id = self.country_id

        post_code: None | str | Unset
        if isinstance(self.post_code, Unset):
            post_code = UNSET
        else:
            post_code = self.post_code

        gender: None | str | Unset
        if isinstance(self.gender, Unset):
            gender = UNSET
        else:
            gender = self.gender

        last_verified: None | str | Unset
        if isinstance(self.last_verified, Unset):
            last_verified = UNSET
        elif isinstance(self.last_verified, datetime.datetime):
            last_verified = self.last_verified.isoformat()
        else:
            last_verified = self.last_verified

        last_login: None | str | Unset
        if isinstance(self.last_login, Unset):
            last_login = UNSET
        elif isinstance(self.last_login, datetime.datetime):
            last_login = self.last_login.isoformat()
        else:
            last_login = self.last_login

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "email": email,
                "is_active": is_active,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if username is not UNSET:
            field_dict["username"] = username
        if full_name is not UNSET:
            field_dict["full_name"] = full_name
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if birthday is not UNSET:
            field_dict["birthday"] = birthday
        if profile_image is not UNSET:
            field_dict["profile_image"] = profile_image
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if country_id is not UNSET:
            field_dict["country_id"] = country_id
        if post_code is not UNSET:
            field_dict["post_code"] = post_code
        if gender is not UNSET:
            field_dict["gender"] = gender
        if last_verified is not UNSET:
            field_dict["last_verified"] = last_verified
        if last_login is not UNSET:
            field_dict["last_login"] = last_login

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        email = d.pop("email")

        is_active = d.pop("is_active")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_username(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        username = _parse_username(d.pop("username", UNSET))

        def _parse_full_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        full_name = _parse_full_name(d.pop("full_name", UNSET))

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

        def _parse_birthday(data: object) -> datetime.date | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                birthday_type_0 = isoparse(data).date()

                return birthday_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.date | None | Unset, data)

        birthday = _parse_birthday(d.pop("birthday", UNSET))

        def _parse_profile_image(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        profile_image = _parse_profile_image(d.pop("profile_image", UNSET))

        def _parse_timezone(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        timezone = _parse_timezone(d.pop("timezone", UNSET))

        def _parse_country_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        country_id = _parse_country_id(d.pop("country_id", UNSET))

        def _parse_post_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        post_code = _parse_post_code(d.pop("post_code", UNSET))

        def _parse_gender(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        gender = _parse_gender(d.pop("gender", UNSET))

        def _parse_last_verified(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_verified_type_0 = isoparse(data)

                return last_verified_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_verified = _parse_last_verified(d.pop("last_verified", UNSET))

        def _parse_last_login(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_login_type_0 = isoparse(data)

                return last_login_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_login = _parse_last_login(d.pop("last_login", UNSET))

        user_profile_response = cls(
            id=id,
            email=email,
            is_active=is_active,
            created_at=created_at,
            updated_at=updated_at,
            username=username,
            full_name=full_name,
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
            profile_image=profile_image,
            timezone=timezone,
            country_id=country_id,
            post_code=post_code,
            gender=gender,
            last_verified=last_verified,
            last_login=last_login,
        )

        user_profile_response.additional_properties = d
        return user_profile_response

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
