from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="OutputModeInfo")


@_attrs_define
class OutputModeInfo:
    """Information about an output mode.

    Attributes:
        mode (str): Output mode identifier
        description (str): Description of the output mode
        is_default (bool): Whether this is the default mode
    """

    mode: str
    description: str
    is_default: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mode = self.mode

        description = self.description

        is_default = self.is_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "mode": mode,
                "description": description,
                "is_default": is_default,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        mode = d.pop("mode")

        description = d.pop("description")

        is_default = d.pop("is_default")

        output_mode_info = cls(
            mode=mode,
            description=description,
            is_default=is_default,
        )

        output_mode_info.additional_properties = d
        return output_mode_info

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
