from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.icon_response import IconResponse
from ...models.icon_update import IconUpdate
from ...types import Response


def _get_kwargs(
    org_id: str,
    icon_id: str,
    *,
    body: IconUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v1/icons/organizations/{org_id}/{icon_id}".format(
            org_id=quote(str(org_id), safe=""),
            icon_id=quote(str(icon_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | IconResponse | None:
    if response.status_code == 200:
        response_200 = IconResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | IconResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: str,
    icon_id: str,
    *,
    client: AuthenticatedClient,
    body: IconUpdate,
) -> Response[HTTPValidationError | IconResponse]:
    """Update Icon Metadata

     Update icon metadata (custom icons only).

    Can update name, description, tags, and is_active status.
    Cannot update system icons.

    Args:
        org_id (str):
        icon_id (str):
        body (IconUpdate): Schema for updating icon metadata.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | IconResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        icon_id=icon_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    icon_id: str,
    *,
    client: AuthenticatedClient,
    body: IconUpdate,
) -> HTTPValidationError | IconResponse | None:
    """Update Icon Metadata

     Update icon metadata (custom icons only).

    Can update name, description, tags, and is_active status.
    Cannot update system icons.

    Args:
        org_id (str):
        icon_id (str):
        body (IconUpdate): Schema for updating icon metadata.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | IconResponse
    """

    return sync_detailed(
        org_id=org_id,
        icon_id=icon_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    icon_id: str,
    *,
    client: AuthenticatedClient,
    body: IconUpdate,
) -> Response[HTTPValidationError | IconResponse]:
    """Update Icon Metadata

     Update icon metadata (custom icons only).

    Can update name, description, tags, and is_active status.
    Cannot update system icons.

    Args:
        org_id (str):
        icon_id (str):
        body (IconUpdate): Schema for updating icon metadata.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | IconResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        icon_id=icon_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    icon_id: str,
    *,
    client: AuthenticatedClient,
    body: IconUpdate,
) -> HTTPValidationError | IconResponse | None:
    """Update Icon Metadata

     Update icon metadata (custom icons only).

    Can update name, description, tags, and is_active status.
    Cannot update system icons.

    Args:
        org_id (str):
        icon_id (str):
        body (IconUpdate): Schema for updating icon metadata.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | IconResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            icon_id=icon_id,
            client=client,
            body=body,
        )
    ).parsed
