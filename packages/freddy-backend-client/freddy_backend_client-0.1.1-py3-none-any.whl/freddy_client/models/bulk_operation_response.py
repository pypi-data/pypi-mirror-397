from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.failed_operation import FailedOperation


T = TypeVar("T", bound="BulkOperationResponse")


@_attrs_define
class BulkOperationResponse:
    """Schema for bulk operation response.

    Attributes:
        success_count (int): Number of successful operations
        failure_count (int): Number of failed operations
        failed_operations (list[FailedOperation]): Details of failed operations
    """

    success_count: int
    failure_count: int
    failed_operations: list[FailedOperation]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success_count = self.success_count

        failure_count = self.failure_count

        failed_operations = []
        for failed_operations_item_data in self.failed_operations:
            failed_operations_item = failed_operations_item_data.to_dict()
            failed_operations.append(failed_operations_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "success_count": success_count,
                "failure_count": failure_count,
                "failed_operations": failed_operations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.failed_operation import FailedOperation

        d = dict(src_dict)
        success_count = d.pop("success_count")

        failure_count = d.pop("failure_count")

        failed_operations = []
        _failed_operations = d.pop("failed_operations")
        for failed_operations_item_data in _failed_operations:
            failed_operations_item = FailedOperation.from_dict(
                failed_operations_item_data
            )

            failed_operations.append(failed_operations_item)

        bulk_operation_response = cls(
            success_count=success_count,
            failure_count=failure_count,
            failed_operations=failed_operations,
        )

        bulk_operation_response.additional_properties = d
        return bulk_operation_response

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
