from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.messages_list_response import MessagesListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    thread_id: str,
    *,
    limit: int | Unset = 20,
    order: str | Unset = "asc",
    after: None | str | Unset = UNSET,
    before: None | str | Unset = UNSET,
    output_mode: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

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

    json_output_mode: None | str | Unset
    if isinstance(output_mode, Unset):
        json_output_mode = UNSET
    else:
        json_output_mode = output_mode
    params["output_mode"] = json_output_mode

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/threads/{thread_id}/messages".format(
            thread_id=quote(str(thread_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | MessagesListResponse | None:
    if response.status_code == 200:
        response_200 = MessagesListResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

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
) -> Response[Any | HTTPValidationError | MessagesListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    thread_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 20,
    order: str | Unset = "asc",
    after: None | str | Unset = UNSET,
    before: None | str | Unset = UNSET,
    output_mode: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError | MessagesListResponse]:
    """Get thread messages

     Retrieve all messages from a specific thread with pagination support.

    Args:
        thread_id (str): The unique identifier of the thread to retrieve messages from
        limit (int | Unset): Number of messages to return per page. Must be between 1 and 100.
            Default: 20.
        order (str | Unset): Sort order for messages. 'asc' = oldest first, 'desc' = newest first.
            Default: 'asc'.
        after (None | str | Unset): Cursor for pagination. Returns messages created after this
            message ID.
        before (None | str | Unset): Cursor for pagination. Returns messages created before this
            message ID.
        output_mode (None | str | Unset): Response format mode. 'text' (default, rich text),
            'plain' (no formatting), 'blocks' or 'structured' (typed blocks). Controls response_blocks
            field inclusion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | MessagesListResponse]
    """

    kwargs = _get_kwargs(
        thread_id=thread_id,
        limit=limit,
        order=order,
        after=after,
        before=before,
        output_mode=output_mode,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    thread_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 20,
    order: str | Unset = "asc",
    after: None | str | Unset = UNSET,
    before: None | str | Unset = UNSET,
    output_mode: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | MessagesListResponse | None:
    """Get thread messages

     Retrieve all messages from a specific thread with pagination support.

    Args:
        thread_id (str): The unique identifier of the thread to retrieve messages from
        limit (int | Unset): Number of messages to return per page. Must be between 1 and 100.
            Default: 20.
        order (str | Unset): Sort order for messages. 'asc' = oldest first, 'desc' = newest first.
            Default: 'asc'.
        after (None | str | Unset): Cursor for pagination. Returns messages created after this
            message ID.
        before (None | str | Unset): Cursor for pagination. Returns messages created before this
            message ID.
        output_mode (None | str | Unset): Response format mode. 'text' (default, rich text),
            'plain' (no formatting), 'blocks' or 'structured' (typed blocks). Controls response_blocks
            field inclusion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | MessagesListResponse
    """

    return sync_detailed(
        thread_id=thread_id,
        client=client,
        limit=limit,
        order=order,
        after=after,
        before=before,
        output_mode=output_mode,
    ).parsed


async def asyncio_detailed(
    thread_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 20,
    order: str | Unset = "asc",
    after: None | str | Unset = UNSET,
    before: None | str | Unset = UNSET,
    output_mode: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError | MessagesListResponse]:
    """Get thread messages

     Retrieve all messages from a specific thread with pagination support.

    Args:
        thread_id (str): The unique identifier of the thread to retrieve messages from
        limit (int | Unset): Number of messages to return per page. Must be between 1 and 100.
            Default: 20.
        order (str | Unset): Sort order for messages. 'asc' = oldest first, 'desc' = newest first.
            Default: 'asc'.
        after (None | str | Unset): Cursor for pagination. Returns messages created after this
            message ID.
        before (None | str | Unset): Cursor for pagination. Returns messages created before this
            message ID.
        output_mode (None | str | Unset): Response format mode. 'text' (default, rich text),
            'plain' (no formatting), 'blocks' or 'structured' (typed blocks). Controls response_blocks
            field inclusion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | MessagesListResponse]
    """

    kwargs = _get_kwargs(
        thread_id=thread_id,
        limit=limit,
        order=order,
        after=after,
        before=before,
        output_mode=output_mode,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    thread_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 20,
    order: str | Unset = "asc",
    after: None | str | Unset = UNSET,
    before: None | str | Unset = UNSET,
    output_mode: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | MessagesListResponse | None:
    """Get thread messages

     Retrieve all messages from a specific thread with pagination support.

    Args:
        thread_id (str): The unique identifier of the thread to retrieve messages from
        limit (int | Unset): Number of messages to return per page. Must be between 1 and 100.
            Default: 20.
        order (str | Unset): Sort order for messages. 'asc' = oldest first, 'desc' = newest first.
            Default: 'asc'.
        after (None | str | Unset): Cursor for pagination. Returns messages created after this
            message ID.
        before (None | str | Unset): Cursor for pagination. Returns messages created before this
            message ID.
        output_mode (None | str | Unset): Response format mode. 'text' (default, rich text),
            'plain' (no formatting), 'blocks' or 'structured' (typed blocks). Controls response_blocks
            field inclusion.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | MessagesListResponse
    """

    return (
        await asyncio_detailed(
            thread_id=thread_id,
            client=client,
            limit=limit,
            order=order,
            after=after,
            before=before,
            output_mode=output_mode,
        )
    ).parsed
