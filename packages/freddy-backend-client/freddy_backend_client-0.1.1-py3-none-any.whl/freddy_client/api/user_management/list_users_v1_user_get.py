from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.user_response import UserResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    active_only: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["skip"] = skip

    params["limit"] = limit

    params["active_only"] = active_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/user/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[UserResponse] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = UserResponse.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[HTTPValidationError | list[UserResponse]]:
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
    active_only: bool | Unset = False,
) -> Response[HTTPValidationError | list[UserResponse]]:
    """List Users

     List users with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: If True, return only active users

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        active_only (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[UserResponse]]
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
    active_only: bool | Unset = False,
) -> HTTPValidationError | list[UserResponse] | None:
    """List Users

     List users with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: If True, return only active users

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        active_only (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[UserResponse]
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
    active_only: bool | Unset = False,
) -> Response[HTTPValidationError | list[UserResponse]]:
    """List Users

     List users with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: If True, return only active users

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        active_only (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[UserResponse]]
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
    active_only: bool | Unset = False,
) -> HTTPValidationError | list[UserResponse] | None:
    """List Users

     List users with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: If True, return only active users

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        active_only (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[UserResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            skip=skip,
            limit=limit,
            active_only=active_only,
        )
    ).parsed
