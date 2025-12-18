from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.validate_invitation_v1_invitations_validate_email_key_get_response_validate_invitation_v1_invitations_validate_email_key_get import (
    ValidateInvitationV1InvitationsValidateEmailKeyGetResponseValidateInvitationV1InvitationsValidateEmailKeyGet,
)
from ...types import Response


def _get_kwargs(
    email_key: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/invitations/validate/{email_key}".format(
            email_key=quote(str(email_key), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    HTTPValidationError
    | ValidateInvitationV1InvitationsValidateEmailKeyGetResponseValidateInvitationV1InvitationsValidateEmailKeyGet
    | None
):
    if response.status_code == 200:
        response_200 = ValidateInvitationV1InvitationsValidateEmailKeyGetResponseValidateInvitationV1InvitationsValidateEmailKeyGet.from_dict(
            response.json()
        )

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
) -> Response[
    HTTPValidationError
    | ValidateInvitationV1InvitationsValidateEmailKeyGetResponseValidateInvitationV1InvitationsValidateEmailKeyGet
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    email_key: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    HTTPValidationError
    | ValidateInvitationV1InvitationsValidateEmailKeyGetResponseValidateInvitationV1InvitationsValidateEmailKeyGet
]:
    """Validate Invitation

     Validate an invitation by email key.

    This endpoint is public (no authentication required) for users
    accepting invitations.

    Args:
        email_key: Unique email key from invitation link
        db: Database session

    Returns:
        Invitation validation details

    Raises:
        ResourceNotFoundException: If invitation not found
        ValidationException: If invitation expired or already used

    Args:
        email_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ValidateInvitationV1InvitationsValidateEmailKeyGetResponseValidateInvitationV1InvitationsValidateEmailKeyGet]
    """

    kwargs = _get_kwargs(
        email_key=email_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    email_key: str,
    *,
    client: AuthenticatedClient | Client,
) -> (
    HTTPValidationError
    | ValidateInvitationV1InvitationsValidateEmailKeyGetResponseValidateInvitationV1InvitationsValidateEmailKeyGet
    | None
):
    """Validate Invitation

     Validate an invitation by email key.

    This endpoint is public (no authentication required) for users
    accepting invitations.

    Args:
        email_key: Unique email key from invitation link
        db: Database session

    Returns:
        Invitation validation details

    Raises:
        ResourceNotFoundException: If invitation not found
        ValidationException: If invitation expired or already used

    Args:
        email_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ValidateInvitationV1InvitationsValidateEmailKeyGetResponseValidateInvitationV1InvitationsValidateEmailKeyGet
    """

    return sync_detailed(
        email_key=email_key,
        client=client,
    ).parsed


async def asyncio_detailed(
    email_key: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    HTTPValidationError
    | ValidateInvitationV1InvitationsValidateEmailKeyGetResponseValidateInvitationV1InvitationsValidateEmailKeyGet
]:
    """Validate Invitation

     Validate an invitation by email key.

    This endpoint is public (no authentication required) for users
    accepting invitations.

    Args:
        email_key: Unique email key from invitation link
        db: Database session

    Returns:
        Invitation validation details

    Raises:
        ResourceNotFoundException: If invitation not found
        ValidationException: If invitation expired or already used

    Args:
        email_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ValidateInvitationV1InvitationsValidateEmailKeyGetResponseValidateInvitationV1InvitationsValidateEmailKeyGet]
    """

    kwargs = _get_kwargs(
        email_key=email_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    email_key: str,
    *,
    client: AuthenticatedClient | Client,
) -> (
    HTTPValidationError
    | ValidateInvitationV1InvitationsValidateEmailKeyGetResponseValidateInvitationV1InvitationsValidateEmailKeyGet
    | None
):
    """Validate Invitation

     Validate an invitation by email key.

    This endpoint is public (no authentication required) for users
    accepting invitations.

    Args:
        email_key: Unique email key from invitation link
        db: Database session

    Returns:
        Invitation validation details

    Raises:
        ResourceNotFoundException: If invitation not found
        ValidationException: If invitation expired or already used

    Args:
        email_key (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ValidateInvitationV1InvitationsValidateEmailKeyGetResponseValidateInvitationV1InvitationsValidateEmailKeyGet
    """

    return (
        await asyncio_detailed(
            email_key=email_key,
            client=client,
        )
    ).parsed
