from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.icon_list_response import IconListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: str,
    *,
    search: None | str | Unset = UNSET,
    category: None | str | Unset = UNSET,
    include_inactive: bool | Unset = False,
    recommended_for: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_search: None | str | Unset
    if isinstance(search, Unset):
        json_search = UNSET
    else:
        json_search = search
    params["search"] = json_search

    json_category: None | str | Unset
    if isinstance(category, Unset):
        json_category = UNSET
    else:
        json_category = category
    params["category"] = json_category

    params["include_inactive"] = include_inactive

    json_recommended_for: None | str | Unset
    if isinstance(recommended_for, Unset):
        json_recommended_for = UNSET
    else:
        json_recommended_for = recommended_for
    params["recommended_for"] = json_recommended_for

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/icons/organizations/{org_id}".format(
            org_id=quote(str(org_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | IconListResponse | None:
    if response.status_code == 200:
        response_200 = IconListResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | IconListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient,
    search: None | str | Unset = UNSET,
    category: None | str | Unset = UNSET,
    include_inactive: bool | Unset = False,
    recommended_for: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> Response[HTTPValidationError | IconListResponse]:
    """List Icons

     List icons available to an organization.

    Returns system icons + organization's custom icons.
    Supports search, category filtering, and pagination.

    Use `recommended_for=assistants` to show icons best suited for assistants first.
    Future contexts: projects, teams, etc.

    Args:
        org_id (str):
        search (None | str | Unset): Search by name, description, or tags
        category (None | str | Unset): Filter by category
        include_inactive (bool | Unset): Include inactive icons Default: False.
        recommended_for (None | str | Unset): Show icons recommended for context (e.g.,
            'assistants') first
        limit (int | Unset): Items per page Default: 50.
        offset (int | Unset): Number of items to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | IconListResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        search=search,
        category=category,
        include_inactive=include_inactive,
        recommended_for=recommended_for,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    *,
    client: AuthenticatedClient,
    search: None | str | Unset = UNSET,
    category: None | str | Unset = UNSET,
    include_inactive: bool | Unset = False,
    recommended_for: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> HTTPValidationError | IconListResponse | None:
    """List Icons

     List icons available to an organization.

    Returns system icons + organization's custom icons.
    Supports search, category filtering, and pagination.

    Use `recommended_for=assistants` to show icons best suited for assistants first.
    Future contexts: projects, teams, etc.

    Args:
        org_id (str):
        search (None | str | Unset): Search by name, description, or tags
        category (None | str | Unset): Filter by category
        include_inactive (bool | Unset): Include inactive icons Default: False.
        recommended_for (None | str | Unset): Show icons recommended for context (e.g.,
            'assistants') first
        limit (int | Unset): Items per page Default: 50.
        offset (int | Unset): Number of items to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | IconListResponse
    """

    return sync_detailed(
        org_id=org_id,
        client=client,
        search=search,
        category=category,
        include_inactive=include_inactive,
        recommended_for=recommended_for,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient,
    search: None | str | Unset = UNSET,
    category: None | str | Unset = UNSET,
    include_inactive: bool | Unset = False,
    recommended_for: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> Response[HTTPValidationError | IconListResponse]:
    """List Icons

     List icons available to an organization.

    Returns system icons + organization's custom icons.
    Supports search, category filtering, and pagination.

    Use `recommended_for=assistants` to show icons best suited for assistants first.
    Future contexts: projects, teams, etc.

    Args:
        org_id (str):
        search (None | str | Unset): Search by name, description, or tags
        category (None | str | Unset): Filter by category
        include_inactive (bool | Unset): Include inactive icons Default: False.
        recommended_for (None | str | Unset): Show icons recommended for context (e.g.,
            'assistants') first
        limit (int | Unset): Items per page Default: 50.
        offset (int | Unset): Number of items to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | IconListResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        search=search,
        category=category,
        include_inactive=include_inactive,
        recommended_for=recommended_for,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    *,
    client: AuthenticatedClient,
    search: None | str | Unset = UNSET,
    category: None | str | Unset = UNSET,
    include_inactive: bool | Unset = False,
    recommended_for: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> HTTPValidationError | IconListResponse | None:
    """List Icons

     List icons available to an organization.

    Returns system icons + organization's custom icons.
    Supports search, category filtering, and pagination.

    Use `recommended_for=assistants` to show icons best suited for assistants first.
    Future contexts: projects, teams, etc.

    Args:
        org_id (str):
        search (None | str | Unset): Search by name, description, or tags
        category (None | str | Unset): Filter by category
        include_inactive (bool | Unset): Include inactive icons Default: False.
        recommended_for (None | str | Unset): Show icons recommended for context (e.g.,
            'assistants') first
        limit (int | Unset): Items per page Default: 50.
        offset (int | Unset): Number of items to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | IconListResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            client=client,
            search=search,
            category=category,
            include_inactive=include_inactive,
            recommended_for=recommended_for,
            limit=limit,
            offset=offset,
        )
    ).parsed
