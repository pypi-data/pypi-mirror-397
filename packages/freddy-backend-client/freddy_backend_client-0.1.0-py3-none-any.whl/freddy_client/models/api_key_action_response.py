from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.api_key_response import ApiKeyResponse


T = TypeVar("T", bound="ApiKeyActionResponse")


@_attrs_define
class ApiKeyActionResponse:
    """Response schema for API key actions (activate, deactivate, etc.).

    Attributes:
        success (bool): Whether the action succeeded
        message (str): Action result message
        key (ApiKeyResponse | None | Unset): Updated key details
    """

    success: bool
    message: str
    key: ApiKeyResponse | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.api_key_response import ApiKeyResponse

        success = self.success

        message = self.message

        key: dict[str, Any] | None | Unset
        if isinstance(self.key, Unset):
            key = UNSET
        elif isinstance(self.key, ApiKeyResponse):
            key = self.key.to_dict()
        else:
            key = self.key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "success": success,
                "message": message,
            }
        )
        if key is not UNSET:
            field_dict["key"] = key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_key_response import ApiKeyResponse

        d = dict(src_dict)
        success = d.pop("success")

        message = d.pop("message")

        def _parse_key(data: object) -> ApiKeyResponse | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                key_type_0 = ApiKeyResponse.from_dict(data)

                return key_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ApiKeyResponse | None | Unset, data)

        key = _parse_key(d.pop("key", UNSET))

        api_key_action_response = cls(
            success=success,
            message=message,
            key=key,
        )

        api_key_action_response.additional_properties = d
        return api_key_action_response

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
