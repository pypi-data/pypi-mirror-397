from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AssistantStandardResponse")


@_attrs_define
class AssistantStandardResponse:
    """Standard assistant response with model configuration.

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
        default_model_key (str): Default model key
        context_strategy (str): Context strategy
        description (None | str | Unset): Assistant description
        icon_id (None | str | Unset): Icon ID
        icon_url (None | str | Unset): Icon URL
        icon_type (None | str | Unset): Icon type (deprecated)
        icon_data (None | str | Unset): Icon data (deprecated)
        user_access_level (None | str | Unset): User's access level: owner, edit, view
        allowed_model_providers (list[str] | None | Unset): Allowed model providers
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
    default_model_key: str
    context_strategy: str
    description: None | str | Unset = UNSET
    icon_id: None | str | Unset = UNSET
    icon_url: None | str | Unset = UNSET
    icon_type: None | str | Unset = UNSET
    icon_data: None | str | Unset = UNSET
    user_access_level: None | str | Unset = UNSET
    allowed_model_providers: list[str] | None | Unset = UNSET
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

        default_model_key = self.default_model_key

        context_strategy = self.context_strategy

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

        allowed_model_providers: list[str] | None | Unset
        if isinstance(self.allowed_model_providers, Unset):
            allowed_model_providers = UNSET
        elif isinstance(self.allowed_model_providers, list):
            allowed_model_providers = self.allowed_model_providers

        else:
            allowed_model_providers = self.allowed_model_providers

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
                "default_model_key": default_model_key,
                "context_strategy": context_strategy,
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
        if allowed_model_providers is not UNSET:
            field_dict["allowed_model_providers"] = allowed_model_providers

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

        default_model_key = d.pop("default_model_key")

        context_strategy = d.pop("context_strategy")

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

        def _parse_allowed_model_providers(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                allowed_model_providers_type_0 = cast(list[str], data)

                return allowed_model_providers_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        allowed_model_providers = _parse_allowed_model_providers(
            d.pop("allowed_model_providers", UNSET)
        )

        assistant_standard_response = cls(
            id=id,
            name=name,
            is_default=is_default,
            created_at=created_at,
            updated_at=updated_at,
            access_mode=access_mode,
            api_enabled=api_enabled,
            is_active=is_active,
            temperature=temperature,
            default_model_key=default_model_key,
            context_strategy=context_strategy,
            description=description,
            icon_id=icon_id,
            icon_url=icon_url,
            icon_type=icon_type,
            icon_data=icon_data,
            user_access_level=user_access_level,
            allowed_model_providers=allowed_model_providers,
        )

        assistant_standard_response.additional_properties = d
        return assistant_standard_response

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
