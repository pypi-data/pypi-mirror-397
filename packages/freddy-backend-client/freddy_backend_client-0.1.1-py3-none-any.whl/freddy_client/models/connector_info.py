from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConnectorInfo")


@_attrs_define
class ConnectorInfo:
    """Available connector information.

    Attributes:
        type_ (str): Connector type identifier
        name (str): Display name
        description (str): Connector description
        icon_id (None | str | Unset): Icon ID
        icon_url (None | str | Unset): Icon URL
        requires_oauth (bool | Unset): Whether OAuth is required Default: True.
    """

    type_: str
    name: str
    description: str
    icon_id: None | str | Unset = UNSET
    icon_url: None | str | Unset = UNSET
    requires_oauth: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        name = self.name

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

        requires_oauth = self.requires_oauth

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "name": name,
                "description": description,
            }
        )
        if icon_id is not UNSET:
            field_dict["icon_id"] = icon_id
        if icon_url is not UNSET:
            field_dict["icon_url"] = icon_url
        if requires_oauth is not UNSET:
            field_dict["requires_oauth"] = requires_oauth

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = d.pop("type")

        name = d.pop("name")

        description = d.pop("description")

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

        requires_oauth = d.pop("requires_oauth", UNSET)

        connector_info = cls(
            type_=type_,
            name=name,
            description=description,
            icon_id=icon_id,
            icon_url=icon_url,
            requires_oauth=requires_oauth,
        )

        connector_info.additional_properties = d
        return connector_info

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
