from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.pricing_tier_response import PricingTierResponse
from ...models.pricing_tier_update import PricingTierUpdate
from ...types import Response


def _get_kwargs(
    tier_id: str,
    *,
    body: PricingTierUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v1/pricing-tiers/{tier_id}".format(
            tier_id=quote(str(tier_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PricingTierResponse | None:
    if response.status_code == 200:
        response_200 = PricingTierResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | PricingTierResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    tier_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PricingTierUpdate,
) -> Response[HTTPValidationError | PricingTierResponse]:
    """Update Pricing Tier

     Update a pricing tier.

    **Admin only** - Requires admin privileges.

    Args:
        tier_id (str):
        body (PricingTierUpdate): Schema for updating a pricing tier.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PricingTierResponse]
    """

    kwargs = _get_kwargs(
        tier_id=tier_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    tier_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PricingTierUpdate,
) -> HTTPValidationError | PricingTierResponse | None:
    """Update Pricing Tier

     Update a pricing tier.

    **Admin only** - Requires admin privileges.

    Args:
        tier_id (str):
        body (PricingTierUpdate): Schema for updating a pricing tier.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PricingTierResponse
    """

    return sync_detailed(
        tier_id=tier_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    tier_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PricingTierUpdate,
) -> Response[HTTPValidationError | PricingTierResponse]:
    """Update Pricing Tier

     Update a pricing tier.

    **Admin only** - Requires admin privileges.

    Args:
        tier_id (str):
        body (PricingTierUpdate): Schema for updating a pricing tier.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PricingTierResponse]
    """

    kwargs = _get_kwargs(
        tier_id=tier_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    tier_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PricingTierUpdate,
) -> HTTPValidationError | PricingTierResponse | None:
    """Update Pricing Tier

     Update a pricing tier.

    **Admin only** - Requires admin privileges.

    Args:
        tier_id (str):
        body (PricingTierUpdate): Schema for updating a pricing tier.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PricingTierResponse
    """

    return (
        await asyncio_detailed(
            tier_id=tier_id,
            client=client,
            body=body,
        )
    ).parsed
