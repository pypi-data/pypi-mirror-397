from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.neurons_trends_response import NeuronsTrendsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: str,
    *,
    months: int | Unset = 6,
    metric: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["months"] = months

    json_metric: None | str | Unset
    if isinstance(metric, Unset):
        json_metric = UNSET
    else:
        json_metric = metric
    params["metric"] = json_metric

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/analytics/usage/trends/{org_id}".format(
            org_id=quote(str(org_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | NeuronsTrendsResponse | None:
    if response.status_code == 200:
        response_200 = NeuronsTrendsResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | NeuronsTrendsResponse]:
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
    months: int | Unset = 6,
    metric: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | NeuronsTrendsResponse]:
    """Get Usage Trends

     Get trends analysis with optional metric filtering.

    Multi-month trend analysis for usage patterns, growth trajectories,
    and seasonal insights.

    **Metric Filtering:**
    - `metric=neurons` - Analyze only neurons trends
    - `metric=synapses` - Analyze only synapses trends
    - `metric=null` or omit - Analyze combined metrics

    **Deep Trend Analysis:**
    - Monthly Progression - Month-over-month usage evolution
    - Growth Patterns - Identify growth stages and acceleration trends
    - Seasonal Analysis - Detect seasonal usage patterns and cycles
    - Pattern Recognition - Identify recurring usage patterns
    - Growth Forecasting - Predictive modeling for future growth

    **Perfect for:**
    - Strategic Planning - Long-term usage strategy
    - Financial Forecasting - Budget planning and cost projections
    - Product Roadmaps - Feature prioritization based on usage trends

    Args:
        org_id (str):
        months (int | Unset): Number of months to analyze (3-12) Default: 6.
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | NeuronsTrendsResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        months=months,
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
    months: int | Unset = 6,
    metric: None | str | Unset = UNSET,
) -> HTTPValidationError | NeuronsTrendsResponse | None:
    """Get Usage Trends

     Get trends analysis with optional metric filtering.

    Multi-month trend analysis for usage patterns, growth trajectories,
    and seasonal insights.

    **Metric Filtering:**
    - `metric=neurons` - Analyze only neurons trends
    - `metric=synapses` - Analyze only synapses trends
    - `metric=null` or omit - Analyze combined metrics

    **Deep Trend Analysis:**
    - Monthly Progression - Month-over-month usage evolution
    - Growth Patterns - Identify growth stages and acceleration trends
    - Seasonal Analysis - Detect seasonal usage patterns and cycles
    - Pattern Recognition - Identify recurring usage patterns
    - Growth Forecasting - Predictive modeling for future growth

    **Perfect for:**
    - Strategic Planning - Long-term usage strategy
    - Financial Forecasting - Budget planning and cost projections
    - Product Roadmaps - Feature prioritization based on usage trends

    Args:
        org_id (str):
        months (int | Unset): Number of months to analyze (3-12) Default: 6.
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | NeuronsTrendsResponse
    """

    return sync_detailed(
        org_id=org_id,
        client=client,
        months=months,
        metric=metric,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    months: int | Unset = 6,
    metric: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | NeuronsTrendsResponse]:
    """Get Usage Trends

     Get trends analysis with optional metric filtering.

    Multi-month trend analysis for usage patterns, growth trajectories,
    and seasonal insights.

    **Metric Filtering:**
    - `metric=neurons` - Analyze only neurons trends
    - `metric=synapses` - Analyze only synapses trends
    - `metric=null` or omit - Analyze combined metrics

    **Deep Trend Analysis:**
    - Monthly Progression - Month-over-month usage evolution
    - Growth Patterns - Identify growth stages and acceleration trends
    - Seasonal Analysis - Detect seasonal usage patterns and cycles
    - Pattern Recognition - Identify recurring usage patterns
    - Growth Forecasting - Predictive modeling for future growth

    **Perfect for:**
    - Strategic Planning - Long-term usage strategy
    - Financial Forecasting - Budget planning and cost projections
    - Product Roadmaps - Feature prioritization based on usage trends

    Args:
        org_id (str):
        months (int | Unset): Number of months to analyze (3-12) Default: 6.
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | NeuronsTrendsResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        months=months,
        metric=metric,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    months: int | Unset = 6,
    metric: None | str | Unset = UNSET,
) -> HTTPValidationError | NeuronsTrendsResponse | None:
    """Get Usage Trends

     Get trends analysis with optional metric filtering.

    Multi-month trend analysis for usage patterns, growth trajectories,
    and seasonal insights.

    **Metric Filtering:**
    - `metric=neurons` - Analyze only neurons trends
    - `metric=synapses` - Analyze only synapses trends
    - `metric=null` or omit - Analyze combined metrics

    **Deep Trend Analysis:**
    - Monthly Progression - Month-over-month usage evolution
    - Growth Patterns - Identify growth stages and acceleration trends
    - Seasonal Analysis - Detect seasonal usage patterns and cycles
    - Pattern Recognition - Identify recurring usage patterns
    - Growth Forecasting - Predictive modeling for future growth

    **Perfect for:**
    - Strategic Planning - Long-term usage strategy
    - Financial Forecasting - Budget planning and cost projections
    - Product Roadmaps - Feature prioritization based on usage trends

    Args:
        org_id (str):
        months (int | Unset): Number of months to analyze (3-12) Default: 6.
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | NeuronsTrendsResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            client=client,
            months=months,
            metric=metric,
        )
    ).parsed
