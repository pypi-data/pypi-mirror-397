from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.attachment_list_response import AttachmentListResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    entity_type: str,
    entity_id: str,
    *,
    include_rule_details: bool | Unset = True,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_rule_details"] = include_rule_details

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/rules/entities/{entity_type}/{entity_id}/rules".format(
            entity_type=quote(str(entity_type), safe=""),
            entity_id=quote(str(entity_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | AttachmentListResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = AttachmentListResponse.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | AttachmentListResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    entity_type: str,
    entity_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_rule_details: bool | Unset = True,
) -> Response[Any | AttachmentListResponse | HTTPValidationError]:
    """List rules for entity

     List all rules attached to a specific entity, ordered by priority (descending).

    Args:
        entity_type (str):
        entity_id (str):
        include_rule_details (bool | Unset): Include rule summary in response Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AttachmentListResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        entity_type=entity_type,
        entity_id=entity_id,
        include_rule_details=include_rule_details,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    entity_type: str,
    entity_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_rule_details: bool | Unset = True,
) -> Any | AttachmentListResponse | HTTPValidationError | None:
    """List rules for entity

     List all rules attached to a specific entity, ordered by priority (descending).

    Args:
        entity_type (str):
        entity_id (str):
        include_rule_details (bool | Unset): Include rule summary in response Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | AttachmentListResponse | HTTPValidationError
    """

    return sync_detailed(
        entity_type=entity_type,
        entity_id=entity_id,
        client=client,
        include_rule_details=include_rule_details,
    ).parsed


async def asyncio_detailed(
    entity_type: str,
    entity_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_rule_details: bool | Unset = True,
) -> Response[Any | AttachmentListResponse | HTTPValidationError]:
    """List rules for entity

     List all rules attached to a specific entity, ordered by priority (descending).

    Args:
        entity_type (str):
        entity_id (str):
        include_rule_details (bool | Unset): Include rule summary in response Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | AttachmentListResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        entity_type=entity_type,
        entity_id=entity_id,
        include_rule_details=include_rule_details,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    entity_type: str,
    entity_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_rule_details: bool | Unset = True,
) -> Any | AttachmentListResponse | HTTPValidationError | None:
    """List rules for entity

     List all rules attached to a specific entity, ordered by priority (descending).

    Args:
        entity_type (str):
        entity_id (str):
        include_rule_details (bool | Unset): Include rule summary in response Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | AttachmentListResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            entity_type=entity_type,
            entity_id=entity_id,
            client=client,
            include_rule_details=include_rule_details,
        )
    ).parsed
