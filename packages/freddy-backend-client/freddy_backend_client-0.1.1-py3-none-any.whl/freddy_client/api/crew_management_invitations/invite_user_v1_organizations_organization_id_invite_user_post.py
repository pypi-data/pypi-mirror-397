from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.invitation_response import InvitationResponse
from ...models.invite_user_request import InviteUserRequest
from ...types import Response


def _get_kwargs(
    organization_id: str,
    *,
    body: InviteUserRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/organizations/{organization_id}/invite-user".format(
            organization_id=quote(str(organization_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | InvitationResponse | None:
    if response.status_code == 201:
        response_201 = InvitationResponse.from_dict(response.json())

        return response_201

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | InvitationResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: InviteUserRequest,
) -> Response[HTTPValidationError | InvitationResponse]:
    """Invite User

     Invite a new user to join the organization.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        request: Invitation request with email, role_id, and send_invitation flag
        db: Database session
        auth: Authenticated user

    Returns:
        Created invitation details

    Raises:
        ConflictException: If user already exists in organization
        ValidationException: If invalid email or role

    Args:
        organization_id (str): Organization ID
        body (InviteUserRequest): Schema for inviting a new user to the organization.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | InvitationResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: InviteUserRequest,
) -> HTTPValidationError | InvitationResponse | None:
    """Invite User

     Invite a new user to join the organization.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        request: Invitation request with email, role_id, and send_invitation flag
        db: Database session
        auth: Authenticated user

    Returns:
        Created invitation details

    Raises:
        ConflictException: If user already exists in organization
        ValidationException: If invalid email or role

    Args:
        organization_id (str): Organization ID
        body (InviteUserRequest): Schema for inviting a new user to the organization.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | InvitationResponse
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: InviteUserRequest,
) -> Response[HTTPValidationError | InvitationResponse]:
    """Invite User

     Invite a new user to join the organization.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        request: Invitation request with email, role_id, and send_invitation flag
        db: Database session
        auth: Authenticated user

    Returns:
        Created invitation details

    Raises:
        ConflictException: If user already exists in organization
        ValidationException: If invalid email or role

    Args:
        organization_id (str): Organization ID
        body (InviteUserRequest): Schema for inviting a new user to the organization.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | InvitationResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: InviteUserRequest,
) -> HTTPValidationError | InvitationResponse | None:
    """Invite User

     Invite a new user to join the organization.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        request: Invitation request with email, role_id, and send_invitation flag
        db: Database session
        auth: Authenticated user

    Returns:
        Created invitation details

    Raises:
        ConflictException: If user already exists in organization
        ValidationException: If invalid email or role

    Args:
        organization_id (str): Organization ID
        body (InviteUserRequest): Schema for inviting a new user to the organization.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | InvitationResponse
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            body=body,
        )
    ).parsed
