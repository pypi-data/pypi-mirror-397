from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.streamline_git_sync_job_response import StreamlineGitSyncJobResponse


T = TypeVar("T", bound="StreamlineGitSyncJobListResponse")


@_attrs_define
class StreamlineGitSyncJobListResponse:
    """Schema for git sync job list response.

    Attributes:
        sync_jobs (list[StreamlineGitSyncJobResponse]):
    """

    sync_jobs: list[StreamlineGitSyncJobResponse]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sync_jobs = []
        for sync_jobs_item_data in self.sync_jobs:
            sync_jobs_item = sync_jobs_item_data.to_dict()
            sync_jobs.append(sync_jobs_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sync_jobs": sync_jobs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.streamline_git_sync_job_response import (
            StreamlineGitSyncJobResponse,
        )

        d = dict(src_dict)
        sync_jobs = []
        _sync_jobs = d.pop("sync_jobs")
        for sync_jobs_item_data in _sync_jobs:
            sync_jobs_item = StreamlineGitSyncJobResponse.from_dict(sync_jobs_item_data)

            sync_jobs.append(sync_jobs_item)

        streamline_git_sync_job_list_response = cls(
            sync_jobs=sync_jobs,
        )

        streamline_git_sync_job_list_response.additional_properties = d
        return streamline_git_sync_job_list_response

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
