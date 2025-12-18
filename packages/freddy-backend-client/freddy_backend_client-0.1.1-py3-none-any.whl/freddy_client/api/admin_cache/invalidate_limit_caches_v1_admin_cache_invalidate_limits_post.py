from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.invalidate_limit_cache_request import InvalidateLimitCacheRequest
from ...models.invalidate_limit_cache_response import InvalidateLimitCacheResponse
from ...types import Response


def _get_kwargs(
    *,
    body: InvalidateLimitCacheRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/admin/cache/invalidate-limits",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | InvalidateLimitCacheResponse | None:
    if response.status_code == 200:
        response_200 = InvalidateLimitCacheResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | InvalidateLimitCacheResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: InvalidateLimitCacheRequest,
) -> Response[HTTPValidationError | InvalidateLimitCacheResponse]:
    """Invalidate Limit Caches

     Invalidate limit caches for organization and/or API keys.

    Use this endpoint when limits are updated directly in the database
    to ensure the cache reflects the new limits immediately.

    Requires:
    - User must be authenticated via API key OR bearer token with global admin role
    - API key authentication: Any valid API key is allowed
    - Bearer token authentication: User must have global_role_id set (global admin)

    Args:
        cache_request: Cache invalidation request with organization_id and optional api_key_ids
        request: FastAPI request object
        current_user: Authenticated user
        cache_manager: Limit cache manager instance

    Returns:
        Response with success status and count of caches cleared

    Raises:
        AuthorizationException: If user is not an admin

    Args:
        body (InvalidateLimitCacheRequest): Request schema for invalidating limit caches.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | InvalidateLimitCacheResponse]
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
    body: InvalidateLimitCacheRequest,
) -> HTTPValidationError | InvalidateLimitCacheResponse | None:
    """Invalidate Limit Caches

     Invalidate limit caches for organization and/or API keys.

    Use this endpoint when limits are updated directly in the database
    to ensure the cache reflects the new limits immediately.

    Requires:
    - User must be authenticated via API key OR bearer token with global admin role
    - API key authentication: Any valid API key is allowed
    - Bearer token authentication: User must have global_role_id set (global admin)

    Args:
        cache_request: Cache invalidation request with organization_id and optional api_key_ids
        request: FastAPI request object
        current_user: Authenticated user
        cache_manager: Limit cache manager instance

    Returns:
        Response with success status and count of caches cleared

    Raises:
        AuthorizationException: If user is not an admin

    Args:
        body (InvalidateLimitCacheRequest): Request schema for invalidating limit caches.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | InvalidateLimitCacheResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: InvalidateLimitCacheRequest,
) -> Response[HTTPValidationError | InvalidateLimitCacheResponse]:
    """Invalidate Limit Caches

     Invalidate limit caches for organization and/or API keys.

    Use this endpoint when limits are updated directly in the database
    to ensure the cache reflects the new limits immediately.

    Requires:
    - User must be authenticated via API key OR bearer token with global admin role
    - API key authentication: Any valid API key is allowed
    - Bearer token authentication: User must have global_role_id set (global admin)

    Args:
        cache_request: Cache invalidation request with organization_id and optional api_key_ids
        request: FastAPI request object
        current_user: Authenticated user
        cache_manager: Limit cache manager instance

    Returns:
        Response with success status and count of caches cleared

    Raises:
        AuthorizationException: If user is not an admin

    Args:
        body (InvalidateLimitCacheRequest): Request schema for invalidating limit caches.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | InvalidateLimitCacheResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: InvalidateLimitCacheRequest,
) -> HTTPValidationError | InvalidateLimitCacheResponse | None:
    """Invalidate Limit Caches

     Invalidate limit caches for organization and/or API keys.

    Use this endpoint when limits are updated directly in the database
    to ensure the cache reflects the new limits immediately.

    Requires:
    - User must be authenticated via API key OR bearer token with global admin role
    - API key authentication: Any valid API key is allowed
    - Bearer token authentication: User must have global_role_id set (global admin)

    Args:
        cache_request: Cache invalidation request with organization_id and optional api_key_ids
        request: FastAPI request object
        current_user: Authenticated user
        cache_manager: Limit cache manager instance

    Returns:
        Response with success status and count of caches cleared

    Raises:
        AuthorizationException: If user is not an admin

    Args:
        body (InvalidateLimitCacheRequest): Request schema for invalidating limit caches.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | InvalidateLimitCacheResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
