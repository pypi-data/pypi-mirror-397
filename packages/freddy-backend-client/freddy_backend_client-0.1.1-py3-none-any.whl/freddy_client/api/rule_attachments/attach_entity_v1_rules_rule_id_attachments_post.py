from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.attachment_create_request import AttachmentCreateRequest
from ...models.attachment_response import AttachmentResponse
from ...types import Response


def _get_kwargs(
    rule_id: str,
    *,
    body: AttachmentCreateRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/rules/{rule_id}/attachments".format(
            rule_id=quote(str(rule_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | AttachmentResponse | None:
    if response.status_code == 201:
        response_201 = AttachmentResponse.from_dict(response.json())

        return response_201

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if response.status_code == 409:
        response_409 = cast(Any, None)
        return response_409

    if response.status_code == 422:
        response_422 = cast(Any, None)
        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | AttachmentResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: AttachmentCreateRequest,
) -> Response[Any | AttachmentResponse]:
    """Attach entity to rule

     Attach an entity (assistant, user, model, vector_store, organization) to a rule with configuration.

    Args:
        rule_id (str):
        body (AttachmentCreateRequest): Request schema for attaching an entity to a rule.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AttachmentResponse]
    """

    kwargs = _get_kwargs(
        rule_id=rule_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: AttachmentCreateRequest,
) -> Any | AttachmentResponse | None:
    """Attach entity to rule

     Attach an entity (assistant, user, model, vector_store, organization) to a rule with configuration.

    Args:
        rule_id (str):
        body (AttachmentCreateRequest): Request schema for attaching an entity to a rule.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | AttachmentResponse
    """

    return sync_detailed(
        rule_id=rule_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: AttachmentCreateRequest,
) -> Response[Any | AttachmentResponse]:
    """Attach entity to rule

     Attach an entity (assistant, user, model, vector_store, organization) to a rule with configuration.

    Args:
        rule_id (str):
        body (AttachmentCreateRequest): Request schema for attaching an entity to a rule.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AttachmentResponse]
    """

    kwargs = _get_kwargs(
        rule_id=rule_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: AttachmentCreateRequest,
) -> Any | AttachmentResponse | None:
    """Attach entity to rule

     Attach an entity (assistant, user, model, vector_store, organization) to a rule with configuration.

    Args:
        rule_id (str):
        body (AttachmentCreateRequest): Request schema for attaching an entity to a rule.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | AttachmentResponse
    """

    return (
        await asyncio_detailed(
            rule_id=rule_id,
            client=client,
            body=body,
        )
    ).parsed
