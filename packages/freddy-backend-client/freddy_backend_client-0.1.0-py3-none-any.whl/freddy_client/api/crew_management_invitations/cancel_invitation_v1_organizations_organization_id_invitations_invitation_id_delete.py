from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    organization_id: str,
    invitation_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v1/organizations/{organization_id}/invitations/{invitation_id}".format(
            organization_id=quote(str(organization_id), safe=""),
            invitation_id=quote(str(invitation_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    invitation_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | HTTPValidationError]:
    """Cancel Invitation

     Cancel a pending invitation.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        invitation_id: Invitation ID to cancel
        db: Database session
        auth: Authenticated user

    Raises:
        ResourceNotFoundException: If invitation not found
        AuthorizationException: If user lacks permissions

    Args:
        organization_id (str): Organization ID
        invitation_id (str): Invitation ID to cancel

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        invitation_id=invitation_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    invitation_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | HTTPValidationError | None:
    """Cancel Invitation

     Cancel a pending invitation.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        invitation_id: Invitation ID to cancel
        db: Database session
        auth: Authenticated user

    Raises:
        ResourceNotFoundException: If invitation not found
        AuthorizationException: If user lacks permissions

    Args:
        organization_id (str): Organization ID
        invitation_id (str): Invitation ID to cancel

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        organization_id=organization_id,
        invitation_id=invitation_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    invitation_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | HTTPValidationError]:
    """Cancel Invitation

     Cancel a pending invitation.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        invitation_id: Invitation ID to cancel
        db: Database session
        auth: Authenticated user

    Raises:
        ResourceNotFoundException: If invitation not found
        AuthorizationException: If user lacks permissions

    Args:
        organization_id (str): Organization ID
        invitation_id (str): Invitation ID to cancel

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        invitation_id=invitation_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    invitation_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | HTTPValidationError | None:
    """Cancel Invitation

     Cancel a pending invitation.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        invitation_id: Invitation ID to cancel
        db: Database session
        auth: Authenticated user

    Raises:
        ResourceNotFoundException: If invitation not found
        AuthorizationException: If user lacks permissions

    Args:
        organization_id (str): Organization ID
        invitation_id (str): Invitation ID to cancel

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            invitation_id=invitation_id,
            client=client,
        )
    ).parsed
