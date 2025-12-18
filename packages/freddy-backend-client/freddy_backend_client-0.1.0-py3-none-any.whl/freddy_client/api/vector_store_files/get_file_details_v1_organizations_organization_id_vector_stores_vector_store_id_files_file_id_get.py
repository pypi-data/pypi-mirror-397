from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.success_response_vector_store_file_response import (
    SuccessResponseVectorStoreFileResponse,
)
from ...types import Response


def _get_kwargs(
    organization_id: str,
    vector_store_id: str,
    file_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/organizations/{organization_id}/vector-stores/{vector_store_id}/files/{file_id}".format(
            organization_id=quote(str(organization_id), safe=""),
            vector_store_id=quote(str(vector_store_id), safe=""),
            file_id=quote(str(file_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SuccessResponseVectorStoreFileResponse | None:
    if response.status_code == 200:
        response_200 = SuccessResponseVectorStoreFileResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | SuccessResponseVectorStoreFileResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    vector_store_id: str,
    file_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | SuccessResponseVectorStoreFileResponse]:
    """Get detailed file information

     Get complete details about a specific file in a vector store, including processing status and
    metadata.

    Args:
        organization_id (str): The unique identifier of the organization
        vector_store_id (str): The unique identifier of the vector store
        file_id (str): The unique identifier of the file

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SuccessResponseVectorStoreFileResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        vector_store_id=vector_store_id,
        file_id=file_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    vector_store_id: str,
    file_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | SuccessResponseVectorStoreFileResponse | None:
    """Get detailed file information

     Get complete details about a specific file in a vector store, including processing status and
    metadata.

    Args:
        organization_id (str): The unique identifier of the organization
        vector_store_id (str): The unique identifier of the vector store
        file_id (str): The unique identifier of the file

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SuccessResponseVectorStoreFileResponse
    """

    return sync_detailed(
        organization_id=organization_id,
        vector_store_id=vector_store_id,
        file_id=file_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    vector_store_id: str,
    file_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | SuccessResponseVectorStoreFileResponse]:
    """Get detailed file information

     Get complete details about a specific file in a vector store, including processing status and
    metadata.

    Args:
        organization_id (str): The unique identifier of the organization
        vector_store_id (str): The unique identifier of the vector store
        file_id (str): The unique identifier of the file

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SuccessResponseVectorStoreFileResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        vector_store_id=vector_store_id,
        file_id=file_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    vector_store_id: str,
    file_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | SuccessResponseVectorStoreFileResponse | None:
    """Get detailed file information

     Get complete details about a specific file in a vector store, including processing status and
    metadata.

    Args:
        organization_id (str): The unique identifier of the organization
        vector_store_id (str): The unique identifier of the vector store
        file_id (str): The unique identifier of the file

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SuccessResponseVectorStoreFileResponse
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            vector_store_id=vector_store_id,
            file_id=file_id,
            client=client,
        )
    ).parsed
