from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.streamline_automation_response_parameters_type_0 import (
        StreamlineAutomationResponseParametersType0,
    )


T = TypeVar("T", bound="StreamlineAutomationResponse")


@_attrs_define
class StreamlineAutomationResponse:
    """Schema for automation response.

    Attributes:
        id (str):
        organization_id (str):
        created_by_user_id (str):
        name (str):
        description (None | str):
        automation_id (str):
        upload_method (str):
        git_repository_url (None | str):
        git_branch (None | str):
        git_last_commit_sha (None | str):
        git_last_sync_at (datetime.datetime | None):
        execution_file_path (str):
        execution_return_mode (str):
        parameters (None | StreamlineAutomationResponseParametersType0):
        schedule_enabled (bool):
        schedule_cron (None | str):
        schedule_timezone (str):
        schedule_next_run_at (datetime.datetime | None):
        is_active (bool):
        last_executed_at (datetime.datetime | None):
        execution_count (int):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    id: str
    organization_id: str
    created_by_user_id: str
    name: str
    description: None | str
    automation_id: str
    upload_method: str
    git_repository_url: None | str
    git_branch: None | str
    git_last_commit_sha: None | str
    git_last_sync_at: datetime.datetime | None
    execution_file_path: str
    execution_return_mode: str
    parameters: None | StreamlineAutomationResponseParametersType0
    schedule_enabled: bool
    schedule_cron: None | str
    schedule_timezone: str
    schedule_next_run_at: datetime.datetime | None
    is_active: bool
    last_executed_at: datetime.datetime | None
    execution_count: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.streamline_automation_response_parameters_type_0 import (
            StreamlineAutomationResponseParametersType0,
        )

        id = self.id

        organization_id = self.organization_id

        created_by_user_id = self.created_by_user_id

        name = self.name

        description: None | str
        description = self.description

        automation_id = self.automation_id

        upload_method = self.upload_method

        git_repository_url: None | str
        git_repository_url = self.git_repository_url

        git_branch: None | str
        git_branch = self.git_branch

        git_last_commit_sha: None | str
        git_last_commit_sha = self.git_last_commit_sha

        git_last_sync_at: None | str
        if isinstance(self.git_last_sync_at, datetime.datetime):
            git_last_sync_at = self.git_last_sync_at.isoformat()
        else:
            git_last_sync_at = self.git_last_sync_at

        execution_file_path = self.execution_file_path

        execution_return_mode = self.execution_return_mode

        parameters: dict[str, Any] | None
        if isinstance(self.parameters, StreamlineAutomationResponseParametersType0):
            parameters = self.parameters.to_dict()
        else:
            parameters = self.parameters

        schedule_enabled = self.schedule_enabled

        schedule_cron: None | str
        schedule_cron = self.schedule_cron

        schedule_timezone = self.schedule_timezone

        schedule_next_run_at: None | str
        if isinstance(self.schedule_next_run_at, datetime.datetime):
            schedule_next_run_at = self.schedule_next_run_at.isoformat()
        else:
            schedule_next_run_at = self.schedule_next_run_at

        is_active = self.is_active

        last_executed_at: None | str
        if isinstance(self.last_executed_at, datetime.datetime):
            last_executed_at = self.last_executed_at.isoformat()
        else:
            last_executed_at = self.last_executed_at

        execution_count = self.execution_count

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "organization_id": organization_id,
                "created_by_user_id": created_by_user_id,
                "name": name,
                "description": description,
                "automation_id": automation_id,
                "upload_method": upload_method,
                "git_repository_url": git_repository_url,
                "git_branch": git_branch,
                "git_last_commit_sha": git_last_commit_sha,
                "git_last_sync_at": git_last_sync_at,
                "execution_file_path": execution_file_path,
                "execution_return_mode": execution_return_mode,
                "parameters": parameters,
                "schedule_enabled": schedule_enabled,
                "schedule_cron": schedule_cron,
                "schedule_timezone": schedule_timezone,
                "schedule_next_run_at": schedule_next_run_at,
                "is_active": is_active,
                "last_executed_at": last_executed_at,
                "execution_count": execution_count,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.streamline_automation_response_parameters_type_0 import (
            StreamlineAutomationResponseParametersType0,
        )

        d = dict(src_dict)
        id = d.pop("id")

        organization_id = d.pop("organization_id")

        created_by_user_id = d.pop("created_by_user_id")

        name = d.pop("name")

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        automation_id = d.pop("automation_id")

        upload_method = d.pop("upload_method")

        def _parse_git_repository_url(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        git_repository_url = _parse_git_repository_url(d.pop("git_repository_url"))

        def _parse_git_branch(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        git_branch = _parse_git_branch(d.pop("git_branch"))

        def _parse_git_last_commit_sha(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        git_last_commit_sha = _parse_git_last_commit_sha(d.pop("git_last_commit_sha"))

        def _parse_git_last_sync_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                git_last_sync_at_type_0 = isoparse(data)

                return git_last_sync_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        git_last_sync_at = _parse_git_last_sync_at(d.pop("git_last_sync_at"))

        execution_file_path = d.pop("execution_file_path")

        execution_return_mode = d.pop("execution_return_mode")

        def _parse_parameters(
            data: object,
        ) -> None | StreamlineAutomationResponseParametersType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameters_type_0 = (
                    StreamlineAutomationResponseParametersType0.from_dict(data)
                )

                return parameters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | StreamlineAutomationResponseParametersType0, data)

        parameters = _parse_parameters(d.pop("parameters"))

        schedule_enabled = d.pop("schedule_enabled")

        def _parse_schedule_cron(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        schedule_cron = _parse_schedule_cron(d.pop("schedule_cron"))

        schedule_timezone = d.pop("schedule_timezone")

        def _parse_schedule_next_run_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                schedule_next_run_at_type_0 = isoparse(data)

                return schedule_next_run_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        schedule_next_run_at = _parse_schedule_next_run_at(
            d.pop("schedule_next_run_at")
        )

        is_active = d.pop("is_active")

        def _parse_last_executed_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_executed_at_type_0 = isoparse(data)

                return last_executed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        last_executed_at = _parse_last_executed_at(d.pop("last_executed_at"))

        execution_count = d.pop("execution_count")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        streamline_automation_response = cls(
            id=id,
            organization_id=organization_id,
            created_by_user_id=created_by_user_id,
            name=name,
            description=description,
            automation_id=automation_id,
            upload_method=upload_method,
            git_repository_url=git_repository_url,
            git_branch=git_branch,
            git_last_commit_sha=git_last_commit_sha,
            git_last_sync_at=git_last_sync_at,
            execution_file_path=execution_file_path,
            execution_return_mode=execution_return_mode,
            parameters=parameters,
            schedule_enabled=schedule_enabled,
            schedule_cron=schedule_cron,
            schedule_timezone=schedule_timezone,
            schedule_next_run_at=schedule_next_run_at,
            is_active=is_active,
            last_executed_at=last_executed_at,
            execution_count=execution_count,
            created_at=created_at,
            updated_at=updated_at,
        )

        streamline_automation_response.additional_properties = d
        return streamline_automation_response

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
