from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.organization_response import OrganizationResponse
from ...models.organization_update import OrganizationUpdate
from ...types import Response


def _get_kwargs(
    organization_id: str,
    *,
    body: OrganizationUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v1/organizations/{organization_id}".format(
            organization_id=quote(str(organization_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | OrganizationResponse | None:
    if response.status_code == 200:
        response_200 = OrganizationResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | OrganizationResponse]:
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
    body: OrganizationUpdate,
) -> Response[HTTPValidationError | OrganizationResponse]:
    """Update Organization

     Update organization details.

    User must be an Admin or Owner of the organization.
    Invalidates limit caches when api_usage_limit or api_key_usage_limit is updated.

    Args:
        organization_id (str):
        body (OrganizationUpdate): Schema for updating an organization.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OrganizationResponse]
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
    body: OrganizationUpdate,
) -> HTTPValidationError | OrganizationResponse | None:
    """Update Organization

     Update organization details.

    User must be an Admin or Owner of the organization.
    Invalidates limit caches when api_usage_limit or api_key_usage_limit is updated.

    Args:
        organization_id (str):
        body (OrganizationUpdate): Schema for updating an organization.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OrganizationResponse
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
    body: OrganizationUpdate,
) -> Response[HTTPValidationError | OrganizationResponse]:
    """Update Organization

     Update organization details.

    User must be an Admin or Owner of the organization.
    Invalidates limit caches when api_usage_limit or api_key_usage_limit is updated.

    Args:
        organization_id (str):
        body (OrganizationUpdate): Schema for updating an organization.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OrganizationResponse]
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
    body: OrganizationUpdate,
) -> HTTPValidationError | OrganizationResponse | None:
    """Update Organization

     Update organization details.

    User must be an Admin or Owner of the organization.
    Invalidates limit caches when api_usage_limit or api_key_usage_limit is updated.

    Args:
        organization_id (str):
        body (OrganizationUpdate): Schema for updating an organization.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OrganizationResponse
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            body=body,
        )
    ).parsed
