from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeviceSessionResponse")


@_attrs_define
class DeviceSessionResponse:
    """Response schema for device session.

    Attributes:
        id (str): Device session ID with dsess_ prefix
        device_id (str):
        is_active (bool):
        last_used_at (datetime.datetime):
        created_at (datetime.datetime):
        device_name (None | str | Unset):
        platform (None | str | Unset):
        operating_system (None | str | Unset):
        location (None | str | Unset):
    """

    id: str
    device_id: str
    is_active: bool
    last_used_at: datetime.datetime
    created_at: datetime.datetime
    device_name: None | str | Unset = UNSET
    platform: None | str | Unset = UNSET
    operating_system: None | str | Unset = UNSET
    location: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        device_id = self.device_id

        is_active = self.is_active

        last_used_at = self.last_used_at.isoformat()

        created_at = self.created_at.isoformat()

        device_name: None | str | Unset
        if isinstance(self.device_name, Unset):
            device_name = UNSET
        else:
            device_name = self.device_name

        platform: None | str | Unset
        if isinstance(self.platform, Unset):
            platform = UNSET
        else:
            platform = self.platform

        operating_system: None | str | Unset
        if isinstance(self.operating_system, Unset):
            operating_system = UNSET
        else:
            operating_system = self.operating_system

        location: None | str | Unset
        if isinstance(self.location, Unset):
            location = UNSET
        else:
            location = self.location

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "device_id": device_id,
                "is_active": is_active,
                "last_used_at": last_used_at,
                "created_at": created_at,
            }
        )
        if device_name is not UNSET:
            field_dict["device_name"] = device_name
        if platform is not UNSET:
            field_dict["platform"] = platform
        if operating_system is not UNSET:
            field_dict["operating_system"] = operating_system
        if location is not UNSET:
            field_dict["location"] = location

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        device_id = d.pop("device_id")

        is_active = d.pop("is_active")

        last_used_at = isoparse(d.pop("last_used_at"))

        created_at = isoparse(d.pop("created_at"))

        def _parse_device_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        device_name = _parse_device_name(d.pop("device_name", UNSET))

        def _parse_platform(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        platform = _parse_platform(d.pop("platform", UNSET))

        def _parse_operating_system(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        operating_system = _parse_operating_system(d.pop("operating_system", UNSET))

        def _parse_location(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        location = _parse_location(d.pop("location", UNSET))

        device_session_response = cls(
            id=id,
            device_id=device_id,
            is_active=is_active,
            last_used_at=last_used_at,
            created_at=created_at,
            device_name=device_name,
            platform=platform,
            operating_system=operating_system,
            location=location,
        )

        device_session_response.additional_properties = d
        return device_session_response

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
