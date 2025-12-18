from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.streamline_execution_response import StreamlineExecutionResponse


T = TypeVar("T", bound="StreamlineExecutionListResponse")


@_attrs_define
class StreamlineExecutionListResponse:
    """Schema for execution list response.

    Attributes:
        executions (list[StreamlineExecutionResponse]):
    """

    executions: list[StreamlineExecutionResponse]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        executions = []
        for executions_item_data in self.executions:
            executions_item = executions_item_data.to_dict()
            executions.append(executions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "executions": executions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.streamline_execution_response import StreamlineExecutionResponse

        d = dict(src_dict)
        executions = []
        _executions = d.pop("executions")
        for executions_item_data in _executions:
            executions_item = StreamlineExecutionResponse.from_dict(
                executions_item_data
            )

            executions.append(executions_item)

        streamline_execution_list_response = cls(
            executions=executions,
        )

        streamline_execution_list_response.additional_properties = d
        return streamline_execution_list_response

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
