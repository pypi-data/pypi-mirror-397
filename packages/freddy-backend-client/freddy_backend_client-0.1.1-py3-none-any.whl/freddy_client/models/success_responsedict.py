from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.success_responsedict_data import SuccessResponsedictData


T = TypeVar("T", bound="SuccessResponsedict")


@_attrs_define
class SuccessResponsedict:
    """
    Attributes:
        message (str): Human-readable success message
        data (SuccessResponsedictData): Response data
        success (bool | Unset): Whether the request was successful Default: True.
    """

    message: str
    data: SuccessResponsedictData
    success: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        data = self.data.to_dict()

        success = self.success

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
                "data": data,
            }
        )
        if success is not UNSET:
            field_dict["success"] = success

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.success_responsedict_data import SuccessResponsedictData

        d = dict(src_dict)
        message = d.pop("message")

        data = SuccessResponsedictData.from_dict(d.pop("data"))

        success = d.pop("success", UNSET)

        success_responsedict = cls(
            message=message,
            data=data,
            success=success,
        )

        success_responsedict.additional_properties = d
        return success_responsedict

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
