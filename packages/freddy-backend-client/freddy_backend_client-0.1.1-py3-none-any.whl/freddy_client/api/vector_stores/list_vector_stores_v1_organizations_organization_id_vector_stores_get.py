from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.success_response_list_vector_store_response import (
    SuccessResponseListVectorStoreResponse,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization_id: str,
    *,
    search: None | str | Unset = UNSET,
    access_mode: None | str | Unset = UNSET,
    skip: int | Unset = 0,
    take: int | Unset = 20,
    sort: str | Unset = "created_at",
    order: str | Unset = "desc",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_search: None | str | Unset
    if isinstance(search, Unset):
        json_search = UNSET
    else:
        json_search = search
    params["search"] = json_search

    json_access_mode: None | str | Unset
    if isinstance(access_mode, Unset):
        json_access_mode = UNSET
    else:
        json_access_mode = access_mode
    params["access_mode"] = json_access_mode

    params["skip"] = skip

    params["take"] = take

    params["sort"] = sort

    params["order"] = order

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/organizations/{organization_id}/vector-stores".format(
            organization_id=quote(str(organization_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SuccessResponseListVectorStoreResponse | None:
    if response.status_code == 200:
        response_200 = SuccessResponseListVectorStoreResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | SuccessResponseListVectorStoreResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    search: None | str | Unset = UNSET,
    access_mode: None | str | Unset = UNSET,
    skip: int | Unset = 0,
    take: int | Unset = 20,
    sort: str | Unset = "created_at",
    order: str | Unset = "desc",
) -> Response[HTTPValidationError | SuccessResponseListVectorStoreResponse]:
    """List vector stores

     Retrieve a list of all vector stores in an organization that the user has access to. Supports
    filtering and search.

    Args:
        organization_id (str):
        search (None | str | Unset): Search by vector store name
        access_mode (None | str | Unset): Filter by access mode (public, organization, department,
            private)
        skip (int | Unset): Number of records to skip Default: 0.
        take (int | Unset): Number of records to return Default: 20.
        sort (str | Unset): Field to sort by Default: 'created_at'.
        order (str | Unset): Sort order (asc or desc) Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SuccessResponseListVectorStoreResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        search=search,
        access_mode=access_mode,
        skip=skip,
        take=take,
        sort=sort,
        order=order,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    search: None | str | Unset = UNSET,
    access_mode: None | str | Unset = UNSET,
    skip: int | Unset = 0,
    take: int | Unset = 20,
    sort: str | Unset = "created_at",
    order: str | Unset = "desc",
) -> HTTPValidationError | SuccessResponseListVectorStoreResponse | None:
    """List vector stores

     Retrieve a list of all vector stores in an organization that the user has access to. Supports
    filtering and search.

    Args:
        organization_id (str):
        search (None | str | Unset): Search by vector store name
        access_mode (None | str | Unset): Filter by access mode (public, organization, department,
            private)
        skip (int | Unset): Number of records to skip Default: 0.
        take (int | Unset): Number of records to return Default: 20.
        sort (str | Unset): Field to sort by Default: 'created_at'.
        order (str | Unset): Sort order (asc or desc) Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SuccessResponseListVectorStoreResponse
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        search=search,
        access_mode=access_mode,
        skip=skip,
        take=take,
        sort=sort,
        order=order,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    search: None | str | Unset = UNSET,
    access_mode: None | str | Unset = UNSET,
    skip: int | Unset = 0,
    take: int | Unset = 20,
    sort: str | Unset = "created_at",
    order: str | Unset = "desc",
) -> Response[HTTPValidationError | SuccessResponseListVectorStoreResponse]:
    """List vector stores

     Retrieve a list of all vector stores in an organization that the user has access to. Supports
    filtering and search.

    Args:
        organization_id (str):
        search (None | str | Unset): Search by vector store name
        access_mode (None | str | Unset): Filter by access mode (public, organization, department,
            private)
        skip (int | Unset): Number of records to skip Default: 0.
        take (int | Unset): Number of records to return Default: 20.
        sort (str | Unset): Field to sort by Default: 'created_at'.
        order (str | Unset): Sort order (asc or desc) Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SuccessResponseListVectorStoreResponse]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        search=search,
        access_mode=access_mode,
        skip=skip,
        take=take,
        sort=sort,
        order=order,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    search: None | str | Unset = UNSET,
    access_mode: None | str | Unset = UNSET,
    skip: int | Unset = 0,
    take: int | Unset = 20,
    sort: str | Unset = "created_at",
    order: str | Unset = "desc",
) -> HTTPValidationError | SuccessResponseListVectorStoreResponse | None:
    """List vector stores

     Retrieve a list of all vector stores in an organization that the user has access to. Supports
    filtering and search.

    Args:
        organization_id (str):
        search (None | str | Unset): Search by vector store name
        access_mode (None | str | Unset): Filter by access mode (public, organization, department,
            private)
        skip (int | Unset): Number of records to skip Default: 0.
        take (int | Unset): Number of records to return Default: 20.
        sort (str | Unset): Field to sort by Default: 'created_at'.
        order (str | Unset): Sort order (asc or desc) Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SuccessResponseListVectorStoreResponse
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            search=search,
            access_mode=access_mode,
            skip=skip,
            take=take,
            sort=sort,
            order=order,
        )
    ).parsed
