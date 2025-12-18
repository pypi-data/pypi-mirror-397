from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChangeDetail")


@_attrs_define
class ChangeDetail:
    """Schema for individual change detail.

    Attributes:
        field (str): Field that was changed
        old_value (None | str | Unset): Previous value
        new_value (None | str | Unset): New value
    """

    field: str
    old_value: None | str | Unset = UNSET
    new_value: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field = self.field

        old_value: None | str | Unset
        if isinstance(self.old_value, Unset):
            old_value = UNSET
        else:
            old_value = self.old_value

        new_value: None | str | Unset
        if isinstance(self.new_value, Unset):
            new_value = UNSET
        else:
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

        def _parse_old_value(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        old_value = _parse_old_value(d.pop("old_value", UNSET))

        def _parse_new_value(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        new_value = _parse_new_value(d.pop("new_value", UNSET))

        change_detail = cls(
            field=field,
            old_value=old_value,
            new_value=new_value,
        )

        change_detail.additional_properties = d
        return change_detail

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
