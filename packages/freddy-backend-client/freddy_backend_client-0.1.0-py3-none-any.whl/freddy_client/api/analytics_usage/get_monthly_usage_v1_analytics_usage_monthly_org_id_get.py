from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.usage_analytics_response import UsageAnalyticsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: str,
    *,
    year: int,
    month: int | None | Unset = UNSET,
    months: int | Unset = 12,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["year"] = year

    json_month: int | None | Unset
    if isinstance(month, Unset):
        json_month = UNSET
    else:
        json_month = month
    params["month"] = json_month

    params["months"] = months

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/analytics/usage/monthly/{org_id}".format(
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
    year: int,
    month: int | None | Unset = UNSET,
    months: int | Unset = 12,
) -> Response[HTTPValidationError | UsageAnalyticsResponse]:
    """Get Monthly Usage

     Get monthly usage analytics for graphing.

    Returns month-by-month breakdown for detailed trend analysis.

    **Perfect for:**
    - Monthly reports - Detailed usage tracking
    - Trend analysis - Seasonal usage patterns
    - Budget monitoring - Monthly cost tracking

    Args:
        org_id (str):
        year (int):
        month (int | None | Unset): Month for validation
        months (int | Unset): Number of months to include Default: 12.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UsageAnalyticsResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        year=year,
        month=month,
        months=months,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    year: int,
    month: int | None | Unset = UNSET,
    months: int | Unset = 12,
) -> HTTPValidationError | UsageAnalyticsResponse | None:
    """Get Monthly Usage

     Get monthly usage analytics for graphing.

    Returns month-by-month breakdown for detailed trend analysis.

    **Perfect for:**
    - Monthly reports - Detailed usage tracking
    - Trend analysis - Seasonal usage patterns
    - Budget monitoring - Monthly cost tracking

    Args:
        org_id (str):
        year (int):
        month (int | None | Unset): Month for validation
        months (int | Unset): Number of months to include Default: 12.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UsageAnalyticsResponse
    """

    return sync_detailed(
        org_id=org_id,
        client=client,
        year=year,
        month=month,
        months=months,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    year: int,
    month: int | None | Unset = UNSET,
    months: int | Unset = 12,
) -> Response[HTTPValidationError | UsageAnalyticsResponse]:
    """Get Monthly Usage

     Get monthly usage analytics for graphing.

    Returns month-by-month breakdown for detailed trend analysis.

    **Perfect for:**
    - Monthly reports - Detailed usage tracking
    - Trend analysis - Seasonal usage patterns
    - Budget monitoring - Monthly cost tracking

    Args:
        org_id (str):
        year (int):
        month (int | None | Unset): Month for validation
        months (int | Unset): Number of months to include Default: 12.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UsageAnalyticsResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        year=year,
        month=month,
        months=months,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    year: int,
    month: int | None | Unset = UNSET,
    months: int | Unset = 12,
) -> HTTPValidationError | UsageAnalyticsResponse | None:
    """Get Monthly Usage

     Get monthly usage analytics for graphing.

    Returns month-by-month breakdown for detailed trend analysis.

    **Perfect for:**
    - Monthly reports - Detailed usage tracking
    - Trend analysis - Seasonal usage patterns
    - Budget monitoring - Monthly cost tracking

    Args:
        org_id (str):
        year (int):
        month (int | None | Unset): Month for validation
        months (int | Unset): Number of months to include Default: 12.

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
            year=year,
            month=month,
            months=months,
        )
    ).parsed
