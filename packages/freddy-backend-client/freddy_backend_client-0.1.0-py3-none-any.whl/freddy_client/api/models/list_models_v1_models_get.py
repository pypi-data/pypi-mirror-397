from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.models_list_response import ModelsListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    ui_models_only: bool | Unset = False,
    include_pricing: bool | Unset = False,
    include_details: bool | Unset = False,
    include_capabilities: bool | Unset = True,
    include_deprecated: bool | Unset = False,
    include_legacy: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["ui_models_only"] = ui_models_only

    params["include_pricing"] = include_pricing

    params["include_details"] = include_details

    params["include_capabilities"] = include_capabilities

    params["include_deprecated"] = include_deprecated

    params["include_legacy"] = include_legacy

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/models",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ModelsListResponse | None:
    if response.status_code == 200:
        response_200 = ModelsListResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | ModelsListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    ui_models_only: bool | Unset = False,
    include_pricing: bool | Unset = False,
    include_details: bool | Unset = False,
    include_capabilities: bool | Unset = True,
    include_deprecated: bool | Unset = False,
    include_legacy: bool | Unset = False,
) -> Response[HTTPValidationError | ModelsListResponse]:
    """List Models

     List available AI models with their capabilities and configuration.

    Authentication:
        Requires either Bearer token or X-API-Key header

    Query Parameters:
        ui_models_only: Filter to show only UI-visible models (default: False)
        include_pricing: Include pricing information (default: False)
        include_details: Include detailed model information (default: False)
        include_capabilities: Include model capabilities array (default: True)
        include_deprecated: Include deprecated models (default: False)
        include_legacy: Include legacy models (default: False)

    Returns:
        ModelsListResponse with list of models and total count

    Args:
        ui_models_only (bool | Unset):  Default: False.
        include_pricing (bool | Unset):  Default: False.
        include_details (bool | Unset):  Default: False.
        include_capabilities (bool | Unset):  Default: True.
        include_deprecated (bool | Unset):  Default: False.
        include_legacy (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ModelsListResponse]
    """

    kwargs = _get_kwargs(
        ui_models_only=ui_models_only,
        include_pricing=include_pricing,
        include_details=include_details,
        include_capabilities=include_capabilities,
        include_deprecated=include_deprecated,
        include_legacy=include_legacy,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    ui_models_only: bool | Unset = False,
    include_pricing: bool | Unset = False,
    include_details: bool | Unset = False,
    include_capabilities: bool | Unset = True,
    include_deprecated: bool | Unset = False,
    include_legacy: bool | Unset = False,
) -> HTTPValidationError | ModelsListResponse | None:
    """List Models

     List available AI models with their capabilities and configuration.

    Authentication:
        Requires either Bearer token or X-API-Key header

    Query Parameters:
        ui_models_only: Filter to show only UI-visible models (default: False)
        include_pricing: Include pricing information (default: False)
        include_details: Include detailed model information (default: False)
        include_capabilities: Include model capabilities array (default: True)
        include_deprecated: Include deprecated models (default: False)
        include_legacy: Include legacy models (default: False)

    Returns:
        ModelsListResponse with list of models and total count

    Args:
        ui_models_only (bool | Unset):  Default: False.
        include_pricing (bool | Unset):  Default: False.
        include_details (bool | Unset):  Default: False.
        include_capabilities (bool | Unset):  Default: True.
        include_deprecated (bool | Unset):  Default: False.
        include_legacy (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ModelsListResponse
    """

    return sync_detailed(
        client=client,
        ui_models_only=ui_models_only,
        include_pricing=include_pricing,
        include_details=include_details,
        include_capabilities=include_capabilities,
        include_deprecated=include_deprecated,
        include_legacy=include_legacy,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    ui_models_only: bool | Unset = False,
    include_pricing: bool | Unset = False,
    include_details: bool | Unset = False,
    include_capabilities: bool | Unset = True,
    include_deprecated: bool | Unset = False,
    include_legacy: bool | Unset = False,
) -> Response[HTTPValidationError | ModelsListResponse]:
    """List Models

     List available AI models with their capabilities and configuration.

    Authentication:
        Requires either Bearer token or X-API-Key header

    Query Parameters:
        ui_models_only: Filter to show only UI-visible models (default: False)
        include_pricing: Include pricing information (default: False)
        include_details: Include detailed model information (default: False)
        include_capabilities: Include model capabilities array (default: True)
        include_deprecated: Include deprecated models (default: False)
        include_legacy: Include legacy models (default: False)

    Returns:
        ModelsListResponse with list of models and total count

    Args:
        ui_models_only (bool | Unset):  Default: False.
        include_pricing (bool | Unset):  Default: False.
        include_details (bool | Unset):  Default: False.
        include_capabilities (bool | Unset):  Default: True.
        include_deprecated (bool | Unset):  Default: False.
        include_legacy (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ModelsListResponse]
    """

    kwargs = _get_kwargs(
        ui_models_only=ui_models_only,
        include_pricing=include_pricing,
        include_details=include_details,
        include_capabilities=include_capabilities,
        include_deprecated=include_deprecated,
        include_legacy=include_legacy,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    ui_models_only: bool | Unset = False,
    include_pricing: bool | Unset = False,
    include_details: bool | Unset = False,
    include_capabilities: bool | Unset = True,
    include_deprecated: bool | Unset = False,
    include_legacy: bool | Unset = False,
) -> HTTPValidationError | ModelsListResponse | None:
    """List Models

     List available AI models with their capabilities and configuration.

    Authentication:
        Requires either Bearer token or X-API-Key header

    Query Parameters:
        ui_models_only: Filter to show only UI-visible models (default: False)
        include_pricing: Include pricing information (default: False)
        include_details: Include detailed model information (default: False)
        include_capabilities: Include model capabilities array (default: True)
        include_deprecated: Include deprecated models (default: False)
        include_legacy: Include legacy models (default: False)

    Returns:
        ModelsListResponse with list of models and total count

    Args:
        ui_models_only (bool | Unset):  Default: False.
        include_pricing (bool | Unset):  Default: False.
        include_details (bool | Unset):  Default: False.
        include_capabilities (bool | Unset):  Default: True.
        include_deprecated (bool | Unset):  Default: False.
        include_legacy (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ModelsListResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            ui_models_only=ui_models_only,
            include_pricing=include_pricing,
            include_details=include_details,
            include_capabilities=include_capabilities,
            include_deprecated=include_deprecated,
            include_legacy=include_legacy,
        )
    ).parsed
