from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.user_profile_response import UserProfileResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/user/me",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> UserProfileResponse | None:
    if response.status_code == 200:
        response_200 = UserProfileResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[UserProfileResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[UserProfileResponse]:
    """Get Current User Profile

     Get current authenticated user's profile.

    Returns detailed profile information for the logged-in user.

    **Requires Authentication:** Bearer token in Authorization header

    **Available at:**
    - GET /v1/user/me
    - GET /v1/user/profile (alias)

    **Returns:**
    - User ID, email, username
    - Full name, first name, last name
    - Profile image, timezone
    - Account status and verification info
    - Timestamps (created_at, updated_at, last_login)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UserProfileResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> UserProfileResponse | None:
    """Get Current User Profile

     Get current authenticated user's profile.

    Returns detailed profile information for the logged-in user.

    **Requires Authentication:** Bearer token in Authorization header

    **Available at:**
    - GET /v1/user/me
    - GET /v1/user/profile (alias)

    **Returns:**
    - User ID, email, username
    - Full name, first name, last name
    - Profile image, timezone
    - Account status and verification info
    - Timestamps (created_at, updated_at, last_login)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UserProfileResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[UserProfileResponse]:
    """Get Current User Profile

     Get current authenticated user's profile.

    Returns detailed profile information for the logged-in user.

    **Requires Authentication:** Bearer token in Authorization header

    **Available at:**
    - GET /v1/user/me
    - GET /v1/user/profile (alias)

    **Returns:**
    - User ID, email, username
    - Full name, first name, last name
    - Profile image, timezone
    - Account status and verification info
    - Timestamps (created_at, updated_at, last_login)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UserProfileResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> UserProfileResponse | None:
    """Get Current User Profile

     Get current authenticated user's profile.

    Returns detailed profile information for the logged-in user.

    **Requires Authentication:** Bearer token in Authorization header

    **Available at:**
    - GET /v1/user/me
    - GET /v1/user/profile (alias)

    **Returns:**
    - User ID, email, username
    - Full name, first name, last name
    - Profile image, timezone
    - Account status and verification info
    - Timestamps (created_at, updated_at, last_login)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UserProfileResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
