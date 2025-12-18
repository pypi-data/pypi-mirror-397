from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.schedule_request import ScheduleRequest
from ...models.streamline_automation_response import StreamlineAutomationResponse
from ...types import Response


def _get_kwargs(
    automation_id: str,
    *,
    body: ScheduleRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/streamline/automations/{automation_id}/schedule".format(
            automation_id=quote(str(automation_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | StreamlineAutomationResponse | None:
    if response.status_code == 200:
        response_200 = StreamlineAutomationResponse.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | StreamlineAutomationResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    automation_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ScheduleRequest,
) -> Response[HTTPValidationError | StreamlineAutomationResponse]:
    """Set Schedule

     Set cron schedule for automation.

    The automation will be executed automatically based on the cron expression.

    Args:
        automation_id (str):
        body (ScheduleRequest): Schema for schedule automation request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | StreamlineAutomationResponse]
    """

    kwargs = _get_kwargs(
        automation_id=automation_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    automation_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ScheduleRequest,
) -> HTTPValidationError | StreamlineAutomationResponse | None:
    """Set Schedule

     Set cron schedule for automation.

    The automation will be executed automatically based on the cron expression.

    Args:
        automation_id (str):
        body (ScheduleRequest): Schema for schedule automation request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | StreamlineAutomationResponse
    """

    return sync_detailed(
        automation_id=automation_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    automation_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ScheduleRequest,
) -> Response[HTTPValidationError | StreamlineAutomationResponse]:
    """Set Schedule

     Set cron schedule for automation.

    The automation will be executed automatically based on the cron expression.

    Args:
        automation_id (str):
        body (ScheduleRequest): Schema for schedule automation request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | StreamlineAutomationResponse]
    """

    kwargs = _get_kwargs(
        automation_id=automation_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    automation_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ScheduleRequest,
) -> HTTPValidationError | StreamlineAutomationResponse | None:
    """Set Schedule

     Set cron schedule for automation.

    The automation will be executed automatically based on the cron expression.

    Args:
        automation_id (str):
        body (ScheduleRequest): Schema for schedule automation request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | StreamlineAutomationResponse
    """

    return (
        await asyncio_detailed(
            automation_id=automation_id,
            client=client,
            body=body,
        )
    ).parsed
