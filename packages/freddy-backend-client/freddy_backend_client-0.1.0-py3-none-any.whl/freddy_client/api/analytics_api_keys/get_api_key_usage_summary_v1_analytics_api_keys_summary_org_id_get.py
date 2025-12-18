from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_key_usage_summary import ApiKeyUsageSummary
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: str,
    *,
    year: int | Unset = UNSET,
    month: int | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["year"] = year

    params["month"] = month

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/analytics/api-keys/summary/{org_id}".format(
            org_id=quote(str(org_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ApiKeyUsageSummary | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ApiKeyUsageSummary.from_dict(response.json())

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
) -> Response[ApiKeyUsageSummary | HTTPValidationError]:
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
    year: int | Unset = UNSET,
    month: int | Unset = UNSET,
) -> Response[ApiKeyUsageSummary | HTTPValidationError]:
    """Get Api Key Usage Summary

     Get API Key Usage Summary.

    Returns summary statistics for API key usage only (programmatic access).
    This excludes bearer token usage from web applications.

    **Use Case:** API Management Pages - show only programmatic usage

    **Metrics:**
    - Total API key requests
    - Total cost in CHF
    - Average cost per request
    - Total synapses
    - Total neurons

    Args:
        org_id (str):
        year (int | Unset): Year
        month (int | Unset): Month

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ApiKeyUsageSummary | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        year=year,
        month=month,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    year: int | Unset = UNSET,
    month: int | Unset = UNSET,
) -> ApiKeyUsageSummary | HTTPValidationError | None:
    """Get Api Key Usage Summary

     Get API Key Usage Summary.

    Returns summary statistics for API key usage only (programmatic access).
    This excludes bearer token usage from web applications.

    **Use Case:** API Management Pages - show only programmatic usage

    **Metrics:**
    - Total API key requests
    - Total cost in CHF
    - Average cost per request
    - Total synapses
    - Total neurons

    Args:
        org_id (str):
        year (int | Unset): Year
        month (int | Unset): Month

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ApiKeyUsageSummary | HTTPValidationError
    """

    return sync_detailed(
        org_id=org_id,
        client=client,
        year=year,
        month=month,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    year: int | Unset = UNSET,
    month: int | Unset = UNSET,
) -> Response[ApiKeyUsageSummary | HTTPValidationError]:
    """Get Api Key Usage Summary

     Get API Key Usage Summary.

    Returns summary statistics for API key usage only (programmatic access).
    This excludes bearer token usage from web applications.

    **Use Case:** API Management Pages - show only programmatic usage

    **Metrics:**
    - Total API key requests
    - Total cost in CHF
    - Average cost per request
    - Total synapses
    - Total neurons

    Args:
        org_id (str):
        year (int | Unset): Year
        month (int | Unset): Month

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ApiKeyUsageSummary | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        year=year,
        month=month,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    year: int | Unset = UNSET,
    month: int | Unset = UNSET,
) -> ApiKeyUsageSummary | HTTPValidationError | None:
    """Get Api Key Usage Summary

     Get API Key Usage Summary.

    Returns summary statistics for API key usage only (programmatic access).
    This excludes bearer token usage from web applications.

    **Use Case:** API Management Pages - show only programmatic usage

    **Metrics:**
    - Total API key requests
    - Total cost in CHF
    - Average cost per request
    - Total synapses
    - Total neurons

    Args:
        org_id (str):
        year (int | Unset): Year
        month (int | Unset): Month

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ApiKeyUsageSummary | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            client=client,
            year=year,
            month=month,
        )
    ).parsed
