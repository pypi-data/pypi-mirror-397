from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.streamline_git_sync_job_list_response import (
    StreamlineGitSyncJobListResponse,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    automation_id: str,
    *,
    limit: int | Unset = 20,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/streamline/automations/{automation_id}/syncs".format(
            automation_id=quote(str(automation_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | StreamlineGitSyncJobListResponse | None:
    if response.status_code == 200:
        response_200 = StreamlineGitSyncJobListResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | StreamlineGitSyncJobListResponse]:
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
    limit: int | Unset = 20,
) -> Response[HTTPValidationError | StreamlineGitSyncJobListResponse]:
    """Get Sync Jobs

     Get Git sync history for an automation.

    Args:
        automation_id (str):
        limit (int | Unset):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | StreamlineGitSyncJobListResponse]
    """

    kwargs = _get_kwargs(
        automation_id=automation_id,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    automation_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 20,
) -> HTTPValidationError | StreamlineGitSyncJobListResponse | None:
    """Get Sync Jobs

     Get Git sync history for an automation.

    Args:
        automation_id (str):
        limit (int | Unset):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | StreamlineGitSyncJobListResponse
    """

    return sync_detailed(
        automation_id=automation_id,
        client=client,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    automation_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 20,
) -> Response[HTTPValidationError | StreamlineGitSyncJobListResponse]:
    """Get Sync Jobs

     Get Git sync history for an automation.

    Args:
        automation_id (str):
        limit (int | Unset):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | StreamlineGitSyncJobListResponse]
    """

    kwargs = _get_kwargs(
        automation_id=automation_id,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    automation_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 20,
) -> HTTPValidationError | StreamlineGitSyncJobListResponse | None:
    """Get Sync Jobs

     Get Git sync history for an automation.

    Args:
        automation_id (str):
        limit (int | Unset):  Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | StreamlineGitSyncJobListResponse
    """

    return (
        await asyncio_detailed(
            automation_id=automation_id,
            client=client,
            limit=limit,
        )
    ).parsed
