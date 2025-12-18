from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.attachment_response import AttachmentResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    rule_id: str,
    entity_type: str,
    entity_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/rules/{rule_id}/attachments/{entity_type}/{entity_id}".format(
            rule_id=quote(str(rule_id), safe=""),
            entity_type=quote(str(entity_type), safe=""),
            entity_id=quote(str(entity_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AttachmentResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = AttachmentResponse.from_dict(response.json())

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
) -> Response[AttachmentResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    rule_id: str,
    entity_type: str,
    entity_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[AttachmentResponse | HTTPValidationError]:
    """Get specific attachment

     Get details of a specific attachment by rule, entity type, and entity ID.

    Args:
        rule_id (str):
        entity_type (str):
        entity_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AttachmentResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        rule_id=rule_id,
        entity_type=entity_type,
        entity_id=entity_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    rule_id: str,
    entity_type: str,
    entity_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> AttachmentResponse | HTTPValidationError | None:
    """Get specific attachment

     Get details of a specific attachment by rule, entity type, and entity ID.

    Args:
        rule_id (str):
        entity_type (str):
        entity_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AttachmentResponse | HTTPValidationError
    """

    return sync_detailed(
        rule_id=rule_id,
        entity_type=entity_type,
        entity_id=entity_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    rule_id: str,
    entity_type: str,
    entity_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[AttachmentResponse | HTTPValidationError]:
    """Get specific attachment

     Get details of a specific attachment by rule, entity type, and entity ID.

    Args:
        rule_id (str):
        entity_type (str):
        entity_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AttachmentResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        rule_id=rule_id,
        entity_type=entity_type,
        entity_id=entity_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    rule_id: str,
    entity_type: str,
    entity_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> AttachmentResponse | HTTPValidationError | None:
    """Get specific attachment

     Get details of a specific attachment by rule, entity type, and entity ID.

    Args:
        rule_id (str):
        entity_type (str):
        entity_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AttachmentResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            rule_id=rule_id,
            entity_type=entity_type,
            entity_id=entity_id,
            client=client,
        )
    ).parsed
