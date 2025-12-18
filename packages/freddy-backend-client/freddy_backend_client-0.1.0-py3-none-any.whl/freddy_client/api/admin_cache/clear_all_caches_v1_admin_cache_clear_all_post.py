from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.clear_all_caches_response import ClearAllCachesResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/admin/cache/clear-all",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ClearAllCachesResponse | None:
    if response.status_code == 200:
        response_200 = ClearAllCachesResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ClearAllCachesResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[ClearAllCachesResponse]:
    """Clear All Caches

     Clear all application caches (Redis + in-memory).

    This endpoint clears:
    - All Redis caches (limits, models, sessions, etc.)
    - In-memory rule caches
    - Model caches

    Use this when you need to force a complete cache refresh across the system.

    Requires:
    - User must be authenticated via API key OR bearer token with global admin role
    - API key authentication: Any valid API key is allowed
    - Bearer token authentication: User must have global_role_id set (global admin)

    Args:
        request: FastAPI request object
        current_user: Authenticated user
        redis: Redis client instance
        model_cache: Model cache service instance

    Returns:
        Response with success status and details of caches cleared

    Raises:
        AuthorizationException: If user is not an admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ClearAllCachesResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> ClearAllCachesResponse | None:
    """Clear All Caches

     Clear all application caches (Redis + in-memory).

    This endpoint clears:
    - All Redis caches (limits, models, sessions, etc.)
    - In-memory rule caches
    - Model caches

    Use this when you need to force a complete cache refresh across the system.

    Requires:
    - User must be authenticated via API key OR bearer token with global admin role
    - API key authentication: Any valid API key is allowed
    - Bearer token authentication: User must have global_role_id set (global admin)

    Args:
        request: FastAPI request object
        current_user: Authenticated user
        redis: Redis client instance
        model_cache: Model cache service instance

    Returns:
        Response with success status and details of caches cleared

    Raises:
        AuthorizationException: If user is not an admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ClearAllCachesResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[ClearAllCachesResponse]:
    """Clear All Caches

     Clear all application caches (Redis + in-memory).

    This endpoint clears:
    - All Redis caches (limits, models, sessions, etc.)
    - In-memory rule caches
    - Model caches

    Use this when you need to force a complete cache refresh across the system.

    Requires:
    - User must be authenticated via API key OR bearer token with global admin role
    - API key authentication: Any valid API key is allowed
    - Bearer token authentication: User must have global_role_id set (global admin)

    Args:
        request: FastAPI request object
        current_user: Authenticated user
        redis: Redis client instance
        model_cache: Model cache service instance

    Returns:
        Response with success status and details of caches cleared

    Raises:
        AuthorizationException: If user is not an admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ClearAllCachesResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> ClearAllCachesResponse | None:
    """Clear All Caches

     Clear all application caches (Redis + in-memory).

    This endpoint clears:
    - All Redis caches (limits, models, sessions, etc.)
    - In-memory rule caches
    - Model caches

    Use this when you need to force a complete cache refresh across the system.

    Requires:
    - User must be authenticated via API key OR bearer token with global admin role
    - API key authentication: Any valid API key is allowed
    - Bearer token authentication: User must have global_role_id set (global admin)

    Args:
        request: FastAPI request object
        current_user: Authenticated user
        redis: Redis client instance
        model_cache: Model cache service instance

    Returns:
        Response with success status and details of caches cleared

    Raises:
        AuthorizationException: If user is not an admin

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ClearAllCachesResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
