from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.assistant_response import AssistantResponse
from ...models.assistant_update import AssistantUpdate
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    assistant_id: str,
    *,
    body: AssistantUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/assistants/{assistant_id}".format(
            assistant_id=quote(str(assistant_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AssistantResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = AssistantResponse.from_dict(response.json())

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
) -> Response[AssistantResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    assistant_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: AssistantUpdate,
) -> Response[AssistantResponse | HTTPValidationError]:
    """Update Assistant

     Update an existing assistant.

    Args:
        assistant_id (str):
        body (AssistantUpdate): Schema for updating an assistant.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AssistantResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        assistant_id=assistant_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    assistant_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: AssistantUpdate,
) -> AssistantResponse | HTTPValidationError | None:
    """Update Assistant

     Update an existing assistant.

    Args:
        assistant_id (str):
        body (AssistantUpdate): Schema for updating an assistant.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AssistantResponse | HTTPValidationError
    """

    return sync_detailed(
        assistant_id=assistant_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    assistant_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: AssistantUpdate,
) -> Response[AssistantResponse | HTTPValidationError]:
    """Update Assistant

     Update an existing assistant.

    Args:
        assistant_id (str):
        body (AssistantUpdate): Schema for updating an assistant.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AssistantResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        assistant_id=assistant_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    assistant_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: AssistantUpdate,
) -> AssistantResponse | HTTPValidationError | None:
    """Update Assistant

     Update an existing assistant.

    Args:
        assistant_id (str):
        body (AssistantUpdate): Schema for updating an assistant.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AssistantResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            assistant_id=assistant_id,
            client=client,
            body=body,
        )
    ).parsed
