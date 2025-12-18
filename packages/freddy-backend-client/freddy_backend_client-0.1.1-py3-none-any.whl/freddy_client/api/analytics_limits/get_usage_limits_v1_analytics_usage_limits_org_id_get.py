from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.usage_limits_response import UsageLimitsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: str,
    *,
    month: int | None | Unset = UNSET,
    year: int | None | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_month: int | None | Unset
    if isinstance(month, Unset):
        json_month = UNSET
    else:
        json_month = month
    params["month"] = json_month

    json_year: int | None | Unset
    if isinstance(year, Unset):
        json_year = UNSET
    else:
        json_year = year
    params["year"] = json_year

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/analytics/usage/limits/{org_id}".format(
            org_id=quote(str(org_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | UsageLimitsResponse | None:
    if response.status_code == 200:
        response_200 = UsageLimitsResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | UsageLimitsResponse]:
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
    month: int | None | Unset = UNSET,
    year: int | None | Unset = UNSET,
) -> Response[HTTPValidationError | UsageLimitsResponse]:
    """Get Usage Limits

     Get usage limits for organization.

    Returns comprehensive usage limits including organization-level limits,
    API-level aggregated limits, and per-API-key breakdown.

    **Query Parameters:**
    - `month` (optional): Month to query (1-12), defaults to current month
    - `year` (optional): Year to query, defaults to current year

    **Response includes:**
    - Organization-level monthly limit, usage, utilization, and status
    - API-level aggregated usage against organization limit
    - Per-API-key breakdown with individual limits and status
    - Summary statistics (total keys, keys with limits, keys exceeded)

    **Status Values:**
    - `ok`: utilization < 80%
    - `warning`: 80% <= utilization < 100%
    - `exceeded`: utilization >= 100%
    - `no_limit`: No limit configured

    **Perfect for:**
    - Budget monitoring dashboards
    - Cost control and alerting
    - API key management
    - Usage forecasting

    Args:
        org_id (str):
        month (int | None | Unset): Month (1-12)
        year (int | None | Unset): Year

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UsageLimitsResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        month=month,
        year=year,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    month: int | None | Unset = UNSET,
    year: int | None | Unset = UNSET,
) -> HTTPValidationError | UsageLimitsResponse | None:
    """Get Usage Limits

     Get usage limits for organization.

    Returns comprehensive usage limits including organization-level limits,
    API-level aggregated limits, and per-API-key breakdown.

    **Query Parameters:**
    - `month` (optional): Month to query (1-12), defaults to current month
    - `year` (optional): Year to query, defaults to current year

    **Response includes:**
    - Organization-level monthly limit, usage, utilization, and status
    - API-level aggregated usage against organization limit
    - Per-API-key breakdown with individual limits and status
    - Summary statistics (total keys, keys with limits, keys exceeded)

    **Status Values:**
    - `ok`: utilization < 80%
    - `warning`: 80% <= utilization < 100%
    - `exceeded`: utilization >= 100%
    - `no_limit`: No limit configured

    **Perfect for:**
    - Budget monitoring dashboards
    - Cost control and alerting
    - API key management
    - Usage forecasting

    Args:
        org_id (str):
        month (int | None | Unset): Month (1-12)
        year (int | None | Unset): Year

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UsageLimitsResponse
    """

    return sync_detailed(
        org_id=org_id,
        client=client,
        month=month,
        year=year,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    month: int | None | Unset = UNSET,
    year: int | None | Unset = UNSET,
) -> Response[HTTPValidationError | UsageLimitsResponse]:
    """Get Usage Limits

     Get usage limits for organization.

    Returns comprehensive usage limits including organization-level limits,
    API-level aggregated limits, and per-API-key breakdown.

    **Query Parameters:**
    - `month` (optional): Month to query (1-12), defaults to current month
    - `year` (optional): Year to query, defaults to current year

    **Response includes:**
    - Organization-level monthly limit, usage, utilization, and status
    - API-level aggregated usage against organization limit
    - Per-API-key breakdown with individual limits and status
    - Summary statistics (total keys, keys with limits, keys exceeded)

    **Status Values:**
    - `ok`: utilization < 80%
    - `warning`: 80% <= utilization < 100%
    - `exceeded`: utilization >= 100%
    - `no_limit`: No limit configured

    **Perfect for:**
    - Budget monitoring dashboards
    - Cost control and alerting
    - API key management
    - Usage forecasting

    Args:
        org_id (str):
        month (int | None | Unset): Month (1-12)
        year (int | None | Unset): Year

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UsageLimitsResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        month=month,
        year=year,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    month: int | None | Unset = UNSET,
    year: int | None | Unset = UNSET,
) -> HTTPValidationError | UsageLimitsResponse | None:
    """Get Usage Limits

     Get usage limits for organization.

    Returns comprehensive usage limits including organization-level limits,
    API-level aggregated limits, and per-API-key breakdown.

    **Query Parameters:**
    - `month` (optional): Month to query (1-12), defaults to current month
    - `year` (optional): Year to query, defaults to current year

    **Response includes:**
    - Organization-level monthly limit, usage, utilization, and status
    - API-level aggregated usage against organization limit
    - Per-API-key breakdown with individual limits and status
    - Summary statistics (total keys, keys with limits, keys exceeded)

    **Status Values:**
    - `ok`: utilization < 80%
    - `warning`: 80% <= utilization < 100%
    - `exceeded`: utilization >= 100%
    - `no_limit`: No limit configured

    **Perfect for:**
    - Budget monitoring dashboards
    - Cost control and alerting
    - API key management
    - Usage forecasting

    Args:
        org_id (str):
        month (int | None | Unset): Month (1-12)
        year (int | None | Unset): Year

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UsageLimitsResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            client=client,
            month=month,
            year=year,
        )
    ).parsed
