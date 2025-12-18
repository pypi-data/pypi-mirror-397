from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    icon_id: str,
    *,
    quality: str | Unset = "medium",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["quality"] = quality

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/icons/{icon_id}".format(
            icon_id=quote(str(icon_id), safe=""),
        ),
        "params": params,
    }

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
    icon_id: str,
    *,
    client: AuthenticatedClient,
    quality: str | Unset = "medium",
) -> Response[Any | HTTPValidationError]:
    """Serve Icon

     Serve icon file with optional quality transformation.

    System icons are publicly accessible.
    Custom icons require organization membership.
    Quality parameter controls image size for raster formats.
    SVG icons always return original regardless of quality.

    Args:
        icon_id (str):
        quality (str | Unset): Quality: thumbnail, small, medium, large, original Default:
            'medium'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        icon_id=icon_id,
        quality=quality,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    icon_id: str,
    *,
    client: AuthenticatedClient,
    quality: str | Unset = "medium",
) -> Any | HTTPValidationError | None:
    """Serve Icon

     Serve icon file with optional quality transformation.

    System icons are publicly accessible.
    Custom icons require organization membership.
    Quality parameter controls image size for raster formats.
    SVG icons always return original regardless of quality.

    Args:
        icon_id (str):
        quality (str | Unset): Quality: thumbnail, small, medium, large, original Default:
            'medium'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        icon_id=icon_id,
        client=client,
        quality=quality,
    ).parsed


async def asyncio_detailed(
    icon_id: str,
    *,
    client: AuthenticatedClient,
    quality: str | Unset = "medium",
) -> Response[Any | HTTPValidationError]:
    """Serve Icon

     Serve icon file with optional quality transformation.

    System icons are publicly accessible.
    Custom icons require organization membership.
    Quality parameter controls image size for raster formats.
    SVG icons always return original regardless of quality.

    Args:
        icon_id (str):
        quality (str | Unset): Quality: thumbnail, small, medium, large, original Default:
            'medium'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        icon_id=icon_id,
        quality=quality,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    icon_id: str,
    *,
    client: AuthenticatedClient,
    quality: str | Unset = "medium",
) -> Any | HTTPValidationError | None:
    """Serve Icon

     Serve icon file with optional quality transformation.

    System icons are publicly accessible.
    Custom icons require organization membership.
    Quality parameter controls image size for raster formats.
    SVG icons always return original regardless of quality.

    Args:
        icon_id (str):
        quality (str | Unset): Quality: thumbnail, small, medium, large, original Default:
            'medium'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            icon_id=icon_id,
            client=client,
            quality=quality,
        )
    ).parsed
