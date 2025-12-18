from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.member_response import MemberResponse
from ...types import Response


def _get_kwargs(
    organization_id: str,
    user_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/organizations/{organization_id}/users/{user_id}".format(
            organization_id=quote(str(organization_id), safe=""),
            user_id=quote(str(user_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | MemberResponse | None:
    if response.status_code == 200:
        response_200 = MemberResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | MemberResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | MemberResponse]:
    """Get Member

     Get details of a specific organization member.

    Accepts either:
    - User ID (usr_...) - will look up by user_id + organization_id
    - OrganizationUser ID (orgusr_...) - will look up directly by organization_user_id

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        user_id: User ID (usr_...) or OrganizationUser ID (orgusr_...)
        db: Database session
        auth: Authenticated user

    Returns:
        Member details

    Args:
        organization_id (str): Organization ID
        user_id (str): User ID (usr_...) or OrganizationUser ID (orgusr_...) of the member to
            retrieve

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | MemberResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        user_id=user_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | MemberResponse | None:
    """Get Member

     Get details of a specific organization member.

    Accepts either:
    - User ID (usr_...) - will look up by user_id + organization_id
    - OrganizationUser ID (orgusr_...) - will look up directly by organization_user_id

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        user_id: User ID (usr_...) or OrganizationUser ID (orgusr_...)
        db: Database session
        auth: Authenticated user

    Returns:
        Member details

    Args:
        organization_id (str): Organization ID
        user_id (str): User ID (usr_...) or OrganizationUser ID (orgusr_...) of the member to
            retrieve

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | MemberResponse
    """

    return sync_detailed(
        organization_id=organization_id,
        user_id=user_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | MemberResponse]:
    """Get Member

     Get details of a specific organization member.

    Accepts either:
    - User ID (usr_...) - will look up by user_id + organization_id
    - OrganizationUser ID (orgusr_...) - will look up directly by organization_user_id

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        user_id: User ID (usr_...) or OrganizationUser ID (orgusr_...)
        db: Database session
        auth: Authenticated user

    Returns:
        Member details

    Args:
        organization_id (str): Organization ID
        user_id (str): User ID (usr_...) or OrganizationUser ID (orgusr_...) of the member to
            retrieve

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | MemberResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        user_id=user_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | MemberResponse | None:
    """Get Member

     Get details of a specific organization member.

    Accepts either:
    - User ID (usr_...) - will look up by user_id + organization_id
    - OrganizationUser ID (orgusr_...) - will look up directly by organization_user_id

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        user_id: User ID (usr_...) or OrganizationUser ID (orgusr_...)
        db: Database session
        auth: Authenticated user

    Returns:
        Member details

    Args:
        organization_id (str): Organization ID
        user_id (str): User ID (usr_...) or OrganizationUser ID (orgusr_...) of the member to
            retrieve

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | MemberResponse
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            user_id=user_id,
            client=client,
        )
    ).parsed
