from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.reasoning_levels_response import ReasoningLevelsResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/model/response/reasoning-levels",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ReasoningLevelsResponse | None:
    if response.status_code == 200:
        response_200 = ReasoningLevelsResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ReasoningLevelsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[ReasoningLevelsResponse]:
    """Get Reasoning Levels

     Get all available reasoning effort levels.

    Returns list of supported reasoning levels with descriptions and default flag.
    Requires authentication (Bearer token or API key).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ReasoningLevelsResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> ReasoningLevelsResponse | None:
    """Get Reasoning Levels

     Get all available reasoning effort levels.

    Returns list of supported reasoning levels with descriptions and default flag.
    Requires authentication (Bearer token or API key).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ReasoningLevelsResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[ReasoningLevelsResponse]:
    """Get Reasoning Levels

     Get all available reasoning effort levels.

    Returns list of supported reasoning levels with descriptions and default flag.
    Requires authentication (Bearer token or API key).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ReasoningLevelsResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> ReasoningLevelsResponse | None:
    """Get Reasoning Levels

     Get all available reasoning effort levels.

    Returns list of supported reasoning levels with descriptions and default flag.
    Requires authentication (Bearer token or API key).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ReasoningLevelsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
