from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.system_tool_response import SystemToolResponse


T = TypeVar("T", bound="SystemToolsListResponse")


@_attrs_define
class SystemToolsListResponse:
    """Response schema for list of system tools.

    Attributes:
        tools (list[SystemToolResponse]): List of system tool entries
        total_count (int): Total number of tools returned
    """

    tools: list[SystemToolResponse]
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tools = []
        for tools_item_data in self.tools:
            tools_item = tools_item_data.to_dict()
            tools.append(tools_item)

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tools": tools,
                "total_count": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.system_tool_response import SystemToolResponse

        d = dict(src_dict)
        tools = []
        _tools = d.pop("tools")
        for tools_item_data in _tools:
            tools_item = SystemToolResponse.from_dict(tools_item_data)

            tools.append(tools_item)

        total_count = d.pop("total_count")

        system_tools_list_response = cls(
            tools=tools,
            total_count=total_count,
        )

        system_tools_list_response.additional_properties = d
        return system_tools_list_response

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
