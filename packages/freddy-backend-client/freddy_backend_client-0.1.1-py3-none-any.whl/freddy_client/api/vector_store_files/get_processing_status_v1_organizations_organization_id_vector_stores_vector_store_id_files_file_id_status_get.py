from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.success_response_processing_status_response import (
    SuccessResponseProcessingStatusResponse,
)
from ...types import Response


def _get_kwargs(
    organization_id: str,
    vector_store_id: str,
    file_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/organizations/{organization_id}/vector-stores/{vector_store_id}/files/{file_id}/status".format(
            organization_id=quote(str(organization_id), safe=""),
            vector_store_id=quote(str(vector_store_id), safe=""),
            file_id=quote(str(file_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SuccessResponseProcessingStatusResponse | None:
    if response.status_code == 200:
        response_200 = SuccessResponseProcessingStatusResponse.from_dict(
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
) -> Response[HTTPValidationError | SuccessResponseProcessingStatusResponse]:
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
) -> Response[HTTPValidationError | SuccessResponseProcessingStatusResponse]:
    """Get processing status

     Get the processing status of a file in a vector store.

    Args:
        organization_id (str): Organization ID
        vector_store_id (str): Vector Store ID
        file_id (str): File ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SuccessResponseProcessingStatusResponse]
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
) -> HTTPValidationError | SuccessResponseProcessingStatusResponse | None:
    """Get processing status

     Get the processing status of a file in a vector store.

    Args:
        organization_id (str): Organization ID
        vector_store_id (str): Vector Store ID
        file_id (str): File ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SuccessResponseProcessingStatusResponse
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
) -> Response[HTTPValidationError | SuccessResponseProcessingStatusResponse]:
    """Get processing status

     Get the processing status of a file in a vector store.

    Args:
        organization_id (str): Organization ID
        vector_store_id (str): Vector Store ID
        file_id (str): File ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SuccessResponseProcessingStatusResponse]
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
) -> HTTPValidationError | SuccessResponseProcessingStatusResponse | None:
    """Get processing status

     Get the processing status of a file in a vector store.

    Args:
        organization_id (str): Organization ID
        vector_store_id (str): Vector Store ID
        file_id (str): File ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SuccessResponseProcessingStatusResponse
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            vector_store_id=vector_store_id,
            file_id=file_id,
            client=client,
        )
    ).parsed
