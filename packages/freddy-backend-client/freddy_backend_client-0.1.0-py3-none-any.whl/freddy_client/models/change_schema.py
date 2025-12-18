from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChangeSchema")


@_attrs_define
class ChangeSchema:
    """Schema for a single change in audit log.

    Attributes:
        field (str): Field that changed
        old_value (Any | Unset): Old value
        new_value (Any | Unset): New value
    """

    field: str
    old_value: Any | Unset = UNSET
    new_value: Any | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field = self.field

        old_value = self.old_value

        new_value = self.new_value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field": field,
            }
        )
        if old_value is not UNSET:
            field_dict["old_value"] = old_value
        if new_value is not UNSET:
            field_dict["new_value"] = new_value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field = d.pop("field")

        old_value = d.pop("old_value", UNSET)

        new_value = d.pop("new_value", UNSET)

        change_schema = cls(
            field=field,
            old_value=old_value,
            new_value=new_value,
        )

        change_schema.additional_properties = d
        return change_schema

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
