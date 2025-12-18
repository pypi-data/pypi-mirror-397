from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.neurons_heatmap_response import NeuronsHeatmapResponse
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
        "url": "/v1/analytics/usage/heatmap/{org_id}".format(
            org_id=quote(str(org_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | NeuronsHeatmapResponse | None:
    if response.status_code == 200:
        response_200 = NeuronsHeatmapResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | NeuronsHeatmapResponse]:
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
) -> Response[HTTPValidationError | NeuronsHeatmapResponse]:
    """Get Usage Heatmap

     Get usage heatmap with optional metric filtering.

    Visual usage pattern analysis showing generation patterns
    by hour and day of week.

    **Metric Filtering:**
    - `metric=neurons` - Heatmap for neurons usage
    - `metric=synapses` - Heatmap for synapses usage
    - `metric=null` or omit - Heatmap for combined metrics

    **Heatmap Visualization:**
    - 24-Hour Analysis - Usage patterns across all hours of the day
    - 7-Day Analysis - Weekly usage patterns (Monday-Sunday)
    - Peak Detection - Identify peak usage hours and days
    - Low Usage Periods - Find opportunities for maintenance windows

    **Perfect for:**
    - Infrastructure Planning - Right-size infrastructure based on usage
    - Cost Management - Schedule expensive operations during low-usage periods
    - User Experience - Ensure adequate capacity during peak usage times

    Args:
        org_id (str):
        days (int | Unset): Number of days to analyze (7-90) Default: 30.
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | NeuronsHeatmapResponse]
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
) -> HTTPValidationError | NeuronsHeatmapResponse | None:
    """Get Usage Heatmap

     Get usage heatmap with optional metric filtering.

    Visual usage pattern analysis showing generation patterns
    by hour and day of week.

    **Metric Filtering:**
    - `metric=neurons` - Heatmap for neurons usage
    - `metric=synapses` - Heatmap for synapses usage
    - `metric=null` or omit - Heatmap for combined metrics

    **Heatmap Visualization:**
    - 24-Hour Analysis - Usage patterns across all hours of the day
    - 7-Day Analysis - Weekly usage patterns (Monday-Sunday)
    - Peak Detection - Identify peak usage hours and days
    - Low Usage Periods - Find opportunities for maintenance windows

    **Perfect for:**
    - Infrastructure Planning - Right-size infrastructure based on usage
    - Cost Management - Schedule expensive operations during low-usage periods
    - User Experience - Ensure adequate capacity during peak usage times

    Args:
        org_id (str):
        days (int | Unset): Number of days to analyze (7-90) Default: 30.
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | NeuronsHeatmapResponse
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
) -> Response[HTTPValidationError | NeuronsHeatmapResponse]:
    """Get Usage Heatmap

     Get usage heatmap with optional metric filtering.

    Visual usage pattern analysis showing generation patterns
    by hour and day of week.

    **Metric Filtering:**
    - `metric=neurons` - Heatmap for neurons usage
    - `metric=synapses` - Heatmap for synapses usage
    - `metric=null` or omit - Heatmap for combined metrics

    **Heatmap Visualization:**
    - 24-Hour Analysis - Usage patterns across all hours of the day
    - 7-Day Analysis - Weekly usage patterns (Monday-Sunday)
    - Peak Detection - Identify peak usage hours and days
    - Low Usage Periods - Find opportunities for maintenance windows

    **Perfect for:**
    - Infrastructure Planning - Right-size infrastructure based on usage
    - Cost Management - Schedule expensive operations during low-usage periods
    - User Experience - Ensure adequate capacity during peak usage times

    Args:
        org_id (str):
        days (int | Unset): Number of days to analyze (7-90) Default: 30.
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | NeuronsHeatmapResponse]
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
) -> HTTPValidationError | NeuronsHeatmapResponse | None:
    """Get Usage Heatmap

     Get usage heatmap with optional metric filtering.

    Visual usage pattern analysis showing generation patterns
    by hour and day of week.

    **Metric Filtering:**
    - `metric=neurons` - Heatmap for neurons usage
    - `metric=synapses` - Heatmap for synapses usage
    - `metric=null` or omit - Heatmap for combined metrics

    **Heatmap Visualization:**
    - 24-Hour Analysis - Usage patterns across all hours of the day
    - 7-Day Analysis - Weekly usage patterns (Monday-Sunday)
    - Peak Detection - Identify peak usage hours and days
    - Low Usage Periods - Find opportunities for maintenance windows

    **Perfect for:**
    - Infrastructure Planning - Right-size infrastructure based on usage
    - Cost Management - Schedule expensive operations during low-usage periods
    - User Experience - Ensure adequate capacity during peak usage times

    Args:
        org_id (str):
        days (int | Unset): Number of days to analyze (7-90) Default: 30.
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | NeuronsHeatmapResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            client=client,
            days=days,
            metric=metric,
        )
    ).parsed
