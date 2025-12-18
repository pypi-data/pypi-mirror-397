from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.organization_list_response import OrganizationListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    active_only: bool | Unset = True,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["skip"] = skip

    params["limit"] = limit

    params["active_only"] = active_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/organizations",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | OrganizationListResponse | None:
    if response.status_code == 200:
        response_200 = OrganizationListResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | OrganizationListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    active_only: bool | Unset = True,
) -> Response[HTTPValidationError | OrganizationListResponse]:
    """List Organizations

     List all organizations the current user belongs to.

    Automatically checks if user's email domain matches any organization domains
    and grants access to new organizations if eligible.

    Args:
        skip (int | Unset): Number of records to skip Default: 0.
        limit (int | Unset): Maximum number of records Default: 100.
        active_only (bool | Unset): Only return active organizations Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OrganizationListResponse]
    """

    kwargs = _get_kwargs(
        skip=skip,
        limit=limit,
        active_only=active_only,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    active_only: bool | Unset = True,
) -> HTTPValidationError | OrganizationListResponse | None:
    """List Organizations

     List all organizations the current user belongs to.

    Automatically checks if user's email domain matches any organization domains
    and grants access to new organizations if eligible.

    Args:
        skip (int | Unset): Number of records to skip Default: 0.
        limit (int | Unset): Maximum number of records Default: 100.
        active_only (bool | Unset): Only return active organizations Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OrganizationListResponse
    """

    return sync_detailed(
        client=client,
        skip=skip,
        limit=limit,
        active_only=active_only,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    active_only: bool | Unset = True,
) -> Response[HTTPValidationError | OrganizationListResponse]:
    """List Organizations

     List all organizations the current user belongs to.

    Automatically checks if user's email domain matches any organization domains
    and grants access to new organizations if eligible.

    Args:
        skip (int | Unset): Number of records to skip Default: 0.
        limit (int | Unset): Maximum number of records Default: 100.
        active_only (bool | Unset): Only return active organizations Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OrganizationListResponse]
    """

    kwargs = _get_kwargs(
        skip=skip,
        limit=limit,
        active_only=active_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    active_only: bool | Unset = True,
) -> HTTPValidationError | OrganizationListResponse | None:
    """List Organizations

     List all organizations the current user belongs to.

    Automatically checks if user's email domain matches any organization domains
    and grants access to new organizations if eligible.

    Args:
        skip (int | Unset): Number of records to skip Default: 0.
        limit (int | Unset): Maximum number of records Default: 100.
        active_only (bool | Unset): Only return active organizations Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OrganizationListResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            skip=skip,
            limit=limit,
            active_only=active_only,
        )
    ).parsed
