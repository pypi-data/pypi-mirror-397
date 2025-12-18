from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    include_deleted: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_deleted"] = include_deleted

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/organizations/{organization_id}/users/ids".format(
            organization_id=quote(str(organization_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[str] | None:
    if response.status_code == 200:
        response_200 = cast(list[str], response.json())

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
) -> Response[HTTPValidationError | list[str]]:
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
    include_deleted: bool | Unset = False,
) -> Response[HTTPValidationError | list[str]]:
    """Get Member Ids

     Get list of all member user IDs in the organization.

    Requires:
    - User must be authenticated
    - User must be a member of the organization

    Args:
        organization_id: Organization ID
        db: Database session
        auth: Authenticated user
        include_deleted: Whether to include soft-deleted members

    Returns:
        List of user IDs

    Args:
        organization_id (str): Organization ID to get member IDs from
        include_deleted (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[str]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        include_deleted=include_deleted,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_deleted: bool | Unset = False,
) -> HTTPValidationError | list[str] | None:
    """Get Member Ids

     Get list of all member user IDs in the organization.

    Requires:
    - User must be authenticated
    - User must be a member of the organization

    Args:
        organization_id: Organization ID
        db: Database session
        auth: Authenticated user
        include_deleted: Whether to include soft-deleted members

    Returns:
        List of user IDs

    Args:
        organization_id (str): Organization ID to get member IDs from
        include_deleted (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[str]
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        include_deleted=include_deleted,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_deleted: bool | Unset = False,
) -> Response[HTTPValidationError | list[str]]:
    """Get Member Ids

     Get list of all member user IDs in the organization.

    Requires:
    - User must be authenticated
    - User must be a member of the organization

    Args:
        organization_id: Organization ID
        db: Database session
        auth: Authenticated user
        include_deleted: Whether to include soft-deleted members

    Returns:
        List of user IDs

    Args:
        organization_id (str): Organization ID to get member IDs from
        include_deleted (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[str]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        include_deleted=include_deleted,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_deleted: bool | Unset = False,
) -> HTTPValidationError | list[str] | None:
    """Get Member Ids

     Get list of all member user IDs in the organization.

    Requires:
    - User must be authenticated
    - User must be a member of the organization

    Args:
        organization_id: Organization ID
        db: Database session
        auth: Authenticated user
        include_deleted: Whether to include soft-deleted members

    Returns:
        List of user IDs

    Args:
        organization_id (str): Organization ID to get member IDs from
        include_deleted (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[str]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            include_deleted=include_deleted,
        )
    ).parsed
