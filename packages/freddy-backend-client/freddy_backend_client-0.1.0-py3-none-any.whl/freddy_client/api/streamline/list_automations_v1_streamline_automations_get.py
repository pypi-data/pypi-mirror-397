from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.streamline_automation_list_response import (
    StreamlineAutomationListResponse,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    organization_id: str,
    include_inactive: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["organization_id"] = organization_id

    params["include_inactive"] = include_inactive

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/streamline/automations",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | StreamlineAutomationListResponse | None:
    if response.status_code == 200:
        response_200 = StreamlineAutomationListResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | StreamlineAutomationListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    include_inactive: bool | Unset = False,
) -> Response[HTTPValidationError | StreamlineAutomationListResponse]:
    """List Automations

     List automations for organization.

    Args:
        organization_id (str):
        include_inactive (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | StreamlineAutomationListResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        include_inactive=include_inactive,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    include_inactive: bool | Unset = False,
) -> HTTPValidationError | StreamlineAutomationListResponse | None:
    """List Automations

     List automations for organization.

    Args:
        organization_id (str):
        include_inactive (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | StreamlineAutomationListResponse
    """

    return sync_detailed(
        client=client,
        organization_id=organization_id,
        include_inactive=include_inactive,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    include_inactive: bool | Unset = False,
) -> Response[HTTPValidationError | StreamlineAutomationListResponse]:
    """List Automations

     List automations for organization.

    Args:
        organization_id (str):
        include_inactive (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | StreamlineAutomationListResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        include_inactive=include_inactive,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    include_inactive: bool | Unset = False,
) -> HTTPValidationError | StreamlineAutomationListResponse | None:
    """List Automations

     List automations for organization.

    Args:
        organization_id (str):
        include_inactive (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | StreamlineAutomationListResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            organization_id=organization_id,
            include_inactive=include_inactive,
        )
    ).parsed
