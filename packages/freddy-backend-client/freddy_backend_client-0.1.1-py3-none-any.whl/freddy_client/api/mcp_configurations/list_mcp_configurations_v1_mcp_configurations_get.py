from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.mcp_configuration_list_response import MCPConfigurationListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    organization_id: str,
    type_: None | str | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["organization_id"] = organization_id

    json_type_: None | str | Unset
    if isinstance(type_, Unset):
        json_type_ = UNSET
    else:
        json_type_ = type_
    params["type"] = json_type_

    json_is_active: bool | None | Unset
    if isinstance(is_active, Unset):
        json_is_active = UNSET
    else:
        json_is_active = is_active
    params["is_active"] = json_is_active

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/mcp-configurations",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | MCPConfigurationListResponse | None:
    if response.status_code == 200:
        response_200 = MCPConfigurationListResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | MCPConfigurationListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    type_: None | str | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
) -> Response[HTTPValidationError | MCPConfigurationListResponse]:
    """List Mcp Configurations

     List MCP configurations for an organization.

    Returns configurations accessible to the current user within the specified organization.

    Args:
        organization_id (str): Organization ID
        type_ (None | str | Unset): Filter by type: custom, streamline, personal_connector
        is_active (bool | None | Unset): Filter by active status

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | MCPConfigurationListResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        type_=type_,
        is_active=is_active,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    type_: None | str | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
) -> HTTPValidationError | MCPConfigurationListResponse | None:
    """List Mcp Configurations

     List MCP configurations for an organization.

    Returns configurations accessible to the current user within the specified organization.

    Args:
        organization_id (str): Organization ID
        type_ (None | str | Unset): Filter by type: custom, streamline, personal_connector
        is_active (bool | None | Unset): Filter by active status

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | MCPConfigurationListResponse
    """

    return sync_detailed(
        client=client,
        organization_id=organization_id,
        type_=type_,
        is_active=is_active,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    type_: None | str | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
) -> Response[HTTPValidationError | MCPConfigurationListResponse]:
    """List Mcp Configurations

     List MCP configurations for an organization.

    Returns configurations accessible to the current user within the specified organization.

    Args:
        organization_id (str): Organization ID
        type_ (None | str | Unset): Filter by type: custom, streamline, personal_connector
        is_active (bool | None | Unset): Filter by active status

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | MCPConfigurationListResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        type_=type_,
        is_active=is_active,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    type_: None | str | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
) -> HTTPValidationError | MCPConfigurationListResponse | None:
    """List Mcp Configurations

     List MCP configurations for an organization.

    Returns configurations accessible to the current user within the specified organization.

    Args:
        organization_id (str): Organization ID
        type_ (None | str | Unset): Filter by type: custom, streamline, personal_connector
        is_active (bool | None | Unset): Filter by active status

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | MCPConfigurationListResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            organization_id=organization_id,
            type_=type_,
            is_active=is_active,
        )
    ).parsed
