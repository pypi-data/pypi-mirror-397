from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.neurons_benchmarks_response import NeuronsBenchmarksResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: str,
    *,
    month: int,
    year: int,
    metric: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["month"] = month

    params["year"] = year

    json_metric: None | str | Unset
    if isinstance(metric, Unset):
        json_metric = UNSET
    else:
        json_metric = metric
    params["metric"] = json_metric

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/analytics/usage/benchmarks/{org_id}".format(
            org_id=quote(str(org_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | NeuronsBenchmarksResponse | None:
    if response.status_code == 200:
        response_200 = NeuronsBenchmarksResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | NeuronsBenchmarksResponse]:
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
    month: int,
    year: int,
    metric: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | NeuronsBenchmarksResponse]:
    """Get Usage Benchmarks

     Get performance benchmarks with optional metric filtering.

    Competitive benchmarking analysis comparing your organization's usage
    against industry averages and best practices.

    **Metric Filtering:**
    - `metric=neurons` - Benchmark neurons usage
    - `metric=synapses` - Benchmark synapses usage
    - `metric=null` or omit - Benchmark combined metrics

    **Benchmark Categories:**
    - Industry Averages - Anonymous comparison with similar organizations
    - Percentile Rankings - Your position relative to all organizations
    - Efficiency Benchmarks - Cost efficiency vs. industry standards
    - Usage Pattern Benchmarks - Comparison of usage patterns

    **Perfect for:**
    - Competitive Positioning - Understand your market position
    - Performance Goals - Set realistic improvement targets
    - Best Practice Adoption - Learn from top performers

    Args:
        org_id (str):
        month (int):
        year (int):
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | NeuronsBenchmarksResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        month=month,
        year=year,
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
    month: int,
    year: int,
    metric: None | str | Unset = UNSET,
) -> HTTPValidationError | NeuronsBenchmarksResponse | None:
    """Get Usage Benchmarks

     Get performance benchmarks with optional metric filtering.

    Competitive benchmarking analysis comparing your organization's usage
    against industry averages and best practices.

    **Metric Filtering:**
    - `metric=neurons` - Benchmark neurons usage
    - `metric=synapses` - Benchmark synapses usage
    - `metric=null` or omit - Benchmark combined metrics

    **Benchmark Categories:**
    - Industry Averages - Anonymous comparison with similar organizations
    - Percentile Rankings - Your position relative to all organizations
    - Efficiency Benchmarks - Cost efficiency vs. industry standards
    - Usage Pattern Benchmarks - Comparison of usage patterns

    **Perfect for:**
    - Competitive Positioning - Understand your market position
    - Performance Goals - Set realistic improvement targets
    - Best Practice Adoption - Learn from top performers

    Args:
        org_id (str):
        month (int):
        year (int):
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | NeuronsBenchmarksResponse
    """

    return sync_detailed(
        org_id=org_id,
        client=client,
        month=month,
        year=year,
        metric=metric,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    month: int,
    year: int,
    metric: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | NeuronsBenchmarksResponse]:
    """Get Usage Benchmarks

     Get performance benchmarks with optional metric filtering.

    Competitive benchmarking analysis comparing your organization's usage
    against industry averages and best practices.

    **Metric Filtering:**
    - `metric=neurons` - Benchmark neurons usage
    - `metric=synapses` - Benchmark synapses usage
    - `metric=null` or omit - Benchmark combined metrics

    **Benchmark Categories:**
    - Industry Averages - Anonymous comparison with similar organizations
    - Percentile Rankings - Your position relative to all organizations
    - Efficiency Benchmarks - Cost efficiency vs. industry standards
    - Usage Pattern Benchmarks - Comparison of usage patterns

    **Perfect for:**
    - Competitive Positioning - Understand your market position
    - Performance Goals - Set realistic improvement targets
    - Best Practice Adoption - Learn from top performers

    Args:
        org_id (str):
        month (int):
        year (int):
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | NeuronsBenchmarksResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        month=month,
        year=year,
        metric=metric,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    month: int,
    year: int,
    metric: None | str | Unset = UNSET,
) -> HTTPValidationError | NeuronsBenchmarksResponse | None:
    """Get Usage Benchmarks

     Get performance benchmarks with optional metric filtering.

    Competitive benchmarking analysis comparing your organization's usage
    against industry averages and best practices.

    **Metric Filtering:**
    - `metric=neurons` - Benchmark neurons usage
    - `metric=synapses` - Benchmark synapses usage
    - `metric=null` or omit - Benchmark combined metrics

    **Benchmark Categories:**
    - Industry Averages - Anonymous comparison with similar organizations
    - Percentile Rankings - Your position relative to all organizations
    - Efficiency Benchmarks - Cost efficiency vs. industry standards
    - Usage Pattern Benchmarks - Comparison of usage patterns

    **Perfect for:**
    - Competitive Positioning - Understand your market position
    - Performance Goals - Set realistic improvement targets
    - Best Practice Adoption - Learn from top performers

    Args:
        org_id (str):
        month (int):
        year (int):
        metric (None | str | Unset): Metric type to analyze: 'neurons', 'synapses', or null for
            combined

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | NeuronsBenchmarksResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            client=client,
            month=month,
            year=year,
            metric=metric,
        )
    ).parsed
