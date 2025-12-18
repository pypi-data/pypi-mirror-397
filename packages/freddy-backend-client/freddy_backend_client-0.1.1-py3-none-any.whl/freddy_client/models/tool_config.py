from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ToolConfig")


@_attrs_define
class ToolConfig:
    """Tool configuration for enabling MCP tools.

    Attributes:
        type_ (str): Tool type (e.g., 'personalConnector')
        configuration_ids (list[str] | None | Unset): Optional list of specific configuration IDs to use
    """

    type_: str
    configuration_ids: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        configuration_ids: list[str] | None | Unset
        if isinstance(self.configuration_ids, Unset):
            configuration_ids = UNSET
        elif isinstance(self.configuration_ids, list):
            configuration_ids = self.configuration_ids

        else:
            configuration_ids = self.configuration_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if configuration_ids is not UNSET:
            field_dict["configuration_ids"] = configuration_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = d.pop("type")

        def _parse_configuration_ids(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                configuration_ids_type_0 = cast(list[str], data)

                return configuration_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        configuration_ids = _parse_configuration_ids(d.pop("configuration_ids", UNSET))

        tool_config = cls(
            type_=type_,
            configuration_ids=configuration_ids,
        )

        tool_config.additional_properties = d
        return tool_config

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
