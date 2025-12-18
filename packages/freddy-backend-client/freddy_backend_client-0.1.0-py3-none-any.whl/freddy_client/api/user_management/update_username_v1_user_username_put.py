from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.update_username_request import UpdateUsernameRequest
from ...models.update_username_response import UpdateUsernameResponse
from ...types import Response


def _get_kwargs(
    *,
    body: UpdateUsernameRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/user/username",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | UpdateUsernameResponse | None:
    if response.status_code == 200:
        response_200 = UpdateUsernameResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | UpdateUsernameResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: UpdateUsernameRequest,
) -> Response[HTTPValidationError | UpdateUsernameResponse]:
    """Update Username

     Update current user's username.

    **Requirements:**
    - 3-100 characters
    - Lowercase letters, numbers, dots, underscores, hyphens only
    - Must be unique

    **Requires Authentication:** Bearer token in Authorization header

    **Errors:**
    - 401: Not authenticated
    - 404: User not found
    - 409: Username already taken
    - 422: Invalid username format

    Args:
        body (UpdateUsernameRequest): Request schema for updating username.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UpdateUsernameResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: UpdateUsernameRequest,
) -> HTTPValidationError | UpdateUsernameResponse | None:
    """Update Username

     Update current user's username.

    **Requirements:**
    - 3-100 characters
    - Lowercase letters, numbers, dots, underscores, hyphens only
    - Must be unique

    **Requires Authentication:** Bearer token in Authorization header

    **Errors:**
    - 401: Not authenticated
    - 404: User not found
    - 409: Username already taken
    - 422: Invalid username format

    Args:
        body (UpdateUsernameRequest): Request schema for updating username.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UpdateUsernameResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: UpdateUsernameRequest,
) -> Response[HTTPValidationError | UpdateUsernameResponse]:
    """Update Username

     Update current user's username.

    **Requirements:**
    - 3-100 characters
    - Lowercase letters, numbers, dots, underscores, hyphens only
    - Must be unique

    **Requires Authentication:** Bearer token in Authorization header

    **Errors:**
    - 401: Not authenticated
    - 404: User not found
    - 409: Username already taken
    - 422: Invalid username format

    Args:
        body (UpdateUsernameRequest): Request schema for updating username.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UpdateUsernameResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: UpdateUsernameRequest,
) -> HTTPValidationError | UpdateUsernameResponse | None:
    """Update Username

     Update current user's username.

    **Requirements:**
    - 3-100 characters
    - Lowercase letters, numbers, dots, underscores, hyphens only
    - Must be unique

    **Requires Authentication:** Bearer token in Authorization header

    **Errors:**
    - 401: Not authenticated
    - 404: User not found
    - 409: Username already taken
    - 422: Invalid username format

    Args:
        body (UpdateUsernameRequest): Request schema for updating username.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UpdateUsernameResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
