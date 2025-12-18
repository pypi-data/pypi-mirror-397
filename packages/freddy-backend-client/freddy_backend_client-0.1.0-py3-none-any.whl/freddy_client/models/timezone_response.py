from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="TimezoneResponse")


@_attrs_define
class TimezoneResponse:
    """Response schema for timezone data.

    Attributes:
        id (str): Timezone ID with tz_ prefix
        name (str): IANA timezone name (e.g., America/New_York)
        display_name (str): User-friendly name (e.g., Eastern Time (US & Canada))
        offset (str): UTC offset (e.g., -05:00, +01:00)
        offset_minutes (int): Offset in minutes from UTC
        is_active (bool): Whether timezone is active
        order (int): Display order
        created_at (datetime.datetime): Creation timestamp
        updated_at (datetime.datetime): Last update timestamp
        country_code (None | str | Unset): ISO 3166-1 alpha-2 country code
    """

    id: str
    name: str
    display_name: str
    offset: str
    offset_minutes: int
    is_active: bool
    order: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    country_code: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        display_name = self.display_name

        offset = self.offset

        offset_minutes = self.offset_minutes

        is_active = self.is_active

        order = self.order

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        country_code: None | str | Unset
        if isinstance(self.country_code, Unset):
            country_code = UNSET
        else:
            country_code = self.country_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "display_name": display_name,
                "offset": offset,
                "offset_minutes": offset_minutes,
                "is_active": is_active,
                "order": order,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if country_code is not UNSET:
            field_dict["country_code"] = country_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        display_name = d.pop("display_name")

        offset = d.pop("offset")

        offset_minutes = d.pop("offset_minutes")

        is_active = d.pop("is_active")

        order = d.pop("order")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_country_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        country_code = _parse_country_code(d.pop("country_code", UNSET))

        timezone_response = cls(
            id=id,
            name=name,
            display_name=display_name,
            offset=offset,
            offset_minutes=offset_minutes,
            is_active=is_active,
            order=order,
            created_at=created_at,
            updated_at=updated_at,
            country_code=country_code,
        )

        timezone_response.additional_properties = d
        return timezone_response

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
