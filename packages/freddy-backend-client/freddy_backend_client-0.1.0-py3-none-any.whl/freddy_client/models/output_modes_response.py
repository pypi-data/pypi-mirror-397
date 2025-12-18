from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.output_mode_info import OutputModeInfo


T = TypeVar("T", bound="OutputModesResponse")


@_attrs_define
class OutputModesResponse:
    """Response schema for available output modes.

    Attributes:
        output_modes (list[OutputModeInfo]): List of available output modes
        success (bool | Unset): Request success status Default: True.
    """

    output_modes: list[OutputModeInfo]
    success: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        output_modes = []
        for output_modes_item_data in self.output_modes:
            output_modes_item = output_modes_item_data.to_dict()
            output_modes.append(output_modes_item)

        success = self.success

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "output_modes": output_modes,
            }
        )
        if success is not UNSET:
            field_dict["success"] = success

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.output_mode_info import OutputModeInfo

        d = dict(src_dict)
        output_modes = []
        _output_modes = d.pop("output_modes")
        for output_modes_item_data in _output_modes:
            output_modes_item = OutputModeInfo.from_dict(output_modes_item_data)

            output_modes.append(output_modes_item)

        success = d.pop("success", UNSET)

        output_modes_response = cls(
            output_modes=output_modes,
            success=success,
        )

        output_modes_response.additional_properties = d
        return output_modes_response

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
