from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.audit_log_schema import AuditLogSchema
    from ..models.pagination_schema import PaginationSchema


T = TypeVar("T", bound="AuditLogListResponse")


@_attrs_define
class AuditLogListResponse:
    """Response schema for audit log list.

    Attributes:
        audit_logs (list[AuditLogSchema]): List of audit logs
        pagination (PaginationSchema): Pagination information schema.
    """

    audit_logs: list[AuditLogSchema]
    pagination: PaginationSchema
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        audit_logs = []
        for audit_logs_item_data in self.audit_logs:
            audit_logs_item = audit_logs_item_data.to_dict()
            audit_logs.append(audit_logs_item)

        pagination = self.pagination.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "audit_logs": audit_logs,
                "pagination": pagination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.audit_log_schema import AuditLogSchema
        from ..models.pagination_schema import PaginationSchema

        d = dict(src_dict)
        audit_logs = []
        _audit_logs = d.pop("audit_logs")
        for audit_logs_item_data in _audit_logs:
            audit_logs_item = AuditLogSchema.from_dict(audit_logs_item_data)

            audit_logs.append(audit_logs_item)

        pagination = PaginationSchema.from_dict(d.pop("pagination"))

        audit_log_list_response = cls(
            audit_logs=audit_logs,
            pagination=pagination,
        )

        audit_log_list_response.additional_properties = d
        return audit_log_list_response

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
