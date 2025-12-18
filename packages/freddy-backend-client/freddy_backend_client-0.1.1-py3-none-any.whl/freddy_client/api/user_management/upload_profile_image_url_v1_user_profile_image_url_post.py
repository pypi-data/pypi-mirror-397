from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.image_upload_response import ImageUploadResponse
from ...models.image_upload_url_request import ImageUploadUrlRequest
from ...types import Response


def _get_kwargs(
    *,
    body: ImageUploadUrlRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/user/profile/image/url",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ImageUploadResponse | None:
    if response.status_code == 200:
        response_200 = ImageUploadResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | ImageUploadResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ImageUploadUrlRequest,
) -> Response[HTTPValidationError | ImageUploadResponse]:
    r"""Upload Profile Image Url

     Upload a profile image from URL.

    Downloads an image from the provided URL and processes it into
    multiple sizes (thumbnail, medium, full). All images are converted to
    WebP format for optimal compression.

    **Requires Authentication:** Bearer token in Authorization header

    **Request Body:**
    ```json
    {
      \"image_url\": \"https://example.com/avatar.jpg\"
    }
    ```

    **Supported Formats:**
    - JPEG/JPG
    - PNG
    - WebP
    - GIF

    **Limits:**
    - Maximum file size: 10MB
    - Images are automatically resized to:
      - Thumbnail: 150x150px
      - Medium: 500x500px
      - Full: 1200x1200px

    **Returns:**
    - success: Whether the upload was successful
    - message: Success message
    - urls: Object with thumbnail, medium, and full size image URLs

    **Automatically Updates:** The user's profile_image field is updated
    with the full-size image URL.

    **Errors:**
    - 401: Not authenticated
    - 422: Invalid URL, download failed, invalid file type, or corrupted image

    Args:
        body (ImageUploadUrlRequest): Request schema for uploading image from URL.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ImageUploadResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: ImageUploadUrlRequest,
) -> HTTPValidationError | ImageUploadResponse | None:
    r"""Upload Profile Image Url

     Upload a profile image from URL.

    Downloads an image from the provided URL and processes it into
    multiple sizes (thumbnail, medium, full). All images are converted to
    WebP format for optimal compression.

    **Requires Authentication:** Bearer token in Authorization header

    **Request Body:**
    ```json
    {
      \"image_url\": \"https://example.com/avatar.jpg\"
    }
    ```

    **Supported Formats:**
    - JPEG/JPG
    - PNG
    - WebP
    - GIF

    **Limits:**
    - Maximum file size: 10MB
    - Images are automatically resized to:
      - Thumbnail: 150x150px
      - Medium: 500x500px
      - Full: 1200x1200px

    **Returns:**
    - success: Whether the upload was successful
    - message: Success message
    - urls: Object with thumbnail, medium, and full size image URLs

    **Automatically Updates:** The user's profile_image field is updated
    with the full-size image URL.

    **Errors:**
    - 401: Not authenticated
    - 422: Invalid URL, download failed, invalid file type, or corrupted image

    Args:
        body (ImageUploadUrlRequest): Request schema for uploading image from URL.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ImageUploadResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ImageUploadUrlRequest,
) -> Response[HTTPValidationError | ImageUploadResponse]:
    r"""Upload Profile Image Url

     Upload a profile image from URL.

    Downloads an image from the provided URL and processes it into
    multiple sizes (thumbnail, medium, full). All images are converted to
    WebP format for optimal compression.

    **Requires Authentication:** Bearer token in Authorization header

    **Request Body:**
    ```json
    {
      \"image_url\": \"https://example.com/avatar.jpg\"
    }
    ```

    **Supported Formats:**
    - JPEG/JPG
    - PNG
    - WebP
    - GIF

    **Limits:**
    - Maximum file size: 10MB
    - Images are automatically resized to:
      - Thumbnail: 150x150px
      - Medium: 500x500px
      - Full: 1200x1200px

    **Returns:**
    - success: Whether the upload was successful
    - message: Success message
    - urls: Object with thumbnail, medium, and full size image URLs

    **Automatically Updates:** The user's profile_image field is updated
    with the full-size image URL.

    **Errors:**
    - 401: Not authenticated
    - 422: Invalid URL, download failed, invalid file type, or corrupted image

    Args:
        body (ImageUploadUrlRequest): Request schema for uploading image from URL.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ImageUploadResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ImageUploadUrlRequest,
) -> HTTPValidationError | ImageUploadResponse | None:
    r"""Upload Profile Image Url

     Upload a profile image from URL.

    Downloads an image from the provided URL and processes it into
    multiple sizes (thumbnail, medium, full). All images are converted to
    WebP format for optimal compression.

    **Requires Authentication:** Bearer token in Authorization header

    **Request Body:**
    ```json
    {
      \"image_url\": \"https://example.com/avatar.jpg\"
    }
    ```

    **Supported Formats:**
    - JPEG/JPG
    - PNG
    - WebP
    - GIF

    **Limits:**
    - Maximum file size: 10MB
    - Images are automatically resized to:
      - Thumbnail: 150x150px
      - Medium: 500x500px
      - Full: 1200x1200px

    **Returns:**
    - success: Whether the upload was successful
    - message: Success message
    - urls: Object with thumbnail, medium, and full size image URLs

    **Automatically Updates:** The user's profile_image field is updated
    with the full-size image URL.

    **Errors:**
    - 401: Not authenticated
    - 422: Invalid URL, download failed, invalid file type, or corrupted image

    Args:
        body (ImageUploadUrlRequest): Request schema for uploading image from URL.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ImageUploadResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
