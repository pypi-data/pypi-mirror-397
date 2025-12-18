from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.api_key_create_response import ApiKeyCreateResponse


T = TypeVar("T", bound="ApiKeyRotateResponse")


@_attrs_define
class ApiKeyRotateResponse:
    """Response schema for API key rotation (includes new raw key ONCE).

    Attributes:
        success (bool): Whether rotation succeeded
        message (str): Rotation result message
        old_key_id (str): ID of the old (deleted) key
        new_key (ApiKeyCreateResponse): Response schema for API key creation (includes raw key ONCE).
    """

    success: bool
    message: str
    old_key_id: str
    new_key: ApiKeyCreateResponse
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        message = self.message

        old_key_id = self.old_key_id

        new_key = self.new_key.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "success": success,
                "message": message,
                "old_key_id": old_key_id,
                "new_key": new_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_key_create_response import ApiKeyCreateResponse

        d = dict(src_dict)
        success = d.pop("success")

        message = d.pop("message")

        old_key_id = d.pop("old_key_id")

        new_key = ApiKeyCreateResponse.from_dict(d.pop("new_key"))

        api_key_rotate_response = cls(
            success=success,
            message=message,
            old_key_id=old_key_id,
            new_key=new_key,
        )

        api_key_rotate_response.additional_properties = d
        return api_key_rotate_response

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
