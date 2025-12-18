from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.streamline_automation_response import StreamlineAutomationResponse
from ...types import Response


def _get_kwargs(
    automation_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/streamline/automations/{automation_id}".format(
            automation_id=quote(str(automation_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | StreamlineAutomationResponse | None:
    if response.status_code == 200:
        response_200 = StreamlineAutomationResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | StreamlineAutomationResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    automation_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | StreamlineAutomationResponse]:
    """Get Automation

     Get automation details.

    Args:
        automation_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | StreamlineAutomationResponse]
    """

    kwargs = _get_kwargs(
        automation_id=automation_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    automation_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | StreamlineAutomationResponse | None:
    """Get Automation

     Get automation details.

    Args:
        automation_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | StreamlineAutomationResponse
    """

    return sync_detailed(
        automation_id=automation_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    automation_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | StreamlineAutomationResponse]:
    """Get Automation

     Get automation details.

    Args:
        automation_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | StreamlineAutomationResponse]
    """

    kwargs = _get_kwargs(
        automation_id=automation_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    automation_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | StreamlineAutomationResponse | None:
    """Get Automation

     Get automation details.

    Args:
        automation_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | StreamlineAutomationResponse
    """

    return (
        await asyncio_detailed(
            automation_id=automation_id,
            client=client,
        )
    ).parsed
