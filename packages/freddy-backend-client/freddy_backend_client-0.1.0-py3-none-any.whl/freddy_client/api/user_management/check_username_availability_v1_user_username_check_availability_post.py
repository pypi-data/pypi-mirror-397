from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.check_username_request import CheckUsernameRequest
from ...models.check_username_response import CheckUsernameResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: CheckUsernameRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/user/username/check-availability",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CheckUsernameResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CheckUsernameResponse.from_dict(response.json())

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
) -> Response[CheckUsernameResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CheckUsernameRequest,
) -> Response[CheckUsernameResponse | HTTPValidationError]:
    """Check Username Availability

     Check if a username is available.

    Validates username format and checks if it's already taken.
    This endpoint does not require authentication.

    **Returns:**
    - available: Whether username is available
    - username: Normalized username
    - message: Explanation of availability status

    Args:
        body (CheckUsernameRequest): Request schema for checking username availability.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CheckUsernameResponse | HTTPValidationError]
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
    body: CheckUsernameRequest,
) -> CheckUsernameResponse | HTTPValidationError | None:
    """Check Username Availability

     Check if a username is available.

    Validates username format and checks if it's already taken.
    This endpoint does not require authentication.

    **Returns:**
    - available: Whether username is available
    - username: Normalized username
    - message: Explanation of availability status

    Args:
        body (CheckUsernameRequest): Request schema for checking username availability.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CheckUsernameResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CheckUsernameRequest,
) -> Response[CheckUsernameResponse | HTTPValidationError]:
    """Check Username Availability

     Check if a username is available.

    Validates username format and checks if it's already taken.
    This endpoint does not require authentication.

    **Returns:**
    - available: Whether username is available
    - username: Normalized username
    - message: Explanation of availability status

    Args:
        body (CheckUsernameRequest): Request schema for checking username availability.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CheckUsernameResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CheckUsernameRequest,
) -> CheckUsernameResponse | HTTPValidationError | None:
    """Check Username Availability

     Check if a username is available.

    Validates username format and checks if it's already taken.
    This endpoint does not require authentication.

    **Returns:**
    - available: Whether username is available
    - username: Normalized username
    - message: Explanation of availability status

    Args:
        body (CheckUsernameRequest): Request schema for checking username availability.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CheckUsernameResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
