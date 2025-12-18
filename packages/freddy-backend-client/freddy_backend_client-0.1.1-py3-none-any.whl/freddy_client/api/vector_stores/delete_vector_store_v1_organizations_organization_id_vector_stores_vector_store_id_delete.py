from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    organization_id: str,
    vector_store_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/v1/organizations/{organization_id}/vector-stores/{vector_store_id}".format(
            organization_id=quote(str(organization_id), safe=""),
            vector_store_id=quote(str(vector_store_id), safe=""),
        ),
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
    organization_id: str,
    vector_store_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | HTTPValidationError]:
    """Delete a vector store

     Permanently delete a vector store and remove all associated files

    Args:
        organization_id (str):
        vector_store_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        vector_store_id=vector_store_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    vector_store_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | HTTPValidationError | None:
    """Delete a vector store

     Permanently delete a vector store and remove all associated files

    Args:
        organization_id (str):
        vector_store_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        organization_id=organization_id,
        vector_store_id=vector_store_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    vector_store_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | HTTPValidationError]:
    """Delete a vector store

     Permanently delete a vector store and remove all associated files

    Args:
        organization_id (str):
        vector_store_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        vector_store_id=vector_store_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    vector_store_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | HTTPValidationError | None:
    """Delete a vector store

     Permanently delete a vector store and remove all associated files

    Args:
        organization_id (str):
        vector_store_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            vector_store_id=vector_store_id,
            client=client,
        )
    ).parsed
