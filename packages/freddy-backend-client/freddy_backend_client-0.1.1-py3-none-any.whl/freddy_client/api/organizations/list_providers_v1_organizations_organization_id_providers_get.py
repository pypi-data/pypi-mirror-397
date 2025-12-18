from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.provider_response import ProviderResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    active_only: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["active_only"] = active_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/organizations/{organization_id}/providers".format(
            organization_id=quote(str(organization_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[ProviderResponse] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ProviderResponse.from_dict(response_200_item_data)

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
) -> Response[HTTPValidationError | list[ProviderResponse]]:
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
    active_only: bool | Unset = False,
) -> Response[HTTPValidationError | list[ProviderResponse]]:
    """List Providers

     List all AI providers configured for the organization.

    Args:
        organization_id (str):
        active_only (bool | Unset): Only return active providers Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[ProviderResponse]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        active_only=active_only,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    active_only: bool | Unset = False,
) -> HTTPValidationError | list[ProviderResponse] | None:
    """List Providers

     List all AI providers configured for the organization.

    Args:
        organization_id (str):
        active_only (bool | Unset): Only return active providers Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[ProviderResponse]
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        active_only=active_only,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    active_only: bool | Unset = False,
) -> Response[HTTPValidationError | list[ProviderResponse]]:
    """List Providers

     List all AI providers configured for the organization.

    Args:
        organization_id (str):
        active_only (bool | Unset): Only return active providers Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[ProviderResponse]]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        active_only=active_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    active_only: bool | Unset = False,
) -> HTTPValidationError | list[ProviderResponse] | None:
    """List Providers

     List all AI providers configured for the organization.

    Args:
        organization_id (str):
        active_only (bool | Unset): Only return active providers Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[ProviderResponse]
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            active_only=active_only,
        )
    ).parsed
