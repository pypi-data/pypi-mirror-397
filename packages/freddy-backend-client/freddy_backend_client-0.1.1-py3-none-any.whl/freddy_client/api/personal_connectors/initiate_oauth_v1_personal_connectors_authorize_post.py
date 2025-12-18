from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.authorization_response import AuthorizationResponse
from ...models.authorize_request import AuthorizeRequest
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    *,
    body: AuthorizeRequest,
    organization_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["organizationId"] = organization_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/personal-connectors/authorize",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AuthorizationResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = AuthorizationResponse.from_dict(response.json())

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
) -> Response[AuthorizationResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: AuthorizeRequest,
    organization_id: str,
) -> Response[AuthorizationResponse | HTTPValidationError]:
    """Initiate Oauth

     Initiate OAuth flow for a connector.

    Args:
        organization_id (str): Organization ID
        body (AuthorizeRequest): Request body for OAuth authorization.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuthorizationResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        organization_id=organization_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: AuthorizeRequest,
    organization_id: str,
) -> AuthorizationResponse | HTTPValidationError | None:
    """Initiate Oauth

     Initiate OAuth flow for a connector.

    Args:
        organization_id (str): Organization ID
        body (AuthorizeRequest): Request body for OAuth authorization.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuthorizationResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
        organization_id=organization_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: AuthorizeRequest,
    organization_id: str,
) -> Response[AuthorizationResponse | HTTPValidationError]:
    """Initiate Oauth

     Initiate OAuth flow for a connector.

    Args:
        organization_id (str): Organization ID
        body (AuthorizeRequest): Request body for OAuth authorization.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuthorizationResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
        organization_id=organization_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: AuthorizeRequest,
    organization_id: str,
) -> AuthorizationResponse | HTTPValidationError | None:
    """Initiate Oauth

     Initiate OAuth flow for a connector.

    Args:
        organization_id (str): Organization ID
        body (AuthorizeRequest): Request body for OAuth authorization.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuthorizationResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            organization_id=organization_id,
        )
    ).parsed
