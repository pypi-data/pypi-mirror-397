from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RetryProcessingRequest")


@_attrs_define
class RetryProcessingRequest:
    """Request schema for retrying failed processing.

    Attributes:
        reset_error (bool | Unset): Clear previous error message Default: True.
    """

    reset_error: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reset_error = self.reset_error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if reset_error is not UNSET:
            field_dict["reset_error"] = reset_error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        reset_error = d.pop("reset_error", UNSET)

        retry_processing_request = cls(
            reset_error=reset_error,
        )

        retry_processing_request.additional_properties = d
        return retry_processing_request

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
