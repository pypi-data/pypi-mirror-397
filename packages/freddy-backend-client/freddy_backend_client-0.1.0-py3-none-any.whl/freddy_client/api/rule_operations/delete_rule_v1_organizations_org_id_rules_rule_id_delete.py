from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    org_id: str,
    rule_id: str,
    *,
    force: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["force"] = force

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v1/organizations/{org_id}/rules/{rule_id}".format(
            org_id=quote(str(org_id), safe=""),
            rule_id=quote(str(rule_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | None:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204

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
    org_id: str,
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Delete a rule

     Soft delete a rule. Requires owner access.

    Args:
        org_id (str):
        rule_id (str):
        force (bool | Unset): Force delete even if rule has active attachments Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        rule_id=rule_id,
        force=force,
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
    force: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Delete a rule

     Soft delete a rule. Requires owner access.

    Args:
        org_id (str):
        rule_id (str):
        force (bool | Unset): Force delete even if rule has active attachments Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        org_id=org_id,
        rule_id=rule_id,
        client=client,
        force=force,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = False,
) -> Response[Any | HTTPValidationError]:
    """Delete a rule

     Soft delete a rule. Requires owner access.

    Args:
        org_id (str):
        rule_id (str):
        force (bool | Unset): Force delete even if rule has active attachments Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        rule_id=rule_id,
        force=force,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    rule_id: str,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = False,
) -> Any | HTTPValidationError | None:
    """Delete a rule

     Soft delete a rule. Requires owner access.

    Args:
        org_id (str):
        rule_id (str):
        force (bool | Unset): Force delete even if rule has active attachments Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            rule_id=rule_id,
            client=client,
            force=force,
        )
    ).parsed
