from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.resend_code_request import ResendCodeRequest
from ...models.resend_code_response import ResendCodeResponse
from ...types import Response


def _get_kwargs(
    *,
    body: ResendCodeRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/auth/resend-code",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ResendCodeResponse | None:
    if response.status_code == 200:
        response_200 = ResendCodeResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResendCodeResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ResendCodeRequest,
) -> Response[HTTPValidationError | ResendCodeResponse]:
    """Resend Verification Code

     Resend verification code.

    Generates and sends a new 4-digit verification code to the user's email.
    Works for login, registration, and password reset verifications.

    **Security Features:**
    - Validates verification record exists
    - Checks if verification already used
    - Generates new random code
    - Updates expiry time

    **Errors:**
    - 404: Verification record not found
    - 422: Verification already used
    - 500: Email sending failed

    Args:
        body (ResendCodeRequest): Request schema for resending verification code. Example:
            {'email_key': 'uuid-12345678-1234-1234-1234-123456789abc'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResendCodeResponse]
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
    body: ResendCodeRequest,
) -> HTTPValidationError | ResendCodeResponse | None:
    """Resend Verification Code

     Resend verification code.

    Generates and sends a new 4-digit verification code to the user's email.
    Works for login, registration, and password reset verifications.

    **Security Features:**
    - Validates verification record exists
    - Checks if verification already used
    - Generates new random code
    - Updates expiry time

    **Errors:**
    - 404: Verification record not found
    - 422: Verification already used
    - 500: Email sending failed

    Args:
        body (ResendCodeRequest): Request schema for resending verification code. Example:
            {'email_key': 'uuid-12345678-1234-1234-1234-123456789abc'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResendCodeResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ResendCodeRequest,
) -> Response[HTTPValidationError | ResendCodeResponse]:
    """Resend Verification Code

     Resend verification code.

    Generates and sends a new 4-digit verification code to the user's email.
    Works for login, registration, and password reset verifications.

    **Security Features:**
    - Validates verification record exists
    - Checks if verification already used
    - Generates new random code
    - Updates expiry time

    **Errors:**
    - 404: Verification record not found
    - 422: Verification already used
    - 500: Email sending failed

    Args:
        body (ResendCodeRequest): Request schema for resending verification code. Example:
            {'email_key': 'uuid-12345678-1234-1234-1234-123456789abc'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResendCodeResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ResendCodeRequest,
) -> HTTPValidationError | ResendCodeResponse | None:
    """Resend Verification Code

     Resend verification code.

    Generates and sends a new 4-digit verification code to the user's email.
    Works for login, registration, and password reset verifications.

    **Security Features:**
    - Validates verification record exists
    - Checks if verification already used
    - Generates new random code
    - Updates expiry time

    **Errors:**
    - 404: Verification record not found
    - 422: Verification already used
    - 500: Email sending failed

    Args:
        body (ResendCodeRequest): Request schema for resending verification code. Example:
            {'email_key': 'uuid-12345678-1234-1234-1234-123456789abc'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResendCodeResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
