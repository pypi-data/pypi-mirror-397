from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.accept_invitation_v1_invitations_accept_post_response_accept_invitation_v1_invitations_accept_post import (
    AcceptInvitationV1InvitationsAcceptPostResponseAcceptInvitationV1InvitationsAcceptPost,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    *,
    email_key: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["email_key"] = email_key

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/invitations/accept",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    AcceptInvitationV1InvitationsAcceptPostResponseAcceptInvitationV1InvitationsAcceptPost
    | HTTPValidationError
    | None
):
    if response.status_code == 200:
        response_200 = AcceptInvitationV1InvitationsAcceptPostResponseAcceptInvitationV1InvitationsAcceptPost.from_dict(
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
    AcceptInvitationV1InvitationsAcceptPostResponseAcceptInvitationV1InvitationsAcceptPost
    | HTTPValidationError
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    email_key: str,
) -> Response[
    AcceptInvitationV1InvitationsAcceptPostResponseAcceptInvitationV1InvitationsAcceptPost
    | HTTPValidationError
]:
    """Accept Invitation

     Accept an invitation to join an organization.

    User must be authenticated.

    Args:
        email_key: Unique email key from invitation link
        db: Database session
        auth: Authenticated user

    Returns:
        Acceptance confirmation with organization details

    Raises:
        ResourceNotFoundException: If invitation not found
        ValidationException: If invitation expired or already used
        ConflictException: If user already member of organization

    Args:
        email_key (str): Unique email key from invitation link

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AcceptInvitationV1InvitationsAcceptPostResponseAcceptInvitationV1InvitationsAcceptPost | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        email_key=email_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    email_key: str,
) -> (
    AcceptInvitationV1InvitationsAcceptPostResponseAcceptInvitationV1InvitationsAcceptPost
    | HTTPValidationError
    | None
):
    """Accept Invitation

     Accept an invitation to join an organization.

    User must be authenticated.

    Args:
        email_key: Unique email key from invitation link
        db: Database session
        auth: Authenticated user

    Returns:
        Acceptance confirmation with organization details

    Raises:
        ResourceNotFoundException: If invitation not found
        ValidationException: If invitation expired or already used
        ConflictException: If user already member of organization

    Args:
        email_key (str): Unique email key from invitation link

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AcceptInvitationV1InvitationsAcceptPostResponseAcceptInvitationV1InvitationsAcceptPost | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        email_key=email_key,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    email_key: str,
) -> Response[
    AcceptInvitationV1InvitationsAcceptPostResponseAcceptInvitationV1InvitationsAcceptPost
    | HTTPValidationError
]:
    """Accept Invitation

     Accept an invitation to join an organization.

    User must be authenticated.

    Args:
        email_key: Unique email key from invitation link
        db: Database session
        auth: Authenticated user

    Returns:
        Acceptance confirmation with organization details

    Raises:
        ResourceNotFoundException: If invitation not found
        ValidationException: If invitation expired or already used
        ConflictException: If user already member of organization

    Args:
        email_key (str): Unique email key from invitation link

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AcceptInvitationV1InvitationsAcceptPostResponseAcceptInvitationV1InvitationsAcceptPost | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        email_key=email_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    email_key: str,
) -> (
    AcceptInvitationV1InvitationsAcceptPostResponseAcceptInvitationV1InvitationsAcceptPost
    | HTTPValidationError
    | None
):
    """Accept Invitation

     Accept an invitation to join an organization.

    User must be authenticated.

    Args:
        email_key: Unique email key from invitation link
        db: Database session
        auth: Authenticated user

    Returns:
        Acceptance confirmation with organization details

    Raises:
        ResourceNotFoundException: If invitation not found
        ValidationException: If invitation expired or already used
        ConflictException: If user already member of organization

    Args:
        email_key (str): Unique email key from invitation link

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AcceptInvitationV1InvitationsAcceptPostResponseAcceptInvitationV1InvitationsAcceptPost | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            email_key=email_key,
        )
    ).parsed
