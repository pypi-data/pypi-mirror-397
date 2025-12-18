from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.update_profile_request import UpdateProfileRequest
from ...models.update_profile_response import UpdateProfileResponse
from ...types import Response


def _get_kwargs(
    *,
    body: UpdateProfileRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v1/user/profile",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | UpdateProfileResponse | None:
    if response.status_code == 200:
        response_200 = UpdateProfileResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | UpdateProfileResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProfileRequest,
) -> Response[HTTPValidationError | UpdateProfileResponse]:
    """Update User Profile

     Update current user's profile.

    Allows partial updates to user profile fields. Only provided fields will be updated.

    **Requires Authentication:** Bearer token in Authorization header

    **Updatable Fields:**
    - username: Must be unique (3-100 characters, lowercase letters/numbers/dots/underscores/hyphens)
    - first_name, last_name, full_name: Personal names
    - birthday: Date of birth (YYYY-MM-DD format, cannot be in future)
    - gender: Gender identity
    - profile_image: Profile image URL
    - timezone: User's timezone
    - country_id: Country ID (must be valid country_ prefixed ID)
    - post_code: Postal/ZIP code

    **Note:** Email cannot be updated through this endpoint.

    **Returns:**
    - success: Whether the update was successful
    - message: Success message
    - profile: Updated user profile with all fields

    **Errors:**
    - 401: Not authenticated
    - 404: User not found
    - 409: Username already taken
    - 422: Validation error (invalid country_id, future birthday, etc.)

    Args:
        body (UpdateProfileRequest): Request schema for updating user profile.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UpdateProfileResponse]
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
    body: UpdateProfileRequest,
) -> HTTPValidationError | UpdateProfileResponse | None:
    """Update User Profile

     Update current user's profile.

    Allows partial updates to user profile fields. Only provided fields will be updated.

    **Requires Authentication:** Bearer token in Authorization header

    **Updatable Fields:**
    - username: Must be unique (3-100 characters, lowercase letters/numbers/dots/underscores/hyphens)
    - first_name, last_name, full_name: Personal names
    - birthday: Date of birth (YYYY-MM-DD format, cannot be in future)
    - gender: Gender identity
    - profile_image: Profile image URL
    - timezone: User's timezone
    - country_id: Country ID (must be valid country_ prefixed ID)
    - post_code: Postal/ZIP code

    **Note:** Email cannot be updated through this endpoint.

    **Returns:**
    - success: Whether the update was successful
    - message: Success message
    - profile: Updated user profile with all fields

    **Errors:**
    - 401: Not authenticated
    - 404: User not found
    - 409: Username already taken
    - 422: Validation error (invalid country_id, future birthday, etc.)

    Args:
        body (UpdateProfileRequest): Request schema for updating user profile.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UpdateProfileResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProfileRequest,
) -> Response[HTTPValidationError | UpdateProfileResponse]:
    """Update User Profile

     Update current user's profile.

    Allows partial updates to user profile fields. Only provided fields will be updated.

    **Requires Authentication:** Bearer token in Authorization header

    **Updatable Fields:**
    - username: Must be unique (3-100 characters, lowercase letters/numbers/dots/underscores/hyphens)
    - first_name, last_name, full_name: Personal names
    - birthday: Date of birth (YYYY-MM-DD format, cannot be in future)
    - gender: Gender identity
    - profile_image: Profile image URL
    - timezone: User's timezone
    - country_id: Country ID (must be valid country_ prefixed ID)
    - post_code: Postal/ZIP code

    **Note:** Email cannot be updated through this endpoint.

    **Returns:**
    - success: Whether the update was successful
    - message: Success message
    - profile: Updated user profile with all fields

    **Errors:**
    - 401: Not authenticated
    - 404: User not found
    - 409: Username already taken
    - 422: Validation error (invalid country_id, future birthday, etc.)

    Args:
        body (UpdateProfileRequest): Request schema for updating user profile.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UpdateProfileResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProfileRequest,
) -> HTTPValidationError | UpdateProfileResponse | None:
    """Update User Profile

     Update current user's profile.

    Allows partial updates to user profile fields. Only provided fields will be updated.

    **Requires Authentication:** Bearer token in Authorization header

    **Updatable Fields:**
    - username: Must be unique (3-100 characters, lowercase letters/numbers/dots/underscores/hyphens)
    - first_name, last_name, full_name: Personal names
    - birthday: Date of birth (YYYY-MM-DD format, cannot be in future)
    - gender: Gender identity
    - profile_image: Profile image URL
    - timezone: User's timezone
    - country_id: Country ID (must be valid country_ prefixed ID)
    - post_code: Postal/ZIP code

    **Note:** Email cannot be updated through this endpoint.

    **Returns:**
    - success: Whether the update was successful
    - message: Success message
    - profile: Updated user profile with all fields

    **Errors:**
    - 401: Not authenticated
    - 404: User not found
    - 409: Username already taken
    - 422: Validation error (invalid country_id, future birthday, etc.)

    Args:
        body (UpdateProfileRequest): Request schema for updating user profile.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UpdateProfileResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
