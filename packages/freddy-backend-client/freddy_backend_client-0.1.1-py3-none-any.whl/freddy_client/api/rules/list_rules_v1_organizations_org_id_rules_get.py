from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.entity_type import EntityType
from ...models.http_validation_error import HTTPValidationError
from ...models.rule_category import RuleCategory
from ...models.rule_list_paginated_response import RuleListPaginatedResponse
from ...models.rule_scope import RuleScope
from ...models.rule_type import RuleType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: str,
    *,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: None | str | Unset = UNSET,
    category: None | RuleCategory | Unset = UNSET,
    rule_type: None | RuleType | Unset = UNSET,
    scope: None | RuleScope | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
    is_public: bool | None | Unset = UNSET,
    entity_type: EntityType | None | Unset = UNSET,
    entity_id: None | str | Unset = UNSET,
    attached_only: bool | None | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["skip"] = skip

    params["limit"] = limit

    json_search: None | str | Unset
    if isinstance(search, Unset):
        json_search = UNSET
    else:
        json_search = search
    params["search"] = json_search

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

    json_is_active: bool | None | Unset
    if isinstance(is_active, Unset):
        json_is_active = UNSET
    else:
        json_is_active = is_active
    params["is_active"] = json_is_active

    json_is_public: bool | None | Unset
    if isinstance(is_public, Unset):
        json_is_public = UNSET
    else:
        json_is_public = is_public
    params["is_public"] = json_is_public

    json_entity_type: None | str | Unset
    if isinstance(entity_type, Unset):
        json_entity_type = UNSET
    elif isinstance(entity_type, EntityType):
        json_entity_type = entity_type.value
    else:
        json_entity_type = entity_type
    params["entity_type"] = json_entity_type

    json_entity_id: None | str | Unset
    if isinstance(entity_id, Unset):
        json_entity_id = UNSET
    else:
        json_entity_id = entity_id
    params["entity_id"] = json_entity_id

    json_attached_only: bool | None | Unset
    if isinstance(attached_only, Unset):
        json_attached_only = UNSET
    else:
        json_attached_only = attached_only
    params["attached_only"] = json_attached_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/organizations/{org_id}/rules".format(
            org_id=quote(str(org_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | RuleListPaginatedResponse | None:
    if response.status_code == 200:
        response_200 = RuleListPaginatedResponse.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | HTTPValidationError | RuleListPaginatedResponse]:
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
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: None | str | Unset = UNSET,
    category: None | RuleCategory | Unset = UNSET,
    rule_type: None | RuleType | Unset = UNSET,
    scope: None | RuleScope | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
    is_public: bool | None | Unset = UNSET,
    entity_type: EntityType | None | Unset = UNSET,
    entity_id: None | str | Unset = UNSET,
    attached_only: bool | None | Unset = UNSET,
) -> Response[Any | HTTPValidationError | RuleListPaginatedResponse]:
    """List rules

     List all rules in an organization with pagination, filtering, and search.

    Args:
        org_id (str):
        skip (int | Unset): Number of records to skip for pagination Default: 0.
        limit (int | Unset): Maximum number of records to return (1-100) Default: 100.
        search (None | str | Unset): Search query to match against name, description, and content
        category (None | RuleCategory | Unset): Filter by category (safety, professional,
            creative, technical, custom)
        rule_type (None | RuleType | Unset): Filter by rule type (behavior, guardrails,
            formatting, context, content_policy, constraint)
        scope (None | RuleScope | Unset): Filter by scope (global, organization, model, assistant,
            user, vector_store)
        is_active (bool | None | Unset): Filter by active status (true/false)
        is_public (bool | None | Unset): Filter by public status (true/false)
        entity_type (EntityType | None | Unset): Filter by entity type (assistant, vector_store,
            user, model, organization)
        entity_id (None | str | Unset): Filter by specific entity ID (e.g., asst_123, vs_456).
            Requires entity_type if provided.
        attached_only (bool | None | Unset): Filter by attachment status - true: only attached
            rules, false: only unattached rules

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | RuleListPaginatedResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        rule_type=rule_type,
        scope=scope,
        is_active=is_active,
        is_public=is_public,
        entity_type=entity_type,
        entity_id=entity_id,
        attached_only=attached_only,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: None | str | Unset = UNSET,
    category: None | RuleCategory | Unset = UNSET,
    rule_type: None | RuleType | Unset = UNSET,
    scope: None | RuleScope | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
    is_public: bool | None | Unset = UNSET,
    entity_type: EntityType | None | Unset = UNSET,
    entity_id: None | str | Unset = UNSET,
    attached_only: bool | None | Unset = UNSET,
) -> Any | HTTPValidationError | RuleListPaginatedResponse | None:
    """List rules

     List all rules in an organization with pagination, filtering, and search.

    Args:
        org_id (str):
        skip (int | Unset): Number of records to skip for pagination Default: 0.
        limit (int | Unset): Maximum number of records to return (1-100) Default: 100.
        search (None | str | Unset): Search query to match against name, description, and content
        category (None | RuleCategory | Unset): Filter by category (safety, professional,
            creative, technical, custom)
        rule_type (None | RuleType | Unset): Filter by rule type (behavior, guardrails,
            formatting, context, content_policy, constraint)
        scope (None | RuleScope | Unset): Filter by scope (global, organization, model, assistant,
            user, vector_store)
        is_active (bool | None | Unset): Filter by active status (true/false)
        is_public (bool | None | Unset): Filter by public status (true/false)
        entity_type (EntityType | None | Unset): Filter by entity type (assistant, vector_store,
            user, model, organization)
        entity_id (None | str | Unset): Filter by specific entity ID (e.g., asst_123, vs_456).
            Requires entity_type if provided.
        attached_only (bool | None | Unset): Filter by attachment status - true: only attached
            rules, false: only unattached rules

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | RuleListPaginatedResponse
    """

    return sync_detailed(
        org_id=org_id,
        client=client,
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        rule_type=rule_type,
        scope=scope,
        is_active=is_active,
        is_public=is_public,
        entity_type=entity_type,
        entity_id=entity_id,
        attached_only=attached_only,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: None | str | Unset = UNSET,
    category: None | RuleCategory | Unset = UNSET,
    rule_type: None | RuleType | Unset = UNSET,
    scope: None | RuleScope | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
    is_public: bool | None | Unset = UNSET,
    entity_type: EntityType | None | Unset = UNSET,
    entity_id: None | str | Unset = UNSET,
    attached_only: bool | None | Unset = UNSET,
) -> Response[Any | HTTPValidationError | RuleListPaginatedResponse]:
    """List rules

     List all rules in an organization with pagination, filtering, and search.

    Args:
        org_id (str):
        skip (int | Unset): Number of records to skip for pagination Default: 0.
        limit (int | Unset): Maximum number of records to return (1-100) Default: 100.
        search (None | str | Unset): Search query to match against name, description, and content
        category (None | RuleCategory | Unset): Filter by category (safety, professional,
            creative, technical, custom)
        rule_type (None | RuleType | Unset): Filter by rule type (behavior, guardrails,
            formatting, context, content_policy, constraint)
        scope (None | RuleScope | Unset): Filter by scope (global, organization, model, assistant,
            user, vector_store)
        is_active (bool | None | Unset): Filter by active status (true/false)
        is_public (bool | None | Unset): Filter by public status (true/false)
        entity_type (EntityType | None | Unset): Filter by entity type (assistant, vector_store,
            user, model, organization)
        entity_id (None | str | Unset): Filter by specific entity ID (e.g., asst_123, vs_456).
            Requires entity_type if provided.
        attached_only (bool | None | Unset): Filter by attachment status - true: only attached
            rules, false: only unattached rules

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | RuleListPaginatedResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        rule_type=rule_type,
        scope=scope,
        is_active=is_active,
        is_public=is_public,
        entity_type=entity_type,
        entity_id=entity_id,
        attached_only=attached_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
    search: None | str | Unset = UNSET,
    category: None | RuleCategory | Unset = UNSET,
    rule_type: None | RuleType | Unset = UNSET,
    scope: None | RuleScope | Unset = UNSET,
    is_active: bool | None | Unset = UNSET,
    is_public: bool | None | Unset = UNSET,
    entity_type: EntityType | None | Unset = UNSET,
    entity_id: None | str | Unset = UNSET,
    attached_only: bool | None | Unset = UNSET,
) -> Any | HTTPValidationError | RuleListPaginatedResponse | None:
    """List rules

     List all rules in an organization with pagination, filtering, and search.

    Args:
        org_id (str):
        skip (int | Unset): Number of records to skip for pagination Default: 0.
        limit (int | Unset): Maximum number of records to return (1-100) Default: 100.
        search (None | str | Unset): Search query to match against name, description, and content
        category (None | RuleCategory | Unset): Filter by category (safety, professional,
            creative, technical, custom)
        rule_type (None | RuleType | Unset): Filter by rule type (behavior, guardrails,
            formatting, context, content_policy, constraint)
        scope (None | RuleScope | Unset): Filter by scope (global, organization, model, assistant,
            user, vector_store)
        is_active (bool | None | Unset): Filter by active status (true/false)
        is_public (bool | None | Unset): Filter by public status (true/false)
        entity_type (EntityType | None | Unset): Filter by entity type (assistant, vector_store,
            user, model, organization)
        entity_id (None | str | Unset): Filter by specific entity ID (e.g., asst_123, vs_456).
            Requires entity_type if provided.
        attached_only (bool | None | Unset): Filter by attachment status - true: only attached
            rules, false: only unattached rules

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | RuleListPaginatedResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            client=client,
            skip=skip,
            limit=limit,
            search=search,
            category=category,
            rule_type=rule_type,
            scope=scope,
            is_active=is_active,
            is_public=is_public,
            entity_type=entity_type,
            entity_id=entity_id,
            attached_only=attached_only,
        )
    ).parsed
