from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.streamline_execution_response_parameters_type_0 import (
        StreamlineExecutionResponseParametersType0,
    )
    from ..models.streamline_execution_response_result_type_0 import (
        StreamlineExecutionResponseResultType0,
    )


T = TypeVar("T", bound="StreamlineExecutionResponse")


@_attrs_define
class StreamlineExecutionResponse:
    """Schema for execution response.

    Attributes:
        id (str):
        automation_id (str):
        organization_id (str):
        triggered_by_user_id (None | str):
        trigger_method (str):
        parameters (None | StreamlineExecutionResponseParametersType0):
        status (str):
        started_at (datetime.datetime | None):
        completed_at (datetime.datetime | None):
        duration_seconds (int | None):
        result (None | StreamlineExecutionResponseResultType0):
        error_message (None | str):
        logs (None | str):
        created_at (datetime.datetime):
    """

    id: str
    automation_id: str
    organization_id: str
    triggered_by_user_id: None | str
    trigger_method: str
    parameters: None | StreamlineExecutionResponseParametersType0
    status: str
    started_at: datetime.datetime | None
    completed_at: datetime.datetime | None
    duration_seconds: int | None
    result: None | StreamlineExecutionResponseResultType0
    error_message: None | str
    logs: None | str
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.streamline_execution_response_parameters_type_0 import (
            StreamlineExecutionResponseParametersType0,
        )
        from ..models.streamline_execution_response_result_type_0 import (
            StreamlineExecutionResponseResultType0,
        )

        id = self.id

        automation_id = self.automation_id

        organization_id = self.organization_id

        triggered_by_user_id: None | str
        triggered_by_user_id = self.triggered_by_user_id

        trigger_method = self.trigger_method

        parameters: dict[str, Any] | None
        if isinstance(self.parameters, StreamlineExecutionResponseParametersType0):
            parameters = self.parameters.to_dict()
        else:
            parameters = self.parameters

        status = self.status

        started_at: None | str
        if isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        completed_at: None | str
        if isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        duration_seconds: int | None
        duration_seconds = self.duration_seconds

        result: dict[str, Any] | None
        if isinstance(self.result, StreamlineExecutionResponseResultType0):
            result = self.result.to_dict()
        else:
            result = self.result

        error_message: None | str
        error_message = self.error_message

        logs: None | str
        logs = self.logs

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "automation_id": automation_id,
                "organization_id": organization_id,
                "triggered_by_user_id": triggered_by_user_id,
                "trigger_method": trigger_method,
                "parameters": parameters,
                "status": status,
                "started_at": started_at,
                "completed_at": completed_at,
                "duration_seconds": duration_seconds,
                "result": result,
                "error_message": error_message,
                "logs": logs,
                "created_at": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.streamline_execution_response_parameters_type_0 import (
            StreamlineExecutionResponseParametersType0,
        )
        from ..models.streamline_execution_response_result_type_0 import (
            StreamlineExecutionResponseResultType0,
        )

        d = dict(src_dict)
        id = d.pop("id")

        automation_id = d.pop("automation_id")

        organization_id = d.pop("organization_id")

        def _parse_triggered_by_user_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        triggered_by_user_id = _parse_triggered_by_user_id(
            d.pop("triggered_by_user_id")
        )

        trigger_method = d.pop("trigger_method")

        def _parse_parameters(
            data: object,
        ) -> None | StreamlineExecutionResponseParametersType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameters_type_0 = (
                    StreamlineExecutionResponseParametersType0.from_dict(data)
                )

                return parameters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | StreamlineExecutionResponseParametersType0, data)

        parameters = _parse_parameters(d.pop("parameters"))

        status = d.pop("status")

        def _parse_started_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = isoparse(data)

                return started_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        started_at = _parse_started_at(d.pop("started_at"))

        def _parse_completed_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                completed_at_type_0 = isoparse(data)

                return completed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        completed_at = _parse_completed_at(d.pop("completed_at"))

        def _parse_duration_seconds(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        duration_seconds = _parse_duration_seconds(d.pop("duration_seconds"))

        def _parse_result(
            data: object,
        ) -> None | StreamlineExecutionResponseResultType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                result_type_0 = StreamlineExecutionResponseResultType0.from_dict(data)

                return result_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | StreamlineExecutionResponseResultType0, data)

        result = _parse_result(d.pop("result"))

        def _parse_error_message(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        error_message = _parse_error_message(d.pop("error_message"))

        def _parse_logs(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        logs = _parse_logs(d.pop("logs"))

        created_at = isoparse(d.pop("created_at"))

        streamline_execution_response = cls(
            id=id,
            automation_id=automation_id,
            organization_id=organization_id,
            triggered_by_user_id=triggered_by_user_id,
            trigger_method=trigger_method,
            parameters=parameters,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration_seconds,
            result=result,
            error_message=error_message,
            logs=logs,
            created_at=created_at,
        )

        streamline_execution_response.additional_properties = d
        return streamline_execution_response

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
