from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.system_tools_list_response import SystemToolsListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    include_capabilities: bool | Unset = True,
    category: None | str | Unset = UNSET,
    model_compatibility: None | str | Unset = UNSET,
    visible_in_ui: bool | None | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_capabilities"] = include_capabilities

    json_category: None | str | Unset
    if isinstance(category, Unset):
        json_category = UNSET
    else:
        json_category = category
    params["category"] = json_category

    json_model_compatibility: None | str | Unset
    if isinstance(model_compatibility, Unset):
        json_model_compatibility = UNSET
    else:
        json_model_compatibility = model_compatibility
    params["model_compatibility"] = json_model_compatibility

    json_visible_in_ui: bool | None | Unset
    if isinstance(visible_in_ui, Unset):
        json_visible_in_ui = UNSET
    else:
        json_visible_in_ui = visible_in_ui
    params["visible_in_ui"] = json_visible_in_ui

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/toolbox/system-tools",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SystemToolsListResponse | None:
    if response.status_code == 200:
        response_200 = SystemToolsListResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | SystemToolsListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    include_capabilities: bool | Unset = True,
    category: None | str | Unset = UNSET,
    model_compatibility: None | str | Unset = UNSET,
    visible_in_ui: bool | None | Unset = UNSET,
) -> Response[HTTPValidationError | SystemToolsListResponse]:
    """List System Tools

     List available built-in Freddy AI system tools.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key

    Query Parameters:
        include_capabilities: Include detailed tool capabilities (default: True)
        category: Filter tools by category (search, computation, generation, automation, analysis)
        model_compatibility: Filter by model type compatibility (text, vision, voice, multimodal)
        visible_in_ui: Filter by UI visibility (true = only UI-visible tools, false = only hidden tools,
    null = all)

    Returns:
        SystemToolsListResponse with list of tools and total count

    Args:
        include_capabilities (bool | Unset):  Default: True.
        category (None | str | Unset):
        model_compatibility (None | str | Unset):
        visible_in_ui (bool | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SystemToolsListResponse]
    """

    kwargs = _get_kwargs(
        include_capabilities=include_capabilities,
        category=category,
        model_compatibility=model_compatibility,
        visible_in_ui=visible_in_ui,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    include_capabilities: bool | Unset = True,
    category: None | str | Unset = UNSET,
    model_compatibility: None | str | Unset = UNSET,
    visible_in_ui: bool | None | Unset = UNSET,
) -> HTTPValidationError | SystemToolsListResponse | None:
    """List System Tools

     List available built-in Freddy AI system tools.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key

    Query Parameters:
        include_capabilities: Include detailed tool capabilities (default: True)
        category: Filter tools by category (search, computation, generation, automation, analysis)
        model_compatibility: Filter by model type compatibility (text, vision, voice, multimodal)
        visible_in_ui: Filter by UI visibility (true = only UI-visible tools, false = only hidden tools,
    null = all)

    Returns:
        SystemToolsListResponse with list of tools and total count

    Args:
        include_capabilities (bool | Unset):  Default: True.
        category (None | str | Unset):
        model_compatibility (None | str | Unset):
        visible_in_ui (bool | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SystemToolsListResponse
    """

    return sync_detailed(
        client=client,
        include_capabilities=include_capabilities,
        category=category,
        model_compatibility=model_compatibility,
        visible_in_ui=visible_in_ui,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    include_capabilities: bool | Unset = True,
    category: None | str | Unset = UNSET,
    model_compatibility: None | str | Unset = UNSET,
    visible_in_ui: bool | None | Unset = UNSET,
) -> Response[HTTPValidationError | SystemToolsListResponse]:
    """List System Tools

     List available built-in Freddy AI system tools.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key

    Query Parameters:
        include_capabilities: Include detailed tool capabilities (default: True)
        category: Filter tools by category (search, computation, generation, automation, analysis)
        model_compatibility: Filter by model type compatibility (text, vision, voice, multimodal)
        visible_in_ui: Filter by UI visibility (true = only UI-visible tools, false = only hidden tools,
    null = all)

    Returns:
        SystemToolsListResponse with list of tools and total count

    Args:
        include_capabilities (bool | Unset):  Default: True.
        category (None | str | Unset):
        model_compatibility (None | str | Unset):
        visible_in_ui (bool | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SystemToolsListResponse]
    """

    kwargs = _get_kwargs(
        include_capabilities=include_capabilities,
        category=category,
        model_compatibility=model_compatibility,
        visible_in_ui=visible_in_ui,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    include_capabilities: bool | Unset = True,
    category: None | str | Unset = UNSET,
    model_compatibility: None | str | Unset = UNSET,
    visible_in_ui: bool | None | Unset = UNSET,
) -> HTTPValidationError | SystemToolsListResponse | None:
    """List System Tools

     List available built-in Freddy AI system tools.

    Supports both authentication methods:
    - Bearer token: Use Authorization header with user token
    - API key: Use X-API-Key header with organization API key

    Query Parameters:
        include_capabilities: Include detailed tool capabilities (default: True)
        category: Filter tools by category (search, computation, generation, automation, analysis)
        model_compatibility: Filter by model type compatibility (text, vision, voice, multimodal)
        visible_in_ui: Filter by UI visibility (true = only UI-visible tools, false = only hidden tools,
    null = all)

    Returns:
        SystemToolsListResponse with list of tools and total count

    Args:
        include_capabilities (bool | Unset):  Default: True.
        category (None | str | Unset):
        model_compatibility (None | str | Unset):
        visible_in_ui (bool | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SystemToolsListResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            include_capabilities=include_capabilities,
            category=category,
            model_compatibility=model_compatibility,
            visible_in_ui=visible_in_ui,
        )
    ).parsed
