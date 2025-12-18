from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.connector_tools_response import ConnectorToolsResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    connector_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/personal-connectors/{connector_id}/tools".format(
            connector_id=quote(str(connector_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ConnectorToolsResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ConnectorToolsResponse.from_dict(response.json())

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
) -> Response[ConnectorToolsResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    connector_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ConnectorToolsResponse | HTTPValidationError]:
    """List Connector Tools

     List available tools for a personal connector.

    This endpoint:
    1. Finds the personal connector by ID
    2. Connects to the MCP server to fetch available tools
    3. Compares with tool_configuration to determine enabled status
    4. Returns list of tools with their status

    Args:
        connector_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ConnectorToolsResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        connector_id=connector_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    connector_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ConnectorToolsResponse | HTTPValidationError | None:
    """List Connector Tools

     List available tools for a personal connector.

    This endpoint:
    1. Finds the personal connector by ID
    2. Connects to the MCP server to fetch available tools
    3. Compares with tool_configuration to determine enabled status
    4. Returns list of tools with their status

    Args:
        connector_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ConnectorToolsResponse | HTTPValidationError
    """

    return sync_detailed(
        connector_id=connector_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    connector_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ConnectorToolsResponse | HTTPValidationError]:
    """List Connector Tools

     List available tools for a personal connector.

    This endpoint:
    1. Finds the personal connector by ID
    2. Connects to the MCP server to fetch available tools
    3. Compares with tool_configuration to determine enabled status
    4. Returns list of tools with their status

    Args:
        connector_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ConnectorToolsResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        connector_id=connector_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    connector_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ConnectorToolsResponse | HTTPValidationError | None:
    """List Connector Tools

     List available tools for a personal connector.

    This endpoint:
    1. Finds the personal connector by ID
    2. Connects to the MCP server to fetch available tools
    3. Compares with tool_configuration to determine enabled status
    4. Returns list of tools with their status

    Args:
        connector_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ConnectorToolsResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            connector_id=connector_id,
            client=client,
        )
    ).parsed
