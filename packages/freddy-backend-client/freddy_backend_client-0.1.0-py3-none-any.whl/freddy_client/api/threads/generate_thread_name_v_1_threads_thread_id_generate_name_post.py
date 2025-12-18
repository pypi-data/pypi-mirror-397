from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.generate_name_request import GenerateNameRequest
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    thread_id: str,
    *,
    body: GenerateNameRequest | Unset = UNSET,
    stream: bool | Unset = False,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["stream"] = stream

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/threads/{thread_id}/generateName".format(
            thread_id=quote(str(thread_id), safe=""),
        ),
        "params": params,
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = response.json()
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
) -> Response[Any | HTTPValidationError]:
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
    body: GenerateNameRequest | Unset = UNSET,
    stream: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Generate Thread Name

     Generate AI-powered thread name.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key

    Analyzes conversation content and generates a concise, descriptive title.
    Can accept messages in request body for real-time scenarios or fetch from database.

    Supports streaming mode for real-time title generation feedback.

    Performance optimizations:
    - Target: < 3 seconds for 95th percentile
    - Single optimized query for thread verification (indexed on thread_id)
    - Zero DB latency when messages provided in request body
    - Async operations throughout (non-blocking)
    - Connection pooling for HTTP client
    - Fast model (ftg-3.0-speed) for < 2s generation
    - Single UPDATE query with RETURNING for title update
    - Comprehensive timing logs for monitoring

    Args:
        thread_id (str):
        stream (bool | Unset): Enable streaming mode Default: False.
        body (GenerateNameRequest | Unset): Request schema for generating thread name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        thread_id=thread_id,
        body=body,
        stream=stream,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    thread_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: GenerateNameRequest | Unset = UNSET,
    stream: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Generate Thread Name

     Generate AI-powered thread name.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key

    Analyzes conversation content and generates a concise, descriptive title.
    Can accept messages in request body for real-time scenarios or fetch from database.

    Supports streaming mode for real-time title generation feedback.

    Performance optimizations:
    - Target: < 3 seconds for 95th percentile
    - Single optimized query for thread verification (indexed on thread_id)
    - Zero DB latency when messages provided in request body
    - Async operations throughout (non-blocking)
    - Connection pooling for HTTP client
    - Fast model (ftg-3.0-speed) for < 2s generation
    - Single UPDATE query with RETURNING for title update
    - Comprehensive timing logs for monitoring

    Args:
        thread_id (str):
        stream (bool | Unset): Enable streaming mode Default: False.
        body (GenerateNameRequest | Unset): Request schema for generating thread name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        thread_id=thread_id,
        client=client,
        body=body,
        stream=stream,
    ).parsed


async def asyncio_detailed(
    thread_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: GenerateNameRequest | Unset = UNSET,
    stream: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Generate Thread Name

     Generate AI-powered thread name.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key

    Analyzes conversation content and generates a concise, descriptive title.
    Can accept messages in request body for real-time scenarios or fetch from database.

    Supports streaming mode for real-time title generation feedback.

    Performance optimizations:
    - Target: < 3 seconds for 95th percentile
    - Single optimized query for thread verification (indexed on thread_id)
    - Zero DB latency when messages provided in request body
    - Async operations throughout (non-blocking)
    - Connection pooling for HTTP client
    - Fast model (ftg-3.0-speed) for < 2s generation
    - Single UPDATE query with RETURNING for title update
    - Comprehensive timing logs for monitoring

    Args:
        thread_id (str):
        stream (bool | Unset): Enable streaming mode Default: False.
        body (GenerateNameRequest | Unset): Request schema for generating thread name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        thread_id=thread_id,
        body=body,
        stream=stream,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    thread_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: GenerateNameRequest | Unset = UNSET,
    stream: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Generate Thread Name

     Generate AI-powered thread name.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key

    Analyzes conversation content and generates a concise, descriptive title.
    Can accept messages in request body for real-time scenarios or fetch from database.

    Supports streaming mode for real-time title generation feedback.

    Performance optimizations:
    - Target: < 3 seconds for 95th percentile
    - Single optimized query for thread verification (indexed on thread_id)
    - Zero DB latency when messages provided in request body
    - Async operations throughout (non-blocking)
    - Connection pooling for HTTP client
    - Fast model (ftg-3.0-speed) for < 2s generation
    - Single UPDATE query with RETURNING for title update
    - Comprehensive timing logs for monitoring

    Args:
        thread_id (str):
        stream (bool | Unset): Enable streaming mode Default: False.
        body (GenerateNameRequest | Unset): Request schema for generating thread name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            thread_id=thread_id,
            client=client,
            body=body,
            stream=stream,
        )
    ).parsed
