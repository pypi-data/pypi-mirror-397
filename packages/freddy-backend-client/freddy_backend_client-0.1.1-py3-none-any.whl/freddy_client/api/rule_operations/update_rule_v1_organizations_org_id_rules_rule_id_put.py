from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.rule_detail_response import RuleDetailResponse
from ...models.rule_update_request import RuleUpdateRequest
from ...types import Response


def _get_kwargs(
    org_id: str,
    rule_id: str,
    *,
    body: RuleUpdateRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/organizations/{org_id}/rules/{rule_id}".format(
            org_id=quote(str(org_id), safe=""),
            rule_id=quote(str(rule_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RuleDetailResponse | None:
    if response.status_code == 200:
        response_200 = RuleDetailResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | RuleDetailResponse]:
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
    body: RuleUpdateRequest,
) -> Response[HTTPValidationError | RuleDetailResponse]:
    """Update a rule

     Update an existing rule. Requires edit or owner access.

    Args:
        org_id (str):
        rule_id (str):
        body (RuleUpdateRequest): Request schema for updating a rule.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RuleDetailResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        rule_id=rule_id,
        body=body,
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
    body: RuleUpdateRequest,
) -> HTTPValidationError | RuleDetailResponse | None:
    """Update a rule

     Update an existing rule. Requires edit or owner access.

    Args:
        org_id (str):
        rule_id (str):
        body (RuleUpdateRequest): Request schema for updating a rule.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RuleDetailResponse
    """

    return sync_detailed(
        org_id=org_id,
        rule_id=rule_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RuleUpdateRequest,
) -> Response[HTTPValidationError | RuleDetailResponse]:
    """Update a rule

     Update an existing rule. Requires edit or owner access.

    Args:
        org_id (str):
        rule_id (str):
        body (RuleUpdateRequest): Request schema for updating a rule.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RuleDetailResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        rule_id=rule_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: RuleUpdateRequest,
) -> HTTPValidationError | RuleDetailResponse | None:
    """Update a rule

     Update an existing rule. Requires edit or owner access.

    Args:
        org_id (str):
        rule_id (str):
        body (RuleUpdateRequest): Request schema for updating a rule.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RuleDetailResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            rule_id=rule_id,
            client=client,
            body=body,
        )
    ).parsed
