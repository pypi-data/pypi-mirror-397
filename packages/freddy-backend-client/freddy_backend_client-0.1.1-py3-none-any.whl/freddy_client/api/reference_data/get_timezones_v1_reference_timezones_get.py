from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.timezone_response import TimezoneResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/reference/timezones",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> list[TimezoneResponse] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = TimezoneResponse.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[list[TimezoneResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[list[TimezoneResponse]]:
    r"""Get Timezones

     Get all active timezones.

    Returns a list of all available timezones from the IANA timezone database.
    Timezones are ordered by display order and name.

    **Returns:**
    - List of timezone objects with:
      - IANA timezone name (e.g., \"America/New_York\")
      - User-friendly display name
      - UTC offset information
      - Country code association

    **Use Cases:**
    - User profile timezone selection
    - Scheduling and calendar features
    - Time conversion utilities

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[TimezoneResponse]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> list[TimezoneResponse] | None:
    r"""Get Timezones

     Get all active timezones.

    Returns a list of all available timezones from the IANA timezone database.
    Timezones are ordered by display order and name.

    **Returns:**
    - List of timezone objects with:
      - IANA timezone name (e.g., \"America/New_York\")
      - User-friendly display name
      - UTC offset information
      - Country code association

    **Use Cases:**
    - User profile timezone selection
    - Scheduling and calendar features
    - Time conversion utilities

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[TimezoneResponse]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[list[TimezoneResponse]]:
    r"""Get Timezones

     Get all active timezones.

    Returns a list of all available timezones from the IANA timezone database.
    Timezones are ordered by display order and name.

    **Returns:**
    - List of timezone objects with:
      - IANA timezone name (e.g., \"America/New_York\")
      - User-friendly display name
      - UTC offset information
      - Country code association

    **Use Cases:**
    - User profile timezone selection
    - Scheduling and calendar features
    - Time conversion utilities

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[TimezoneResponse]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> list[TimezoneResponse] | None:
    r"""Get Timezones

     Get all active timezones.

    Returns a list of all available timezones from the IANA timezone database.
    Timezones are ordered by display order and name.

    **Returns:**
    - List of timezone objects with:
      - IANA timezone name (e.g., \"America/New_York\")
      - User-friendly display name
      - UTC offset information
      - Country code association

    **Use Cases:**
    - User profile timezone selection
    - Scheduling and calendar features
    - Time conversion utilities

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[TimezoneResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
