from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.assistant_list_response import AssistantListResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    organization_id: str,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    search: None | str | Unset = UNSET,
    access_mode: None | str | Unset = UNSET,
    vector_store_id: None | str | Unset = UNSET,
    include_inactive: bool | Unset = False,
    sort_by: str | Unset = "name",
    sort_order: str | Unset = "asc",
    fields: str | Unset = "summary",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["organization_id"] = organization_id

    params["limit"] = limit

    params["offset"] = offset

    json_search: None | str | Unset
    if isinstance(search, Unset):
        json_search = UNSET
    else:
        json_search = search
    params["search"] = json_search

    json_access_mode: None | str | Unset
    if isinstance(access_mode, Unset):
        json_access_mode = UNSET
    else:
        json_access_mode = access_mode
    params["access_mode"] = json_access_mode

    json_vector_store_id: None | str | Unset
    if isinstance(vector_store_id, Unset):
        json_vector_store_id = UNSET
    else:
        json_vector_store_id = vector_store_id
    params["vector_store_id"] = json_vector_store_id

    params["include_inactive"] = include_inactive

    params["sort_by"] = sort_by

    params["sort_order"] = sort_order

    params["fields"] = fields

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/assistants",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AssistantListResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = AssistantListResponse.from_dict(response.json())

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
) -> Response[AssistantListResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    search: None | str | Unset = UNSET,
    access_mode: None | str | Unset = UNSET,
    vector_store_id: None | str | Unset = UNSET,
    include_inactive: bool | Unset = False,
    sort_by: str | Unset = "name",
    sort_order: str | Unset = "asc",
    fields: str | Unset = "summary",
) -> Response[AssistantListResponse | HTTPValidationError]:
    """List Assistants

     List assistants for an organization with filters.

    Only returns assistants the user has access to.
    Fields parameter controls response detail:
    - summary: Minimal fields for list views
    - standard: Summary + model configuration
    - full: Complete assistant objects

    Filters:
    - vector_store_id: Only return assistants using this vector store

    Args:
        organization_id (str): Organization ID
        limit (int | Unset): Items per page Default: 50.
        offset (int | Unset): Number of items to skip Default: 0.
        search (None | str | Unset): Search term
        access_mode (None | str | Unset): Filter by access mode
        vector_store_id (None | str | Unset): Filter by vector store ID
        include_inactive (bool | Unset): Include inactive assistants Default: False.
        sort_by (str | Unset): Sort field Default: 'name'.
        sort_order (str | Unset): Sort direction Default: 'asc'.
        fields (str | Unset): Response detail level: summary, standard, full Default: 'summary'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AssistantListResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        limit=limit,
        offset=offset,
        search=search,
        access_mode=access_mode,
        vector_store_id=vector_store_id,
        include_inactive=include_inactive,
        sort_by=sort_by,
        sort_order=sort_order,
        fields=fields,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    search: None | str | Unset = UNSET,
    access_mode: None | str | Unset = UNSET,
    vector_store_id: None | str | Unset = UNSET,
    include_inactive: bool | Unset = False,
    sort_by: str | Unset = "name",
    sort_order: str | Unset = "asc",
    fields: str | Unset = "summary",
) -> AssistantListResponse | HTTPValidationError | None:
    """List Assistants

     List assistants for an organization with filters.

    Only returns assistants the user has access to.
    Fields parameter controls response detail:
    - summary: Minimal fields for list views
    - standard: Summary + model configuration
    - full: Complete assistant objects

    Filters:
    - vector_store_id: Only return assistants using this vector store

    Args:
        organization_id (str): Organization ID
        limit (int | Unset): Items per page Default: 50.
        offset (int | Unset): Number of items to skip Default: 0.
        search (None | str | Unset): Search term
        access_mode (None | str | Unset): Filter by access mode
        vector_store_id (None | str | Unset): Filter by vector store ID
        include_inactive (bool | Unset): Include inactive assistants Default: False.
        sort_by (str | Unset): Sort field Default: 'name'.
        sort_order (str | Unset): Sort direction Default: 'asc'.
        fields (str | Unset): Response detail level: summary, standard, full Default: 'summary'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AssistantListResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        organization_id=organization_id,
        limit=limit,
        offset=offset,
        search=search,
        access_mode=access_mode,
        vector_store_id=vector_store_id,
        include_inactive=include_inactive,
        sort_by=sort_by,
        sort_order=sort_order,
        fields=fields,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    search: None | str | Unset = UNSET,
    access_mode: None | str | Unset = UNSET,
    vector_store_id: None | str | Unset = UNSET,
    include_inactive: bool | Unset = False,
    sort_by: str | Unset = "name",
    sort_order: str | Unset = "asc",
    fields: str | Unset = "summary",
) -> Response[AssistantListResponse | HTTPValidationError]:
    """List Assistants

     List assistants for an organization with filters.

    Only returns assistants the user has access to.
    Fields parameter controls response detail:
    - summary: Minimal fields for list views
    - standard: Summary + model configuration
    - full: Complete assistant objects

    Filters:
    - vector_store_id: Only return assistants using this vector store

    Args:
        organization_id (str): Organization ID
        limit (int | Unset): Items per page Default: 50.
        offset (int | Unset): Number of items to skip Default: 0.
        search (None | str | Unset): Search term
        access_mode (None | str | Unset): Filter by access mode
        vector_store_id (None | str | Unset): Filter by vector store ID
        include_inactive (bool | Unset): Include inactive assistants Default: False.
        sort_by (str | Unset): Sort field Default: 'name'.
        sort_order (str | Unset): Sort direction Default: 'asc'.
        fields (str | Unset): Response detail level: summary, standard, full Default: 'summary'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AssistantListResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        limit=limit,
        offset=offset,
        search=search,
        access_mode=access_mode,
        vector_store_id=vector_store_id,
        include_inactive=include_inactive,
        sort_by=sort_by,
        sort_order=sort_order,
        fields=fields,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    organization_id: str,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    search: None | str | Unset = UNSET,
    access_mode: None | str | Unset = UNSET,
    vector_store_id: None | str | Unset = UNSET,
    include_inactive: bool | Unset = False,
    sort_by: str | Unset = "name",
    sort_order: str | Unset = "asc",
    fields: str | Unset = "summary",
) -> AssistantListResponse | HTTPValidationError | None:
    """List Assistants

     List assistants for an organization with filters.

    Only returns assistants the user has access to.
    Fields parameter controls response detail:
    - summary: Minimal fields for list views
    - standard: Summary + model configuration
    - full: Complete assistant objects

    Filters:
    - vector_store_id: Only return assistants using this vector store

    Args:
        organization_id (str): Organization ID
        limit (int | Unset): Items per page Default: 50.
        offset (int | Unset): Number of items to skip Default: 0.
        search (None | str | Unset): Search term
        access_mode (None | str | Unset): Filter by access mode
        vector_store_id (None | str | Unset): Filter by vector store ID
        include_inactive (bool | Unset): Include inactive assistants Default: False.
        sort_by (str | Unset): Sort field Default: 'name'.
        sort_order (str | Unset): Sort direction Default: 'asc'.
        fields (str | Unset): Response detail level: summary, standard, full Default: 'summary'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AssistantListResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            organization_id=organization_id,
            limit=limit,
            offset=offset,
            search=search,
            access_mode=access_mode,
            vector_store_id=vector_store_id,
            include_inactive=include_inactive,
            sort_by=sort_by,
            sort_order=sort_order,
            fields=fields,
        )
    ).parsed
