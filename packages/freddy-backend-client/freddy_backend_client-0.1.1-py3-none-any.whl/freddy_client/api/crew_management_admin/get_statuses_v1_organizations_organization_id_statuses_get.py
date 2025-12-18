from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.status_list_response import StatusListResponse
from ...types import Response


def _get_kwargs(
    organization_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/organizations/{organization_id}/statuses".format(
            organization_id=quote(str(organization_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | StatusListResponse | None:
    if response.status_code == 200:
        response_200 = StatusListResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | StatusListResponse]:
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
) -> Response[HTTPValidationError | StatusListResponse]:
    """Get Statuses

     Get list of available statuses for the organization.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        db: Database session
        auth: Authenticated user

    Returns:
        List of available statuses with selectable_in_ui flag

    Args:
        organization_id (str): Organization ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | StatusListResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | StatusListResponse | None:
    """Get Statuses

     Get list of available statuses for the organization.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        db: Database session
        auth: Authenticated user

    Returns:
        List of available statuses with selectable_in_ui flag

    Args:
        organization_id (str): Organization ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | StatusListResponse
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | StatusListResponse]:
    """Get Statuses

     Get list of available statuses for the organization.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        db: Database session
        auth: Authenticated user

    Returns:
        List of available statuses with selectable_in_ui flag

    Args:
        organization_id (str): Organization ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | StatusListResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | StatusListResponse | None:
    """Get Statuses

     Get list of available statuses for the organization.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        db: Database session
        auth: Authenticated user

    Returns:
        List of available statuses with selectable_in_ui flag

    Args:
        organization_id (str): Organization ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | StatusListResponse
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
        )
    ).parsed
