from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.neurons_analytics_dashboard_response import (
    NeuronsAnalyticsDashboardResponse,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: str,
    *,
    days: int | Unset = 30,
    metric: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["days"] = days

    json_metric: None | str | Unset
    if isinstance(metric, Unset):
        json_metric = UNSET
    else:
        json_metric = metric
    params["metric"] = json_metric

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/analytics/usage/dashboard/{org_id}".format(
            org_id=quote(str(org_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | NeuronsAnalyticsDashboardResponse | None:
    if response.status_code == 200:
        response_200 = NeuronsAnalyticsDashboardResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | NeuronsAnalyticsDashboardResponse]:
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
    days: int | Unset = 30,
    metric: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | NeuronsAnalyticsDashboardResponse]:
    """Get Usage Dashboard

     Get comprehensive analytics dashboard with optional metric filtering.

    Executive-level analytics with comprehensive insights, trends,
    and optimization recommendations.

    **Metric Filtering:**
    - `metric=neurons` - Analyze only neurons usage
    - `metric=synapses` - Analyze only synapses usage
    - `metric=null` or omit - Analyze combined metrics

    **What You Get:**
    - Current Period Summary - Key metrics for the analysis period
    - Daily Trends - Day-by-day usage patterns and trends
    - Usage Patterns - Peak hours, weekday/weekend analysis
    - Efficiency Metrics - Cost efficiency and optimization scores
    - Predictive Projections - Monthly usage and cost forecasts
    - Actionable Insights - AI-generated recommendations

    **Perfect for:**
    - Executive Dashboards - High-level usage overview
    - Cost Management - Track spending and efficiency
    - Capacity Planning - Forecast future requirements
    - Performance Monitoring - Monitor generation efficiency

    Args:
        org_id (str):
        days (int | Unset): Number of days to analyze (7-90) Default: 30.
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | NeuronsAnalyticsDashboardResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        days=days,
        metric=metric,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    days: int | Unset = 30,
    metric: None | str | Unset = UNSET,
) -> HTTPValidationError | NeuronsAnalyticsDashboardResponse | None:
    """Get Usage Dashboard

     Get comprehensive analytics dashboard with optional metric filtering.

    Executive-level analytics with comprehensive insights, trends,
    and optimization recommendations.

    **Metric Filtering:**
    - `metric=neurons` - Analyze only neurons usage
    - `metric=synapses` - Analyze only synapses usage
    - `metric=null` or omit - Analyze combined metrics

    **What You Get:**
    - Current Period Summary - Key metrics for the analysis period
    - Daily Trends - Day-by-day usage patterns and trends
    - Usage Patterns - Peak hours, weekday/weekend analysis
    - Efficiency Metrics - Cost efficiency and optimization scores
    - Predictive Projections - Monthly usage and cost forecasts
    - Actionable Insights - AI-generated recommendations

    **Perfect for:**
    - Executive Dashboards - High-level usage overview
    - Cost Management - Track spending and efficiency
    - Capacity Planning - Forecast future requirements
    - Performance Monitoring - Monitor generation efficiency

    Args:
        org_id (str):
        days (int | Unset): Number of days to analyze (7-90) Default: 30.
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | NeuronsAnalyticsDashboardResponse
    """

    return sync_detailed(
        org_id=org_id,
        client=client,
        days=days,
        metric=metric,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    days: int | Unset = 30,
    metric: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | NeuronsAnalyticsDashboardResponse]:
    """Get Usage Dashboard

     Get comprehensive analytics dashboard with optional metric filtering.

    Executive-level analytics with comprehensive insights, trends,
    and optimization recommendations.

    **Metric Filtering:**
    - `metric=neurons` - Analyze only neurons usage
    - `metric=synapses` - Analyze only synapses usage
    - `metric=null` or omit - Analyze combined metrics

    **What You Get:**
    - Current Period Summary - Key metrics for the analysis period
    - Daily Trends - Day-by-day usage patterns and trends
    - Usage Patterns - Peak hours, weekday/weekend analysis
    - Efficiency Metrics - Cost efficiency and optimization scores
    - Predictive Projections - Monthly usage and cost forecasts
    - Actionable Insights - AI-generated recommendations

    **Perfect for:**
    - Executive Dashboards - High-level usage overview
    - Cost Management - Track spending and efficiency
    - Capacity Planning - Forecast future requirements
    - Performance Monitoring - Monitor generation efficiency

    Args:
        org_id (str):
        days (int | Unset): Number of days to analyze (7-90) Default: 30.
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | NeuronsAnalyticsDashboardResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        days=days,
        metric=metric,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    days: int | Unset = 30,
    metric: None | str | Unset = UNSET,
) -> HTTPValidationError | NeuronsAnalyticsDashboardResponse | None:
    """Get Usage Dashboard

     Get comprehensive analytics dashboard with optional metric filtering.

    Executive-level analytics with comprehensive insights, trends,
    and optimization recommendations.

    **Metric Filtering:**
    - `metric=neurons` - Analyze only neurons usage
    - `metric=synapses` - Analyze only synapses usage
    - `metric=null` or omit - Analyze combined metrics

    **What You Get:**
    - Current Period Summary - Key metrics for the analysis period
    - Daily Trends - Day-by-day usage patterns and trends
    - Usage Patterns - Peak hours, weekday/weekend analysis
    - Efficiency Metrics - Cost efficiency and optimization scores
    - Predictive Projections - Monthly usage and cost forecasts
    - Actionable Insights - AI-generated recommendations

    **Perfect for:**
    - Executive Dashboards - High-level usage overview
    - Cost Management - Track spending and efficiency
    - Capacity Planning - Forecast future requirements
    - Performance Monitoring - Monitor generation efficiency

    Args:
        org_id (str):
        days (int | Unset): Number of days to analyze (7-90) Default: 30.
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | NeuronsAnalyticsDashboardResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            client=client,
            days=days,
            metric=metric,
        )
    ).parsed
