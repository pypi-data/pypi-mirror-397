from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_key_rotate_response import ApiKeyRotateResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    org_id: str,
    key_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/organizations/{org_id}/api-keys/{key_id}/rotate".format(
            org_id=quote(str(org_id), safe=""),
            key_id=quote(str(key_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ApiKeyRotateResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ApiKeyRotateResponse.from_dict(response.json())

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
) -> Response[ApiKeyRotateResponse | HTTPValidationError]:
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
) -> Response[ApiKeyRotateResponse | HTTPValidationError]:
    """Rotate Api Key

     Rotate an API key (delete old, create new with same settings).

    Requires admin or owner role.
    The new raw API key is returned ONCE and must be stored securely.

    Args:
        org_id: Organization ID
        key_id: API key ID to rotate
        db: Database session
        auth: Authenticated user

    Returns:
        Rotation result with new key (raw key shown ONCE only)

    Raises:
        ResourceNotFoundException: If organization or key not found
        AuthorizationException: If user lacks permissions

    Args:
        org_id (str):
        key_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ApiKeyRotateResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        key_id=key_id,
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
) -> ApiKeyRotateResponse | HTTPValidationError | None:
    """Rotate Api Key

     Rotate an API key (delete old, create new with same settings).

    Requires admin or owner role.
    The new raw API key is returned ONCE and must be stored securely.

    Args:
        org_id: Organization ID
        key_id: API key ID to rotate
        db: Database session
        auth: Authenticated user

    Returns:
        Rotation result with new key (raw key shown ONCE only)

    Raises:
        ResourceNotFoundException: If organization or key not found
        AuthorizationException: If user lacks permissions

    Args:
        org_id (str):
        key_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ApiKeyRotateResponse | HTTPValidationError
    """

    return sync_detailed(
        org_id=org_id,
        key_id=key_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    key_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ApiKeyRotateResponse | HTTPValidationError]:
    """Rotate Api Key

     Rotate an API key (delete old, create new with same settings).

    Requires admin or owner role.
    The new raw API key is returned ONCE and must be stored securely.

    Args:
        org_id: Organization ID
        key_id: API key ID to rotate
        db: Database session
        auth: Authenticated user

    Returns:
        Rotation result with new key (raw key shown ONCE only)

    Raises:
        ResourceNotFoundException: If organization or key not found
        AuthorizationException: If user lacks permissions

    Args:
        org_id (str):
        key_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ApiKeyRotateResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        key_id=key_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    key_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ApiKeyRotateResponse | HTTPValidationError | None:
    """Rotate Api Key

     Rotate an API key (delete old, create new with same settings).

    Requires admin or owner role.
    The new raw API key is returned ONCE and must be stored securely.

    Args:
        org_id: Organization ID
        key_id: API key ID to rotate
        db: Database session
        auth: Authenticated user

    Returns:
        Rotation result with new key (raw key shown ONCE only)

    Raises:
        ResourceNotFoundException: If organization or key not found
        AuthorizationException: If user lacks permissions

    Args:
        org_id (str):
        key_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ApiKeyRotateResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            key_id=key_id,
            client=client,
        )
    ).parsed
