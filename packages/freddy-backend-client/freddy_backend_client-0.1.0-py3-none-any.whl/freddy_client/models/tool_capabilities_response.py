from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.model_compatibility_response import ModelCompatibilityResponse
    from ..models.tool_parameter_response import ToolParameterResponse


T = TypeVar("T", bound="ToolCapabilitiesResponse")


@_attrs_define
class ToolCapabilitiesResponse:
    """Tool capabilities and configuration options.

    Attributes:
        modes (list[str]): Available configuration modes (e.g., ['on', 'off', 'auto'])
        parameters (list[ToolParameterResponse]): Available configuration parameters for this tool
        model_compatibility (ModelCompatibilityResponse): Model type compatibility configuration.
    """

    modes: list[str]
    parameters: list[ToolParameterResponse]
    model_compatibility: ModelCompatibilityResponse
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        modes = self.modes

        parameters = []
        for parameters_item_data in self.parameters:
            parameters_item = parameters_item_data.to_dict()
            parameters.append(parameters_item)

        model_compatibility = self.model_compatibility.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "modes": modes,
                "parameters": parameters,
                "modelCompatibility": model_compatibility,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_compatibility_response import ModelCompatibilityResponse
        from ..models.tool_parameter_response import ToolParameterResponse

        d = dict(src_dict)
        modes = cast(list[str], d.pop("modes"))

        parameters = []
        _parameters = d.pop("parameters")
        for parameters_item_data in _parameters:
            parameters_item = ToolParameterResponse.from_dict(parameters_item_data)

            parameters.append(parameters_item)

        model_compatibility = ModelCompatibilityResponse.from_dict(
            d.pop("modelCompatibility")
        )

        tool_capabilities_response = cls(
            modes=modes,
            parameters=parameters,
            model_compatibility=model_compatibility,
        )

        tool_capabilities_response.additional_properties = d
        return tool_capabilities_response

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
