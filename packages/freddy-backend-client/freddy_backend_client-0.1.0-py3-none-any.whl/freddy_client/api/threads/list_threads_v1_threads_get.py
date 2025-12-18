from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.thread_list_response import ThreadListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    organization_id: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    order: str | Unset = "desc",
    after: None | str | Unset = UNSET,
    before: None | str | Unset = UNSET,
    assistant_id: None | str | Unset = UNSET,
    visible_in_ui: bool | None | Unset = True,
    include_deleted: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_organization_id: None | str | Unset
    if isinstance(organization_id, Unset):
        json_organization_id = UNSET
    else:
        json_organization_id = organization_id
    params["organization_id"] = json_organization_id

    params["limit"] = limit

    params["order"] = order

    json_after: None | str | Unset
    if isinstance(after, Unset):
        json_after = UNSET
    else:
        json_after = after
    params["after"] = json_after

    json_before: None | str | Unset
    if isinstance(before, Unset):
        json_before = UNSET
    else:
        json_before = before
    params["before"] = json_before

    json_assistant_id: None | str | Unset
    if isinstance(assistant_id, Unset):
        json_assistant_id = UNSET
    else:
        json_assistant_id = assistant_id
    params["assistant_id"] = json_assistant_id

    json_visible_in_ui: bool | None | Unset
    if isinstance(visible_in_ui, Unset):
        json_visible_in_ui = UNSET
    else:
        json_visible_in_ui = visible_in_ui
    params["visible_in_ui"] = json_visible_in_ui

    params["include_deleted"] = include_deleted

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/threads",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ThreadListResponse | None:
    if response.status_code == 200:
        response_200 = ThreadListResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | ThreadListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    organization_id: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    order: str | Unset = "desc",
    after: None | str | Unset = UNSET,
    before: None | str | Unset = UNSET,
    assistant_id: None | str | Unset = UNSET,
    visible_in_ui: bool | None | Unset = True,
    include_deleted: bool | Unset = False,
) -> Response[HTTPValidationError | ThreadListResponse]:
    """List Threads

     List threads for the authenticated user.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key
    List threads for the current user with cursor-based pagination.

    If organization_id is provided, returns threads from that organization only.
    If organization_id is not provided, returns all threads from all organizations the user belongs to.
    Results are paginated using cursor-based pagination (after/before) and sorted by last activity.

    Cursor-based pagination:
    - Use 'after' to get threads after a specific thread (for next page)
    - Use 'before' to get threads before a specific thread (for previous page)
    - The 'first_id' and 'last_id' in the response can be used as cursors

    Args:
        organization_id (None | str | Unset): Organization ID to filter by (optional)
        limit (int | Unset): Maximum number of records Default: 20.
        order (str | Unset): Sort order by last activity. 'desc' = newest first, 'asc' = oldest
            first Default: 'desc'.
        after (None | str | Unset): Cursor for pagination. Returns threads after this thread ID
        before (None | str | Unset): Cursor for pagination. Returns threads before this thread ID
        assistant_id (None | str | Unset): Filter by assistant ID
        visible_in_ui (bool | None | Unset): Filter by UI visibility. None returns all threads,
            True returns only visible threads, False returns only hidden threads Default: True.
        include_deleted (bool | Unset): Include deleted threads Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ThreadListResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        limit=limit,
        order=order,
        after=after,
        before=before,
        assistant_id=assistant_id,
        visible_in_ui=visible_in_ui,
        include_deleted=include_deleted,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    organization_id: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    order: str | Unset = "desc",
    after: None | str | Unset = UNSET,
    before: None | str | Unset = UNSET,
    assistant_id: None | str | Unset = UNSET,
    visible_in_ui: bool | None | Unset = True,
    include_deleted: bool | Unset = False,
) -> HTTPValidationError | ThreadListResponse | None:
    """List Threads

     List threads for the authenticated user.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key
    List threads for the current user with cursor-based pagination.

    If organization_id is provided, returns threads from that organization only.
    If organization_id is not provided, returns all threads from all organizations the user belongs to.
    Results are paginated using cursor-based pagination (after/before) and sorted by last activity.

    Cursor-based pagination:
    - Use 'after' to get threads after a specific thread (for next page)
    - Use 'before' to get threads before a specific thread (for previous page)
    - The 'first_id' and 'last_id' in the response can be used as cursors

    Args:
        organization_id (None | str | Unset): Organization ID to filter by (optional)
        limit (int | Unset): Maximum number of records Default: 20.
        order (str | Unset): Sort order by last activity. 'desc' = newest first, 'asc' = oldest
            first Default: 'desc'.
        after (None | str | Unset): Cursor for pagination. Returns threads after this thread ID
        before (None | str | Unset): Cursor for pagination. Returns threads before this thread ID
        assistant_id (None | str | Unset): Filter by assistant ID
        visible_in_ui (bool | None | Unset): Filter by UI visibility. None returns all threads,
            True returns only visible threads, False returns only hidden threads Default: True.
        include_deleted (bool | Unset): Include deleted threads Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ThreadListResponse
    """

    return sync_detailed(
        client=client,
        organization_id=organization_id,
        limit=limit,
        order=order,
        after=after,
        before=before,
        assistant_id=assistant_id,
        visible_in_ui=visible_in_ui,
        include_deleted=include_deleted,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    organization_id: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    order: str | Unset = "desc",
    after: None | str | Unset = UNSET,
    before: None | str | Unset = UNSET,
    assistant_id: None | str | Unset = UNSET,
    visible_in_ui: bool | None | Unset = True,
    include_deleted: bool | Unset = False,
) -> Response[HTTPValidationError | ThreadListResponse]:
    """List Threads

     List threads for the authenticated user.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key
    List threads for the current user with cursor-based pagination.

    If organization_id is provided, returns threads from that organization only.
    If organization_id is not provided, returns all threads from all organizations the user belongs to.
    Results are paginated using cursor-based pagination (after/before) and sorted by last activity.

    Cursor-based pagination:
    - Use 'after' to get threads after a specific thread (for next page)
    - Use 'before' to get threads before a specific thread (for previous page)
    - The 'first_id' and 'last_id' in the response can be used as cursors

    Args:
        organization_id (None | str | Unset): Organization ID to filter by (optional)
        limit (int | Unset): Maximum number of records Default: 20.
        order (str | Unset): Sort order by last activity. 'desc' = newest first, 'asc' = oldest
            first Default: 'desc'.
        after (None | str | Unset): Cursor for pagination. Returns threads after this thread ID
        before (None | str | Unset): Cursor for pagination. Returns threads before this thread ID
        assistant_id (None | str | Unset): Filter by assistant ID
        visible_in_ui (bool | None | Unset): Filter by UI visibility. None returns all threads,
            True returns only visible threads, False returns only hidden threads Default: True.
        include_deleted (bool | Unset): Include deleted threads Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ThreadListResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        limit=limit,
        order=order,
        after=after,
        before=before,
        assistant_id=assistant_id,
        visible_in_ui=visible_in_ui,
        include_deleted=include_deleted,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    organization_id: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    order: str | Unset = "desc",
    after: None | str | Unset = UNSET,
    before: None | str | Unset = UNSET,
    assistant_id: None | str | Unset = UNSET,
    visible_in_ui: bool | None | Unset = True,
    include_deleted: bool | Unset = False,
) -> HTTPValidationError | ThreadListResponse | None:
    """List Threads

     List threads for the authenticated user.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key
    List threads for the current user with cursor-based pagination.

    If organization_id is provided, returns threads from that organization only.
    If organization_id is not provided, returns all threads from all organizations the user belongs to.
    Results are paginated using cursor-based pagination (after/before) and sorted by last activity.

    Cursor-based pagination:
    - Use 'after' to get threads after a specific thread (for next page)
    - Use 'before' to get threads before a specific thread (for previous page)
    - The 'first_id' and 'last_id' in the response can be used as cursors

    Args:
        organization_id (None | str | Unset): Organization ID to filter by (optional)
        limit (int | Unset): Maximum number of records Default: 20.
        order (str | Unset): Sort order by last activity. 'desc' = newest first, 'asc' = oldest
            first Default: 'desc'.
        after (None | str | Unset): Cursor for pagination. Returns threads after this thread ID
        before (None | str | Unset): Cursor for pagination. Returns threads before this thread ID
        assistant_id (None | str | Unset): Filter by assistant ID
        visible_in_ui (bool | None | Unset): Filter by UI visibility. None returns all threads,
            True returns only visible threads, False returns only hidden threads Default: True.
        include_deleted (bool | Unset): Include deleted threads Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ThreadListResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            organization_id=organization_id,
            limit=limit,
            order=order,
            after=after,
            before=before,
            assistant_id=assistant_id,
            visible_in_ui=visible_in_ui,
            include_deleted=include_deleted,
        )
    ).parsed
