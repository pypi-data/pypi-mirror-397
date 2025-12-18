from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_key_list_response import ApiKeyListResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: str,
    *,
    page: int | Unset = 1,
    page_size: int | Unset = 20,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["page_size"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/organizations/{org_id}/api-keys".format(
            org_id=quote(str(org_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ApiKeyListResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ApiKeyListResponse.from_dict(response.json())

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
) -> Response[ApiKeyListResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    page: int | Unset = 1,
    page_size: int | Unset = 20,
) -> Response[ApiKeyListResponse | HTTPValidationError]:
    """List Api Keys

     List API keys for an organization.

    Requires organization membership.

    Args:
        org_id: Organization ID
        db: Database session
        auth: Authenticated user
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Paginated list of API keys

    Raises:
        ResourceNotFoundException: If organization not found
        AuthorizationException: If user is not a member

    Args:
        org_id (str):
        page (int | Unset): Page number Default: 1.
        page_size (int | Unset): Items per page Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ApiKeyListResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        page=page,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    page: int | Unset = 1,
    page_size: int | Unset = 20,
) -> ApiKeyListResponse | HTTPValidationError | None:
    """List Api Keys

     List API keys for an organization.

    Requires organization membership.

    Args:
        org_id: Organization ID
        db: Database session
        auth: Authenticated user
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Paginated list of API keys

    Raises:
        ResourceNotFoundException: If organization not found
        AuthorizationException: If user is not a member

    Args:
        org_id (str):
        page (int | Unset): Page number Default: 1.
        page_size (int | Unset): Items per page Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ApiKeyListResponse | HTTPValidationError
    """

    return sync_detailed(
        org_id=org_id,
        client=client,
        page=page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    page: int | Unset = 1,
    page_size: int | Unset = 20,
) -> Response[ApiKeyListResponse | HTTPValidationError]:
    """List Api Keys

     List API keys for an organization.

    Requires organization membership.

    Args:
        org_id: Organization ID
        db: Database session
        auth: Authenticated user
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Paginated list of API keys

    Raises:
        ResourceNotFoundException: If organization not found
        AuthorizationException: If user is not a member

    Args:
        org_id (str):
        page (int | Unset): Page number Default: 1.
        page_size (int | Unset): Items per page Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ApiKeyListResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        page=page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    page: int | Unset = 1,
    page_size: int | Unset = 20,
) -> ApiKeyListResponse | HTTPValidationError | None:
    """List Api Keys

     List API keys for an organization.

    Requires organization membership.

    Args:
        org_id: Organization ID
        db: Database session
        auth: Authenticated user
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Paginated list of API keys

    Raises:
        ResourceNotFoundException: If organization not found
        AuthorizationException: If user is not a member

    Args:
        org_id (str):
        page (int | Unset): Page number Default: 1.
        page_size (int | Unset): Items per page Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ApiKeyListResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            client=client,
            page=page,
            page_size=page_size,
        )
    ).parsed
