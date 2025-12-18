from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateProfileRequest")


@_attrs_define
class UpdateProfileRequest:
    """Request schema for updating user profile.

    Attributes:
        username (None | str | Unset): Username
        first_name (None | str | Unset): First name
        last_name (None | str | Unset): Last name
        full_name (None | str | Unset): Full name
        birthday (datetime.date | None | Unset): Date of birth
        gender (None | str | Unset): Gender
        profile_image (None | str | Unset): Profile image URL
        timezone (None | str | Unset): Timezone
        country_id (None | str | Unset): Country ID (country_ prefix)
        post_code (None | str | Unset): Postal code
    """

    username: None | str | Unset = UNSET
    first_name: None | str | Unset = UNSET
    last_name: None | str | Unset = UNSET
    full_name: None | str | Unset = UNSET
    birthday: datetime.date | None | Unset = UNSET
    gender: None | str | Unset = UNSET
    profile_image: None | str | Unset = UNSET
    timezone: None | str | Unset = UNSET
    country_id: None | str | Unset = UNSET
    post_code: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username: None | str | Unset
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

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

        full_name: None | str | Unset
        if isinstance(self.full_name, Unset):
            full_name = UNSET
        else:
            full_name = self.full_name

        birthday: None | str | Unset
        if isinstance(self.birthday, Unset):
            birthday = UNSET
        elif isinstance(self.birthday, datetime.date):
            birthday = self.birthday.isoformat()
        else:
            birthday = self.birthday

        gender: None | str | Unset
        if isinstance(self.gender, Unset):
            gender = UNSET
        else:
            gender = self.gender

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if username is not UNSET:
            field_dict["username"] = username
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if full_name is not UNSET:
            field_dict["full_name"] = full_name
        if birthday is not UNSET:
            field_dict["birthday"] = birthday
        if gender is not UNSET:
            field_dict["gender"] = gender
        if profile_image is not UNSET:
            field_dict["profile_image"] = profile_image
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if country_id is not UNSET:
            field_dict["country_id"] = country_id
        if post_code is not UNSET:
            field_dict["post_code"] = post_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_username(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        username = _parse_username(d.pop("username", UNSET))

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

        def _parse_full_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        full_name = _parse_full_name(d.pop("full_name", UNSET))

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

        def _parse_gender(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        gender = _parse_gender(d.pop("gender", UNSET))

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

        update_profile_request = cls(
            username=username,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            birthday=birthday,
            gender=gender,
            profile_image=profile_image,
            timezone=timezone,
            country_id=country_id,
            post_code=post_code,
        )

        update_profile_request.additional_properties = d
        return update_profile_request

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
