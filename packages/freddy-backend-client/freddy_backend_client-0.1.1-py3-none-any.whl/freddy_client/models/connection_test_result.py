from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConnectionTestResult")


@_attrs_define
class ConnectionTestResult:
    """Result of MCP connection test.

    Attributes:
        success (bool): Whether connection was successful
        status (str): Connection status
        message (str): Result message
        available_tools (list[str] | None | Unset): List of available tool names
    """

    success: bool
    status: str
    message: str
    available_tools: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        status = self.status

        message = self.message

        available_tools: list[str] | None | Unset
        if isinstance(self.available_tools, Unset):
            available_tools = UNSET
        elif isinstance(self.available_tools, list):
            available_tools = self.available_tools

        else:
            available_tools = self.available_tools

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "success": success,
                "status": status,
                "message": message,
            }
        )
        if available_tools is not UNSET:
            field_dict["available_tools"] = available_tools

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = d.pop("success")

        status = d.pop("status")

        message = d.pop("message")

        def _parse_available_tools(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                available_tools_type_0 = cast(list[str], data)

                return available_tools_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        available_tools = _parse_available_tools(d.pop("available_tools", UNSET))

        connection_test_result = cls(
            success=success,
            status=status,
            message=message,
            available_tools=available_tools,
        )

        connection_test_result.additional_properties = d
        return connection_test_result

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
