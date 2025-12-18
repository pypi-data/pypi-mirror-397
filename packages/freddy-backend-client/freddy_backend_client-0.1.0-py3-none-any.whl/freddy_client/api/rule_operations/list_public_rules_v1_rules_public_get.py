from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.rule_category import RuleCategory
from ...models.rule_list_paginated_response import RuleListPaginatedResponse
from ...models.rule_scope import RuleScope
from ...models.rule_type import RuleType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    category: None | RuleCategory | Unset = UNSET,
    rule_type: None | RuleType | Unset = UNSET,
    scope: None | RuleScope | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["skip"] = skip

    params["limit"] = limit

    json_category: None | str | Unset
    if isinstance(category, Unset):
        json_category = UNSET
    elif isinstance(category, RuleCategory):
        json_category = category.value
    else:
        json_category = category
    params["category"] = json_category

    json_rule_type: None | str | Unset
    if isinstance(rule_type, Unset):
        json_rule_type = UNSET
    elif isinstance(rule_type, RuleType):
        json_rule_type = rule_type.value
    else:
        json_rule_type = rule_type
    params["rule_type"] = json_rule_type

    json_scope: None | str | Unset
    if isinstance(scope, Unset):
        json_scope = UNSET
    elif isinstance(scope, RuleScope):
        json_scope = scope.value
    else:
        json_scope = scope
    params["scope"] = json_scope

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/rules/public",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RuleListPaginatedResponse | None:
    if response.status_code == 200:
        response_200 = RuleListPaginatedResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | RuleListPaginatedResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    category: None | RuleCategory | Unset = UNSET,
    rule_type: None | RuleType | Unset = UNSET,
    scope: None | RuleScope | Unset = UNSET,
) -> Response[HTTPValidationError | RuleListPaginatedResponse]:
    """List public rules

     List all public rules from all organizations.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        category (None | RuleCategory | Unset):
        rule_type (None | RuleType | Unset):
        scope (None | RuleScope | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RuleListPaginatedResponse]
    """

    kwargs = _get_kwargs(
        skip=skip,
        limit=limit,
        category=category,
        rule_type=rule_type,
        scope=scope,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    category: None | RuleCategory | Unset = UNSET,
    rule_type: None | RuleType | Unset = UNSET,
    scope: None | RuleScope | Unset = UNSET,
) -> HTTPValidationError | RuleListPaginatedResponse | None:
    """List public rules

     List all public rules from all organizations.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        category (None | RuleCategory | Unset):
        rule_type (None | RuleType | Unset):
        scope (None | RuleScope | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RuleListPaginatedResponse
    """

    return sync_detailed(
        client=client,
        skip=skip,
        limit=limit,
        category=category,
        rule_type=rule_type,
        scope=scope,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    category: None | RuleCategory | Unset = UNSET,
    rule_type: None | RuleType | Unset = UNSET,
    scope: None | RuleScope | Unset = UNSET,
) -> Response[HTTPValidationError | RuleListPaginatedResponse]:
    """List public rules

     List all public rules from all organizations.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        category (None | RuleCategory | Unset):
        rule_type (None | RuleType | Unset):
        scope (None | RuleScope | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RuleListPaginatedResponse]
    """

    kwargs = _get_kwargs(
        skip=skip,
        limit=limit,
        category=category,
        rule_type=rule_type,
        scope=scope,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    category: None | RuleCategory | Unset = UNSET,
    rule_type: None | RuleType | Unset = UNSET,
    scope: None | RuleScope | Unset = UNSET,
) -> HTTPValidationError | RuleListPaginatedResponse | None:
    """List public rules

     List all public rules from all organizations.

    Args:
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.
        category (None | RuleCategory | Unset):
        rule_type (None | RuleType | Unset):
        scope (None | RuleScope | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RuleListPaginatedResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            skip=skip,
            limit=limit,
            category=category,
            rule_type=rule_type,
            scope=scope,
        )
    ).parsed
