from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.audit_log_list_response import AuditLogListResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    assistant_id: str,
    *,
    action: None | str | Unset = UNSET,
    user_id: None | str | Unset = UNSET,
    start_date: None | str | Unset = UNSET,
    end_date: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_action: None | str | Unset
    if isinstance(action, Unset):
        json_action = UNSET
    else:
        json_action = action
    params["action"] = json_action

    json_user_id: None | str | Unset
    if isinstance(user_id, Unset):
        json_user_id = UNSET
    else:
        json_user_id = user_id
    params["user_id"] = json_user_id

    json_start_date: None | str | Unset
    if isinstance(start_date, Unset):
        json_start_date = UNSET
    else:
        json_start_date = start_date
    params["start_date"] = json_start_date

    json_end_date: None | str | Unset
    if isinstance(end_date, Unset):
        json_end_date = UNSET
    else:
        json_end_date = end_date
    params["end_date"] = json_end_date

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/assistants/{assistant_id}/history".format(
            assistant_id=quote(str(assistant_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AuditLogListResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = AuditLogListResponse.from_dict(response.json())

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
) -> Response[AuditLogListResponse | HTTPValidationError]:
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
    action: None | str | Unset = UNSET,
    user_id: None | str | Unset = UNSET,
    start_date: None | str | Unset = UNSET,
    end_date: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> Response[AuditLogListResponse | HTTPValidationError]:
    """Get Assistant History

     Get audit history for an assistant.

    Args:
        assistant_id (str):
        action (None | str | Unset): Filter by action
        user_id (None | str | Unset): Filter by user
        start_date (None | str | Unset): Start date (ISO 8601)
        end_date (None | str | Unset): End date (ISO 8601)
        limit (int | Unset): Items per page Default: 50.
        offset (int | Unset): Number of items to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuditLogListResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        assistant_id=assistant_id,
        action=action,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    assistant_id: str,
    *,
    client: AuthenticatedClient | Client,
    action: None | str | Unset = UNSET,
    user_id: None | str | Unset = UNSET,
    start_date: None | str | Unset = UNSET,
    end_date: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> AuditLogListResponse | HTTPValidationError | None:
    """Get Assistant History

     Get audit history for an assistant.

    Args:
        assistant_id (str):
        action (None | str | Unset): Filter by action
        user_id (None | str | Unset): Filter by user
        start_date (None | str | Unset): Start date (ISO 8601)
        end_date (None | str | Unset): End date (ISO 8601)
        limit (int | Unset): Items per page Default: 50.
        offset (int | Unset): Number of items to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuditLogListResponse | HTTPValidationError
    """

    return sync_detailed(
        assistant_id=assistant_id,
        client=client,
        action=action,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    assistant_id: str,
    *,
    client: AuthenticatedClient | Client,
    action: None | str | Unset = UNSET,
    user_id: None | str | Unset = UNSET,
    start_date: None | str | Unset = UNSET,
    end_date: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> Response[AuditLogListResponse | HTTPValidationError]:
    """Get Assistant History

     Get audit history for an assistant.

    Args:
        assistant_id (str):
        action (None | str | Unset): Filter by action
        user_id (None | str | Unset): Filter by user
        start_date (None | str | Unset): Start date (ISO 8601)
        end_date (None | str | Unset): End date (ISO 8601)
        limit (int | Unset): Items per page Default: 50.
        offset (int | Unset): Number of items to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuditLogListResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        assistant_id=assistant_id,
        action=action,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    assistant_id: str,
    *,
    client: AuthenticatedClient | Client,
    action: None | str | Unset = UNSET,
    user_id: None | str | Unset = UNSET,
    start_date: None | str | Unset = UNSET,
    end_date: None | str | Unset = UNSET,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
) -> AuditLogListResponse | HTTPValidationError | None:
    """Get Assistant History

     Get audit history for an assistant.

    Args:
        assistant_id (str):
        action (None | str | Unset): Filter by action
        user_id (None | str | Unset): Filter by user
        start_date (None | str | Unset): Start date (ISO 8601)
        end_date (None | str | Unset): End date (ISO 8601)
        limit (int | Unset): Items per page Default: 50.
        offset (int | Unset): Number of items to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuditLogListResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            assistant_id=assistant_id,
            client=client,
            action=action,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
    ).parsed
