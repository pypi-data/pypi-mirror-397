from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.connector_response import ConnectorResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    organization_id: str,
    force_check: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["organization_id"] = organization_id

    params["forceCheck"] = force_check

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/personal-connectors",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[ConnectorResponse] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ConnectorResponse.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[HTTPValidationError | list[ConnectorResponse]]:
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
    force_check: bool | Unset = False,
) -> Response[HTTPValidationError | list[ConnectorResponse]]:
    """List Connected Connectors

     List user's connected personal connectors.

    Args:
        organization_id (str): Organization ID
        force_check (bool | Unset): Bypass cache and force fresh check Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[ConnectorResponse]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        force_check=force_check,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    force_check: bool | Unset = False,
) -> HTTPValidationError | list[ConnectorResponse] | None:
    """List Connected Connectors

     List user's connected personal connectors.

    Args:
        organization_id (str): Organization ID
        force_check (bool | Unset): Bypass cache and force fresh check Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[ConnectorResponse]
    """

    return sync_detailed(
        client=client,
        organization_id=organization_id,
        force_check=force_check,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    force_check: bool | Unset = False,
) -> Response[HTTPValidationError | list[ConnectorResponse]]:
    """List Connected Connectors

     List user's connected personal connectors.

    Args:
        organization_id (str): Organization ID
        force_check (bool | Unset): Bypass cache and force fresh check Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[ConnectorResponse]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        force_check=force_check,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    force_check: bool | Unset = False,
) -> HTTPValidationError | list[ConnectorResponse] | None:
    """List Connected Connectors

     List user's connected personal connectors.

    Args:
        organization_id (str): Organization ID
        force_check (bool | Unset): Bypass cache and force fresh check Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[ConnectorResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            organization_id=organization_id,
            force_check=force_check,
        )
    ).parsed
