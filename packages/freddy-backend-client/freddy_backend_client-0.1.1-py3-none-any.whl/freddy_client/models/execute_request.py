from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.execution_return_mode import ExecutionReturnMode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.execute_request_parameters import ExecuteRequestParameters


T = TypeVar("T", bound="ExecuteRequest")


@_attrs_define
class ExecuteRequest:
    """Schema for execute automation request.

    Attributes:
        parameters (ExecuteRequestParameters | Unset): Execution parameters
        return_mode (ExecutionReturnMode | Unset): Execution return mode enum.
    """

    parameters: ExecuteRequestParameters | Unset = UNSET
    return_mode: ExecutionReturnMode | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        parameters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters.to_dict()

        return_mode: str | Unset = UNSET
        if not isinstance(self.return_mode, Unset):
            return_mode = self.return_mode.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if return_mode is not UNSET:
            field_dict["return_mode"] = return_mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.execute_request_parameters import ExecuteRequestParameters

        d = dict(src_dict)
        _parameters = d.pop("parameters", UNSET)
        parameters: ExecuteRequestParameters | Unset
        if isinstance(_parameters, Unset):
            parameters = UNSET
        else:
            parameters = ExecuteRequestParameters.from_dict(_parameters)

        _return_mode = d.pop("return_mode", UNSET)
        return_mode: ExecutionReturnMode | Unset
        if isinstance(_return_mode, Unset):
            return_mode = UNSET
        else:
            return_mode = ExecutionReturnMode(_return_mode)

        execute_request = cls(
            parameters=parameters,
            return_mode=return_mode,
        )

        execute_request.additional_properties = d
        return execute_request

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
