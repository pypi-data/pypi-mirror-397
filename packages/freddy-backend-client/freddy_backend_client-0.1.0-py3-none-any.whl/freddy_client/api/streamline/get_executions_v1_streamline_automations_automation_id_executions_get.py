from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.streamline_execution_list_response import StreamlineExecutionListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    automation_id: str,
    *,
    limit: int | Unset = 50,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/streamline/automations/{automation_id}/executions".format(
            automation_id=quote(str(automation_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | StreamlineExecutionListResponse | None:
    if response.status_code == 200:
        response_200 = StreamlineExecutionListResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | StreamlineExecutionListResponse]:
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
    limit: int | Unset = 50,
) -> Response[HTTPValidationError | StreamlineExecutionListResponse]:
    """Get Executions

     Get execution history for an automation.

    Args:
        automation_id (str):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | StreamlineExecutionListResponse]
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
    limit: int | Unset = 50,
) -> HTTPValidationError | StreamlineExecutionListResponse | None:
    """Get Executions

     Get execution history for an automation.

    Args:
        automation_id (str):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | StreamlineExecutionListResponse
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
    limit: int | Unset = 50,
) -> Response[HTTPValidationError | StreamlineExecutionListResponse]:
    """Get Executions

     Get execution history for an automation.

    Args:
        automation_id (str):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | StreamlineExecutionListResponse]
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
    limit: int | Unset = 50,
) -> HTTPValidationError | StreamlineExecutionListResponse | None:
    """Get Executions

     Get execution history for an automation.

    Args:
        automation_id (str):
        limit (int | Unset):  Default: 50.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | StreamlineExecutionListResponse
    """

    return (
        await asyncio_detailed(
            automation_id=automation_id,
            client=client,
            limit=limit,
        )
    ).parsed
