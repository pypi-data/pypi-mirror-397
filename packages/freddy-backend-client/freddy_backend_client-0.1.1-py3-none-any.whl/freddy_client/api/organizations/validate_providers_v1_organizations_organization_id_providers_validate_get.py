from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.validate_providers_v1_organizations_organization_id_providers_validate_get_response_validate_providers_v1_organizations_organization_id_providers_validate_get import (
    ValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGetResponseValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGet,
)
from ...types import Response


def _get_kwargs(
    organization_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/organizations/{organization_id}/providers/validate".format(
            organization_id=quote(str(organization_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    HTTPValidationError
    | ValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGetResponseValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGet
    | None
):
    if response.status_code == 200:
        response_200 = ValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGetResponseValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGet.from_dict(
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
    | ValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGetResponseValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGet
]:
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
) -> Response[
    HTTPValidationError
    | ValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGetResponseValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGet
]:
    """Validate Providers

     Validate all provider configurations for the organization.

    Args:
        organization_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGetResponseValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGet]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> (
    HTTPValidationError
    | ValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGetResponseValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGet
    | None
):
    """Validate Providers

     Validate all provider configurations for the organization.

    Args:
        organization_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGetResponseValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGet
    """

    return sync_detailed(
        organization_id=organization_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[
    HTTPValidationError
    | ValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGetResponseValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGet
]:
    """Validate Providers

     Validate all provider configurations for the organization.

    Args:
        organization_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGetResponseValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGet]
    """

    kwargs = _get_kwargs(
        organization_id=organization_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> (
    HTTPValidationError
    | ValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGetResponseValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGet
    | None
):
    """Validate Providers

     Validate all provider configurations for the organization.

    Args:
        organization_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGetResponseValidateProvidersV1OrganizationsOrganizationIdProvidersValidateGet
    """

    return (
        await asyncio_detailed(
            organization_id=organization_id,
            client=client,
        )
    ).parsed
