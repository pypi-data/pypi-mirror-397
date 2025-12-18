from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.connector_response import ConnectorResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.update_connector_request import UpdateConnectorRequest
from ...types import Response


def _get_kwargs(
    connector_id: str,
    *,
    body: UpdateConnectorRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v1/personal-connectors/{connector_id}".format(
            connector_id=quote(str(connector_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ConnectorResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ConnectorResponse.from_dict(response.json())

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
) -> Response[ConnectorResponse | HTTPValidationError]:
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
    body: UpdateConnectorRequest,
) -> Response[ConnectorResponse | HTTPValidationError]:
    """Update Connector

     Update a personal connector's status (enable/disable).

    This endpoint:
    1. Finds the personal connector by ID
    2. Updates the is_active flag on both connector and MCP configuration
    3. Returns updated connector information

    Args:
        connector_id (str):
        body (UpdateConnectorRequest): Request to update connector status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ConnectorResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        connector_id=connector_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    connector_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateConnectorRequest,
) -> ConnectorResponse | HTTPValidationError | None:
    """Update Connector

     Update a personal connector's status (enable/disable).

    This endpoint:
    1. Finds the personal connector by ID
    2. Updates the is_active flag on both connector and MCP configuration
    3. Returns updated connector information

    Args:
        connector_id (str):
        body (UpdateConnectorRequest): Request to update connector status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ConnectorResponse | HTTPValidationError
    """

    return sync_detailed(
        connector_id=connector_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    connector_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateConnectorRequest,
) -> Response[ConnectorResponse | HTTPValidationError]:
    """Update Connector

     Update a personal connector's status (enable/disable).

    This endpoint:
    1. Finds the personal connector by ID
    2. Updates the is_active flag on both connector and MCP configuration
    3. Returns updated connector information

    Args:
        connector_id (str):
        body (UpdateConnectorRequest): Request to update connector status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ConnectorResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        connector_id=connector_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    connector_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateConnectorRequest,
) -> ConnectorResponse | HTTPValidationError | None:
    """Update Connector

     Update a personal connector's status (enable/disable).

    This endpoint:
    1. Finds the personal connector by ID
    2. Updates the is_active flag on both connector and MCP configuration
    3. Returns updated connector information

    Args:
        connector_id (str):
        body (UpdateConnectorRequest): Request to update connector status.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ConnectorResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            connector_id=connector_id,
            client=client,
            body=body,
        )
    ).parsed
