from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_key_response import ApiKeyResponse
from ...models.api_key_update import ApiKeyUpdate
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    org_id: str,
    key_id: str,
    *,
    body: ApiKeyUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v1/organizations/{org_id}/api-keys/{key_id}".format(
            org_id=quote(str(org_id), safe=""),
            key_id=quote(str(key_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ApiKeyResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ApiKeyResponse.from_dict(response.json())

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
) -> Response[ApiKeyResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: str,
    key_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ApiKeyUpdate,
) -> Response[ApiKeyResponse | HTTPValidationError]:
    """Update Api Key

     Update API key metadata.

    Requires admin or owner role.
    Invalidates per-key limit cache when usage_limit_chf is updated.

    Args:
        org_id: Organization ID
        key_id: API key ID
        request: Update request
        db: Database session
        auth: Authenticated user

    Returns:
        Updated API key details

    Raises:
        ResourceNotFoundException: If organization or key not found
        AuthorizationException: If user lacks permissions
        ValidationException: If validation fails

    Args:
        org_id (str):
        key_id (str):
        body (ApiKeyUpdate): Request schema for updating an API key.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ApiKeyResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        key_id=key_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    key_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ApiKeyUpdate,
) -> ApiKeyResponse | HTTPValidationError | None:
    """Update Api Key

     Update API key metadata.

    Requires admin or owner role.
    Invalidates per-key limit cache when usage_limit_chf is updated.

    Args:
        org_id: Organization ID
        key_id: API key ID
        request: Update request
        db: Database session
        auth: Authenticated user

    Returns:
        Updated API key details

    Raises:
        ResourceNotFoundException: If organization or key not found
        AuthorizationException: If user lacks permissions
        ValidationException: If validation fails

    Args:
        org_id (str):
        key_id (str):
        body (ApiKeyUpdate): Request schema for updating an API key.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ApiKeyResponse | HTTPValidationError
    """

    return sync_detailed(
        org_id=org_id,
        key_id=key_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    key_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ApiKeyUpdate,
) -> Response[ApiKeyResponse | HTTPValidationError]:
    """Update Api Key

     Update API key metadata.

    Requires admin or owner role.
    Invalidates per-key limit cache when usage_limit_chf is updated.

    Args:
        org_id: Organization ID
        key_id: API key ID
        request: Update request
        db: Database session
        auth: Authenticated user

    Returns:
        Updated API key details

    Raises:
        ResourceNotFoundException: If organization or key not found
        AuthorizationException: If user lacks permissions
        ValidationException: If validation fails

    Args:
        org_id (str):
        key_id (str):
        body (ApiKeyUpdate): Request schema for updating an API key.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ApiKeyResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        key_id=key_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    key_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ApiKeyUpdate,
) -> ApiKeyResponse | HTTPValidationError | None:
    """Update Api Key

     Update API key metadata.

    Requires admin or owner role.
    Invalidates per-key limit cache when usage_limit_chf is updated.

    Args:
        org_id: Organization ID
        key_id: API key ID
        request: Update request
        db: Database session
        auth: Authenticated user

    Returns:
        Updated API key details

    Raises:
        ResourceNotFoundException: If organization or key not found
        AuthorizationException: If user lacks permissions
        ValidationException: If validation fails

    Args:
        org_id (str):
        key_id (str):
        body (ApiKeyUpdate): Request schema for updating an API key.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ApiKeyResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            key_id=key_id,
            client=client,
            body=body,
        )
    ).parsed
