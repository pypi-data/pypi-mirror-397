from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.limit_update_request import LimitUpdateRequest
from ...models.limit_update_response import LimitUpdateResponse
from ...types import Response


def _get_kwargs(
    org_id: str,
    *,
    body: LimitUpdateRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/analytics/usage/limits/{org_id}".format(
            org_id=quote(str(org_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | LimitUpdateResponse | None:
    if response.status_code == 200:
        response_200 = LimitUpdateResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | LimitUpdateResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: LimitUpdateRequest,
) -> Response[HTTPValidationError | LimitUpdateResponse]:
    """Update Usage Limits

     Update organization, total API key, and/or individual API key spending limits.

    Supports multiple update modes:
    1. Update organization limit only (provide `monthlyApiLimit`)
    2. Update total API key limit only (provide `totalApiKeyLimit`)
    3. Update individual API key limit only (provide `apiKeyId` and `apiKeyLimit`)
    4. Update any combination of the above limits atomically

    **Request Body:**
    - `monthlyApiLimit` (optional): Organization limit in CHF (must be > 0)
    - `totalApiKeyLimit` (optional): Total API key limit in CHF (must be > 0)
    - `apiKeyId` (optional): API key ID
    - `apiKeyLimit` (optional): Individual API key limit in CHF (must be > 0)

    **Validation:**
    - At least one field must be provided
    - All provided limits must be positive numbers (> 0)
    - If `apiKeyId` provided, `apiKeyLimit` must also be provided
    - API key must belong to the specified organization
    - Total API key limit cannot exceed organization limit

    **Cross-Limit Constraints:**
    - Total API key limit ≤ organization limit (if org limit configured)
    - Validation applies when updating either limit or both simultaneously
    - Returns 422 error if constraint violated

    **Cache Behavior:**
    - If limit is increased above current usage, exceeded cache is cleared
    - If limit is still below usage, exceeded cache is retained
    - Requests are immediately allowed/blocked based on new limits

    **Atomic Updates:**
    - When updating multiple limits, either all succeed or all fail
    - No partial updates on validation errors

    **Perfect for:**
    - Budget adjustments
    - API key provisioning
    - Cost control management
    - Emergency limit increases

    Args:
        org_id (str):
        body (LimitUpdateRequest): Request model for PUT /v1/analytics/usage/limits/{org_id}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | LimitUpdateResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: LimitUpdateRequest,
) -> HTTPValidationError | LimitUpdateResponse | None:
    """Update Usage Limits

     Update organization, total API key, and/or individual API key spending limits.

    Supports multiple update modes:
    1. Update organization limit only (provide `monthlyApiLimit`)
    2. Update total API key limit only (provide `totalApiKeyLimit`)
    3. Update individual API key limit only (provide `apiKeyId` and `apiKeyLimit`)
    4. Update any combination of the above limits atomically

    **Request Body:**
    - `monthlyApiLimit` (optional): Organization limit in CHF (must be > 0)
    - `totalApiKeyLimit` (optional): Total API key limit in CHF (must be > 0)
    - `apiKeyId` (optional): API key ID
    - `apiKeyLimit` (optional): Individual API key limit in CHF (must be > 0)

    **Validation:**
    - At least one field must be provided
    - All provided limits must be positive numbers (> 0)
    - If `apiKeyId` provided, `apiKeyLimit` must also be provided
    - API key must belong to the specified organization
    - Total API key limit cannot exceed organization limit

    **Cross-Limit Constraints:**
    - Total API key limit ≤ organization limit (if org limit configured)
    - Validation applies when updating either limit or both simultaneously
    - Returns 422 error if constraint violated

    **Cache Behavior:**
    - If limit is increased above current usage, exceeded cache is cleared
    - If limit is still below usage, exceeded cache is retained
    - Requests are immediately allowed/blocked based on new limits

    **Atomic Updates:**
    - When updating multiple limits, either all succeed or all fail
    - No partial updates on validation errors

    **Perfect for:**
    - Budget adjustments
    - API key provisioning
    - Cost control management
    - Emergency limit increases

    Args:
        org_id (str):
        body (LimitUpdateRequest): Request model for PUT /v1/analytics/usage/limits/{org_id}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | LimitUpdateResponse
    """

    return sync_detailed(
        org_id=org_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: LimitUpdateRequest,
) -> Response[HTTPValidationError | LimitUpdateResponse]:
    """Update Usage Limits

     Update organization, total API key, and/or individual API key spending limits.

    Supports multiple update modes:
    1. Update organization limit only (provide `monthlyApiLimit`)
    2. Update total API key limit only (provide `totalApiKeyLimit`)
    3. Update individual API key limit only (provide `apiKeyId` and `apiKeyLimit`)
    4. Update any combination of the above limits atomically

    **Request Body:**
    - `monthlyApiLimit` (optional): Organization limit in CHF (must be > 0)
    - `totalApiKeyLimit` (optional): Total API key limit in CHF (must be > 0)
    - `apiKeyId` (optional): API key ID
    - `apiKeyLimit` (optional): Individual API key limit in CHF (must be > 0)

    **Validation:**
    - At least one field must be provided
    - All provided limits must be positive numbers (> 0)
    - If `apiKeyId` provided, `apiKeyLimit` must also be provided
    - API key must belong to the specified organization
    - Total API key limit cannot exceed organization limit

    **Cross-Limit Constraints:**
    - Total API key limit ≤ organization limit (if org limit configured)
    - Validation applies when updating either limit or both simultaneously
    - Returns 422 error if constraint violated

    **Cache Behavior:**
    - If limit is increased above current usage, exceeded cache is cleared
    - If limit is still below usage, exceeded cache is retained
    - Requests are immediately allowed/blocked based on new limits

    **Atomic Updates:**
    - When updating multiple limits, either all succeed or all fail
    - No partial updates on validation errors

    **Perfect for:**
    - Budget adjustments
    - API key provisioning
    - Cost control management
    - Emergency limit increases

    Args:
        org_id (str):
        body (LimitUpdateRequest): Request model for PUT /v1/analytics/usage/limits/{org_id}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | LimitUpdateResponse]
    """

    kwargs = _get_kwargs(
        org_id=org_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    org_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: LimitUpdateRequest,
) -> HTTPValidationError | LimitUpdateResponse | None:
    """Update Usage Limits

     Update organization, total API key, and/or individual API key spending limits.

    Supports multiple update modes:
    1. Update organization limit only (provide `monthlyApiLimit`)
    2. Update total API key limit only (provide `totalApiKeyLimit`)
    3. Update individual API key limit only (provide `apiKeyId` and `apiKeyLimit`)
    4. Update any combination of the above limits atomically

    **Request Body:**
    - `monthlyApiLimit` (optional): Organization limit in CHF (must be > 0)
    - `totalApiKeyLimit` (optional): Total API key limit in CHF (must be > 0)
    - `apiKeyId` (optional): API key ID
    - `apiKeyLimit` (optional): Individual API key limit in CHF (must be > 0)

    **Validation:**
    - At least one field must be provided
    - All provided limits must be positive numbers (> 0)
    - If `apiKeyId` provided, `apiKeyLimit` must also be provided
    - API key must belong to the specified organization
    - Total API key limit cannot exceed organization limit

    **Cross-Limit Constraints:**
    - Total API key limit ≤ organization limit (if org limit configured)
    - Validation applies when updating either limit or both simultaneously
    - Returns 422 error if constraint violated

    **Cache Behavior:**
    - If limit is increased above current usage, exceeded cache is cleared
    - If limit is still below usage, exceeded cache is retained
    - Requests are immediately allowed/blocked based on new limits

    **Atomic Updates:**
    - When updating multiple limits, either all succeed or all fail
    - No partial updates on validation errors

    **Perfect for:**
    - Budget adjustments
    - API key provisioning
    - Cost control management
    - Emergency limit increases

    Args:
        org_id (str):
        body (LimitUpdateRequest): Request model for PUT /v1/analytics/usage/limits/{org_id}.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | LimitUpdateResponse
    """

    return (
        await asyncio_detailed(
            org_id=org_id,
            client=client,
            body=body,
        )
    ).parsed
