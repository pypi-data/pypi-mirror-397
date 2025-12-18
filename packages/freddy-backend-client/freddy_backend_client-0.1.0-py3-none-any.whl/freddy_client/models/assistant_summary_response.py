from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AssistantSummaryResponse")


@_attrs_define
class AssistantSummaryResponse:
    """Minimal assistant response for list views.

    Attributes:
        id (str): Assistant ID
        name (str): Assistant name
        is_default (bool): Is default assistant
        created_at (int): Creation timestamp
        updated_at (int): Update timestamp
        access_mode (str): Access mode
        api_enabled (bool): API enabled
        is_active (bool): Is active
        temperature (float): Temperature
        description (None | str | Unset): Assistant description
        icon_id (None | str | Unset): Icon ID
        icon_url (None | str | Unset): Icon URL
        icon_type (None | str | Unset): Icon type (deprecated)
        icon_data (None | str | Unset): Icon data (deprecated)
        user_access_level (None | str | Unset): User's access level: owner, edit, view
    """

    id: str
    name: str
    is_default: bool
    created_at: int
    updated_at: int
    access_mode: str
    api_enabled: bool
    is_active: bool
    temperature: float
    description: None | str | Unset = UNSET
    icon_id: None | str | Unset = UNSET
    icon_url: None | str | Unset = UNSET
    icon_type: None | str | Unset = UNSET
    icon_data: None | str | Unset = UNSET
    user_access_level: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        is_default = self.is_default

        created_at = self.created_at

        updated_at = self.updated_at

        access_mode = self.access_mode

        api_enabled = self.api_enabled

        is_active = self.is_active

        temperature = self.temperature

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        icon_id: None | str | Unset
        if isinstance(self.icon_id, Unset):
            icon_id = UNSET
        else:
            icon_id = self.icon_id

        icon_url: None | str | Unset
        if isinstance(self.icon_url, Unset):
            icon_url = UNSET
        else:
            icon_url = self.icon_url

        icon_type: None | str | Unset
        if isinstance(self.icon_type, Unset):
            icon_type = UNSET
        else:
            icon_type = self.icon_type

        icon_data: None | str | Unset
        if isinstance(self.icon_data, Unset):
            icon_data = UNSET
        else:
            icon_data = self.icon_data

        user_access_level: None | str | Unset
        if isinstance(self.user_access_level, Unset):
            user_access_level = UNSET
        else:
            user_access_level = self.user_access_level

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "is_default": is_default,
                "created_at": created_at,
                "updated_at": updated_at,
                "access_mode": access_mode,
                "api_enabled": api_enabled,
                "is_active": is_active,
                "temperature": temperature,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if icon_id is not UNSET:
            field_dict["icon_id"] = icon_id
        if icon_url is not UNSET:
            field_dict["icon_url"] = icon_url
        if icon_type is not UNSET:
            field_dict["icon_type"] = icon_type
        if icon_data is not UNSET:
            field_dict["icon_data"] = icon_data
        if user_access_level is not UNSET:
            field_dict["user_access_level"] = user_access_level

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        is_default = d.pop("is_default")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        access_mode = d.pop("access_mode")

        api_enabled = d.pop("api_enabled")

        is_active = d.pop("is_active")

        temperature = d.pop("temperature")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_icon_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        icon_id = _parse_icon_id(d.pop("icon_id", UNSET))

        def _parse_icon_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        icon_url = _parse_icon_url(d.pop("icon_url", UNSET))

        def _parse_icon_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        icon_type = _parse_icon_type(d.pop("icon_type", UNSET))

        def _parse_icon_data(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        icon_data = _parse_icon_data(d.pop("icon_data", UNSET))

        def _parse_user_access_level(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_access_level = _parse_user_access_level(d.pop("user_access_level", UNSET))

        assistant_summary_response = cls(
            id=id,
            name=name,
            is_default=is_default,
            created_at=created_at,
            updated_at=updated_at,
            access_mode=access_mode,
            api_enabled=api_enabled,
            is_active=is_active,
            temperature=temperature,
            description=description,
            icon_id=icon_id,
            icon_url=icon_url,
            icon_type=icon_type,
            icon_data=icon_data,
            user_access_level=user_access_level,
        )

        assistant_summary_response.additional_properties = d
        return assistant_summary_response

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
