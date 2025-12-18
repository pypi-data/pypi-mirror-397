from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.oauth_callback_v1_personal_connectors_callback_get_response_oauth_callback_v1_personal_connectors_callback_get import (
    OauthCallbackV1PersonalConnectorsCallbackGetResponseOauthCallbackV1PersonalConnectorsCallbackGet,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    code: str,
    state: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["code"] = code

    json_state: None | str | Unset
    if isinstance(state, Unset):
        json_state = UNSET
    else:
        json_state = state
    params["state"] = json_state

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/personal-connectors/callback",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    HTTPValidationError
    | OauthCallbackV1PersonalConnectorsCallbackGetResponseOauthCallbackV1PersonalConnectorsCallbackGet
    | None
):
    if response.status_code == 200:
        response_200 = OauthCallbackV1PersonalConnectorsCallbackGetResponseOauthCallbackV1PersonalConnectorsCallbackGet.from_dict(
            response.json()
        )

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
) -> Response[
    HTTPValidationError
    | OauthCallbackV1PersonalConnectorsCallbackGetResponseOauthCallbackV1PersonalConnectorsCallbackGet
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    code: str,
    state: None | str | Unset = UNSET,
) -> Response[
    HTTPValidationError
    | OauthCallbackV1PersonalConnectorsCallbackGetResponseOauthCallbackV1PersonalConnectorsCallbackGet
]:
    """Oauth Callback

     Handle OAuth callback from third-party services (Atlassian, GitHub, ClickUp, Notion).

    This endpoint:
    1. Validates the state token (or finds most recent for ClickUp)
    2. Exchanges the authorization code for access/refresh tokens
    3. Stores the tokens securely in the database
    4. Creates MCP configuration and personal connector records

    Note: ClickUp doesn't return the state parameter, so we find the most recent
    unexpired OAuth state for ClickUp connectors.

    Args:
        code (str): OAuth authorization code
        state (None | str | Unset): OAuth state token (not provided by ClickUp)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OauthCallbackV1PersonalConnectorsCallbackGetResponseOauthCallbackV1PersonalConnectorsCallbackGet]
    """

    kwargs = _get_kwargs(
        code=code,
        state=state,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    code: str,
    state: None | str | Unset = UNSET,
) -> (
    HTTPValidationError
    | OauthCallbackV1PersonalConnectorsCallbackGetResponseOauthCallbackV1PersonalConnectorsCallbackGet
    | None
):
    """Oauth Callback

     Handle OAuth callback from third-party services (Atlassian, GitHub, ClickUp, Notion).

    This endpoint:
    1. Validates the state token (or finds most recent for ClickUp)
    2. Exchanges the authorization code for access/refresh tokens
    3. Stores the tokens securely in the database
    4. Creates MCP configuration and personal connector records

    Note: ClickUp doesn't return the state parameter, so we find the most recent
    unexpired OAuth state for ClickUp connectors.

    Args:
        code (str): OAuth authorization code
        state (None | str | Unset): OAuth state token (not provided by ClickUp)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OauthCallbackV1PersonalConnectorsCallbackGetResponseOauthCallbackV1PersonalConnectorsCallbackGet
    """

    return sync_detailed(
        client=client,
        code=code,
        state=state,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    code: str,
    state: None | str | Unset = UNSET,
) -> Response[
    HTTPValidationError
    | OauthCallbackV1PersonalConnectorsCallbackGetResponseOauthCallbackV1PersonalConnectorsCallbackGet
]:
    """Oauth Callback

     Handle OAuth callback from third-party services (Atlassian, GitHub, ClickUp, Notion).

    This endpoint:
    1. Validates the state token (or finds most recent for ClickUp)
    2. Exchanges the authorization code for access/refresh tokens
    3. Stores the tokens securely in the database
    4. Creates MCP configuration and personal connector records

    Note: ClickUp doesn't return the state parameter, so we find the most recent
    unexpired OAuth state for ClickUp connectors.

    Args:
        code (str): OAuth authorization code
        state (None | str | Unset): OAuth state token (not provided by ClickUp)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OauthCallbackV1PersonalConnectorsCallbackGetResponseOauthCallbackV1PersonalConnectorsCallbackGet]
    """

    kwargs = _get_kwargs(
        code=code,
        state=state,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    code: str,
    state: None | str | Unset = UNSET,
) -> (
    HTTPValidationError
    | OauthCallbackV1PersonalConnectorsCallbackGetResponseOauthCallbackV1PersonalConnectorsCallbackGet
    | None
):
    """Oauth Callback

     Handle OAuth callback from third-party services (Atlassian, GitHub, ClickUp, Notion).

    This endpoint:
    1. Validates the state token (or finds most recent for ClickUp)
    2. Exchanges the authorization code for access/refresh tokens
    3. Stores the tokens securely in the database
    4. Creates MCP configuration and personal connector records

    Note: ClickUp doesn't return the state parameter, so we find the most recent
    unexpired OAuth state for ClickUp connectors.

    Args:
        code (str): OAuth authorization code
        state (None | str | Unset): OAuth state token (not provided by ClickUp)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OauthCallbackV1PersonalConnectorsCallbackGetResponseOauthCallbackV1PersonalConnectorsCallbackGet
    """

    return (
        await asyncio_detailed(
            client=client,
            code=code,
            state=state,
        )
    ).parsed
