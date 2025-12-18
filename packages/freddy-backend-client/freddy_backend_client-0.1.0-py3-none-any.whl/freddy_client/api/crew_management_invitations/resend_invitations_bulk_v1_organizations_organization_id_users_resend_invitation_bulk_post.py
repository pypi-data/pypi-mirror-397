from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.bulk_invitation_request import BulkInvitationRequest
from ...models.bulk_operation_response import BulkOperationResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    organization_id: str,
    *,
    body: BulkInvitationRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/organizations/{organization_id}/users/resend-invitation-bulk".format(
            organization_id=quote(str(organization_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> BulkOperationResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = BulkOperationResponse.from_dict(response.json())

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
) -> Response[BulkOperationResponse | HTTPValidationError]:
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
    body: BulkInvitationRequest,
) -> Response[BulkOperationResponse | HTTPValidationError]:
    """Resend Invitations Bulk

     Bulk resend invitations with partial failure handling.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        request: List of user IDs to resend invitations to
        db: Database session
        auth: Authenticated user

    Returns:
        Bulk operation response with success/failure counts

    Args:
        organization_id (str): Organization ID
        body (BulkInvitationRequest): Schema for bulk invitation resend request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BulkOperationResponse | HTTPValidationError]
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
    body: BulkInvitationRequest,
) -> BulkOperationResponse | HTTPValidationError | None:
    """Resend Invitations Bulk

     Bulk resend invitations with partial failure handling.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        request: List of user IDs to resend invitations to
        db: Database session
        auth: Authenticated user

    Returns:
        Bulk operation response with success/failure counts

    Args:
        organization_id (str): Organization ID
        body (BulkInvitationRequest): Schema for bulk invitation resend request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BulkOperationResponse | HTTPValidationError
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
    body: BulkInvitationRequest,
) -> Response[BulkOperationResponse | HTTPValidationError]:
    """Resend Invitations Bulk

     Bulk resend invitations with partial failure handling.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        request: List of user IDs to resend invitations to
        db: Database session
        auth: Authenticated user

    Returns:
        Bulk operation response with success/failure counts

    Args:
        organization_id (str): Organization ID
        body (BulkInvitationRequest): Schema for bulk invitation resend request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BulkOperationResponse | HTTPValidationError]
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
    body: BulkInvitationRequest,
) -> BulkOperationResponse | HTTPValidationError | None:
    """Resend Invitations Bulk

     Bulk resend invitations with partial failure handling.

    Requires:
    - User must be authenticated
    - User must be a member of the organization
    - User must have Admin or Owner role

    Args:
        organization_id: Organization ID
        request: List of user IDs to resend invitations to
        db: Database session
        auth: Authenticated user

    Returns:
        Bulk operation response with success/failure counts

    Args:
        organization_id (str): Organization ID
        body (BulkInvitationRequest): Schema for bulk invitation resend request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BulkOperationResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
            body=body,
        )
    ).parsed
