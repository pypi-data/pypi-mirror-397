from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="StreamlineGitSyncJobResponse")


@_attrs_define
class StreamlineGitSyncJobResponse:
    """Schema for git sync job response.

    Attributes:
        id (str):
        automation_id (str):
        status (str):
        commit_sha_before (None | str):
        commit_sha_after (None | str):
        changes_detected (bool):
        error_message (None | str):
        synced_at (datetime.datetime | None):
        created_at (datetime.datetime):
    """

    id: str
    automation_id: str
    status: str
    commit_sha_before: None | str
    commit_sha_after: None | str
    changes_detected: bool
    error_message: None | str
    synced_at: datetime.datetime | None
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        automation_id = self.automation_id

        status = self.status

        commit_sha_before: None | str
        commit_sha_before = self.commit_sha_before

        commit_sha_after: None | str
        commit_sha_after = self.commit_sha_after

        changes_detected = self.changes_detected

        error_message: None | str
        error_message = self.error_message

        synced_at: None | str
        if isinstance(self.synced_at, datetime.datetime):
            synced_at = self.synced_at.isoformat()
        else:
            synced_at = self.synced_at

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "automation_id": automation_id,
                "status": status,
                "commit_sha_before": commit_sha_before,
                "commit_sha_after": commit_sha_after,
                "changes_detected": changes_detected,
                "error_message": error_message,
                "synced_at": synced_at,
                "created_at": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        automation_id = d.pop("automation_id")

        status = d.pop("status")

        def _parse_commit_sha_before(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        commit_sha_before = _parse_commit_sha_before(d.pop("commit_sha_before"))

        def _parse_commit_sha_after(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        commit_sha_after = _parse_commit_sha_after(d.pop("commit_sha_after"))

        changes_detected = d.pop("changes_detected")

        def _parse_error_message(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        error_message = _parse_error_message(d.pop("error_message"))

        def _parse_synced_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                synced_at_type_0 = isoparse(data)

                return synced_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        synced_at = _parse_synced_at(d.pop("synced_at"))

        created_at = isoparse(d.pop("created_at"))

        streamline_git_sync_job_response = cls(
            id=id,
            automation_id=automation_id,
            status=status,
            commit_sha_before=commit_sha_before,
            commit_sha_after=commit_sha_after,
            changes_detected=changes_detected,
            error_message=error_message,
            synced_at=synced_at,
            created_at=created_at,
        )

        streamline_git_sync_job_response.additional_properties = d
        return streamline_git_sync_job_response

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
