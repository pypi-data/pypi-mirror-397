from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.reasoning_level_info import ReasoningLevelInfo


T = TypeVar("T", bound="ReasoningLevelsResponse")


@_attrs_define
class ReasoningLevelsResponse:
    """Response schema for available reasoning levels.

    Attributes:
        reasoning_levels (list[ReasoningLevelInfo]): List of available reasoning effort levels
        success (bool | Unset): Request success status Default: True.
    """

    reasoning_levels: list[ReasoningLevelInfo]
    success: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reasoning_levels = []
        for reasoning_levels_item_data in self.reasoning_levels:
            reasoning_levels_item = reasoning_levels_item_data.to_dict()
            reasoning_levels.append(reasoning_levels_item)

        success = self.success

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "reasoning_levels": reasoning_levels,
            }
        )
        if success is not UNSET:
            field_dict["success"] = success

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.reasoning_level_info import ReasoningLevelInfo

        d = dict(src_dict)
        reasoning_levels = []
        _reasoning_levels = d.pop("reasoning_levels")
        for reasoning_levels_item_data in _reasoning_levels:
            reasoning_levels_item = ReasoningLevelInfo.from_dict(
                reasoning_levels_item_data
            )

            reasoning_levels.append(reasoning_levels_item)

        success = d.pop("success", UNSET)

        reasoning_levels_response = cls(
            reasoning_levels=reasoning_levels,
            success=success,
        )

        reasoning_levels_response.additional_properties = d
        return reasoning_levels_response

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
