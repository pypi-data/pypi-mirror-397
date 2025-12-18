from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ReasoningLevelInfo")


@_attrs_define
class ReasoningLevelInfo:
    """Information about a reasoning effort level.

    Attributes:
        level (str): Reasoning effort level identifier
        description (str): Description of the reasoning level
        is_default (bool): Whether this is the default level
    """

    level: str
    description: str
    is_default: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        level = self.level

        description = self.description

        is_default = self.is_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "level": level,
                "description": description,
                "is_default": is_default,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        level = d.pop("level")

        description = d.pop("description")

        is_default = d.pop("is_default")

        reasoning_level_info = cls(
            level=level,
            description=description,
            is_default=is_default,
        )

        reasoning_level_info.additional_properties = d
        return reasoning_level_info

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
