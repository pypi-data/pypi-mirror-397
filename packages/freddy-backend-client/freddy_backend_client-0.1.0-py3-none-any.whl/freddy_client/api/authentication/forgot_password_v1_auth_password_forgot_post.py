from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.password_reset_request import PasswordResetRequest
from ...models.password_reset_response import PasswordResetResponse
from ...types import Response


def _get_kwargs(
    *,
    body: PasswordResetRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/auth/password/forgot",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PasswordResetResponse | None:
    if response.status_code == 200:
        response_200 = PasswordResetResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | PasswordResetResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PasswordResetRequest,
) -> Response[HTTPValidationError | PasswordResetResponse]:
    """Forgot Password

     Request a password reset (alias for /password/reset).

    Sends a 4-digit verification code to the user's email if the account exists.
    For security, always returns success regardless of whether the email exists.

    **Security Features:**
    - Generic response (prevents email enumeration)
    - Rate limiting (1 request per minute per email)
    - Time-limited codes (5 minutes expiry)
    - Automatic cleanup of expired codes

    **Flow:**
    1. User requests password reset with email
    2. If account exists, receives 4-digit code via email
    3. User submits code + new password to /password/reset
    4. All existing sessions are revoked on successful reset

    Args:
        body (PasswordResetRequest): Request schema for password reset endpoint. Example:
            {'email': 'user@example.com'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PasswordResetResponse]
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
    body: PasswordResetRequest,
) -> HTTPValidationError | PasswordResetResponse | None:
    """Forgot Password

     Request a password reset (alias for /password/reset).

    Sends a 4-digit verification code to the user's email if the account exists.
    For security, always returns success regardless of whether the email exists.

    **Security Features:**
    - Generic response (prevents email enumeration)
    - Rate limiting (1 request per minute per email)
    - Time-limited codes (5 minutes expiry)
    - Automatic cleanup of expired codes

    **Flow:**
    1. User requests password reset with email
    2. If account exists, receives 4-digit code via email
    3. User submits code + new password to /password/reset
    4. All existing sessions are revoked on successful reset

    Args:
        body (PasswordResetRequest): Request schema for password reset endpoint. Example:
            {'email': 'user@example.com'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PasswordResetResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PasswordResetRequest,
) -> Response[HTTPValidationError | PasswordResetResponse]:
    """Forgot Password

     Request a password reset (alias for /password/reset).

    Sends a 4-digit verification code to the user's email if the account exists.
    For security, always returns success regardless of whether the email exists.

    **Security Features:**
    - Generic response (prevents email enumeration)
    - Rate limiting (1 request per minute per email)
    - Time-limited codes (5 minutes expiry)
    - Automatic cleanup of expired codes

    **Flow:**
    1. User requests password reset with email
    2. If account exists, receives 4-digit code via email
    3. User submits code + new password to /password/reset
    4. All existing sessions are revoked on successful reset

    Args:
        body (PasswordResetRequest): Request schema for password reset endpoint. Example:
            {'email': 'user@example.com'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PasswordResetResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PasswordResetRequest,
) -> HTTPValidationError | PasswordResetResponse | None:
    """Forgot Password

     Request a password reset (alias for /password/reset).

    Sends a 4-digit verification code to the user's email if the account exists.
    For security, always returns success regardless of whether the email exists.

    **Security Features:**
    - Generic response (prevents email enumeration)
    - Rate limiting (1 request per minute per email)
    - Time-limited codes (5 minutes expiry)
    - Automatic cleanup of expired codes

    **Flow:**
    1. User requests password reset with email
    2. If account exists, receives 4-digit code via email
    3. User submits code + new password to /password/reset
    4. All existing sessions are revoked on successful reset

    Args:
        body (PasswordResetRequest): Request schema for password reset endpoint. Example:
            {'email': 'user@example.com'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PasswordResetResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
