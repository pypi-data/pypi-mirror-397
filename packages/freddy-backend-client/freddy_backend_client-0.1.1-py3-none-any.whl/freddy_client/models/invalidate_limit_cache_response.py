from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.invalidate_limit_cache_response_caches_cleared import (
        InvalidateLimitCacheResponseCachesCleared,
    )


T = TypeVar("T", bound="InvalidateLimitCacheResponse")


@_attrs_define
class InvalidateLimitCacheResponse:
    """Response schema for cache invalidation.

    Attributes:
        success (bool): Whether invalidation was successful
        message (str): Status message
        caches_cleared (InvalidateLimitCacheResponseCachesCleared): Count of caches cleared by type
    """

    success: bool
    message: str
    caches_cleared: InvalidateLimitCacheResponseCachesCleared
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        message = self.message

        caches_cleared = self.caches_cleared.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "success": success,
                "message": message,
                "caches_cleared": caches_cleared,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.invalidate_limit_cache_response_caches_cleared import (
            InvalidateLimitCacheResponseCachesCleared,
        )

        d = dict(src_dict)
        success = d.pop("success")

        message = d.pop("message")

        caches_cleared = InvalidateLimitCacheResponseCachesCleared.from_dict(
            d.pop("caches_cleared")
        )

        invalidate_limit_cache_response = cls(
            success=success,
            message=message,
            caches_cleared=caches_cleared,
        )

        invalidate_limit_cache_response.additional_properties = d
        return invalidate_limit_cache_response

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
