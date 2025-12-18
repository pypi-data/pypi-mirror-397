from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.usage_analytics_response import UsageAnalyticsResponse
from ...types import UNSET, Response


def _get_kwargs(
    org_id: str,
    *,
    date: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["date"] = date

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/analytics/usage/hourly/{org_id}".format(
            org_id=quote(str(org_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | UsageAnalyticsResponse | None:
    if response.status_code == 200:
        response_200 = UsageAnalyticsResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | UsageAnalyticsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    date: str,
) -> Response[HTTPValidationError | UsageAnalyticsResponse]:
    """Get Hourly Usage

     Get hourly usage analytics for graphing.

    Returns hour-by-hour breakdown for detailed analysis.

    **Perfect for:**
    - Real-time dashboards - Live usage monitoring
    - Performance optimization - Peak load analysis
    - Capacity planning - Hour-based scaling decisions

    Args:
        org_id (str):
        date (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UsageAnalyticsResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        date=date,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    date: str,
) -> HTTPValidationError | UsageAnalyticsResponse | None:
    """Get Hourly Usage

     Get hourly usage analytics for graphing.

    Returns hour-by-hour breakdown for detailed analysis.

    **Perfect for:**
    - Real-time dashboards - Live usage monitoring
    - Performance optimization - Peak load analysis
    - Capacity planning - Hour-based scaling decisions

    Args:
        org_id (str):
        date (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UsageAnalyticsResponse
    """

    return sync_detailed(
        org_id=org_id,
        client=client,
        date=date,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    date: str,
) -> Response[HTTPValidationError | UsageAnalyticsResponse]:
    """Get Hourly Usage

     Get hourly usage analytics for graphing.

    Returns hour-by-hour breakdown for detailed analysis.

    **Perfect for:**
    - Real-time dashboards - Live usage monitoring
    - Performance optimization - Peak load analysis
    - Capacity planning - Hour-based scaling decisions

    Args:
        org_id (str):
        date (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UsageAnalyticsResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        date=date,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    date: str,
) -> HTTPValidationError | UsageAnalyticsResponse | None:
    """Get Hourly Usage

     Get hourly usage analytics for graphing.

    Returns hour-by-hour breakdown for detailed analysis.

    **Perfect for:**
    - Real-time dashboards - Live usage monitoring
    - Performance optimization - Peak load analysis
    - Capacity planning - Hour-based scaling decisions

    Args:
        org_id (str):
        date (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UsageAnalyticsResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            client=client,
            date=date,
        )
    ).parsed
