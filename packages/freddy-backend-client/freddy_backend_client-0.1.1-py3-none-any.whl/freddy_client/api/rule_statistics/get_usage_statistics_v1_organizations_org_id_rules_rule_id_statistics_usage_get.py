from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.usage_statistics_response import UsageStatisticsResponse
from ...types import Response


def _get_kwargs(
    org_id: str,
    rule_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/organizations/{org_id}/rules/{rule_id}/statistics/usage".format(
            org_id=quote(str(org_id), safe=""),
            rule_id=quote(str(rule_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | UsageStatisticsResponse | None:
    if response.status_code == 200:
        response_200 = UsageStatisticsResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | UsageStatisticsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: str,
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | UsageStatisticsResponse]:
    """Get rule usage statistics

     Get usage statistics for a specific rule showing attachments by entity type.

    Args:
        org_id (str):
        rule_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UsageStatisticsResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        rule_id=rule_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | UsageStatisticsResponse | None:
    """Get rule usage statistics

     Get usage statistics for a specific rule showing attachments by entity type.

    Args:
        org_id (str):
        rule_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UsageStatisticsResponse
    """

    return sync_detailed(
        org_id=org_id,
        rule_id=rule_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | UsageStatisticsResponse]:
    """Get rule usage statistics

     Get usage statistics for a specific rule showing attachments by entity type.

    Args:
        org_id (str):
        rule_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UsageStatisticsResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        rule_id=rule_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | UsageStatisticsResponse | None:
    """Get rule usage statistics

     Get usage statistics for a specific rule showing attachments by entity type.

    Args:
        org_id (str):
        rule_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UsageStatisticsResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            rule_id=rule_id,
            client=client,
        )
    ).parsed
