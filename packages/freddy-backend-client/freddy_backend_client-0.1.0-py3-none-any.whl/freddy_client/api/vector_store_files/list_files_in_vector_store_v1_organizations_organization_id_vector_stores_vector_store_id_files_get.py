from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.success_response_vector_store_file_list_response import (
    SuccessResponseVectorStoreFileListResponse,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    vector_store_id: str,
    *,
    page: int | Unset = 1,
    page_size: int | Unset = 20,
    status: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["page_size"] = page_size

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/organizations/{organization_id}/vector-stores/{vector_store_id}/files".format(
            organization_id=quote(str(organization_id), safe=""),
            vector_store_id=quote(str(vector_store_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SuccessResponseVectorStoreFileListResponse | None:
    if response.status_code == 200:
        response_200 = SuccessResponseVectorStoreFileListResponse.from_dict(
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
) -> Response[HTTPValidationError | SuccessResponseVectorStoreFileListResponse]:
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
    page: int | Unset = 1,
    page_size: int | Unset = 20,
    status: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SuccessResponseVectorStoreFileListResponse]:
    """List files in vector store

     Get a list of all files attached to a vector store. Supports both user and API key authentication.

    Args:
        organization_id (str): The unique identifier of the organization
        vector_store_id (str): The unique identifier of the vector store
        page (int | Unset): Page number for pagination Default: 1.
        page_size (int | Unset): Number of items per page Default: 20.
        status (None | str | Unset): Filter by processing status (comma-separated)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SuccessResponseVectorStoreFileListResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        vector_store_id=vector_store_id,
        page=page,
        page_size=page_size,
        status=status,
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
    page: int | Unset = 1,
    page_size: int | Unset = 20,
    status: None | str | Unset = UNSET,
) -> HTTPValidationError | SuccessResponseVectorStoreFileListResponse | None:
    """List files in vector store

     Get a list of all files attached to a vector store. Supports both user and API key authentication.

    Args:
        organization_id (str): The unique identifier of the organization
        vector_store_id (str): The unique identifier of the vector store
        page (int | Unset): Page number for pagination Default: 1.
        page_size (int | Unset): Number of items per page Default: 20.
        status (None | str | Unset): Filter by processing status (comma-separated)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SuccessResponseVectorStoreFileListResponse
    """

    return sync_detailed(
        organization_id=organization_id,
        vector_store_id=vector_store_id,
        client=client,
        page=page,
        page_size=page_size,
        status=status,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    vector_store_id: str,
    *,
    client: AuthenticatedClient | Client,
    page: int | Unset = 1,
    page_size: int | Unset = 20,
    status: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | SuccessResponseVectorStoreFileListResponse]:
    """List files in vector store

     Get a list of all files attached to a vector store. Supports both user and API key authentication.

    Args:
        organization_id (str): The unique identifier of the organization
        vector_store_id (str): The unique identifier of the vector store
        page (int | Unset): Page number for pagination Default: 1.
        page_size (int | Unset): Number of items per page Default: 20.
        status (None | str | Unset): Filter by processing status (comma-separated)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SuccessResponseVectorStoreFileListResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        vector_store_id=vector_store_id,
        page=page,
        page_size=page_size,
        status=status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    vector_store_id: str,
    *,
    client: AuthenticatedClient | Client,
    page: int | Unset = 1,
    page_size: int | Unset = 20,
    status: None | str | Unset = UNSET,
) -> HTTPValidationError | SuccessResponseVectorStoreFileListResponse | None:
    """List files in vector store

     Get a list of all files attached to a vector store. Supports both user and API key authentication.

    Args:
        organization_id (str): The unique identifier of the organization
        vector_store_id (str): The unique identifier of the vector store
        page (int | Unset): Page number for pagination Default: 1.
        page_size (int | Unset): Number of items per page Default: 20.
        status (None | str | Unset): Filter by processing status (comma-separated)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SuccessResponseVectorStoreFileListResponse
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            vector_store_id=vector_store_id,
            client=client,
            page=page,
            page_size=page_size,
            status=status,
        )
    ).parsed
