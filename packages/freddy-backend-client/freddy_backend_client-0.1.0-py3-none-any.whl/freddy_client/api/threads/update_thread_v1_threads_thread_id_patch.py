from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.thread_response import ThreadResponse
from ...models.thread_update import ThreadUpdate
from ...types import Response


def _get_kwargs(
    thread_id: str,
    *,
    body: ThreadUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v1/threads/{thread_id}".format(
            thread_id=quote(str(thread_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ThreadResponse | None:
    if response.status_code == 200:
        response_200 = ThreadResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | ThreadResponse]:
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
    body: ThreadUpdate,
) -> Response[HTTPValidationError | ThreadResponse]:
    """Update Thread

     Update a thread's title, metadata, or visibility.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key

    Only the thread creator can update it.

    Note: assistant_id cannot be changed once a thread has messages.
    The assistant binding is locked after the first message to ensure
    conversation consistency.

    Args:
        thread_id (str):
        body (ThreadUpdate): Request schema for updating a thread.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ThreadResponse]
    """

    kwargs = _get_kwargs(
        thread_id=thread_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    thread_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ThreadUpdate,
) -> HTTPValidationError | ThreadResponse | None:
    """Update Thread

     Update a thread's title, metadata, or visibility.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key

    Only the thread creator can update it.

    Note: assistant_id cannot be changed once a thread has messages.
    The assistant binding is locked after the first message to ensure
    conversation consistency.

    Args:
        thread_id (str):
        body (ThreadUpdate): Request schema for updating a thread.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ThreadResponse
    """

    return sync_detailed(
        thread_id=thread_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    thread_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ThreadUpdate,
) -> Response[HTTPValidationError | ThreadResponse]:
    """Update Thread

     Update a thread's title, metadata, or visibility.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key

    Only the thread creator can update it.

    Note: assistant_id cannot be changed once a thread has messages.
    The assistant binding is locked after the first message to ensure
    conversation consistency.

    Args:
        thread_id (str):
        body (ThreadUpdate): Request schema for updating a thread.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ThreadResponse]
    """

    kwargs = _get_kwargs(
        thread_id=thread_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    thread_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ThreadUpdate,
) -> HTTPValidationError | ThreadResponse | None:
    """Update Thread

     Update a thread's title, metadata, or visibility.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key

    Only the thread creator can update it.

    Note: assistant_id cannot be changed once a thread has messages.
    The assistant binding is locked after the first message to ensure
    conversation consistency.

    Args:
        thread_id (str):
        body (ThreadUpdate): Request schema for updating a thread.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ThreadResponse
    """

    return (
        await asyncio_detailed(
            thread_id=thread_id,
            client=client,
            body=body,
        )
    ).parsed
