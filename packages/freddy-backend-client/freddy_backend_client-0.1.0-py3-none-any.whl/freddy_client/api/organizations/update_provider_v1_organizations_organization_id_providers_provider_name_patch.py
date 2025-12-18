from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.update_provider_request import UpdateProviderRequest
from ...models.update_provider_v1_organizations_organization_id_providers_provider_name_patch_response_update_provider_v1_organizations_organization_id_providers_provider_name_patch import (
    UpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatchResponseUpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatch,
)
from ...types import Response


def _get_kwargs(
    organization_id: str,
    provider_name: str,
    *,
    body: UpdateProviderRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/v1/organizations/{organization_id}/providers/{provider_name}".format(
            organization_id=quote(str(organization_id), safe=""),
            provider_name=quote(str(provider_name), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    HTTPValidationError
    | UpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatchResponseUpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatch
    | None
):
    if response.status_code == 200:
        response_200 = UpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatchResponseUpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatch.from_dict(
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
    | UpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatchResponseUpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatch
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization_id: str,
    provider_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProviderRequest,
) -> Response[
    HTTPValidationError
    | UpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatchResponseUpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatch
]:
    """Update Provider

     Update provider configuration (enable/disable, update credentials).

    User must be an Admin or Owner of the organization.

    Args:
        organization_id (str):
        provider_name (str):
        body (UpdateProviderRequest): Schema for updating provider configuration.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatchResponseUpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatch]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        provider_name=provider_name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    provider_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProviderRequest,
) -> (
    HTTPValidationError
    | UpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatchResponseUpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatch
    | None
):
    """Update Provider

     Update provider configuration (enable/disable, update credentials).

    User must be an Admin or Owner of the organization.

    Args:
        organization_id (str):
        provider_name (str):
        body (UpdateProviderRequest): Schema for updating provider configuration.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatchResponseUpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatch
    """

    return sync_detailed(
        organization_id=organization_id,
        provider_name=provider_name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    provider_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProviderRequest,
) -> Response[
    HTTPValidationError
    | UpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatchResponseUpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatch
]:
    """Update Provider

     Update provider configuration (enable/disable, update credentials).

    User must be an Admin or Owner of the organization.

    Args:
        organization_id (str):
        provider_name (str):
        body (UpdateProviderRequest): Schema for updating provider configuration.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatchResponseUpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatch]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
        provider_name=provider_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    provider_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProviderRequest,
) -> (
    HTTPValidationError
    | UpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatchResponseUpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatch
    | None
):
    """Update Provider

     Update provider configuration (enable/disable, update credentials).

    User must be an Admin or Owner of the organization.

    Args:
        organization_id (str):
        provider_name (str):
        body (UpdateProviderRequest): Schema for updating provider configuration.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatchResponseUpdateProviderV1OrganizationsOrganizationIdProvidersProviderNamePatch
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            provider_name=provider_name,
            client=client,
            body=body,
        )
    ).parsed
