from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ToolParameterResponse")


@_attrs_define
class ToolParameterResponse:
    """Parameter structure for tool configuration.

    Attributes:
        name (str): Parameter name (e.g., 'sources', 'outputs')
        type_ (str): Parameter data type (e.g., 'boolean', 'string', 'integer')
        default (Any): Default value for the parameter
        description (str): Description of what the parameter controls
    """

    name: str
    type_: str
    default: Any
    description: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_ = self.type_

        default = self.default

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type_,
                "default": default,
                "description": description,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        type_ = d.pop("type")

        default = d.pop("default")

        description = d.pop("description")

        tool_parameter_response = cls(
            name=name,
            type_=type_,
            default=default,
            description=description,
        )

        tool_parameter_response.additional_properties = d
        return tool_parameter_response

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
