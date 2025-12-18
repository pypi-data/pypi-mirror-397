from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.rule_detail_response import RuleDetailResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: str,
    rule_id: str,
    *,
    include_attachments: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_attachments"] = include_attachments

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/organizations/{org_id}/rules/{rule_id}".format(
            org_id=quote(str(org_id), safe=""),
            rule_id=quote(str(rule_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | RuleDetailResponse | None:
    if response.status_code == 200:
        response_200 = RuleDetailResponse.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | HTTPValidationError | RuleDetailResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: str,
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_attachments: bool | Unset = False,
) -> Response[Any | HTTPValidationError | RuleDetailResponse]:
    """Get rule details

     Get complete details of a specific rule including full content.

    Args:
        org_id (str):
        rule_id (str):
        include_attachments (bool | Unset): Include list of attached entities in response Default:
            False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | RuleDetailResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        rule_id=rule_id,
        include_attachments=include_attachments,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_attachments: bool | Unset = False,
) -> Any | HTTPValidationError | RuleDetailResponse | None:
    """Get rule details

     Get complete details of a specific rule including full content.

    Args:
        org_id (str):
        rule_id (str):
        include_attachments (bool | Unset): Include list of attached entities in response Default:
            False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | RuleDetailResponse
    """

    return sync_detailed(
        org_id=org_id,
        rule_id=rule_id,
        client=client,
        include_attachments=include_attachments,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_attachments: bool | Unset = False,
) -> Response[Any | HTTPValidationError | RuleDetailResponse]:
    """Get rule details

     Get complete details of a specific rule including full content.

    Args:
        org_id (str):
        rule_id (str):
        include_attachments (bool | Unset): Include list of attached entities in response Default:
            False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | RuleDetailResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        rule_id=rule_id,
        include_attachments=include_attachments,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    include_attachments: bool | Unset = False,
) -> Any | HTTPValidationError | RuleDetailResponse | None:
    """Get rule details

     Get complete details of a specific rule including full content.

    Args:
        org_id (str):
        rule_id (str):
        include_attachments (bool | Unset): Include list of attached entities in response Default:
            False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | RuleDetailResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            rule_id=rule_id,
            client=client,
            include_attachments=include_attachments,
        )
    ).parsed
