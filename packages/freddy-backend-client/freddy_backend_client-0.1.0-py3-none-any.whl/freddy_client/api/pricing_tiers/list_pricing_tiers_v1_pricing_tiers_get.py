from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.pricing_tier_response import PricingTierResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    active_only: bool | Unset = True,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["active_only"] = active_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/pricing-tiers",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[PricingTierResponse] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = PricingTierResponse.from_dict(response_200_item_data)

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
) -> Response[HTTPValidationError | list[PricingTierResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    active_only: bool | Unset = True,
) -> Response[HTTPValidationError | list[PricingTierResponse]]:
    """List Pricing Tiers

     List all pricing tiers.

    Args:
        active_only: If True, only return active tiers

    Args:
        active_only (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[PricingTierResponse]]
    """

    kwargs = _get_kwargs(
        active_only=active_only,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    active_only: bool | Unset = True,
) -> HTTPValidationError | list[PricingTierResponse] | None:
    """List Pricing Tiers

     List all pricing tiers.

    Args:
        active_only: If True, only return active tiers

    Args:
        active_only (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[PricingTierResponse]
    """

    return sync_detailed(
        client=client,
        active_only=active_only,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    active_only: bool | Unset = True,
) -> Response[HTTPValidationError | list[PricingTierResponse]]:
    """List Pricing Tiers

     List all pricing tiers.

    Args:
        active_only: If True, only return active tiers

    Args:
        active_only (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[PricingTierResponse]]
    """

    kwargs = _get_kwargs(
        active_only=active_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    active_only: bool | Unset = True,
) -> HTTPValidationError | list[PricingTierResponse] | None:
    """List Pricing Tiers

     List all pricing tiers.

    Args:
        active_only: If True, only return active tiers

    Args:
        active_only (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[PricingTierResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            active_only=active_only,
        )
    ).parsed
