from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.file_upload_url_request import FileUploadUrlRequest
from ...models.file_upload_url_response import FileUploadUrlResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    organization_id: str,
    *,
    body: FileUploadUrlRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/organizations/{organization_id}/files/upload-url".format(
            organization_id=quote(str(organization_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> FileUploadUrlResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = FileUploadUrlResponse.from_dict(response.json())

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
) -> Response[FileUploadUrlResponse | HTTPValidationError]:
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
    body: FileUploadUrlRequest,
) -> Response[FileUploadUrlResponse | HTTPValidationError]:
    """Generate Upload Url

     Generate resumable upload URL for file (advanced).

    Returns a resumable upload session URI valid for 7 days.
    Client uploads directly to GCS using the resumable protocol.
    Use this for large files (>100MB) or when you need resumable uploads.

    For simpler uploads, use POST /files/upload instead.

    Args:
        organization_id (str):
        body (FileUploadUrlRequest): Request schema for generating upload URL. Example:
            {'file_size': 5242880, 'filename': 'document.pdf', 'mime_type': 'application/pdf',
            'upload_type': 'standard'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FileUploadUrlResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: FileUploadUrlRequest,
) -> FileUploadUrlResponse | HTTPValidationError | None:
    """Generate Upload Url

     Generate resumable upload URL for file (advanced).

    Returns a resumable upload session URI valid for 7 days.
    Client uploads directly to GCS using the resumable protocol.
    Use this for large files (>100MB) or when you need resumable uploads.

    For simpler uploads, use POST /files/upload instead.

    Args:
        organization_id (str):
        body (FileUploadUrlRequest): Request schema for generating upload URL. Example:
            {'file_size': 5242880, 'filename': 'document.pdf', 'mime_type': 'application/pdf',
            'upload_type': 'standard'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FileUploadUrlResponse | HTTPValidationError
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: FileUploadUrlRequest,
) -> Response[FileUploadUrlResponse | HTTPValidationError]:
    """Generate Upload Url

     Generate resumable upload URL for file (advanced).

    Returns a resumable upload session URI valid for 7 days.
    Client uploads directly to GCS using the resumable protocol.
    Use this for large files (>100MB) or when you need resumable uploads.

    For simpler uploads, use POST /files/upload instead.

    Args:
        organization_id (str):
        body (FileUploadUrlRequest): Request schema for generating upload URL. Example:
            {'file_size': 5242880, 'filename': 'document.pdf', 'mime_type': 'application/pdf',
            'upload_type': 'standard'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[FileUploadUrlResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: FileUploadUrlRequest,
) -> FileUploadUrlResponse | HTTPValidationError | None:
    """Generate Upload Url

     Generate resumable upload URL for file (advanced).

    Returns a resumable upload session URI valid for 7 days.
    Client uploads directly to GCS using the resumable protocol.
    Use this for large files (>100MB) or when you need resumable uploads.

    For simpler uploads, use POST /files/upload instead.

    Args:
        organization_id (str):
        body (FileUploadUrlRequest): Request schema for generating upload URL. Example:
            {'file_size': 5242880, 'filename': 'document.pdf', 'mime_type': 'application/pdf',
            'upload_type': 'standard'}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        FileUploadUrlResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            body=body,
        )
    ).parsed
